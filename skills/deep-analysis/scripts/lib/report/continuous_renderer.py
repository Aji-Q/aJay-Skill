"""Continuous, task-led report. Reuses audited server-rendered research, not an iframe.

The index consumes only HTML emitted by assemble_report after its escaping/quality
boundary. Raw provider strings are never interpreted as HTML by this module.
"""
from __future__ import annotations
from html import escape
from html.parser import HTMLParser
import json
import re
from lib.report.council import build_council
from lib.report.council_renderer import ASSETS, json_safe, uri
from lib.report.model_supplement import render_model_supplement
from lib.report.valuation_brief import render_valuation_brief
from lib.report.chan_desk import render_chan_desk

VOID = {'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'}

class ReportIndex(HTMLParser):
    """Source-span index preserves SVG, escaping and table markup byte-for-byte."""
    def __init__(self, source):
        super().__init__(convert_charrefs=False)
        self.source, self.nodes, self.stack = source, [], []
        self.lines = [0]
        for match in re.finditer('\n', source): self.lines.append(match.end())
        self.feed(source)
    def source_offset(self):
        line, col = self.getpos()
        return self.lines[line-1] + col
    def handle_starttag(self, tag, attrs):
        start = self.source_offset()
        node = {'tag':tag, 'attrs':dict(attrs), 'start':start,
                'inside':start+len(self.get_starttag_text()), 'end':None, 'close':None}
        self.nodes.append(node)
        if tag in VOID: node.update(end=node['inside'], close=node['inside'])
        else: self.stack.append(node)
    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID:
            node=self.stack.pop();node.update(end=node['inside'],close=node['inside'])
    def handle_endtag(self, tag):
        for i in range(len(self.stack)-1, -1, -1):
            if self.stack[i]['tag'] == tag:
                close=self.source_offset();end=self.source.find('>',close)+1
                for node in self.stack[i:]:node.update(close=close,end=end)
                del self.stack[i:]
                break
    def select(self, cls=None, id=None, tag=None, within=None):
        return [n for n in self.nodes if n['end'] is not None
                and (not cls or cls in n['attrs'].get('class','').split())
                and (not id or id==n['attrs'].get('id')) and (not tag or tag==n['tag'])
                and (not within or within['inside']<=n['start']<within['close'])]
    def html(self, node, inner=False):
        return self.source[node['inside'] if inner else node['start']:node['close'] if inner else node['end']]
    def first(self, **selector):
        nodes=self.select(**selector)
        return self.html(nodes[0]) if nodes else ''

# Remove legacy ornamental glyphs, not mathematical operators or numeric evidence.
ORNAMENTS=re.compile('[\U0001f000-\U0001faff\u2600-\u27bf\u2b50\ufe0e\ufe0f]')

# Explicit presentation adapter for reused, server-rendered fragments. It does
# not inspect/infer financial meaning from values, and never touches raw JSON.
PRESENTATION_COLORS = {
    '#fff':'--bg-card', '#ffffff':'--bg-card', '#f8fafc':'--bg-card',
    '#f9fafb':'--bg-card', '#f3f4f6':'--bg-tinted', '#f1f5f9':'--bg-tinted',
    '#e5e7eb':'--border-soft', '#e2e8f0':'--border-soft', '#cbd5e1':'--border',
    '#111':'--text-bright', '#111827':'--text-bright', '#0f172a':'--text-bright',
    '#1e293b':'--text-bright', '#334155':'--text-main', '#374151':'--text-main',
    '#475569':'--text-mid', '#64748b':'--text-mid', '#6b7280':'--text-mid',
    '#9ca3af':'--text-dim', '#94a3b8':'--text-dim',
    '#0369a1':'--neon-cyan', '#0891b2':'--neon-cyan', '#06b6d4':'--neon-cyan',
    '#059669':'--bull-green', '#10b981':'--bull-green', '#065f46':'--heat-positive',
    '#ef4444':'--bear-red', '#dc2626':'--bear-red', '#b91c1c':'--heat-negative',
    '#f59e0b':'--neon-gold', '#d97706':'--neon-gold', '#f97316':'--heat-caution',
    # Semantic legacy fills: summaries / target peers, gains, losses and information.
    '#fef3c7':'--gold-tint', '#fffbeb':'--gold-tint', '#fef9c3':'--gold-tint',
    '#cffafe':'--cyan-tint', '#e0f2fe':'--cyan-tint', '#eff6ff':'--cyan-tint',
    '#d1fae5':'--bull-tint', '#dcfce7':'--bull-tint', '#ecfdf5':'--bull-tint',
    '#fee2e2':'--bear-tint', '#fef2f2':'--bear-tint',
    '#e0e7ff':'--cyan-tint', '#f3e8ff':'--cyan-tint',
}

def normalize_presentation(markup):
    def style(match):
        declarations=[]
        for declaration in match[1].split(';'):
            key, sep, value=declaration.partition(':')
            if not sep or key.strip().lower() in {'box-shadow','animation','border-radius'}:
                continue
            if 'var(' not in value and key.strip().lower() in {'color','background','background-color','border','border-color','border-top','border-bottom','fill','stroke'}:
                def color(token):
                    literal=token[0].lower()
                    role=PRESENTATION_COLORS.get(literal)
                    if key.strip().lower()=='color' and literal in {'#fff','#ffffff'}:
                        role='--text-bright'
                    return f'var({role},{literal})' if role else literal
                value=re.sub(r'#[0-9a-fA-F]{3,8}\b',color,value)
            declarations.append(key+sep+value)
        return 'style="'+';'.join(declarations)+'"'
    return re.sub(r'style="([^"]*)"',style,markup)

def clean(markup):
    markup=re.sub(r'<img\b[^>]*\bsrc="avatars/[^>]*>', '', markup)
    return normalize_presentation(ORNAMENTS.sub('',markup).replace('★','').replace('☆',''))

def committee_record(markup):
    """Translate the legacy game vocabulary into an IC comparison record.

    Class names stay stable because the standalone interaction layer and old
    exports still target them; only user-facing semantics change here.
    """
    substitutions = (
        ('THE GREAT DIVIDE', 'THE INVESTMENT COMMITTEE RECORD'),
        ('最看多 VS 最看空', '支持、挑战与待核验'),
        ('▶ BULL', 'SUPPORT / 支持方'),
        ('BEAR ◀', 'CHALLENGE / 挑战方'),
        ('<div class="sub">VS</div>', '<div class="sub">对照</div>'),
        ('<div class="round-label">ROUND 1</div>', '<div class="round-label">01 / 核心论点</div>'),
        ('<div class="round-label">ROUND 2</div>', '<div class="round-label">02 / 证据展开</div>'),
        ('<div class="round-label">ROUND 3</div>', '<div class="round-label">03 / 当前结论</div>'),
        ('<div class="round-vs">VS</div>', '<div class="round-vs" aria-hidden="true"></div>'),
        ('看多核心：', '支持：'),
        ('看空核心：', '挑战：'),
        ('<div class="conf-label">SCORE</div>', '<div class="conf-label">规则分</div>'),
    )
    for old, new in substitutions:
        markup = markup.replace(old, new)
    markup = re.sub(r'综合看，[^。]*我的立场不变。', '支持方规则草稿维持支持；仍需核对独立证据。', markup)
    markup = re.sub(r'综合看，[^。]*风险大于收益。', '挑战方规则草稿认为风险大于收益；仍需核对适用性。', markup)
    return markup

def panel_record(markup):
    """Keep the legacy aggregate visible without mislabelling it agreement."""
    markup = markup.replace('Agreement · 模拟一致度', 'Panel score · 原始聚合分')
    return re.sub(
        r'(<div class="stat-tile total"><div class="num">)([^<]+)%',
        r'\g<1>\2 / 100',
        markup,
        count=1,
    )

def render_continuous(raw, analysis, legacy_html):
    raw=raw if isinstance(raw,dict) else {}
    idx=ReportIndex(legacy_html)
    council=build_council(raw)
    basic=((raw.get('dimensions') or {}).get('0_basic') or {}).get('data') or {}
    name=escape(str(basic.get('name') or raw.get('name') or raw.get('ticker') or '研究报告'))
    ticker=escape(str(raw.get('ticker') or '—'))
    categories=idx.select(cls='research-category')
    def category(i): return clean(idx.html(categories[i])) if len(categories)>i else ''
    market_html=category(1)
    technical_html=''
    if len(categories)>1:
        technical=next((n for n in idx.select(cls='dim-card',within=categories[1])
                        if n['attrs'].get('data-dim')=='02'),None)
        if technical:
            # Preserve the ordinary technical record exactly once, below the new
            # main workbench. Expanding its JSON never changes chart/photo sizing.
            technical_html=clean(idx.html(technical))
            market_html=clean(idx.html(categories[1]).replace(idx.html(technical),'',1))
    fin=idx.select(cls='dim-card',within=categories[0]) if categories else []
    def card(i):return clean(idx.html(fin[i])) if len(fin)>i else '<p>维度未评估</p>'
    def block(cls):return clean(idx.first(cls=cls))
    def observed(dim, key):
        return next((f['text'] for f in council['evidence'][dim]['facts'] if f['id'].endswith('.'+key)), '未记录')
    financial_point=observed('1_financials','roe_latest')
    growth_point=observed('1_financials','revenue_growth')
    governance=council['evidence']['11_governance']['status']
    governance_point='治理记录缺失，尚待核验' if governance=='missing' else '治理记录须与原始披露交叉核验'
    def quality_snapshot(label, text, evidence, note):
        return f'<button class="quality-snapshot evidence-link" type="button" data-evidence="{evidence}"><span>{escape(label)}<small>{escape(note)}</small></span><strong>{escape(text)} <i aria-hidden="true">↗</i></strong></button>'
    chat_html=block('chat-container')
    if governance=='missing':
        # A missing fixture field must not remain inside a "passed rules" list.
        chat_html=re.sub(r'\s*•\s*\[权\d+\]\s*治理干净', '', chat_html)
        chat_html=chat_html.replace('治理干净','治理材料缺失 · 待核验')
    hero=block('hero-copy').replace('href="#section-core"','href="#briefing-detail"')
    conclusion=idx.select(cls='text',within=idx.select(cls='core-conclusion')[0]) if idx.select(cls='core-conclusion') else []
    conclusion_html=idx.html(conclusion[0],inner=True) if conclusion else '当前证据尚不足以形成完整研究结论。'
    hero=re.sub(r'<p class="one-liner">.*?</p>',lambda _: '<p class="one-liner">'+conclusion_html+'</p>',hero,flags=re.S)
    brief=f'<div class="arrival-findings"><p><span>支持核验</span><button class="evidence-link" type="button" data-evidence="1_financials">{escape(financial_point)} ↗</button></p><p><span>反证 / 缺口</span><button class="evidence-link" type="button" data-evidence="11_governance">{escape(governance_point)} ↗</button></p></div>'
    hero=hero.replace('<div class="price-row">',brief+'<div class="price-row">',1)
    hero=hero.replace('href="#briefing-detail"','href="#section-modeling"').replace('阅读研究 <span','进入估值 <span')
    stage, assumptions_html=render_valuation_brief(raw)
    photos=json.loads((ASSETS/'ajay-council/photography.json').read_text())
    def photo(city, cls):
        item=next(p for p in photos if p['id']==city)
        notes=''
        dimensions=''
        if city=='shanghai':
            dimensions=' width="4994" height="11270"'
            notes='<nav class="tower-notes" aria-label="建筑研究导航">'+''.join(
                f'<div class="tower-marker" data-research-marker="{anchor}"><a href="#{anchor}" class="tower-anchor" data-research-target="{anchor}"><span>{label}</span><b aria-hidden="true">↗</b></a><div class="tower-detail"><p>{escape(point)}</p><button type="button" class="evidence-link" data-evidence="{key}">核对来源 ↗</button></div></div>'
                for anchor,label,point,key in [('quality-return','I / 回报记录',financial_point,'1_financials'),('quality-growth','II / 增长来源',growth_point,'1_financials'),('quality-governance','III / 治理根基',governance_point,'11_governance')])+'</nav>'
            notes+='<span class="tower-navigation-note">研究导航 · 楼层位置不代表财务评分</span>'
        return f'<figure class="location {cls}"><img src="{uri(ASSETS/"ajay-council"/item["asset"])}" alt="{escape(item["description"],quote=True)}"{dimensions} {"fetchpriority=high" if city=="new-york" else "loading=lazy"}>{notes}<figcaption class="image-credit-mark"><a href="#visual-notes" aria-label="图像来源与生成说明">*</a></figcaption></figure>'
    def voice(person, topic, size='compact'):
        p=next(p for p in council['profiles'] if p['id']==person)
        v=next(v for t in council['topics'] if t['id']==topic for v in t['voices'] if v['id']==person)
        image=ASSETS/('ajay-brand' if person in ('buffett','simons') else 'ajay-council')/(person+'-portrait.png')
        cutout=ASSETS/'ajay-speakers'/(person+'.png')
        if cutout.is_file(): image=cutout
        refs=''.join(f'<button type="button" class="evidence-link" data-evidence="{escape(d,quote=True)}">{escape(council["evidence"][d]["title"])} ↗</button>' for d in v.get('evidence_ids',[]) if d in council['evidence'])
        return f'''<article class="method-voice {size}" data-person="{person}"><div class="voice-photo{' is-cutout' if cutout.is_file() else ''}"><img src="{uri(image)}" width="1024" height="1536" alt="AI 生成的 {escape(p['name_en'])} 方法论肖像，非本人背书" loading="lazy"></div><div class="voice-report"><span class="eyebrow">{escape(p['role'])}<a class="portrait-note" href="#visual-notes" aria-label="人物图像与模拟视角说明">*</a></span><h3>{escape(p['name_zh'])}<em>{escape(p['name_en'])}</em></h3><span class="speaker-status">方法讲解</span><p class="voice-claim">{escape(v['claim'])}</p><div class="voice-evidence">{refs}</div><details class="voice-condition"><summary>什么会改变这个判断</summary><p>{escape(v['rebuttal'])}</p></details></div></article>'''
    model_nodes=idx.select(cls='report-chapter')
    modeling=next((n for n in model_nodes if idx.select(id='section-modeling',within=n)),None)
    model_html=idx.html(modeling,inner=True) if modeling else '<p>估值模型未提供</p>'
    # New chapter owns the stable anchor and title; keep every model and segment node.
    model_html=re.sub(r'<div class="section-head" id="section-modeling">.*?<div class="section-line"></div>\s*</div>','',model_html,flags=re.S)
    model_html += render_model_supplement(raw, segment_present=bool(idx.select(cls='segmental-section')))
    for cls,anchor in [('dcf-block','model-dcf'),('comps-block','model-comps'),('lbo-block','model-lbo'),('model-supplement','model-research')]:
        model_html=model_html.replace(f'class="{cls}"',f'id="{anchor}" class="{cls}"',1)
    payload=json.dumps(json_safe({'raw':raw,'analysis':analysis,'council':council}),ensure_ascii=False,allow_nan=False)
    for a,b in [('&','\\u0026'),('<','\\u003c'),('>','\\u003e'),('\u2028','\\u2028'),('\u2029','\\u2029')]:payload=payload.replace(a,b)
    credits=''.join(f'<li><strong>{escape(p["name"])}</strong><p>{escape(p["author"])} · {escape(p["date"])} {"拍摄" if p["date_kind"]=="captured" else "发布，拍摄日未确认"} · <a href="{escape(p["source_url"],quote=True)}" target="_blank" rel="noopener noreferrer">原摄影作品</a> · <a href="{escape(p["license_url"],quote=True)}" target="_blank" rel="noopener noreferrer">{escape(p["license"])}</a></p><p>{escape(p["credit"])}</p></li>' for p in photos)
    refresh=raw.get('partial_refresh') or {}
    refresh_notice=''
    if isinstance(refresh,dict) and refresh.get('dimensions'):
        refreshed_at=escape(str(refresh.get('refreshed_at') or '时间未记录'))
        original_at=escape(str(raw.get('fetched_at') or '时间未记录'))
        refresh_notice=(f'<aside class="partial-refresh-note" role="note"><strong>局部数据更新</strong> '
                        f'技术面 / 缠论更新于 {refreshed_at}；其它研究记录仍为 {original_at} 的快照。'
                        '既有讨论与综合结论尚未按本次行情重新审阅。</aside>')
    values={
      'TITLE':name+' · J Trader Private Research','NAME':name,'TICKER':ticker,
      'CSS':'\n'.join((ASSETS/name).read_text() for name in ('report-continuous.css','report-chan.css','report-chan-table.css')),
      'PRICE_MAP':stage,'ASSUMPTIONS':assumptions_html,'AS_OF':escape(str(raw.get('fetched_at') or '采集时间未记录')),
      'HERO_COPY':hero,'CORE':block('core-overview')+block('dashboard-bento'),
      'NOTICES':block('report-notices')+refresh_notice,'EVIDENCE':block('evidence-strip'),
      'NY':photo('new-york','ny-arrival'),'SHANGHAI':photo('shanghai','shanghai-tower'),
      'RETURN_SNAPSHOT':quality_snapshot('当期回报记录',financial_point,'1_financials','历史持续性需另行核验'),
      'GROWTH_SNAPSHOT':quality_snapshot('增长输入记录',growth_point,'1_financials','来源需要销量、价格与并购拆分'),
      'GOVERNANCE_SNAPSHOT':quality_snapshot('治理核验状态','材料缺失 · 未评估' if governance=='missing' else '记录已收集 · 待核验','11_governance','点击打开原始记录与出处'),
      'LONDON':photo('london','london-frieze'),'HK':photo('hong-kong','hk-horizon'),
      'BUFFETT':voice('buffett','quality','lead'),'LYNCH':voice('lynch','quality'),
      'MUNGER':voice('munger','risk'),'GRAHAM':voice('graham','price'),
      'SIMONS':voice('simons','price'),'SOROS':voice('soros','risk','lead'),
      'DALIO':voice('dalio','risk'),'LIVERMORE':voice('livermore','risk'),
      'FINANCIAL':card(0),'VALUATION':card(1).replace('<div ', '<div id="model-valuation" ',1),'MOAT':card(2),
      'COMPANY':category(3),'INDUSTRY':category(2),'MARKET':market_html,'ENV':category(4),'SAFETY':category(5),
      'CHAN_DESK':render_chan_desk(raw),
      'TECHNICAL_DETAILS':f'<details class="technical-details"><summary>常规技术指标 · 均线、动量与量能</summary>{technical_html}</details>' if technical_html else '',
      'MODELS':clean(model_html),'CLASH':committee_record(block('divide-section')),'PANEL':panel_record(block('panel-section')),
      'CHAT':chat_html,'FRIENDLY':block('friendly-trio'),'HOLDINGS':block('fund-mgr-section'),
      'RISKS':block('risk-box'),'ZONES':block('zones-grid'),'SHARE':idx.first(id='share-overlay'),
      'EXPORT_SURFACES':clean(idx.first(id='share-card')+idx.first(id='war-report')),'FOOTER':idx.first(tag='footer'),'CREDITS':credits,'DATA':payload,
      'GSAP':(ASSETS/'vendor/gsap.min.js').read_text(),
      'JS':(ASSETS/'report-continuous.js').read_text()+'\n'+(ASSETS/'report-chan.js').read_text(),
    }
    result=(ASSETS/'report-continuous.html').read_text()
    # Single substitution: user text containing a template marker is never evaluated twice.
    return re.sub(r'\[\[([A-Z_]+)\]\]',lambda m:values[m[1]],result)

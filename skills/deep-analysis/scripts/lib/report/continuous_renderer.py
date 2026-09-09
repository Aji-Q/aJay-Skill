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

def clean(markup):
    markup=re.sub(r'<img\b[^>]*\bsrc="avatars/[^>]*>', '', markup)
    return ORNAMENTS.sub('',markup).replace('★','').replace('☆','')

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
    fin=idx.select(cls='dim-card',within=categories[0]) if categories else []
    def card(i):return clean(idx.html(fin[i])) if len(fin)>i else '<p>维度未评估</p>'
    def block(cls):return clean(idx.first(cls=cls))
    def observed(dim, key):
        return next((f['text'] for f in council['evidence'][dim]['facts'] if f['id'].endswith('.'+key)), '未记录')
    financial_point=observed('1_financials','roe_latest')
    growth_point=observed('1_financials','revenue_growth')
    governance=council['evidence']['11_governance']['status']
    governance_point='治理记录缺失，尚待核验' if governance=='missing' else '治理记录须与原始披露交叉核验'
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
    photos=json.loads((ASSETS/'ajay-council/photography.json').read_text())
    def photo(city, cls):
        item=next(p for p in photos if p['id']==city)
        notes=''
        if city=='shanghai':
            notes='<div class="tower-notes">'+''.join(f'<div><span>{label}</span><p>{escape(point)}</p><button type="button" class="evidence-link" data-evidence="{key}">核对记录 ↗</button></div>' for label,point,key in [('I / 回报记录',financial_point,'1_financials'),('II / 增长来源',growth_point,'1_financials'),('III / 治理根基',governance_point,'11_governance')])+'</div>'
        return f'<figure class="location {cls}"><img src="{uri(ASSETS/"ajay-council"/item["asset"])}" alt="{escape(item["description"],quote=True)}" {"fetchpriority=high" if city=="new-york" else "loading=lazy"}>{notes}<figcaption><span>{escape(item["label"])} / PHOTOGRAPHIC STUDY</span><a href="#photography-credits">摄影来源与重构说明</a></figcaption></figure>'
    def voice(person, topic, size='compact'):
        p=next(p for p in council['profiles'] if p['id']==person)
        v=next(v for t in council['topics'] if t['id']==topic for v in t['voices'] if v['id']==person)
        image=ASSETS/('ajay-brand' if person in ('buffett','simons') else 'ajay-council')/(person+'-portrait.png')
        refs=''.join(f'<button type="button" class="evidence-link" data-evidence="{escape(d,quote=True)}">{escape(council["evidence"][d]["title"])} ↗</button>' for d in v.get('evidence_ids',[]) if d in council['evidence'])
        return f'''<article class="method-voice {size}" data-person="{person}"><div class="voice-photo"><img src="{uri(image)}" alt="AI 生成的 {escape(p['name_en'])} 方法论肖像，非本人背书" loading="lazy"></div><div class="voice-report"><span class="eyebrow">{escape(p['role'])} / 模拟视角</span><h3>{escape(p['name_zh'])}<em>{escape(p['name_en'])}</em></h3><p class="voice-claim">{escape(v['claim'])}</p><div class="voice-evidence">{refs}</div><details class="voice-condition"><summary>什么会改变这个判断</summary><p>{escape(v['rebuttal'])}</p></details></div></article>'''
    model_nodes=idx.select(cls='report-chapter')
    modeling=next((n for n in model_nodes if idx.select(id='section-modeling',within=n)),None)
    model_html=idx.html(modeling,inner=True) if modeling else '<p>估值模型未提供</p>'
    # New chapter owns the stable anchor and title; keep every model and segment node.
    model_html=re.sub(r'<div class="section-head" id="section-modeling">.*?<div class="section-line"></div>\s*</div>','',model_html,flags=re.S)
    model_html += render_model_supplement(raw, segment_present=bool(idx.select(cls='segmental-section')))
    for cls,anchor in [('dcf-block','model-dcf'),('comps-block','model-comps'),('lbo-block','model-lbo'),('model-supplement','model-research')]:
        model_html=model_html.replace(f'class="{cls}"',f'id="{anchor}" class="{cls}"',1)
    old_styles='\n'.join(idx.html(n,inner=True) for n in idx.select(tag='style'))
    legacy_script='\n'.join(idx.html(n,inner=True) for n in idx.select(tag='script') if not n['attrs'].get('src'))
    payload=json.dumps(json_safe({'raw':raw,'analysis':analysis,'council':council}),ensure_ascii=False,allow_nan=False)
    for a,b in [('&','\\u0026'),('<','\\u003c'),('>','\\u003e'),('\u2028','\\u2028'),('\u2029','\\u2029')]:payload=payload.replace(a,b)
    credits=''.join(f'<li><strong>{escape(p["name"])}</strong><p>{escape(p["author"])} · {escape(p["date"])} {"拍摄" if p["date_kind"]=="captured" else "发布，拍摄日未确认"} · <a href="{escape(p["source_url"],quote=True)}" target="_blank" rel="noopener noreferrer">原摄影作品</a> · <a href="{escape(p["license_url"],quote=True)}" target="_blank" rel="noopener noreferrer">{escape(p["license"])}</a></p><p>以原图为参照，经 image 工具局部重构曝光与材质；不是未经修改的实拍。{escape(p["credit"])}</p></li>' for p in photos)
    values={
      'TITLE':name+' · aJay Private Research','NAME':name,'TICKER':ticker,
      'LEGACY_CSS':old_styles,'CSS':(ASSETS/'report-continuous.css').read_text(),
      'HERO_COPY':hero,'CORE':block('core-overview')+block('dashboard-bento'),
      'NOTICES':block('report-notices'),'EVIDENCE':block('evidence-strip'),
      'NY':photo('new-york','ny-arrival'),'SHANGHAI':photo('shanghai','shanghai-tower'),
      'LONDON':photo('london','london-frieze'),'HK':photo('hong-kong','hk-horizon'),
      'BUFFETT':voice('buffett','quality','lead'),'LYNCH':voice('lynch','quality'),
      'MUNGER':voice('munger','risk'),'GRAHAM':voice('graham','price'),
      'SIMONS':voice('simons','price'),'SOROS':voice('soros','risk','lead'),
      'DALIO':voice('dalio','risk'),'LIVERMORE':voice('livermore','risk'),
      'FINANCIAL':card(0),'VALUATION':card(1).replace('<div ', '<div id="model-valuation" ',1),'MOAT':card(2),
      'COMPANY':category(3),'INDUSTRY':category(2),'MARKET':category(1),'ENV':category(4),'SAFETY':category(5),
      'MODELS':clean(model_html),'CLASH':committee_record(block('divide-section')),'PANEL':panel_record(block('panel-section')),
      'CHAT':chat_html,'FRIENDLY':block('friendly-trio'),'HOLDINGS':block('fund-mgr-section'),
      'RISKS':block('risk-box'),'ZONES':block('zones-grid'),'SHARE':idx.first(id='share-overlay'),
      'EXPORT_SURFACES':clean(idx.first(id='share-card')+idx.first(id='war-report')),'FOOTER':idx.first(tag='footer'),'CREDITS':credits,'DATA':payload,
      'LEGACY_JS':legacy_script,'GSAP':(ASSETS/'vendor/gsap.min.js').read_text(),
      'JS':(ASSETS/'report-continuous.js').read_text(),
    }
    result=(ASSETS/'report-continuous.html').read_text()
    # Single substitution: user text containing a template marker is never evaluated twice.
    return re.sub(r'\[\[([A-Z_]+)\]\]',lambda m:values[m[1]],result)

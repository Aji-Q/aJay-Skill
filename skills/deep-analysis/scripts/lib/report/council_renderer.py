"""Offline investment council renderer; no external media/runtime requests."""
from __future__ import annotations
import base64,json,math
from pathlib import Path
from lib.report.council import build_council

ASSETS=Path(__file__).resolve().parents[3]/'assets'

def json_safe(value):
    if isinstance(value,float) and not math.isfinite(value): return None
    if isinstance(value,dict): return {str(k):json_safe(v) for k,v in value.items()}
    if isinstance(value,(list,tuple)): return [json_safe(v) for v in value]
    return value

def uri(path):
    if path is None:
        return ''
    mime={'.webp':'image/webp','.jpg':'image/jpeg','.jpeg':'image/jpeg','.svg':'image/svg+xml'}.get(path.suffix.lower(),'image/png')
    return f'data:{mime};base64,'+base64.b64encode(path.read_bytes()).decode('ascii')

def render_council(raw, analysis=None):
    from html import escape
    raw=raw if isinstance(raw,dict) else {}
    council=build_council(raw)
    portraits={p['id']:uri(ASSETS/('ajay-brand' if p['id'] in ('buffett','simons') else 'ajay-council')/(p['id']+'-portrait.png')) for p in council['profiles']}
    cities=[]
    for item in json.loads((ASSETS/'ajay-council'/'photography.json').read_text()):
        city={k:item[k] for k in ('id','label','name','description','credit','source_url','license','license_url','composition','date','date_kind','author')}
        city['image']=uri(ASSETS/'ajay-council'/item['asset'])
        cities.append(city)
    basic=((raw.get('dimensions') or {}).get('0_basic') or {}).get('data') or {}
    data={'analysis':analysis or {},'council':council,'portraits':portraits,'cities':cities,'raw':raw,'security':{'ticker':raw.get('ticker'),'name':basic.get('name') or raw.get('name'),'collected_at':raw.get('fetched_at')},'icons':{p.stem:p.read_text() for p in (ASSETS/'vendor').glob('*.svg')}}
    payload=json.dumps(json_safe(data),ensure_ascii=False,allow_nan=False).replace('&','\\u0026').replace('<','\\u003c').replace('>','\\u003e').replace('\u2028','\\u2028').replace('\u2029','\\u2029')
    html=(ASSETS/'report-council.html').read_text().replace('{{PAGE_TITLE}}',escape(str(data['security']['name'] or 'J Trader')+' · J Trader Investment Council'))
    for marker,content in [('/* INJECT_COUNCIL_CSS */',(ASSETS/'report-council.css').read_text()),('/* INJECT_COUNCIL_DATA */',payload),('/* INJECT_GSAP */',(ASSETS/'vendor'/'gsap.min.js').read_text()),('/* INJECT_COUNCIL_JS */',(ASSETS/'report-council.js').read_text())]:html=html.replace(marker,content)
    fallback='<noscript><main class=\"noscript\"><h1>J Trader 研究会议</h1><p>此交互报告需要启用 JavaScript。原始研究输入保留如下：</p><pre>'+escape(json.dumps(json_safe(raw),ensure_ascii=False,indent=2))+'</pre></main></noscript>'
    return html.replace('</body>',fallback+'</body>')

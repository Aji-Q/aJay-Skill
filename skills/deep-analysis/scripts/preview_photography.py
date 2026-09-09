"""Build a local source/derivative contact sheet; do not transform either image."""
from pathlib import Path
from datetime import datetime
import hashlib,json,shutil
from html import escape
from urllib.request import Request, urlopen
ROOT=Path(__file__).resolve().parents[3]
ASSETS=Path(__file__).resolve().parents[1]/'assets/ajay-council'

def _original_for(item: dict) -> Path:
    """Resolve the ignored source-photo cache, downloading and verifying on demand."""
    target=ROOT/'docs/research/photo-originals'/item['original']
    if not target.exists():
        target.parent.mkdir(parents=True,exist_ok=True)
        request=Request(item['original_url'],headers={'User-Agent':'aJay-Skill provenance review/1.1'})
        with urlopen(request,timeout=45) as response:
            target.write_bytes(response.read())
    digest=hashlib.sha256(target.read_bytes()).hexdigest()
    if digest != item['source_sha256']:
        raise ValueError(f"source hash mismatch for {item['id']}: {digest}")
    return target

def main():
    out=Path('reports')/f'AJAY.DEMO_{datetime.now():%Y%m%d}'
    images=out/'photo-review-assets';images.mkdir(parents=True,exist_ok=True)
    rows=[]
    for item in json.loads((ASSETS/'photography.json').read_text()):
        original=_original_for(item)
        shutil.copy2(original,images/item['original']);shutil.copy2(ASSETS/item['asset'],images/item['asset'])
        rows.append(f'''<section><header><span>{escape(item['label'])}</span><h2>{escape(item['composition'])}</h2><p>{escape(item['credit'])}</p><a href="{escape(item['source_url'])}">原始作品 / {escape(item['author'])}</a> · <a href="{escape(item['license_url'])}">{escape(item['license'])}</a></header><div class="pair"><figure><img loading="lazy" src="photo-review-assets/{escape(item['original'])}" alt="{escape(item['name'])} 原始摄影"><figcaption>01 / 原始摄影 · 未改动</figcaption></figure><figure><img loading="lazy" src="photo-review-assets/{escape(item['asset'])}" alt="{escape(item['name'])} 编辑版本"><figcaption>02 / image 工具轻微重构 · aJay 界面使用版</figcaption></figure></div></section>''')
    html='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>aJay / 金融摄影选片与重构对照</title><style>body{margin:0;background:#10171f;color:#e0e7e6;font:15px/1.8 'Avenir Next','PingFang SC',sans-serif}main{max-width:1450px;margin:auto;padding:50px 5vw}h1{font:42px Georgia,'Songti SC',serif;margin:10px 0 25px}h2{font-size:24px;font-weight:400}p{max-width:950px;color:#a9b9bd}a{color:#d8dfd3}section{border-top:1px solid #3e5058;padding:34px 0 44px;margin-top:30px}header>span{font-size:11px;letter-spacing:3px;color:#8ba8b1}.pair{display:grid;grid-template-columns:1fr 1fr;gap:24px;margin-top:24px}figure{margin:0;background:#0a1016;padding:16px}img{width:100%;height:620px;object-fit:contain}figcaption{font-size:12px;margin:12px 0;color:#a6babe}@media(max-width:700px){main{padding:30px 20px}h1{font-size:32px}.pair{grid-template-columns:1fr}img{height:480px}}</style><main><span>aJay / FINANCIAL GEOGRAPHIES</span><h1>真实原作，克制重构。</h1><p>筛选以金融投资相关性为先，再检验摄影构图、曝光与层次。四组作品不是同一提示词换城市：街牌近景、办公立面、超高层竖幅、港湾金融天际线各自保留空间语言。前三个 Unsplash 日期为作品页公开日期，不推断拍摄日期；上海为可核实拍摄日期。所有右图为 AI 编辑衍生图，非未经编辑的纪实原片。</p><a href="full-report-standalone.html">进入 aJay 研究会议 →</a>'''+''.join(rows)+'</main></html>'
    # The three Unsplash works are New York, London and Hong Kong (not the first three rows).
    html=html.replace('前三个 Unsplash 日期','纽约、伦敦、香港的 Unsplash 日期')
    target=out/'photography-review.html';target.write_text(html);print(target.resolve())
if __name__=='__main__':main()

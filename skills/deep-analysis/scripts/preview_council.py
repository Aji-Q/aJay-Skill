"""Build a clearly labeled offline council fixture without providers."""
from datetime import datetime
from pathlib import Path
from lib.cache import read_task_output
from lib.report.council_renderer import render_council

def main():
    ticker='JTRADER.DEMO';raw=read_task_output(ticker,'raw_data')
    if not raw or not raw.get('is_demo'):raise RuntimeError('Run preview_editorial.py to create the clearly marked synthetic fixture first.')
    out=Path('reports')/f'{ticker}_{datetime.now():%Y%m%d}'/'council-preview.html';out.parent.mkdir(parents=True,exist_ok=True);out.write_text(render_council(raw));print(out.resolve())
if __name__=='__main__':main()

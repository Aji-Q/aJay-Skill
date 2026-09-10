#!/usr/bin/env python3
"""Create an offline, annotated research chart for any supported ticker.

Explicit --refresh fetches history; otherwise read --input or an existing local
cache. This command never writes raw_data.json, panel.json or review flags.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
from datetime import datetime, timezone
from html import escape
import json
from pathlib import Path
import re
import sys

from chan_signals import build_chan_v1
from price_action import enrich_chan_price_action

HERE = Path(__file__).resolve().parent
ASSETS = HERE.parent / 'assets'


def _kline_payload(payload):
    if isinstance(payload, list):
        return {'rows': payload}
    if not isinstance(payload, dict):
        raise ValueError('input must be a JSON object or OHLCV list')
    dims = payload.get('dimensions') or {}
    if isinstance(dims.get('2_kline'), dict):
        return dims['2_kline'].get('data') or dims['2_kline']
    if (payload.get('schema_version') or payload.get('version')) == 'chan.v1':
        return {'chan': payload}
    if payload.get('schema_version') == 'jtrader.chart.v1':
        return payload['data']
    nested = payload.get('data')
    if isinstance(nested, dict):
        return nested
    return payload


def prepare_chart(ticker, payload, *, input_source='offline JSON'):
    """Reuse validated Chan geometry when present; otherwise derive from rows."""
    if not re.fullmatch(r'[A-Za-z0-9^][A-Za-z0-9.^=_-]{0,39}', ticker):
        raise ValueError('ticker must be a market symbol, e.g. AAPL, 0700.HK or 600519.SH')
    ticker = ticker.upper()
    data = deepcopy(_kline_payload(payload))
    original_ticker = (payload.get('ticker') if isinstance(payload, dict) else None) or (data.get('chan') or {}).get('ticker')
    if original_ticker and str(original_ticker).upper() != ticker:
        raise ValueError(f'input ticker {original_ticker} does not match requested {ticker}')
    chan = data.get('chan') or data.get('chan_v1')
    provenance = data.get('kline_provenance') or data.get('provenance') or {}
    if not isinstance(chan, dict) or not isinstance(chan.get('levels'), dict) or not chan['levels']:
        rows = next((data.get(key) for key in ('rows', 'klines', 'ohlcv', 'bars', 'candles_60d')
                     if isinstance(data.get(key), list)), [])
        if not rows:
            raise ValueError('input contains no daily OHLCV rows or Chan levels')
        chan = build_chan_v1(ticker, rows, market=data.get('market', 'unknown'),
                             source=provenance.get('source') or data.get('source') or input_source,
                             adjusted=provenance.get('adjusted'),
                             computed_at=provenance.get('computed_at'))
        for key in ('rows', 'klines', 'ohlcv', 'bars', 'candles_60d'):
            data.pop(key, None)
        data['chan'] = chan
    data['price_action'] = enrich_chan_price_action(chan)
    data['chan'] = chan
    if not any(isinstance(level.get('bars'), list) and level['bars'] for level in chan['levels'].values()):
        raise ValueError('input has no valid OHLCV candles after normalization')
    return dict(schema_version='jtrader.chart.v1', ticker=ticker,
                generated_at=datetime.now(timezone.utc).isoformat(timespec='seconds'),
                purpose='offline research snapshot; not a backtest or trading instruction',
                input_source=input_source, data=data)


def render_chart_html(bundle):
    from lib.report.chan_desk import render_chan_desk
    title = escape(bundle['ticker'])
    styles = '\n'.join((ASSETS / file).read_text() for file in ('report-continuous.css', 'report-chan.css', 'report-chan-table.css'))
    gsap = (ASSETS / 'vendor/gsap.min.js').read_text()
    runtime = (ASSETS / 'report-chan.js').read_text()
    payload = json.dumps(bundle, ensure_ascii=False, allow_nan=False, separators=(',', ':')).replace('<', '\\u003c')
    desk = render_chan_desk({'ticker': bundle['ticker'], 'dimensions': {'2_kline': {'data': bundle['data']}}})
    return f'''<!doctype html><html lang="zh-CN" data-theme="dark"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>{title} · J Trader 价格结构图</title>
<style>{styles}
.chart-report-header{{max-width:1680px;margin:auto;padding:28px 28px 0;display:flex;gap:20px;flex-wrap:wrap;justify-content:space-between}}
.chart-report-header button{{padding:8px 12px;color:var(--text-main);background:var(--bg-card);border:1px solid var(--border)}}
.chart-report-main{{max-width:1680px;margin:auto;padding:20px 28px}} .chart-report-footer{{padding:20px 28px;color:var(--text-dim);font-size:12px}}
@media(max-width:600px){{.chart-report-main{{padding:12px}}}} @media print{{.chart-report-header button{{display:none}}}}
</style></head><body class="continuous-report">
<header class="chart-report-header"><div><strong>J TRADER / {title}</strong><p>价格结构研究 · 同源坐标 · 离线可交互</p></div>
<div><button id="chart-theme" type="button">切换深浅主题</button> <button id="chart-motion" type="button">停用动态</button> <button id="chart-print" type="button">打印 / PDF</button></div></header>
<main class="chart-report-main">{desk}</main><footer class="chart-report-footer">aJay · J Trader | 当前行情快照的条件图解，不是历史信号回测或投资承诺。<br>价格行为：两侧确认摆动、ATR 区域与突破/回踩观察；与严格缠论买卖点分开标识。</footer>
<script type="application/json" id="jtrader-chart-data">{payload}</script><script>{gsap}</script><script>{runtime}</script>
<script>document.getElementById('chart-theme').onclick=function(){{var h=document.documentElement;h.dataset.theme=h.dataset.theme==='dark'?'light':'dark';}};
document.getElementById('chart-motion').onclick=function(){{var h=document.documentElement;h.dataset.motion=h.dataset.motion==='off'?'on':'off';this.textContent=h.dataset.motion==='off'?'启用动态':'停用动态';}};
document.getElementById('chart-print').onclick=function(){{window.print();}};</script></body></html>'''


def _resolve_output(output):
    output = Path(output).expanduser().resolve()
    if output.suffix.lower() in ('.html', '.json'):
        return output.with_suffix('.html'), output.with_suffix('.json')
    return output / 'chart.html', output / 'chart.json'


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('ticker', help='AAPL, MSFT, 600519.SH, 0700.HK, etc.')
    source = parser.add_mutually_exclusive_group()
    source.add_argument('--input', type=Path, help='offline OHLCV / fetch_kline / chan.v1 / raw_data JSON')
    source.add_argument('--refresh', action='store_true', help='explicitly fetch current history, leaving prior caches/review files untouched')
    parser.add_argument('--output', type=Path, required=True, help='output directory, or .html/.json file stem; always emits both')
    parser.add_argument('--force', action='store_true', help='replace existing chart outputs (never replaces source input)')
    args = parser.parse_args(argv)
    try:
        ticker = args.ticker.upper()
        if not re.fullmatch(r'[A-Za-z0-9^][A-Za-z0-9.^=_-]{0,39}', ticker):
            raise ValueError('invalid ticker')
        source_path = None
        if args.refresh:
            from fetch_kline import main as fetch
            payload = fetch(ticker)
            source_label = 'explicit refresh via fetch_kline'
        else:
            source_path = (args.input or HERE / '.cache' / ticker / 'raw_data.json').expanduser().resolve()
            payload = json.loads(source_path.read_text())
            source_label = str(source_path)
        html_path, json_path = _resolve_output(args.output)
        if source_path in (html_path, json_path):
            raise ValueError('output would overwrite input; choose another output path')
        # Reserved analysis cache/review artifacts stay immutable even with --force.
        if any(p.name in {'raw_data.json', 'panel.json', 'agent_analysis.json', 'synthesis.json', 'review.json'} for p in (html_path, json_path)):
            raise ValueError('output name is reserved for the analysis/review pipeline')
        if not args.force and any(p.exists() for p in (html_path, json_path)):
            raise ValueError('output already exists; choose a new output or add --force')
        bundle = prepare_chart(ticker, payload, input_source=source_label)
        encoded = json.dumps(bundle, ensure_ascii=False, indent=2, allow_nan=False)
        rendered = render_chart_html(bundle)
        html_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text(encoded)
        html_path.write_text(rendered)
        print(json.dumps({'ticker': ticker, 'html': str(html_path), 'json': str(json_path),
                          'levels': {k: {'bars': v.get('bar_count'), 'price_action_levels': len(v.get('price_action', {}).get('levels', [])),
                                         'events': len(v.get('price_action', {}).get('events', []))} for k, v in bundle['data']['chan']['levels'].items()}}, ensure_ascii=False))
        return 0
    except (OSError, ValueError, TypeError, KeyError) as exc:
        parser.exit(2, f'chart_stock: {exc}\n')


if __name__ == '__main__':
    raise SystemExit(main())

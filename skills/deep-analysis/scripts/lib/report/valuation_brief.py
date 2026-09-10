"""A snapshot-only price map. All views share the same recorded model values.

This is a presentation layer: it neither recalculates models nor invents a
target range. A missing observation remains missing in the chart and table.
"""
from html import escape
import math


def _number(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    return float(value) if math.isfinite(value) else None


def render_valuation_brief(raw):
    dimensions = raw.get('dimensions') or {}
    basic = (dimensions.get('0_basic') or {}).get('data') or {}
    record = dimensions.get('20_valuation_models') or {}
    models = record.get('data') or {}
    dcf, comps = models.get('dcf') or {}, models.get('comps') or {}
    assumptions = dcf.get('assumptions') or {}
    wacc = (dcf.get('wacc_breakdown') or {}).get('wacc')
    currency = {'U': 'USD', 'H': 'HKD', 'A': 'CNY'}.get(raw.get('market'), '币种未记录')
    observed_at = escape(str(raw.get('fetched_at') or '采集时间未记录'))
    values = [
        ('市场价格', _number(basic.get('price')), 'market', '采集时的报价，不是实时行情'),
        ('DCF 基础案例', _number(dcf.get('intrinsic_per_share')), 'dcf', '模型输入与默认假设下的每股结果'),
        ('可比公司隐含价', _number((comps.get('implied_price') or {}).get('via_median_pe')), 'comps', '同行中位 PE × 输入 EPS；同行可比性待核验'),
    ]
    def fmt(value):
        return f'{value:,.2f}' if value is not None else '—'
    finite = [v for _, v, _, _ in values if v is not None]
    low, high = min([0] + finite), max([1] + finite)
    span = max(high - low, 1)
    high += span * .16
    left, width = 160, 425
    def x(value):
        return left + (value - low) / (high - low) * width
    marks = []
    for i in range(5):
        value = low + (high-low) * i / 4
        px = x(value)
        marks.append(f'<line class="price-grid" x1="{px:.2f}" x2="{px:.2f}" y1="28" y2="254"/><text class="price-axis" x="{px:.2f}" y="282" text-anchor="middle">{value:,.0f}</text>')
    for i, (label, value, role, _) in enumerate(values):
        y = 64 + i * 76
        marks.append(f'<text class="price-label" x="0" y="{y+5}">{label}</text>')
        if value is not None:
            px, zero = x(value), x(0)
            marks.append(f'<rect class="price-bar price-{role}" x="{min(px,zero):.2f}" y="{y-9}" width="{max(abs(px-zero),1):.2f}" height="18" rx="1"/>')
            marks.append(f'<circle class="price-point price-{role}" cx="{px:.2f}" cy="{y}" r="4"/>')
            marks.append(f'<text class="price-value" x="{px+10:.2f}" y="{y+5}">{fmt(value)}</text>')
        else:
            marks.append(f'<text class="price-axis" x="{left}" y="{y+5}">输入缺失 / 未绘制</text>')
    # Keep labels at native text size on a phone rather than shrinking the
    # desktop SVG. Both presentations use the same observations and scale.
    mobile_rows = []
    zero_percent = (0-low) / (high-low) * 100
    for label, value, role, _ in values:
        if value is None:
            mark = '<span class="mobile-price-missing">输入缺失 / 未绘制</span>'
        else:
            point = (value-low) / (high-low) * 100
            mark = (f'<span class="mobile-price-bar price-{role}" '
                    f'style="left:{min(point,zero_percent):.4f}%;width:{abs(point-zero_percent):.4f}%"></span>'
                    f'<i class="mobile-price-point price-{role}" style="left:{point:.4f}%"></i>')
        mobile_rows.append(f'<div class="mobile-price-row"><div class="mobile-price-label"><span>{label}</span><strong>{fmt(value)}</strong></div><div class="mobile-price-track" aria-hidden="true"><i class="mobile-price-zero" style="left:{zero_percent:.4f}%"></i>{mark}</div></div>')
    mobile_chart = f'<div class="price-mobile" aria-label="三种每股价格，共用刻度">{"".join(mobile_rows)}<div class="mobile-price-scale"><span>{low:,.0f}</span><span>{high:,.0f} {currency} / 股</span></div></div>'
    rows = ''.join(f'<tr><th scope="row">{label}</th><td>{fmt(value)}</td><td>{note}</td></tr>' for label, value, _, note in values)
    source = escape(str(record.get('source') or '来源未记录'))
    stage = f'''<section class="valuation-stage" data-viz-switcher aria-labelledby="price-map-title">
      <header class="viz-heading"><div><span class="eyebrow">PRICE MAP / {currency} PER SHARE</span><h3 id="price-map-title">同一家公司，三种价格。</h3></div><span class="snapshot-label">输入快照</span></header>
      <div class="viz-tabs" role="tablist" aria-label="价格地图视图">
        <button type="button" id="price-tab-chart" role="tab" aria-selected="true" aria-controls="price-panel-chart" data-model-view="chart">价格地图</button>
        <button type="button" id="price-tab-table" role="tab" aria-selected="false" aria-controls="price-panel-table" tabindex="-1" data-model-view="table">数据表</button>
        <button type="button" id="price-tab-source" role="tab" aria-selected="false" aria-controls="price-panel-source" tabindex="-1" data-model-view="source">来源与边界</button>
      </div>
      <div id="price-panel-chart" class="price-map" role="tabpanel" aria-labelledby="price-tab-chart" data-model-panel="chart">
        <svg class="price-desktop" viewBox="0 0 680 305" role="img" aria-labelledby="price-svg-title price-svg-desc"><title id="price-svg-title">市场报价、DCF 与可比公司每股估值</title><desc id="price-svg-desc">三组已有输入快照，统一 {currency} 每股刻度；不构成目标价区间或收益预测。</desc>{''.join(marks)}</svg>
        {mobile_chart}
      </div>
      <div id="price-panel-table" role="tabpanel" aria-labelledby="price-tab-table" data-model-panel="table" hidden><table><caption>每股结果 · {currency}</caption><thead><tr><th scope="col">口径</th><th scope="col">记录值</th><th scope="col">解释</th></tr></thead><tbody>{rows}</tbody></table></div>
      <div id="price-panel-source" role="tabpanel" aria-labelledby="price-tab-source" data-model-panel="source" hidden><p>模型来源：{source}</p><p>输入采集：{observed_at}</p><p>DCF 是假设驱动的基础案例；可比公司隐含价使用同行中位数。两者不是价格上下限，也不是概率区间。默认资本成本、跨市场同行与输入完整性均需单独复核。</p><button class="evidence-link" type="button" data-evidence="20_valuation_models">核验模型原始输入 ↗</button></div>
      <p class="viz-footnote">{observed_at} · {currency} / 股<br>同尺度比较，不代表价格区间。读差异，先查假设。</p>
    </section>'''
    assumptions_rows = [
        ('折现率 WACC', _number(wacc)),
        ('第一阶段增长', _number(assumptions.get('stage1_growth'))),
        ('第二阶段增长', _number(assumptions.get('stage2_growth'))),
        ('永续增长 g', _number(assumptions.get('terminal_g'))),
    ]
    definition = ''.join(f'<div><dt>{label}</dt><dd>{f"{value*100:.2f}%" if value is not None else "—"}</dd></div>' for label, value in assumptions_rows)
    assumptions_html = f'''<section class="assumption-brief"><span class="eyebrow">THE ASSUMPTIONS</span><h3>先打开假设，再相信结果。</h3><dl>{definition}</dl><p>模型采用记录中的资本成本与增长设定；默认值不等于公司的已实现表现。</p><button class="evidence-link" type="button" data-evidence="20_valuation_models">逐项核验模型输入 ↗</button></section>'''
    return stage, assumptions_html

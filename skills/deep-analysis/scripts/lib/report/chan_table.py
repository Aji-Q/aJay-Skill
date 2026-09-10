"""Readable structure ledger for the Chan desk. Coordinates are never inferred."""
from html import escape
from collections.abc import Mapping
import math


def finite(value):
    if isinstance(value, bool):
        return None
    try:
        number = float(value)
        return number if math.isfinite(number) else None
    except (TypeError, ValueError):
        return None


def number(value):
    value = finite(value)
    return '—' if value is None else f'{value:,.2f}'


def e(value):
    return escape(str(value if value is not None else '—'), quote=True)


def endpoint(item, side):
    value = finite(item.get(side + '_price'))
    nested = item.get(side)
    return value if value is not None else finite(nested.get('price')) if isinstance(nested, Mapping) else None


def condition_text(value):
    """Format only supplied invalidation values; no calculated stop or target."""
    if not value:
        return '未记录具体失效价位'
    if isinstance(value, str):
        return value
    if isinstance(value, Mapping):
        parts = []
        for key, label in [('below', '价格跌破'), ('above', '价格突破')]:
            if finite(value.get(key)) is not None:
                parts.append(label + ' ' + number(value[key]))
        if value.get('text'):
            parts.append(str(value['text']))
        if value.get('description'):
            parts.append(str(value['description']))
        return '；'.join(parts) or '未记录具体失效价位'
    return '未记录具体失效价位'


def row_details(annotation, model):
    item, kind = annotation['item'], annotation['kind']
    bars = {x.get('index'): x for x in model.get('bars', [])}
    start = item.get('sdt') or item.get('dt') or item.get('at')
    end = item.get('edt')
    if not start:
        index = item.get('anchor_index', item.get('bar_index', item.get('start_index')))
        start = (bars.get(index) or {}).get('dt')
    if not end and item.get('end_index') is not None:
        end = (bars.get(item['end_index']) or {}).get('dt')
    date = ' → '.join(str(x)[:10] for x in [start, end if end != start else None] if x) or '未记录'
    note = item.get('annotation') or {}
    note = note if isinstance(note, Mapping) else {}
    if kind in ('bi', 'unfinished-bi'):
        price = number(endpoint(item, 'start')) + ' → ' + number(endpoint(item, 'end'))
        basis = note.get('text') or ('当前摆动仍可重绘' if kind == 'unfinished-bi' else 'CZSC 完成笔记录；按已提供端点绘制')
    elif kind == 'center':
        price = number(item.get('zd')) + ' — ' + number(item.get('zg'))
        ids = item.get('bi_ids') or []
        basis = f'{len(ids)} 笔构成的重叠区间' if ids else 'CZSC 中枢记录；按已提供上下边界绘制'
    elif kind == 'signal':
        price = number(item.get('level', item.get('price')))
        basis = item.get('rule') or (item.get('evidence') if isinstance(item.get('evidence'), str) else None) or note.get('text') or '未记录成立依据'
        divergence = item.get('divergence') or {}
        if isinstance(divergence, Mapping) and divergence.get('method') == 'bi_power_proxy':
            basis += '；仅笔力度代理，非严格 MACD 背驰'
    else:
        price = number(item.get('price', item.get('level')))
        basis = note.get('text') or 'CZSC 分型记录' if kind == 'fractal' else note.get('text') or '按输入条件绘制'
    invalid = item.get('invalid_if')
    if not invalid:
        if finite(item.get('invalid_below')) is not None:
            invalid = {'below': item['invalid_below']}
        elif finite(item.get('invalid_above')) is not None:
            invalid = {'above': item['invalid_above']}
    invalid_text = condition_text(invalid) if kind in ('signal','condition','invalid') or invalid else ('新 K 线可能改变当前端点' if kind == 'unfinished-bi' else '历史结构记录；后续走势另判')
    return date, price, str(basis), invalid_text


def render_chan_table(model):
    """Seven-column ledger; dataset keys match chan_desk's SVG identifiers."""
    rows=[]
    priority={'signal':0,'condition':1,'invalid':1,'unfinished-bi':2,'center':3,'bi':4,'fractal':5}
    records=list(model.get('annotations') or [])
    records.sort(key=lambda a:(priority.get(a.get('kind'),6),-(finite(a.get('index')) or 0)))
    for record in records:
        key=record['key']; raw_id=record.get('raw_id') or key
        date, price, basis, invalid=row_details(record,model)
        status={'candidate':'候选 · 未确认','unfinished':'未完成 · 可重绘','complete':'完成结构','confirmed':'已确认'}.get(record.get('status'),str(record.get('status') or '未标注'))
        rows.append(f'<tr data-chan-point-row="{e(key)}" data-annotation-id="{e(key)}"><td><button type="button" class="chan-point-button" data-chan-point="{e(key)}">{e(record["label"])}</button><small class="chan-structure-id">{e(raw_id)}</small></td><td>{e(model.get("level"))}</td><td class="chan-date-cell">{e(date)}</td><td class="chan-price-cell">{e(price)}</td><td><span class="chan-point-status">{e(status)}</span></td><td class="chan-basis-cell">{e(basis)}</td><td class="chan-invalid-cell">{e(invalid)}</td></tr>')
    if not rows:
        rows=['<tr><td colspan="7" class="chan-table-empty">暂无可联动结构记录</td></tr>']
    return '<div class="chan-point-table-wrap" tabindex="0" role="region" aria-label="缠论结构点位表，可横向滚动"><table class="chan-point-table"><caption>结构点位记录 · 选择结构，联动图线与讲解</caption><thead><tr>'+''.join('<th scope="col">'+label+'</th>' for label in ['结构名称','周期','日期','价位 / 区间','状态','成立依据','失效条件'])+'</tr></thead><tbody>'+''.join(rows)+'</tbody></table></div>'

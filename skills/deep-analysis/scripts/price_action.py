"""Deterministic OHLCV price-action evidence, complementary to (not) Chan rules.

Confirmed swing levels become available only AFTER their right-hand bars.
Breakouts and retests are evaluated in chronological order thereafter; no
backfilled signal probabilities or trading orders are produced.
"""
from __future__ import annotations

from copy import deepcopy
from typing import Mapping

from chan_signals import normalize_ohlcv_rows

SCHEMA_VERSION = "price_action.v1"


def _round(value):
    return round(value, 8) if value is not None else None


def _sma(values, period):
    return [None if i < period - 1 else _round(sum(values[i-period+1:i+1]) / period) for i in range(len(values))]


def _atr(rows, period=14):
    out, seed, prev = [], [], None
    for i, row in enumerate(rows):
        if i == 0:
            out.append(None)
            continue
        prior = rows[i-1]['close']
        tr = max(row['high']-row['low'], abs(row['high']-prior), abs(row['low']-prior))
        seed.append(tr)
        if i == period:
            prev = sum(seed)/period
        elif i > period:
            prev = (prev * (period-1) + tr)/period
        out.append(_round(prev))
    return out


def build_price_action_level(rows, *, period='D', source='unknown', adjusted=None,
                             last_bar_complete=False, swing_span=3, max_levels=24):
    """Normalize rows; expose only confirmed history plus last-bar observations.

    Default conservatively excludes the final date-only candle from confirming
    swings/events because a daily/weekly close timestamp has not been verified.
    Indicators still show it, explicitly as an observed snapshot.
    """
    if not isinstance(swing_span, int) or not 1 <= swing_span <= 10:
        raise ValueError('swing_span must be an integer in 1..10')
    if not isinstance(max_levels, int) or max_levels < 1:
        raise ValueError('max_levels must be positive')
    bars, quality = normalize_ohlcv_rows(rows)
    count = len(bars)
    confirmed_end = count-1 if last_bar_complete else count-2
    closes, volumes = [b['close'] for b in bars], [b['volume'] for b in bars]
    ma20, ma60, atr14 = _sma(closes, 20), _sma(closes, 60), _atr(bars)
    # The current bar is deliberately NOT in its own volume baseline.
    vol20 = [None if i < 20 else _round(sum(volumes[i-20:i])/20) for i in range(count)]
    rvol = [_round(volumes[i]/v) if v and volumes[i] > 0 else None for i, v in enumerate(vol20)]
    swings, levels, events = [], [], []
    for i in range(swing_span, max(swing_span, count-swing_span)):
        confirmation = i+swing_span
        if confirmation > confirmed_end:
            continue
        window = bars[i-swing_span:i+swing_span+1]
        high, low = bars[i]['high'], bars[i]['low']
        # Strict extrema avoid inventing a single turning point on a plateau.
        kinds = []
        if all(high > b['high'] for j, b in enumerate(window) if j != swing_span):
            kinds.append(('swing_high', 'resistance', high, '摆动阻力'))
        if all(low < b['low'] for j, b in enumerate(window) if j != swing_span):
            kinds.append(('swing_low', 'support', low, '摆动支撑'))
        for kind, level_kind, price, label in kinds:
            sid = f'PA-{period}-{kind}-{bars[i]["date"]}'
            swing = dict(id=sid, kind=kind, anchor_index=i, confirmed_index=confirmation,
                         dt=bars[i]['date'], confirmed_at=bars[confirmation]['date'], price=_round(price))
            swings.append(swing)
            # ATR absent => exact horizontal price, not an invented tolerance.
            tolerance = (atr14[confirmation] or 0) * .25
            lo, hi = _round(price-tolerance), _round(price+tolerance)
            rule = f'{bars[i]["date"]} 的{price:.2f}为两侧各{swing_span}根K线的严格局部极值；到 {bars[confirmation]["date"]} 才可用。'
            invalid = {'above' if level_kind == 'resistance' else 'below': hi if level_kind == 'resistance' else lo,
                       'text': f'后续收盘{"高于" if level_kind == "resistance" else "低于"} {hi if level_kind == "resistance" else lo:.2f}，原{"阻力" if level_kind == "resistance" else "支撑"}观察失效。'}
            level = dict(id=sid+'-level', swing_id=sid, kind=level_kind, label=label,
                         anchor_index=i, start_index=confirmation, end_index=count-1,
                         confirmed_index=confirmation, dt=bars[i]['date'], confirmed_at=bars[confirmation]['date'],
                         price=_round(price), zone_low=lo, zone_high=hi, status='confirmed_observation',
                         evidence=rule, reason=rule, invalid_if=invalid, initial_invalid_if=deepcopy(invalid), method='heuristic',
                         status_as_of=bars[confirmed_end]['date'] if confirmed_end >= 0 else None)
            break_index = None
            first_retest_index = None
            up = level_kind == 'resistance'
            # Ignore earlier candles even when the pivot appears retrospectively obvious.
            for j in range(confirmation+1, confirmed_end+1):
                bar, previous = bars[j], bars[j-1]
                if break_index is None:
                    crossed = (previous['close'] <= hi < bar['close']) if up else (previous['close'] >= lo > bar['close'])
                    if not crossed:
                        continue
                    break_index = j
                    level['status'] = 'broken_up' if up else 'broken_down'
                    event_kind = 'breakout_up' if up else 'breakout_down'
                    event_label = '向上突破观察' if up else '向下跌破观察'
                    reason = f'{bar["date"]} 收盘 {bar["close"]:.2f}，由前一根收盘 {previous["close"]:.2f} 穿越已确认区间 {lo:.2f}–{hi:.2f}。'
                    if rvol[j] is not None:
                        reason += f' 成交量为前20根均量的 {rvol[j]:.2f} 倍。'
                    invalid = {'below' if up else 'above': lo if up else hi,
                               'text': f'后续收盘{"跌回" if up else "升回"} {lo if up else hi:.2f}，突破延续观察失效。'}
                else:
                    failed = bar['close'] < lo if up else bar['close'] > hi
                    touched = bar['low'] <= hi and bar['high'] >= lo
                    held = touched and (bar['close'] > hi if up else bar['close'] < lo)
                    if not failed and not held:
                        continue
                    if held and first_retest_index is not None:
                        continue
                    event_kind = 'retest_failed' if failed else 'retest_hold'
                    event_label = '突破失效观察' if failed else '回踩守住观察'
                    level['status'] = event_kind
                    reason = (f'{bar["date"]} 收盘 {bar["close"]:.2f}；相对 {bars[break_index]["date"]} 的突破，'
                              + (f'已收回区间另一侧 {lo if up else hi:.2f}。' if failed else f'本根范围 {bar["low"]:.2f}–{bar["high"]:.2f} 触及 {lo:.2f}–{hi:.2f} 后收在突破侧。'))
                event = dict(id=f'{sid}-{event_kind}-{bar["date"]}', level_id=level['id'], kind=event_kind,
                             label=event_label, index=j, anchor_index=j, dt=bar['date'], price=_round(bar['close']),
                             confirmed_index=j, confirmed_at=bar['date'], level_confirmed_index=confirmation,
                             breakout_index=break_index, status='historical_observation', evidence=reason, reason=reason,
                             invalid_if=deepcopy(invalid), relative_volume=rvol[j], method='heuristic')
                events.append(event)
                level['invalid_if'] = deepcopy(invalid)
                if event_kind == 'retest_hold':
                    first_retest_index = j
                    level['first_retest_index'] = j
                    # Keep scanning: a later failed close supersedes an early held retest.
                elif event_kind == 'retest_failed':
                    level['status'] = 'invalidated'
                    level['end_index'] = j
                    level['invalidated_index'] = j
                    level['invalidated_at'] = bar['date']
                    level['reason'] += f' {bar["date"]} 收盘 {bar["close"]:.2f} 已触发突破延续失效；水平观察线截止该日。'
                    level['evidence'] = level['reason']
                    break
            levels.append(level)
    # Bounded visible set; retained events always have a retained parent level.
    levels = sorted(levels, key=lambda level: (level['confirmed_index'], level['id']))[-max_levels:]
    visible_ids = {level['id'] for level in levels}
    events = sorted((e for e in events if e['level_id'] in visible_ids), key=lambda e: (e['index'], e['id']))
    as_of = bars[-1]['date'] if bars else None
    summary = dict(as_of=as_of, last_close=closes[-1] if closes else None,
                   ma20=ma20[-1] if ma20 else None, ma60=ma60[-1] if ma60 else None,
                   atr14=atr14[-1] if atr14 else None, relative_volume=rvol[-1] if rvol else None,
                   confirmed_through=bars[confirmed_end]['date'] if confirmed_end >= 0 else None,
                   visible_levels=len(levels), event_count=len(events), last_bar_complete=bool(last_bar_complete))
    return dict(schema_version=SCHEMA_VERSION, period=period, status='ok' if count >= 20 else 'partial' if count else 'unavailable',
                method='heuristic', bar_count=count, quality=quality,
                provenance=dict(source=source, adjusted=adjusted, as_of=as_of, last_bar_complete=bool(last_bar_complete)),
                parameters=dict(swing_left=swing_span, swing_right=swing_span, atr_period=14, zone_atr_multiplier=.25,
                                volume_baseline='previous_20_bars', max_visible_levels=max_levels),
                indicators=dict(ma20=ma20, ma60=ma60, atr14=atr14, volume_sma20=vol20, relative_volume=rvol),
                moving_averages=[dict(id=f'PA-{period}-MA{n}', label=f'MA{n}', period=n,
                                     points=[dict(index=i, price=p) for i, p in enumerate(series) if p is not None])
                                 for n, series in ((20, ma20), (60, ma60))],
                volume=[dict(index=i, volume=v) for i, v in enumerate(volumes)],
                swings=swings, levels=levels, events=events, summary=summary,
                warnings=['价格行为为明确规则的启发式观察，不是严格缠论买卖点、概率预测或回测结果。',
                          '末根K线收盘状态未核验时，仅供观察，不用于确认新摆动或突破。',
                          '缺失或异常成交量按0保留，量比不可用时为null；不推定量能确认。'])


def enrich_chan_price_action(chan: dict) -> dict:
    """Attach same-coordinate deterministic price action to existing Chan levels."""
    result = dict(schema_version=SCHEMA_VERSION, method='heuristic', ticker=chan.get('ticker'), levels={})
    for key, level in (chan.get('levels') or {}).items():
        if key not in ('D', 'W') or not isinstance(level, Mapping):
            continue
        bars = level.get('bars')
        if not isinstance(bars, list):
            bars = []
        provenance = level.get('provenance') or chan.get('provenance') or {}
        complete = provenance.get('last_bar_is_complete') is True
        if key == 'W':
            complete = provenance.get('weekly_last_bar_is_complete') is True
        value = build_price_action_level(bars, period=key, source=provenance.get('source') or chan.get('source', 'unknown'),
                                        adjusted=provenance.get('adjusted', chan.get('adjusted')), last_bar_complete=complete)
        # Existing Chan snapshots must retain the identical date/index basis.
        # Invalid or reordered third-party level payloads receive no overlays,
        # rather than silently attaching lines to different candles.
        normalized, _ = normalize_ohlcv_rows(bars)
        source_dates = [str(b.get('dt') or b.get('date') or b.get('Date') or b.get('日期') or '')[:10] if isinstance(b, Mapping) else '' for b in bars]
        indices_match = all(isinstance(b, Mapping) and b.get('index', i) == i for i, b in enumerate(bars))
        if source_dates != [b['date'] for b in normalized] or not indices_match:
            value['status'] = 'unavailable'
            value['reason'] = 'unaligned_source_coordinates'
            value['warnings'].append('输入日期/索引未与原始图对齐，价格行为叠加层已停用；请先规范OHLCV再重新计算。')
            for field in ('moving_averages', 'volume', 'swings', 'levels', 'events'):
                value[field] = []
            value['summary']['visible_levels'] = value['summary']['event_count'] = 0
        level['price_action'] = value
        result['levels'][key] = value
    return result

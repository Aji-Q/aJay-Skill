/* J Trader Chan v1 offline workbench. No CDN, no data mutation, no generic SVG tracing. */
(function () {
  'use strict';

  function all(selector, scope) {
    return Array.prototype.slice.call((scope || document).querySelectorAll(selector));
  }

  function first(selector, scope) {
    return (scope || document).querySelector(selector);
  }

  function setHidden(element, hidden) {
    if (!element) return;
    element.hidden = !!hidden;
    if (hidden) element.setAttribute('hidden', '');
    else element.removeAttribute('hidden');
  }

  function motionOff(root) {
    var html = document.documentElement;
    if (html && html.dataset.motion === 'off') return true;
    if (html && html.dataset.motion === 'on') return false;
    return !!(window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches);
  }

  function currentPanel(root) {
    return first('.chan-level-panel:not([hidden])', root) || first('.chan-level-panel', root);
  }

  function levelPanels(root) {
    return all('.chan-level-panel[data-chan-level-panel]', root);
  }

  function activeLevel(root) {
    var tab = first('.chan-level-tab[aria-selected="true"]', root);
    return tab ? tab.dataset.chanLevel : 'D';
  }

  function levelState(root, level) {
    root._chanState = root._chanState || {};
    root._chanState[level] = root._chanState[level] || { step: 0, selected: null, overview: true };
    return root._chanState[level];
  }

  function steps(panel) {
    return all('[data-chan-step-list] .chan-step-card[data-chan-step-card]', panel);
  }

  function annotations(panel) {
    return all('[data-chan-annotation]', panel);
  }

  function conditionMarks(panel) {
    return all('.chan-condition-line,.chan-condition-link,.chan-condition-arrow,.chan-condition-label', panel);
  }

  function updateLive(root) {
    var panel = currentPanel(root);
    var live = first('[data-chan-live]', root);
    if (!panel || !live) return;
    var cards = steps(panel);
    var state = levelState(root, activeLevel(root));
    if (state.overview) live.textContent = cards.length ? ('全览 · ' + cards.length + ' 步') : '全览';
    else live.textContent = cards.length ? ('第 ' + (Math.min(state.step, cards.length - 1) + 1) + ' 步 / ' + cards.length) : '暂无步骤';
    var prev = first('[data-chan-action="prev"]', root);
    var next = first('[data-chan-action="next"]', root);
    if (prev) prev.disabled = !cards.length || (state.overview && state.step <= 0);
    if (next) next.disabled = !cards.length || (!state.overview && state.step >= cards.length - 1);
  }

  function clearRangeFocus(panel) {
    if (!panel) return;
    all('.chan-candle.is-range-focus', panel).forEach(function (bar) {
      bar.classList.remove('is-range-focus');
    });
    panel.removeAttribute('data-focus-range');
  }

  function numberOrNull(value) {
    if (value === null || value === undefined || value === '') return null;
    var number = Number(value);
    return Number.isFinite(number) ? number : null;
  }

  function focusRange(root, panel, target) {
    clearRangeFocus(panel);
    if (!panel || !target) return;
    var start = numberOrNull(target.dataset.startIndex);
    var end = numberOrNull(target.dataset.endIndex);
    var anchor = numberOrNull(target.dataset.anchorIndex);
    if (start === null && anchor !== null) start = anchor;
    if (end === null && anchor !== null) end = anchor;
    if (start === null && end === null) return;
    if (start === null) start = end;
    if (end === null) end = start;
    if (start > end) {
      var swap = start;
      start = end;
      end = swap;
    }
    panel.dataset.focusRange = start + ':' + end;
    var focusBar = null;
    all('.chan-candle[data-bar-index]', panel).forEach(function (bar) {
      var index = numberOrNull(bar.dataset.barIndex);
      var selected = index !== null && index >= start && index <= end;
      bar.classList.toggle('is-range-focus', selected);
      if (selected && !focusBar) focusBar = bar;
    });
    if (focusBar) {
      // Keep focus inside the chart's own overflow container; do not move the
      // whole report while a point-table row is being inspected.
      var frame = first('.chan-chart-frame', panel);
      if (frame && frame.scrollWidth > frame.clientWidth && typeof frame.scrollTo === 'function') {
        var barRect = focusBar.getBoundingClientRect();
        var frameRect = frame.getBoundingClientRect();
        var nextLeft = frame.scrollLeft + (barRect.left + barRect.width / 2) - (frameRect.left + frameRect.width / 2);
        frame.scrollTo({ left: Math.max(0, nextLeft), behavior: motionOff(root) ? 'auto' : 'smooth' });
      }
    }
  }

  function focusStepRange(root, panel, ids) {
    clearRangeFocus(panel);
    if (!ids.length) return;
    var targets = ids.map(function (id) { return annotationByKey(panel, id); }).filter(Boolean);
    if (!targets.length) return;
    var ranges = targets.map(function (target) {
      var start = numberOrNull(target.dataset.startIndex);
      var end = numberOrNull(target.dataset.endIndex);
      var anchor = numberOrNull(target.dataset.anchorIndex);
      return {
        start: start === null ? anchor : start,
        end: end === null ? anchor : end,
      };
    }).filter(function (range) { return range.start !== null || range.end !== null; });
    if (!ranges.length) return;
    var min = Math.min.apply(Math, ranges.map(function (range) { return range.start === null ? range.end : range.start; }));
    var max = Math.max.apply(Math, ranges.map(function (range) { return range.end === null ? range.start : range.end; }));
    var pseudo = { dataset: { startIndex: String(min), endIndex: String(max) } };
    focusRange(root, panel, pseudo);
    var range=chartRange(panel);if(range && (min<range.start || max>range.end)){var width=Math.max(chartLayout(panel).mobile?40:60,(max-min)*1.3),mid=(min+max)/2;setRange(panel,mid-width/2,mid+width/2);}
  }

  function selectLevel(root, level, focusTab) {
    var tabs = all('.chan-level-tab[data-chan-level]', root);
    stopAnimations(root);
    tabs.forEach(function (tab) {
      var selected = tab.dataset.chanLevel === level;
      tab.setAttribute('aria-selected', selected ? 'true' : 'false');
      if (selected && focusTab) tab.focus({ preventScroll: true });
    });
    levelPanels(root).forEach(function (panel) {
      setHidden(panel, panel.dataset.chanLevelPanel !== level);
    });
    updateStepView(root);
    updateLive(root);
    var panel=currentPanel(root),range=panel && chartRange(panel);if(range)setRange(panel,range.start,range.end);

  }

  function updateStepView(root) {
    var panel = currentPanel(root);
    if (!panel) return;
    var state = levelState(root, activeLevel(root));
    var cards = steps(panel);
    var current = Math.max(0, Math.min(state.step, Math.max(cards.length - 1, 0)));
    state.step = current;
    var currentHost = first('[data-chan-current-step]', panel);
    if (currentHost) {
      if (state.overview) {
        var overview = panel.querySelector('[data-chan-overview]');
        if (overview) {
          var overviewClone = overview.cloneNode(true);
          setHidden(overviewClone, false);
          overviewClone.classList.remove('chan-overview-source');
          currentHost.innerHTML = overviewClone.outerHTML;
        } else {
          currentHost.innerHTML = '<p>当前级别处于全览。</p>';
        }
      } else {
        var currentCard = cards[current];
        currentHost.innerHTML = currentCard ? currentCard.outerHTML : '<p>当前级别暂无步骤讲解。</p>';
      }
    }
    cards.forEach(function (card, index) {
      card.classList.toggle('is-step-current', index === current && !state.overview);
      card.setAttribute('aria-current', !state.overview && index === current ? 'step' : 'false');
    });
    var ids = (!state.overview && cards[current]) ? cards[current].dataset.annotationIds : '';
    // The renderer marks annotation IDs on each card for a pure-DOM bridge.
    var selectedIds = ids ? ids.split(/\s+/).filter(Boolean) : [];
    var focalIds = (!state.overview && cards[current]) ? (cards[current].dataset.focusIds || ids).split(/\s+/).filter(Boolean) : [];
    annotations(panel).forEach(function (annotation) {
      annotation.classList.toggle('is-step-focus', focalIds.indexOf(annotation.dataset.chanAnnotation) >= 0);
    });
    var mode = root.dataset.annotationMode || (state.overview ? 'all' : 'step');
    var allToggle = first('[data-chan-action="all"]', root);
    var hideToggle = first('[data-chan-action="hide"]', root);
    if (allToggle) allToggle.setAttribute('aria-pressed', mode === 'all' ? 'true' : 'false');
    if (hideToggle) hideToggle.setAttribute('aria-pressed', mode === 'hidden' ? 'true' : 'false');
    var reveal = {};
    var currentCard = cards[current];
    var phase = mode === 'hidden' ? 'hidden' : mode === 'all' || state.overview ? 'all' : (currentCard && currentCard.dataset.stepKind) || ('step-' + current);
    panel.dataset.chanPhase = phase;
    if (!state.overview && mode === 'step') {
      cards.slice(0, current + 1).forEach(function (card) {
        (card.dataset.annotationIds || '').split(/\s+/).filter(Boolean).forEach(function (id) { reveal[id] = true; });
      });
    }
    annotations(panel).forEach(function (annotation) {
      var visible = mode !== 'hidden' && (mode === 'all' || state.overview || reveal[annotation.dataset.chanAnnotation]);
      setHidden(annotation, !visible);
    });
    var showConditions = mode !== 'hidden' && (mode === 'all' || state.overview || phase === 'invalidations' || current >= cards.length - 1 && current >= 5);
    conditionMarks(panel).forEach(function (mark) {
      setHidden(mark, !showConditions);
    });
    if (state.selected) {
      var selected = annotationByKey(panel, state.selected);
      if (selected) focusRange(root, panel, selected);
      else focusStepRange(root, panel, focalIds);
    } else {
      focusStepRange(root, panel, focalIds);
    }
    updateLive(root);
    updateOverlays(root);
  }

  function setAnnotations(root, visible) {
    root.dataset.annotations = visible ? 'all' : 'hidden';
    root.dataset.annotationMode = visible ? 'all' : 'hidden';
    levelPanels(root).forEach(function (panel) {
      annotations(panel).forEach(function (annotation) {
        setHidden(annotation, !visible);
      });
      conditionMarks(panel).forEach(function (mark) {
        setHidden(mark, !visible);
      });
    });
    var allButton = first('[data-chan-action="all"]', root);
    var hideButton = first('[data-chan-action="hide"]', root);
    if (allButton) allButton.setAttribute('aria-pressed', visible ? 'true' : 'false');
    if (hideButton) hideButton.setAttribute('aria-pressed', visible ? 'false' : 'true');
    updateOverlays(root);
  }

  function annotationByKey(panel, key) {
    return annotations(panel).find(function (item) { return item.dataset.chanAnnotation === key; });
  }

  function showPointDetail(root, panel, key) {
    var host = first('[data-chan-current-step]', panel);
    if (!host) return;
    var row = all('[data-chan-point-row]', panel).find(function (entry) { return entry.dataset.chanPointRow === key; });
    if (!row) return;
    var cells = all('td', row);
    if (cells.length < 7) return;
    var detail = document.createElement('article');
    detail.className = 'chan-selected-detail';
    detail.setAttribute('data-chan-selected-detail', key);
    var title = document.createElement('h4');
    title.textContent = first('button', cells[0]).textContent;
    detail.appendChild(title);
    [ ['日期 / 周期', cells[2].textContent + ' · ' + cells[1].textContent],
      ['价格 / 区间', cells[3].textContent], ['状态', cells[4].textContent],
      ['成立依据', cells[5].textContent], ['失效条件', cells[6].textContent] ].forEach(function (entry) {
        var p = document.createElement('p');
        var label = document.createElement('strong');
        label.textContent = entry[0];
        p.appendChild(label);
        p.appendChild(document.createTextNode(entry[1]));
        detail.appendChild(p);
      });
    var previous = first('[data-chan-selected-detail]', host);
    if (previous) previous.remove();
    host.replaceChildren(detail);
  }

  function selectPoint(root, key, moveToStep) {
    var panel = currentPanel(root);
    if (!panel || !key) return;
    var state = levelState(root, activeLevel(root));
    state.selected = key;
    root.dataset.annotationMode = 'step';
    root.dataset.annotations = 'all';
    annotations(panel).forEach(function (annotation) {
      var selected = annotation.dataset.chanAnnotation === key;
      annotation.classList.toggle('is-selected', selected);
      annotation.setAttribute('aria-pressed', selected ? 'true' : 'false');
    });
    all('[data-chan-point-row]', panel).forEach(function (row) {
      var selected = row.dataset.chanPointRow === key;
      row.classList.toggle('is-selected', selected);
      row.setAttribute('aria-selected', selected ? 'true' : 'false');
    });
    if (moveToStep) {
      var cards = steps(panel);
      var stepIndex = cards.findIndex(function (card) {
        return (card.dataset.annotationIds || '').split(/\s+/).indexOf(key) >= 0;
      });
      if (stepIndex >= 0) {
        state.overview = false;
        state.step = stepIndex;
        updateStepView(root);
      }
    }
    showPointDetail(root, panel, key);
    var target = annotationByKey(panel, key);
    if (target) {
      focusRange(root, panel, target);
      var rr = chartRange(panel), aa = numberOrNull(target.dataset.anchorIndex), ss = numberOrNull(target.dataset.startIndex), ee = numberOrNull(target.dataset.endIndex);
      if (ss === null) ss = aa; if (ee === null) ee = aa;
      if (rr && ss !== null && ee !== null && (Math.min(ss,ee) < rr.start || Math.max(ss,ee) > rr.end)) { var span = Math.max(60, Math.abs(ee-ss)*1.5); var mid = (ss+ee)/2; setRange(panel,mid-span/2,mid+span/2); }
      target.focus({ preventScroll: true });
      // A table click may originate below the chart.  Move the page only for
      // this explicit user action; step changes stay in place.
      var chartFrame = first('.chan-chart-frame', panel);
      if (chartFrame && typeof window.scrollTo === 'function' && typeof window.innerHeight === 'number') {
        var chartRect = chartFrame.getBoundingClientRect();
        if (chartRect.bottom < 0 || chartRect.top > window.innerHeight) {
          var pageTop = (window.pageYOffset || document.documentElement.scrollTop || 0) + chartRect.top - 100;
          window.scrollTo({ top: Math.max(0, pageTop), behavior: motionOff(root) ? 'auto' : 'smooth' });
        }
      }
    }
  }

  function stopAnimations(root) {
    var gsap = window.gsap;
    var animated = all('.chan-bi,.chan-center-band,.chan-condition-line,.chan-condition-link,.chan-condition-arrow,.chan-annotation-halo,.chan-annotation-label', root);
    if (gsap && typeof gsap.killTweensOf === 'function') gsap.killTweensOf(animated);
    all('[data-chan-motion-dash]', root).forEach(function (line) {
      line.style.removeProperty('stroke-dasharray');
      line.style.removeProperty('stroke-dashoffset');
      line.removeAttribute('stroke-dasharray');
      line.removeAttribute('stroke-dashoffset');
      line.removeAttribute('data-chan-motion-dash');
    });
    all('.chan-center-band,.chan-condition-arrow,.chan-annotation-halo,.chan-annotation-label', root).forEach(function (element) {
      element.style.removeProperty('opacity');
    });
  }

  function semanticLength(element) {
    if (!element) return 0;
    if (typeof element.getTotalLength === 'function') {
      var measured = element.getTotalLength();
      if (Number.isFinite(measured) && measured > 0) return measured;
    }
    // SVGRectElement is not consistently an SVGGeometryElement across
    // browsers.  Its center band is still semantic geometry, so use its
    // explicit perimeter only as a local fallback.
    if (element.classList.contains('chan-center-band')) {
      var width = numberOrNull(element.getAttribute('width')) || 0;
      var height = numberOrNull(element.getAttribute('height')) || 0;
      var perimeter = 2 * (width + height);
      return perimeter > 0 ? perimeter : 0;
    }
    return 0;
  }

  function replay(root) {
    var panel = currentPanel(root);
    if (!panel || motionOff(root)) {
      stopAnimations(root);
      return;
    }
    var state = levelState(root, activeLevel(root));
    if (state.overview) return;
    stopAnimations(root);
    var cards = steps(panel);
    var card = cards[state.step];
    var ids = card ? (card.dataset.focusIds || card.dataset.annotationIds || '').split(/\s+/).filter(Boolean) : [];
    var targets = ids.map(function (id) { return annotationByKey(panel, id); }).filter(function (target) {
      return target && ['bi', 'unfinished-bi', 'center', 'signal'].indexOf(target.dataset.kind) >= 0;
    });
    if (!targets.length && state.selected) {
      var selected = annotationByKey(panel, state.selected);
      if (selected) targets = [selected];
    }
    var gsap = window.gsap;
    var drawing = [];
    var fading = [];
    targets.forEach(function (target) {
      // Draw only semantic lines; candles and generic SVG geometry remain static.
      all('.chan-bi,.chan-center-band,.chan-condition-line,.chan-condition-link', target).forEach(function (line) {
        var length = semanticLength(line);
        if (!length) return;
        line.style.strokeDasharray = length + ' ' + length;
        line.style.strokeDashoffset = length + 'px';
        line.setAttribute('data-chan-motion-dash', 'true');
        drawing.push(line);
      });
      fading = fading.concat(all('.chan-center-band,.chan-annotation-halo,.chan-annotation-label,.chan-condition-arrow', target));
    });
    if (gsap && typeof gsap.to === 'function' && drawing.length) {
      gsap.to(drawing, { strokeDashoffset: 0, duration: 0.62, stagger: 0.08, ease: 'power2.out', overwrite: true });
    } else {
      drawing.forEach(function (line) { line.style.strokeDashoffset = '0px'; });
    }
    if (gsap && typeof gsap.fromTo === 'function' && fading.length) {
      gsap.fromTo(fading, { opacity: 0.25 }, { opacity: 1, duration: 0.42, stagger: 0.04, ease: 'power2.out', overwrite: true });
    }
  }

  function changeStep(root, delta) {
    var panel = currentPanel(root);
    if (!panel) return;
    var state = levelState(root, activeLevel(root));
    var cards = steps(panel);
    if (!cards.length) return;
    state.selected = null;
    all('.is-selected', panel).forEach(function (element) { element.classList.remove('is-selected'); element.removeAttribute('aria-selected'); });
    root.dataset.annotationMode = 'step';
    if (state.overview) {
      if (delta > 0) {
        state.overview = false;
        state.step = 0;
        root.dataset.annotationMode = 'step';
        updateStepView(root);
        replay(root);
      }
      return;
    }
    if (delta < 0 && state.step <= 0) {
      state.overview = true;
      root.dataset.annotationMode = 'all';
      stopAnimations(root);
    } else {
      state.step = Math.max(0, Math.min(cards.length - 1, state.step + delta));
    }
    updateStepView(root);
    if (!state.overview) replay(root);
  }

  function restartExplanation(root) {
    var panel = currentPanel(root);
    if (!panel) return;
    var cards = steps(panel);
    if (!cards.length) return;
    var state = levelState(root, activeLevel(root));
    state.overview = false;
    state.step = 0;
    root.dataset.annotationMode = 'step';
    updateStepView(root);
    replay(root);
  }

  function bindTabs(root) {
    var tabs = all('.chan-level-tab[data-chan-level]', root);
    tabs.forEach(function (tab, index) {
      tab.addEventListener('click', function () { selectLevel(root, tab.dataset.chanLevel, false); });
      tab.addEventListener('keydown', function (event) {
        var next = null;
        if (event.key === 'ArrowRight' || event.key === 'ArrowDown') next = tabs[(index + 1) % tabs.length];
        if (event.key === 'ArrowLeft' || event.key === 'ArrowUp') next = tabs[(index - 1 + tabs.length) % tabs.length];
        if (event.key === 'Home') next = tabs[0];
        if (event.key === 'End') next = tabs[tabs.length - 1];
        if (next) { event.preventDefault(); selectLevel(root, next.dataset.chanLevel, true); }
      });
    });
  }

  function bindActions(root) {
    all('[data-chan-action]', root).forEach(function (button) {
      button.addEventListener('click', function () {
        var action = button.dataset.chanAction;
        if (action === 'prev') changeStep(root, -1);
        if (action === 'next') changeStep(root, 1);
        if (action === 'all') setAnnotations(root, true);
        if (action === 'hide') setAnnotations(root, false);
        if (action === 'replay') restartExplanation(root);
      });
    });
  }

  function bindPoints(root) {
    all('[data-chan-point]', root).forEach(function (button) {
      button.addEventListener('click', function () { selectPoint(root, button.dataset.chanPoint, true); });
    });
    all('[data-chan-annotation]', root).forEach(function (annotation) {
      annotation.addEventListener('click', function () { selectPoint(root, annotation.dataset.chanAnnotation, true); });
      annotation.addEventListener('keydown', function (event) {
        if (event.key === 'Enter' || event.key === ' ') {
          event.preventDefault();
          selectPoint(root, annotation.dataset.chanAnnotation, true);
        }
      });
    });
  }

  function updateMotion(root) {
    var off = motionOff(root);
    stopAnimations(root);
    root.classList.toggle('chan-motion-off', off);
  }

  function watchMotion(root) {
    var html = document.documentElement;
    if (html && window.MutationObserver) {
      var observer = new MutationObserver(function () { updateMotion(root); });
      observer.observe(html, { attributes: true, attributeFilter: ['data-motion'] });
      root._chanMotionObserver = observer;
    }
    if (window.matchMedia) {
      var media = window.matchMedia('(prefers-reduced-motion: reduce)');
      var listener = function () { updateMotion(root); };
      if (media.addEventListener) media.addEventListener('change', listener);
      else if (media.addListener) media.addListener(listener);
      root._chanMotionMedia = media;
    }
    updateMotion(root);
  }

  // Viewport manipulation stays inside this chart. No wheel listener: page scrolling is never captured.
  function chartRange(panel) {
    var svg = first('[data-chan-chart]', panel);
    if (!svg) return null;
    var min = numberOrNull(svg.dataset.minIndex) || 0;
    var max = numberOrNull(svg.dataset.maxIndex);
    if (max === null || max <= min) max = min + 1;
    var recent = window.matchMedia && window.matchMedia('(max-width: 760px)').matches ? 44 : 119;
    panel._chanRange = panel._chanRange || { min: min, max: max, start: Math.max(min, max - recent), end: max };
    return panel._chanRange;
  }

  function chartLayout(panel) {
    var root=panel.closest('.chan-desk'), frame=first('.chan-chart-frame',panel);
    var mobile=!(root && root._chanPrinting) && window.matchMedia && window.matchMedia('(max-width: 760px)').matches;
    var width=mobile ? Math.max(240,frame.clientWidth || (root ? root.clientWidth-32 : window.innerWidth-64)) : 960;
    return {mobile:mobile,width:width,height:mobile?390:550,left:mobile?56:84,right:mobile?width-12:930,top:mobile?22:28,bottom:mobile?292:410,volumeTop:mobile?310:450,volumeBottom:mobile?354:512,dateY:mobile?380:535};
  }

  function setRange(panel, start, end) {
    var state = chartRange(panel);
    var svg = first('[data-chan-chart]', panel);
    var viewport = first('.chan-plot-viewport', panel);
    if (!state || !svg || !viewport) return;
    var layout=chartLayout(panel);panel._chanLayout=layout;
    svg.setAttribute('viewBox','0 0 '+layout.width+' '+layout.height);svg.style.height=layout.mobile?'390px':'';
    var surface=first('.chan-plot-surface',svg);surface.setAttribute('width',layout.width);surface.setAttribute('height',layout.height);
    var priceClip=first('[id="chan-clip-'+panel.dataset.chanLevelPanel+'"] rect',svg);
    priceClip.setAttribute('x',layout.left);priceClip.setAttribute('width',layout.right-layout.left);priceClip.setAttribute('y',layout.top-12);priceClip.setAttribute('height',layout.bottom-layout.top+24);
    var volumeClip=first('[id="chan-volume-clip-'+panel.dataset.chanLevelPanel+'"] rect',svg);
    volumeClip.setAttribute('x',layout.left);volumeClip.setAttribute('width',layout.right-layout.left);volumeClip.setAttribute('y',layout.volumeTop-2);volumeClip.setAttribute('height',layout.volumeBottom-layout.volumeTop+4);
    all('.chan-empty-label',svg).forEach(function(label){label.setAttribute('x',(layout.left+layout.right)/2);label.setAttribute('y',(layout.top+layout.bottom)/2);});
    var full = state.max - state.min;
    var span = Math.max(Math.min(19, full), Math.min(full, end - start));
    start = Math.max(state.min, Math.min(state.max - span, start));
    end = start + span;
    state.start = start; state.end = end;
    var scale = (layout.right-layout.left)/846 * full / Math.max(span, 1);
    var translate = layout.left - (84 + (start - state.min) / full * 846) * scale;
    all('.chan-plot-viewport',panel).forEach(function(layer){layer.setAttribute('transform', 'translate(' + translate + ' 0) scale(' + scale + ' 1)');});
    // Keep annotation text glyphs unscaled while their anchors follow the time viewport.
    all('text,circle,polygon', viewport).forEach(function (label) {
      var tag=label.tagName.toLowerCase();
      var x = numberOrNull(label.getAttribute(tag==='circle' ? 'cx' : 'x')) || 0;
      if(tag==='polygon'){var points=(label.getAttribute('points')||'').trim().split(/\s+/).map(function(p){return Number(p.split(',')[0]);});if(points.length)x=points.reduce(function(a,b){return a+b;},0)/points.length;}
      label.setAttribute('transform', 'translate(' + x + ' 0) scale(' + (1 / scale) + ' 1) translate(' + (-x) + ' 0)');
    });
    all('[data-chan-annotation],[data-pa-point]', viewport).forEach(function (mark) {
      var anchor = numberOrNull(mark.dataset.anchorIndex);
      var from = numberOrNull(mark.dataset.startIndex);
      var to = numberOrNull(mark.dataset.endIndex);
      if (from === null) from = anchor;
      if (to === null) to = anchor;
      var visible = from !== null && to !== null && Math.max(from, to) >= start && Math.min(from, to) <= end;
      mark.setAttribute('tabindex', visible ? '0' : '-1');
    });
    var bars = all('.chan-candle', panel);
    // Fit the price axis to the visible real candles; preserve base coordinates for exact reversible redraw.
    var visible = bars.filter(function(bar){var i=Number(bar.dataset.barIndex);return i>=Math.floor(start)&&i<=Math.ceil(end);});
    if(visible.length){
      var lo=Math.min.apply(Math,visible.map(function(b){return Number(b.dataset.low);}));
      var hi=Math.max.apply(Math,visible.map(function(b){return Number(b.dataset.high);}));
      var pad=Math.max((hi-lo)*.09,Math.abs(hi)*.004,.000001);lo-=pad;hi+=pad;
      var oldLo=Number(svg.dataset.priceLow),oldHi=Number(svg.dataset.priceHigh);
      panel._chanPriceRange={low:lo,high:hi};
      function mapY(v){var price=oldHi-(v-28)/382*(oldHi-oldLo);return layout.bottom-(price-lo)/(hi-lo)*(layout.bottom-layout.top);}
      var geometry=first('.chan-price-viewport',panel);
      all('line,rect,circle,text,polygon,polyline',geometry).forEach(function(node){
        if(!node._chanBase){node._chanBase={};['y','y1','y2','cy','height','points'].forEach(function(attr){var value=node.getAttribute(attr);if(value!==null)node._chanBase[attr]=value;});}
        var base=node._chanBase;
        ['y','y1','y2','cy'].forEach(function(attr){if(base[attr]!==undefined)node.setAttribute(attr,mapY(Number(base[attr])).toFixed(3));});
        if(base.height!==undefined){var size=Number(base.height)*(oldHi-oldLo)/(hi-lo)*(layout.bottom-layout.top)/382;node.setAttribute('height',Math.max(.4,size).toFixed(3));}
        if(node.dataset.anchorY!==undefined){node.setAttribute('y',Math.max(layout.top-8,Math.min(layout.bottom+16,mapY(Number(node.dataset.anchorY))+Number(node.dataset.labelOffset||0))).toFixed(3));}
        if(base.points!==undefined){node.setAttribute('points',base.points.trim().split(/\s+/).map(function(pair){var xy=pair.split(',');return xy[0]+','+mapY(Number(xy[1])).toFixed(3);}).join(' '));}
      });
      all('.chan-axis-label',svg).forEach(function(label,i){label.textContent=(hi-(hi-lo)*i/4).toLocaleString(undefined,{maximumFractionDigits:2,minimumFractionDigits:2});label.setAttribute('x',layout.left-10);label.setAttribute('y',layout.top+(layout.bottom-layout.top)*i/4+3);});
    }
    all('.chan-grid-line',svg).forEach(function(line,i){var y=layout.top+(layout.bottom-layout.top)*i/4;line.setAttribute('x1',layout.left);line.setAttribute('x2',layout.right);line.setAttribute('y1',y);line.setAttribute('y2',y);});
    all('.chan-axis-line',svg).forEach(function(line){line.setAttribute('x1',layout.left);line.setAttribute('x2',layout.right);line.setAttribute('y1',layout.bottom);line.setAttribute('y2',layout.bottom);});
    all('.chan-volume rect',svg).forEach(function(bar){if(!bar._chanBase)bar._chanBase={y:bar.getAttribute('y'),height:bar.getAttribute('height')};var scale=(layout.volumeBottom-layout.volumeTop)/62;bar.setAttribute('y',layout.volumeBottom-(512-Number(bar._chanBase.y))*scale);bar.setAttribute('height',Number(bar._chanBase.height)*scale);});
    function barNear(index) {
      return bars.reduce(function (best, bar) {
        return !best || Math.abs(Number(bar.dataset.barIndex)-index) < Math.abs(Number(best.dataset.barIndex)-index) ? bar : best;
      }, null);
    }
    var visibleBars = [barNear(start), barNear((start+end)/2), barNear(end)];
    all('.chan-date-label', svg).forEach(function (label, i) {
      if (!visibleBars[i]) return;
      label.textContent = visibleBars[i].dataset.date.slice(0,10);
      label.setAttribute('x', String([layout.left,(layout.left+layout.right)/2,layout.right][i]));
      label.setAttribute('y',layout.dateY);setHidden(label,layout.mobile && i===1);
      label.setAttribute('text-anchor', ['start','middle','end'][i]);
    });
    var rangeLabel = first('[data-chan-visible-range]', panel);
    if (rangeLabel && visibleBars[0] && visibleBars[2]) rangeLabel.textContent = visibleBars[0].dataset.date.slice(0,10) + ' — ' + visibleBars[2].dataset.date.slice(0,10);
    panel.dataset.visibleStart = String(start); panel.dataset.visibleEnd = String(end);
    setHidden(first('.chan-crosshair', panel), true);
  }

  function rangeAction(root, action) {
    stopAnimations(root);
    var panel = currentPanel(root), range = panel && chartRange(panel);
    if (!range) return;
    var span = range.end - range.start;
    if (action === 'full') return setRange(panel, range.min, range.max);
    if (action === 'recent') return setRange(panel, Math.max(range.min, range.max-(chartLayout(panel).mobile?44:119)), range.max);
    if (action === 'left') return setRange(panel, range.start-span*.25, range.end-span*.25);
    if (action === 'right') return setRange(panel, range.start+span*.25, range.end+span*.25);
    var factor = action === 'zoom-in' ? .65 : 1.5;
    var mid = (range.start+range.end)/2;
    setRange(panel, mid-span*factor/2, mid+span*factor/2);
  }

  function updateOverlays(root) {
    var selected = {};
    all('[data-chan-overlay]', root).forEach(function (button) { selected[button.dataset.chanOverlay] = button.getAttribute('aria-pressed') === 'true'; });
    levelPanels(root).forEach(function (panel) {
      all('[data-pa-layer]', panel).forEach(function (layer) { setHidden(layer, selected[layer.dataset.paLayer] === false || layer.dataset.paLayer==='levels' && layer.dataset.paSecondary==='true' && !selected['level-history'] || root.dataset.annotationMode === 'hidden' && ['levels','events'].indexOf(layer.dataset.paLayer)>=0); });
      panel.dataset.showFractals = selected.fractals ? 'true' : 'false';
    });
  }

  function showPriceAction(root, target) {
    var panel = currentPanel(root), host = panel && first('[data-chan-current-step]', panel);
    if (!host) return;
    all('.chan-pa-point.is-selected', panel).forEach(function (p) { p.classList.remove('is-selected'); });
    target.classList.add('is-selected');
    var article = document.createElement('article'); article.className = 'chan-selected-detail';
    var title = document.createElement('h4'); var price=numberOrNull(target.dataset.price);title.textContent = target.dataset.label + ' · ' + (price===null?'未记录':price.toLocaleString(undefined,{minimumFractionDigits:2,maximumFractionDigits:Math.abs(price)<1?4:2})); article.appendChild(title);
    [ ['成立依据', target.dataset.evidence], ['失效条件', target.dataset.invalid] ].forEach(function (entry) {
      var p = document.createElement('p'), label = document.createElement('strong'); label.textContent = entry[0]; p.appendChild(label); p.appendChild(document.createTextNode(entry[1] || '未记录')); article.appendChild(p);
    });
    host.replaceChildren(article);
    focusRange(root, panel, target);
  }

  function bindChartInteraction(root) {
    all('[data-chan-range]', root).forEach(function (button) { button.addEventListener('click', function () { rangeAction(root, button.dataset.chanRange); }); });
    all('[data-chan-overlay]', root).forEach(function (button) { button.addEventListener('click', function () { button.setAttribute('aria-pressed', button.getAttribute('aria-pressed') !== 'true' ? 'true' : 'false'); updateOverlays(root); }); });
    levelPanels(root).forEach(function (panel) {
      var svg = first('[data-chan-chart]', panel);
      if (!svg) return;
      // Expand only semantic line hit areas without changing the visible geometry.
      all('.chan-bi,.chan-pa-level', svg).forEach(function(line){var hit=line.cloneNode(false);hit.removeAttribute('id');hit.setAttribute('class','chan-hit-line');hit.setAttribute('aria-hidden','true');line.parentNode.insertBefore(hit,line);});
      var bars = all('.chan-candle', panel), pointers = {}, drag = null, pinch = null, suppressClick = false;
      function coordinate(event) {
        var point = svg.createSVGPoint(); point.x = event.clientX; point.y = event.clientY;
        return point.matrixTransform(svg.getScreenCTM().inverse());
      }
      function readAt(event) {
        var range = chartRange(panel), p = coordinate(event), layout=panel._chanLayout || chartLayout(panel);
        if (!bars.length || p.x < layout.left || p.x > layout.right || p.y < layout.top || p.y > layout.volumeBottom) return setHidden(first('.chan-crosshair', panel), true);
        var index = range.start + (p.x-layout.left)/(layout.right-layout.left)*(range.end-range.start);
        var bar = bars.reduce(function (best, item) { return !best || Math.abs(Number(item.dataset.barIndex)-index) < Math.abs(Number(best.dataset.barIndex)-index) ? item : best; }, null);
        var data = bar.dataset, x = layout.left + (Number(data.barIndex)-range.start)/(range.end-range.start)*(layout.right-layout.left);
        var cross = first('.chan-crosshair', panel), vertical = first('.chan-crosshair-v', cross), horizontal = first('.chan-crosshair-h', cross);
        setHidden(cross, false); vertical.setAttribute('x1',x); vertical.setAttribute('x2',x);vertical.setAttribute('y1',layout.top);vertical.setAttribute('y2',layout.volumeBottom);
        var yy = Math.min(layout.bottom, Math.max(layout.top, p.y)); horizontal.setAttribute('y1',yy); horizontal.setAttribute('y2',yy);horizontal.setAttribute('x1',layout.left);horizontal.setAttribute('x2',layout.right);
        var pr=panel._chanPriceRange||{low:Number(svg.dataset.priceLow),high:Number(svg.dataset.priceHigh)};
        var price = pr.high - (yy-layout.top)/(layout.bottom-layout.top)*(pr.high-pr.low);
        var label = first('text', cross), box = first('rect', cross); label.textContent = price.toFixed(2); label.setAttribute('y', yy+4); label.setAttribute('x',layout.left-5);box.setAttribute('y', yy-12);box.setAttribute('width',layout.left-4);
        var volume = numberOrNull(data.volume), readout = first('[data-chan-ohlc]', panel);
        function num(value) { return Number(value).toLocaleString(undefined, {minimumFractionDigits:2, maximumFractionDigits:2}); }
        readout.textContent = data.date.slice(0,10) + '  O ' + num(data.open) + '  H ' + num(data.high) + '  L ' + num(data.low) + '  C ' + num(data.close) + (volume === null ? '' : '  VOL ' + volume.toLocaleString());
      }
      svg.addEventListener('pointerdown', function (event) {
        if (event.button !== 0 && event.pointerType !== 'touch') return;
        stopAnimations(root);
        readAt(event);
        pointers[event.pointerId] = event.clientX;
        var range = chartRange(panel); drag = {x:event.clientX, start:range.start, end:range.end}; suppressClick=false;
        if (Object.keys(pointers).length === 2) { var values=Object.values(pointers); pinch={distance:Math.abs(values[0]-values[1]), start:range.start,end:range.end}; }
        // Capture only after a drag starts, leaving ordinary annotation clicks intact.
      });
      svg.addEventListener('pointermove', function (event) {
        if (Object.prototype.hasOwnProperty.call(pointers,event.pointerId)) {
          pointers[event.pointerId]=event.clientX;
          var values=Object.values(pointers);
          if (values.length===2 && pinch) {
            var distance=Math.abs(values[0]-values[1]);
            if (distance>5 && pinch.distance>5) { var span=(pinch.end-pinch.start)*pinch.distance/distance, mid=(pinch.start+pinch.end)/2; setRange(panel,mid-span/2,mid+span/2); suppressClick=true; }
          } else if (drag && Math.abs(event.clientX-drag.x)>4) {
            var layout=panel._chanLayout || chartLayout(panel);
            var pixels=svg.getBoundingClientRect().width*(layout.right-layout.left)/layout.width;
            var shift=(event.clientX-drag.x)/pixels*(drag.end-drag.start); setRange(panel,drag.start-shift,drag.end-shift); suppressClick=true;
          }
          if (suppressClick) { if (!svg.hasPointerCapture(event.pointerId)) svg.setPointerCapture(event.pointerId); event.preventDefault(); }
        } else readAt(event);
      });
      function endPointer(event) { delete pointers[event.pointerId]; if (!Object.keys(pointers).length) { drag=null;pinch=null; } if (svg.hasPointerCapture(event.pointerId)) svg.releasePointerCapture(event.pointerId); }
      svg.addEventListener('pointerup',endPointer); svg.addEventListener('pointercancel',endPointer);
      svg.addEventListener('pointerleave',function () { if (!drag) setHidden(first('.chan-crosshair',panel),true); });
      svg.addEventListener('click',function (event) { if (suppressClick) {event.preventDefault();event.stopImmediatePropagation();suppressClick=false;} },true);
      svg.addEventListener('keydown',function (event) {
        var action={'ArrowLeft':'left','ArrowRight':'right','+':'zoom-in','=':'zoom-in','-':'zoom-out','Home':'full','End':'recent'}[event.key];
        if(action && event.target===svg) {event.preventDefault();rangeAction(root,action);}
      });
      all('[data-pa-point]',panel).forEach(function (point) { point.addEventListener('click',function(){showPriceAction(root,point);}); point.addEventListener('keydown',function(event){if(event.key==='Enter'||event.key===' '){event.preventDefault();showPriceAction(root,point);}}); });
      all('[data-pa-select]',panel).forEach(function(button){button.addEventListener('click',function(){var target=all('[data-pa-point]',panel).find(function(p){return p.dataset.paPoint===button.dataset.paSelect;});if(!target)return;var rr=chartRange(panel),anchor=numberOrNull(target.dataset.anchorIndex),start=numberOrNull(target.dataset.startIndex); if(anchor===null)anchor=start;if(anchor!==null)setRange(panel,anchor-40,anchor+40);showPriceAction(root,target);setHidden(target,false);target.focus({preventScroll:true});});});
      var range=chartRange(panel);setRange(panel,range.start,range.end);
    });
    updateOverlays(root);
    function responsiveLayout(){
      var mobile=window.matchMedia && window.matchMedia('(max-width: 760px)').matches;
      all('[data-chan-compact-tools]',root).forEach(function(d){if(d.dataset.layoutMode!==(mobile?'mobile':'desktop')){d.open=!mobile;d.dataset.layoutMode=mobile?'mobile':'desktop';}});
      levelPanels(root).forEach(function(panel){var r=chartRange(panel);if(mobile && panel.dataset.layoutMode!=='mobile')setRange(panel,Math.max(r.start,r.end-44),r.end);else setRange(panel,r.start,r.end);panel.dataset.layoutMode=mobile?'mobile':'desktop';});
    }
    responsiveLayout();
    var resizeFrame=null;window.addEventListener('resize',function(){if(resizeFrame)cancelAnimationFrame(resizeFrame);resizeFrame=requestAnimationFrame(function(){responsiveLayout();resizeFrame=null;});});
    // Printing always restores full history; afterprint restores the reader's viewport.
    window.addEventListener('beforeprint',function(){root._chanPrinting=true;stopAnimations(root);all('details',root).forEach(function(d){d._chanPrintOpen=d.open;d.open=true;});levelPanels(root).forEach(function(panel){var r=chartRange(panel); panel._chanPrintRange={start:r.start,end:r.end};setRange(panel,r.min,r.max);});});
    window.addEventListener('afterprint',function(){root._chanPrinting=false;all('details',root).forEach(function(d){d.open=!!d._chanPrintOpen;});levelPanels(root).forEach(function(panel){var r=panel._chanPrintRange;if(r)setRange(panel,r.start,r.end);});});
  }

  function init(root) {
    if (!root || root.dataset.chanReady === 'true') return;
    root.dataset.chanReady = 'true';
    root._chanState = {};
    bindTabs(root);
    bindActions(root);
    bindPoints(root);
    bindChartInteraction(root);
    selectLevel(root, activeLevel(root), false);
    setAnnotations(root, root.dataset.annotations !== 'hidden');
    watchMotion(root);
  }

  function boot() {
    all('.chan-desk#chan-workspace').forEach(init);
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot, { once: true });
  else boot();
  window.JTraderChanDesk = window.JTraderChanDesk || { init: init };
}());

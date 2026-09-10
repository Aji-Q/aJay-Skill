/* Continuous report runtime: navigation, evidence, chat, export, and accessible model views. */
(() => {
  'use strict';

  const $ = (selector, root = document) => root.querySelector(selector);
  const $$ = (selector, root = document) => Array.from(root.querySelectorAll(selector));
  const node = (tag, text, className) => {
    const element = document.createElement(tag);
    if (text !== undefined) element.textContent = String(text);
    if (className) element.className = className;
    return element;
  };

  const root = document.documentElement;
  const dataElement = $('#council-data');
  let data = { raw: {}, analysis: {}, council: { evidence: {} } };
  try {
    if (dataElement?.textContent) data = JSON.parse(dataElement.textContent);
  } catch (_) {
    data = { raw: {}, analysis: {}, council: { evidence: {} } };
  }

  const statusLabel = (value) => ({
    available: '输入已记录 · 尚待来源核验',
    derived: '由记录计算',
    missing: '缺失 / 未评估',
    stale: '记录已过期',
    not_applicable: '不适用',
  }[value] || value || '未标注');
  const extraTitles = {
    '0_basic': '基础报价',
    '20_valuation_models': '估值模型输入',
    '21_research_workflow': '研究工作流输入',
    '22_deep_methods': '深度研究方法输入',
  };
  const safeSource = (value) => {
    try {
      const url = new URL(value);
      return ['https:','http:'].includes(url.protocol) ? url.href : null;
    } catch (_) {
      return null;
    }
  };
  const parseNumericText = (value) => {
    const text = String(value || '').trim();
    if (!text || text.length > 26 || /[年月日时]|(?:19|20)\d{2}[-/]\d/.test(text)) return null;
    let compact = text.replace(/[,$¥£€\s]/g, '')
      .replace(/(?:HKD|USD|CNY|RMB|bps)$/i, '')
      .replace(/[％%x×倍]$/i, '');
    const parenthetical = /^\(.+\)$/.test(compact);
    compact = compact.replace(/^\((.+)\)$/, '-$1');
    if (!/^[+-]?\d+(?:\.\d+)?$/.test(compact)) return null;
    const valueNumber = Number(compact);
    return Number.isFinite(valueNumber) ? { value: valueNumber, text, parenthetical } : null;
  };

  function upgradeTable(table) {
    if (!table?.parentNode || table.closest('.table-frame') || table.classList.contains('chan-point-table')) return;
    table.classList.add('ajay-data-table');
    const rows = $$('tbody tr', table);
    const columnMax = [];
    rows.forEach((row) => $$('td', row).forEach((cell, index) => {
      const parsed = parseNumericText(cell.textContent);
      if (parsed) columnMax[index] = Math.max(columnMax[index] || 0, Math.abs(parsed.value));
    }));
    rows.forEach((row) => $$('td', row).forEach((cell, index) => {
      const parsed = parseNumericText(cell.textContent);
      if (!parsed) return;
      const max = columnMax[index] || 1;
      cell.dataset.cellLevel = 'true';
      cell.style.setProperty('--cell-level', Math.max(.06, Math.min(.94, Math.abs(parsed.value) / max)).toFixed(3));
      if (parsed.value < 0 || parsed.parenthetical) cell.dataset.signal = 'negative';
      else if (/^\+/.test(parsed.text)) cell.dataset.signal = 'positive';
      else if (/[％%x×倍]$/.test(parsed.text)) cell.dataset.signal = 'emphasis';
    }));
    const frame = node('div', undefined, 'table-frame');
    table.parentNode.insertBefore(frame, table);
    frame.appendChild(table);
  }

  function upgradeTables(scope = document) {
    $$('table', scope).forEach(upgradeTable);
  }

  const displayRecordValue = (value) => {
    if (value === undefined || value === null || value === '' || value === '未记录') return null;
    if (Array.isArray(value)) return value.length ? value.join(' · ') : null;
    return String(value);
  };
  const firstRecordValue = (values) => {
    for (const value of values) {
      const displayed = displayRecordValue(value);
      if (displayed) return displayed;
    }
    return '未记录';
  };
  function dimensionPeriod(raw, evidence) {
    const factDates = Array.isArray(evidence?.facts) ? evidence.facts.map((fact) => fact?.date) : [];
    const record = raw?.data || {};
    return firstRecordValue([
      evidence?.date,
      raw?.date,
      raw?.period,
      record.period,
      record.report_date,
      record.initiating_coverage?.headline?.report_date,
      record.financial_years,
      record.dividend_years,
      ...factDates,
    ]);
  }

  const evidenceDialog = $('#evidence-dialog');
  let evidenceFocus = null;
  function openEvidence(id) {
    const evidence = data?.council?.evidence?.[id] || {};
    const raw = (data?.raw?.dimensions || {})[id];
    const content = $('#evidence-content');
    if (!evidenceDialog || !content || (!raw && !Object.keys(evidence).length)) return;
    evidenceFocus = document.activeElement;
    content.replaceChildren();
    const title = evidence.title || data?.analysis?.dimension_titles?.[id] || extraTitles[id] || id;
    const titleElement = $('#evidence-title');
    if (titleElement) titleElement.textContent = title;
    content.appendChild(node('p', `状态：${statusLabel(evidence.status || (raw ? 'available' : 'missing'))}`, 'evidence-status'));
    content.appendChild(node('p', `来源：${evidence.source || raw?.source || '未记录'} · 时期：${evidence.date || raw?.data?.period || '未记录'}`));
    content.appendChild(node('p', `采集时间：${evidence.collected_at || data?.raw?.fetched_at || '未记录'}`));
    if (evidence.summary) content.appendChild(node('p', evidence.summary));
    const source = safeSource(raw?.source_url || raw?.url || raw?.source || evidence.source);
    if (source) {
      const link = node('a', '打开原始来源 ↗');
      link.href = source;
      link.target = '_blank';
      link.rel = 'noopener noreferrer';
      content.appendChild(link);
    }
    const facts = Array.isArray(evidence.facts) ? evidence.facts : [];
    if (facts.length) {
      const table = node('table');
      const head = node('tr');
      ['指标', '记录值 / 单位', '时期'].forEach((label) => head.appendChild(node('th', label)));
      table.appendChild(head);
      facts.forEach((fact) => {
        const row = node('tr');
        [fact.label, fact.text ?? `${fact.value ?? '—'} ${fact.unit || ''}`, fact.date || '未记录']
          .forEach((value) => row.appendChild(node('td', value)));
        table.appendChild(row);
      });
      content.appendChild(table);
    }
    const details = node('details');
    details.appendChild(node('summary', '完整原始维度数据'));
    details.appendChild(node('pre', JSON.stringify(raw || { status: 'missing' }, null, 2)));
    content.appendChild(details);
    upgradeTables(content);
    if (typeof evidenceDialog.showModal === 'function') evidenceDialog.showModal();
    else evidenceDialog.setAttribute('open', '');
  }

  $$('.evidence-link').forEach((link) => {
    link.addEventListener('click', (event) => {
      event.preventDefault();
      openEvidence(link.dataset.evidence);
    });
  });
  const evidenceIndex = $('#evidence-index');
  if (evidenceIndex) {
    const dimensions = { ...(data?.analysis?.dimension_titles || {}) };
    Object.keys(data?.raw?.dimensions || {}).forEach((id) => {
      dimensions[id] ||= extraTitles[id] || id;
    });
    const evidence = data?.council?.evidence || {};
    Object.keys(evidence).forEach((id) => {
      dimensions[id] ||= extraTitles[id] || id;
    });
    Object.entries(dimensions).forEach(([id, title]) => {
      const raw = (data?.raw?.dimensions || {})[id];
      const entry = evidence[id] || {};
      const status = entry.status || raw?.status || (raw ? 'available' : 'missing');
      const sourceText = firstRecordValue([entry.source, raw?.source]);
      const period = dimensionPeriod(raw, entry);
      const collected = firstRecordValue([entry.collected_at, raw?.collected_at, data?.raw?.fetched_at]);
      const card = node('article', undefined, 'evidence-record');
      card.dataset.status = status;
      card.dataset.source = sourceText;
      card.dataset.period = period;
      card.appendChild(node('h3', title));
      card.appendChild(node('p', `状态：${statusLabel(status)}`));
      card.appendChild(node('p', `来源：${sourceText}`));
      card.appendChild(node('p', `时期：${period} · 采集：${collected}`));
      const source = safeSource(entry.source || raw?.source);
      if (source) {
        const sourceLink = node('a', '打开来源 ↗');
        sourceLink.href = source;
        sourceLink.target = '_blank';
        sourceLink.rel = 'noopener noreferrer';
        card.appendChild(sourceLink);
      }
      const button = node('button', '核对原始记录 ↗', 'tool-button');
      button.type = 'button';
      button.dataset.evidence = id;
      button.addEventListener('click', () => openEvidence(id));
      card.appendChild(button);
      evidenceIndex.appendChild(card);
    });
  }
  if (evidenceDialog) {
    evidenceDialog.addEventListener('click', (event) => {
      if (event.target === evidenceDialog) evidenceDialog.close?.();
    });
    evidenceDialog.addEventListener('close', () => {
      evidenceFocus?.focus?.({ preventScroll: true });
      evidenceFocus = null;
    });
  }

  const shareOverlay = $('#share-overlay');
  const shareButtons = Array.from(new Set($$('[data-open-share], #open-share')));
  const openShare = () => {
    if (!shareOverlay) return;
    if (typeof shareOverlay.showModal === 'function') shareOverlay.showModal();
    else shareOverlay.setAttribute('open', '');
    const canvas = $('#report-qr-canvas');
    const context = canvas?.getContext?.('2d');
    if (context) context.clearRect(0, 0, canvas.width, canvas.height);
  };
  shareButtons.forEach((button) => button.addEventListener('click', openShare));
  shareOverlay?.addEventListener('click', (event) => {
    if (event.target === shareOverlay) shareOverlay.close?.();
  });
  $('#print-report')?.addEventListener('click', () => {
    shareOverlay?.close?.();
    window.print();
  });

  const downloadButton = $('#download-inputs');
  if (downloadButton) {
    downloadButton.dataset.defaultLabel = downloadButton.textContent.trim();
    downloadButton.addEventListener('click', () => {
      if (downloadButton.dataset.busy === 'true') return;
      downloadButton.dataset.busy = 'true';
      downloadButton.setAttribute('aria-busy', 'true');
      downloadButton.textContent = '准备下载…';
      const exportInputs = () => {
        try {
          const payload = {
            report: 'J Trader continuous research',
            exported_at: new Date().toISOString(),
            raw: data?.raw || {},
            analysis: data?.analysis || {},
          };
          const blob = new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' });
          const objectUrl = URL.createObjectURL(blob);
          const anchor = node('a');
          anchor.href = objectUrl;
          anchor.download = `J-Trader-${String(data?.raw?.ticker || 'report').replace(/[^a-zA-Z0-9._-]/g, '_')}-inputs.json`;
          anchor.click();
          window.setTimeout(() => URL.revokeObjectURL(objectUrl), 1000);
          downloadButton.textContent = '已导出输入';
        } catch (_) {
          downloadButton.textContent = '导出失败，请重试';
        } finally {
          downloadButton.dataset.busy = 'false';
          downloadButton.removeAttribute('aria-busy');
          window.setTimeout(() => {
            downloadButton.textContent = downloadButton.dataset.defaultLabel || '下载输入';
          }, 1800);
        }
      };
      if (typeof window.requestAnimationFrame === 'function') window.requestAnimationFrame(exportInputs);
      else exportInputs();
    });
  }

  $('#expand-research')?.addEventListener('click', (event) => {
    $$('details.research-category').forEach((details) => { details.open = true; });
    event.currentTarget.textContent = '全部研究维度已展开';
  });
  $$('.photography-credit').forEach((credit) => {
    credit.addEventListener('click', () => credit.closest('details')?.setAttribute('open', ''));
  });

  const search = $('#perspective-search');
  const messages = $$('.chat-msg');
  const chatTabs = $$('.chat-tab[data-group]');
  let activeGroup = chatTabs.find((tab) => tab.classList.contains('active'))?.dataset.group || 'all';
  const availableGroups = new Set(messages.map((message) => message.dataset.group).filter(Boolean));
  chatTabs.forEach((tab) => {
    if (tab.dataset.group !== 'all' && !availableGroups.has(tab.dataset.group)) tab.hidden = true;
  });
  function applyNoteFilter() {
    const query = (search?.value || '').trim().toLowerCase();
    const visible = messages.filter((message) => {
      const groupMatch = activeGroup === 'all' || message.dataset.group === activeGroup;
      const textMatch = !query || message.textContent.toLowerCase().includes(query);
      message.hidden = !(groupMatch && textMatch);
      return groupMatch && textMatch;
    });
    chatTabs.forEach((tab) => {
      const selected = tab.dataset.group === activeGroup;
      tab.classList.toggle('active', selected);
      tab.setAttribute('aria-pressed', selected ? 'true' : 'false');
    });
    const count = $('#perspective-count');
    if (count) count.textContent = `显示 ${visible.length} / ${messages.length} 条方法记录 · 非真实投资者意见`;
  }
  chatTabs.forEach((tab) => {
    tab.addEventListener('click', () => {
      activeGroup = tab.dataset.group || 'all';
      applyNoteFilter();
    });
  });
  search?.addEventListener('input', applyNoteFilter);

  const motionQuery = typeof window.matchMedia === 'function'
    ? window.matchMedia('(prefers-reduced-motion: reduce)')
    : null;
  const motionPreferenceKey = 'ajay-motion';
  let userMotionOff = false;
  try {
    userMotionOff = window.localStorage.getItem(motionPreferenceKey) === 'off';
  } catch (_) {
    userMotionOff = false;
  }
  const motion = {
    systemReduced: Boolean(motionQuery?.matches),
    userOff: userMotionOff,
  };
  const motionToggle = $('#motion-toggle');
  const motionHandles = new Set();
  const motionObservers = new Set();
  let motionFrame = null;
  let editorialObserver = null;
  let arrivalPlayed = false;
  let editorialPrepared = false;
  const editorialPlayed = new WeakSet();
  const motionIsOff = () => motion.systemReduced || motion.userOff;

  function syncMotionUI() {
    const off = motionIsOff();
    root.setAttribute('data-motion', off ? 'off' : 'on');
    if (!motionToggle) return;
    motionToggle.setAttribute('aria-pressed', off ? 'true' : 'false');
    motionToggle.setAttribute('aria-label', off ? '启用页面动态' : '停用页面动态');
    motionToggle.textContent = off ? '启用动态' : '停用动态';
    if (motion.systemReduced) motionToggle.dataset.systemReduced = 'true';
    else delete motionToggle.dataset.systemReduced;
  }

  function trackMotion(handle) {
    if (handle && typeof handle.kill === 'function') motionHandles.add(handle);
    return handle;
  }

  function clearMotionArtifacts() {
    motionHandles.forEach((handle) => {
      try { handle.kill(); } catch (_) { /* ignore an already-finished tween */ }
    });
    motionHandles.clear();
    if (motionFrame !== null && typeof window.cancelAnimationFrame === 'function') {
      window.cancelAnimationFrame(motionFrame);
      motionFrame = null;
    }
    motionObservers.forEach((observer) => observer.disconnect?.());
    motionObservers.clear();
    editorialObserver = null;
    editorialPrepared = false;
    if (window.gsap) {
      const targets = $$('.arrival-copy .eyebrow, .arrival-copy h1, .arrival-copy .dek, .chapter-heading, .voice-photo');
      if (targets.length) window.gsap.set(targets, { clearProps: 'transform,opacity' });
    }
    $$('.arrival, .shanghai-tower, .model-opening, .market-opening').forEach((scene) => {
      scene.style.setProperty('--scene-progress', '0');
    });
  }

  function stopMotion() {
    clearMotionArtifacts();
    updateScroll();
  }

  function prepareDataMotion() {
    upgradeTables();
    // Never gate prose on an animation-ready class: the report is readable before any script runs.
    $$('.data-reveal').forEach((target) => {
      target.classList.remove('data-reveal');
      target.classList.add('is-data-revealed');
      target.style.removeProperty('transition-delay');
    });
  }

  function prepareChartMotion() {
    // Charts stay fully readable; no generic SVG drawing animation is installed here.
  }

  function preparePointerDepth() {
    // Pointer spotlight/depth effects are deliberately absent from the continuous report.
  }

  function prepareEditorialMotion() {
    if (motionIsOff() || editorialPrepared || !window.gsap || typeof window.IntersectionObserver !== 'function') return;
    const headings = $$('.chapter-heading, .voice-photo').filter((target) => !editorialPlayed.has(target));
    if (!headings.length) return;
    editorialPrepared = true;
    editorialObserver = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting || motionIsOff()) return;
        editorialPlayed.add(entry.target);
        const tween = window.gsap.from(entry.target, {
          y: entry.target.classList.contains('voice-photo') ? 10 : 14,
          duration: entry.target.classList.contains('voice-photo') ? 0.38 : 0.58,
          ease: 'power2.out',
          clearProps: 'transform',
        });
        trackMotion(tween);
        editorialObserver?.unobserve(entry.target);
      });
    }, { rootMargin: '0px 0px -12% 0px', threshold: 0.08 });
    motionObservers.add(editorialObserver);
    headings.forEach((heading) => editorialObserver.observe(heading));
  }

  function playArrivalSequence() {
    if (motionIsOff() || arrivalPlayed || !window.gsap) return;
    const targets = $$('.arrival-copy .eyebrow, .arrival-copy h1, .arrival-copy .dek');
    if (!targets.length) return;
    arrivalPlayed = true;
    const tween = window.gsap.from(targets, {
      y: 18,
      duration: 0.72,
      stagger: 0.05,
      ease: 'power3.out',
      clearProps: 'transform',
    });
    trackMotion(tween);
  }

  function applyMotionState() {
    syncMotionUI();
    if (motionIsOff()) {
      stopMotion();
      return;
    }
    prepareEditorialMotion();
    playArrivalSequence();
  }
  motionToggle?.addEventListener('click', () => {
    motion.userOff = !motion.userOff;
    try {
      window.localStorage.setItem(motionPreferenceKey, motion.userOff ? 'off' : 'on');
    } catch (_) { /* storage is optional for an offline report */ }
    applyMotionState();
  });
  if (motionQuery) {
    const onMotionPreferenceChange = (event) => {
      motion.systemReduced = Boolean(event.matches);
      applyMotionState();
    };
    if (typeof motionQuery.addEventListener === 'function') motionQuery.addEventListener('change', onMotionPreferenceChange);
    else motionQuery.addListener?.(onMotionPreferenceChange);
  }

  const themeToggle = $('#theme-toggle');
  const themeStorageKey = 'ajay-theme';
  let theme = root.dataset.theme || 'dark';
  try {
    const storedTheme = window.localStorage.getItem(themeStorageKey);
    if (storedTheme === 'dark' || storedTheme === 'light') theme = storedTheme;
  } catch (_) { /* localStorage is optional */ }
  function syncTheme() {
    root.dataset.theme = theme;
    if (!themeToggle) return;
    const dark = theme === 'dark';
    themeToggle.textContent = dark ? '浅' : '深';
    themeToggle.setAttribute('aria-label', dark ? '切换到浅色主题' : '切换到深色主题');
    themeToggle.setAttribute('aria-pressed', dark ? 'true' : 'false');
  }
  syncTheme();
  themeToggle?.addEventListener('click', () => {
    theme = theme === 'dark' ? 'light' : 'dark';
    try { window.localStorage.setItem(themeStorageKey, theme); } catch (_) { /* optional */ }
    syncTheme();
  });

  const actionLabels = {
    '#scroll-bull': '跳至看多席位',
    '#scroll-bear': '跳至看空席位',
    '#expand-research': '展开全部研究维度',
    '#download-inputs': '下载输入数据',
    '#print-report': '打印报告',
  };
  Object.entries(actionLabels).forEach(([selector, label]) => {
    const button = $(selector);
    if (button) button.setAttribute('aria-label', label);
  });

  function scrollToElement(target, extraOffset = 0) {
    if (!target) return;
    const nav = $('.chapter-nav');
    const offset = Math.max(72, (nav?.getBoundingClientRect().height || 0) + 16) + extraOffset;
    const currentY = window.scrollY || window.pageYOffset || 0;
    const top = Math.max(0, target.getBoundingClientRect().top + currentY - offset);
    window.scrollTo({ top, behavior: motionIsOff() ? 'auto' : 'smooth' });
  }

  function flashMessage(targetId) {
    const target = document.getElementById(targetId);
    if (!target) return;
    activeGroup = 'all';
    if (search) search.value = '';
    applyNoteFilter();
    target.querySelectorAll('details').forEach((details) => { details.open = true; });
    $$('.chat-messages').forEach((container) => {
      const targetTop = target.getBoundingClientRect().top - container.getBoundingClientRect().top + container.scrollTop;
      container.scrollTop = Math.max(0, targetTop - 18);
    });
    const section = $('#section-chat') || target.closest('section');
    scrollToElement(section || target);
    target.classList.remove('flash-highlight');
    void target.offsetWidth;
    target.classList.add('flash-highlight');
    window.clearTimeout(flashMessage.timer);
    if (motionIsOff()) target.classList.remove('flash-highlight');
    else flashMessage.timer = window.setTimeout(() => target.classList.remove('flash-highlight'), 1700);
  }

  $$('.seat[data-target]').forEach((seat) => {
    seat.setAttribute('role', 'button');
    if (!seat.hasAttribute('tabindex')) seat.setAttribute('tabindex', '0');
    seat.addEventListener('click', () => flashMessage(seat.dataset.target));
    seat.addEventListener('keydown', (event) => {
      if (event.key !== 'Enter' && event.key !== ' ') return;
      event.preventDefault();
      flashMessage(seat.dataset.target);
    });
  });
  $('#scroll-bull')?.addEventListener('click', () => {
    const target = $('.chat-msg.bullish');
    if (target?.id) flashMessage(target.id);
  });
  $('#scroll-bear')?.addEventListener('click', () => {
    const target = $('.chat-msg.bearish');
    if (target?.id) flashMessage(target.id);
  });
  $('#expand-all')?.addEventListener('click', () => {
    $$('.chat-msg details').forEach((details) => { details.open = true; });
  });
  $('#collapse-all')?.addEventListener('click', () => {
    $$('.chat-msg details').forEach((details) => { details.open = false; });
  });

  function initModelViewSwitchers() {
    const allowedViews = ['chart', 'table', 'source'];
    $$('.valuation-stage[data-viz-switcher]').forEach((stage, stageIndex) => {
      const buttons = $$('[data-model-view]', stage).filter((button) => allowedViews.includes(button.dataset.modelView));
      const panels = $$('[data-model-panel]', stage).filter((panel) => allowedViews.includes(panel.dataset.modelPanel));
      if (!buttons.length || !panels.length) return;
      const stageId = stage.id || `valuation-stage-${stageIndex + 1}`;
      if (!stage.id) stage.id = stageId;
      const panelByView = new Map();
      panels.forEach((panel, panelIndex) => {
        const view = panel.dataset.modelPanel;
        if (!panelByView.has(view)) panelByView.set(view, panel);
        if (!panel.id) panel.id = `${stageId}-panel-${view}-${panelIndex + 1}`;
        panel.setAttribute('role', 'tabpanel');
        panel.setAttribute('aria-hidden', 'true');
      });
      const buttonByView = new Map();
      buttons.forEach((button, buttonIndex) => {
        const view = button.dataset.modelView;
        if (!buttonByView.has(view)) buttonByView.set(view, button);
        const panel = panelByView.get(view);
        if (!button.id) button.id = `${stageId}-tab-${view}-${buttonIndex + 1}`;
        button.setAttribute('role', 'tab');
        button.setAttribute('type', 'button');
        button.setAttribute('tabindex', '-1');
        if (panel) {
          button.setAttribute('aria-controls', panel.id);
          panel.setAttribute('aria-labelledby', button.id);
        }
      });
      const views = buttons.map((button) => button.dataset.modelView).filter((view, index, list) => list.indexOf(view) === index && panelByView.has(view));
      if (!views.length) return;
      const initialView = views.includes('chart') ? 'chart' : views[0];
      const activate = (view, focus = false) => {
        const button = buttonByView.get(view);
        const panel = panelByView.get(view);
        if (!button || !panel) return;
        stage.dataset.activeView = view;
        buttons.forEach((candidate) => {
          const selected = candidate === button;
          candidate.classList.toggle('active', selected);
          candidate.setAttribute('aria-selected', selected ? 'true' : 'false');
          candidate.setAttribute('tabindex', selected ? '0' : '-1');
        });
        panels.forEach((candidate) => {
          const selected = candidate === panel;
          candidate.hidden = !selected;
          candidate.setAttribute('aria-hidden', selected ? 'false' : 'true');
        });
        if (focus) button.focus();
      };
      buttons.forEach((button) => {
        button.addEventListener('click', () => activate(button.dataset.modelView));
        button.addEventListener('keydown', (event) => {
          const currentIndex = views.indexOf(button.dataset.modelView);
          if (currentIndex < 0) return;
          let nextIndex = currentIndex;
          if (event.key === 'ArrowRight' || event.key === 'ArrowDown') nextIndex = (currentIndex + 1) % views.length;
          else if (event.key === 'ArrowLeft' || event.key === 'ArrowUp') nextIndex = (currentIndex - 1 + views.length) % views.length;
          else if (event.key === 'Home') nextIndex = 0;
          else if (event.key === 'End') nextIndex = views.length - 1;
          else return;
          event.preventDefault();
          activate(views[nextIndex], true);
        });
      });
      activate(initialView);
    });
  }

  const chapterLinks = $$('a[href^="#"]', $('.chapter-nav') || document);
  const chapterTargets = chapterLinks.map((link) => document.getElementById(link.getAttribute('href').slice(1))).filter(Boolean);
  const modelLinks = $$('.model-directory a[href^="#"]');
  const modelTargets = modelLinks.map((link) => document.getElementById(link.getAttribute('href').slice(1))).filter(Boolean);
  const chapterPosition = $('#chapter-position');
  const chapterTitle = $('#chapter-title');
  const scenes = $$('.arrival, .shanghai-tower, .model-opening, .market-opening');
  let scrollFrame = null;
  let activeModelTarget = null;
  const progress = $('.reading-progress');
  const qualityLevels = $$('[data-quality-step]');
  const towerMarkers = $$('[data-research-marker]');
  const tower = $('.shanghai-tower');
  let activeQuality = null;
  root.setAttribute('data-tower-ready', 'true');

  function updateQualityScene() {
    if (!qualityLevels.length || !tower) return;
    const readingLine = window.innerHeight * 0.42;
    let current = qualityLevels[0];
    qualityLevels.forEach((level) => {
      if (level.getBoundingClientRect().top <= readingLine) current = level;
    });
    // The mobile photograph precedes the prose. Follow its local landmarks there,
    // not the full-document scroll ratio, then resume text-linked navigation.
    const photoRect = tower.getBoundingClientRect();
    if (window.innerWidth <= 760 && photoRect.top < readingLine && photoRect.bottom > readingLine) {
      towerMarkers.forEach((marker, i) => {
        if (marker.getBoundingClientRect().top <= readingLine) current = qualityLevels[i];
      });
    }
    if (current === activeQuality) return;
    activeQuality = current;
    qualityLevels.forEach((level) => {
      const selected = level === current;
      level.classList.toggle('is-current', selected);
      const status = $('.speaker-status', level);
      if (status) status.textContent = selected ? '当前讲解者' : '方法讲解';
    });
    towerMarkers.forEach((marker) => {
      const selected = marker.dataset.researchMarker === current.id;
      marker.classList.toggle('is-current', selected);
      const link = $('.tower-anchor', marker);
      if (selected) link?.setAttribute('aria-current', 'step');
      else link?.removeAttribute('aria-current');
    });
  }

  $$('[data-research-target]').forEach((link) => {
    link.addEventListener('click', (event) => {
      const target = document.getElementById(link.dataset.researchTarget);
      if (!target) return;
      event.preventDefault();
      scrollToElement(target);
      target.setAttribute('tabindex', '-1');
      target.focus({ preventScroll: true });
      history.replaceState?.(null, '', `#${target.id}`);
    });
  });

  function setCurrentLink(links, current) {
    links.forEach((link) => {
      const selected = link.getAttribute('href') === `#${current?.id || ''}`;
      if (selected) link.setAttribute('aria-current', 'location');
      else link.removeAttribute('aria-current');
      link.classList.toggle('is-current', selected);
    });
  }

  function updateScroll() {
    scrollFrame = null;
    updateQualityScene();
    const currentY = window.scrollY || window.pageYOffset || 0;
    let chapterIndex = 0;
    chapterTargets.forEach((target, index) => {
      if (target.getBoundingClientRect().top + currentY <= currentY + 160) chapterIndex = index;
    });
    const currentChapter = chapterTargets[chapterIndex];
    setCurrentLink(chapterLinks, currentChapter);
    if (chapterPosition) chapterPosition.textContent = `${String(chapterIndex + 1).padStart(2, '0')} / ${String(Math.max(1, chapterTargets.length)).padStart(2, '0')}`;
    const currentChapterLink = chapterLinks.find((link) => link.getAttribute('href') === `#${currentChapter?.id || ''}`);
    if (chapterTitle && currentChapter) chapterTitle.textContent = currentChapterLink?.textContent.replace(/^\s*\d+\s*/, '').trim() || currentChapter.dataset.chapterTitle || currentChapter.id;

    let modelIndex = 0;
    const modelThreshold = Math.min(210, window.innerHeight * 0.34);
    modelTargets.forEach((target, index) => {
      if (target.getBoundingClientRect().top <= modelThreshold) modelIndex = index;
    });
    const currentModel = modelTargets[modelIndex];
    if (currentModel !== activeModelTarget) {
      activeModelTarget = currentModel;
      setCurrentLink(modelLinks, currentModel);
    }
    const scrollable = Math.max(1, document.documentElement.scrollHeight - window.innerHeight);
    const ratio = Math.min(1, Math.max(0, currentY / scrollable));
    progress?.style.setProperty('transform', `scaleX(${ratio})`);
    scenes.forEach((scene) => {
      scene.style.setProperty('--scene-progress', motionIsOff() ? '0' : ratio.toFixed(4));
    });
  }

  function requestScrollUpdate() {
    if (scrollFrame !== null) return;
    if (typeof window.requestAnimationFrame === 'function') scrollFrame = window.requestAnimationFrame(updateScroll);
    else updateScroll();
  }
  window.addEventListener('scroll', requestScrollUpdate, { passive: true });
  window.addEventListener('resize', requestScrollUpdate, { passive: true });
  chapterLinks.forEach((link) => {
    link.addEventListener('click', (event) => {
      if (event.button !== undefined && event.button !== 0) return;
      const target = document.getElementById(link.getAttribute('href').slice(1));
      if (!target) return;
      event.preventDefault();
      scrollToElement(target);
      history.replaceState?.(null, '', link.getAttribute('href'));
    });
  });
  modelLinks.forEach((link) => {
    link.addEventListener('click', (event) => {
      const target = document.getElementById(link.getAttribute('href').slice(1));
      if (!target) return;
      event.preventDefault();
      activeModelTarget = target;
      setCurrentLink(modelLinks, target);
      const modelDirectory = $('.model-directory');
      const modelRailOffset = (modelDirectory?.getBoundingClientRect().height || 0) + 12;
      scrollToElement(target, modelRailOffset);
      history.replaceState?.(null, '', link.getAttribute('href'));
    });
  });

  let printDetailsState = null;
  let printChatState = null;
  window.addEventListener('beforeprint', () => {
    printDetailsState = $$('details').map((details) => [details, details.open]);
    printChatState = messages.map((message) => [message, message.hidden]);
    $$('details').forEach((details) => { details.open = true; });
    messages.forEach((message) => { message.hidden = false; });
  });
  window.addEventListener('afterprint', () => {
    printDetailsState?.forEach(([details, open]) => { details.open = open; });
    printChatState?.forEach(([message, hidden]) => { message.hidden = hidden; });
    printDetailsState = null;
    printChatState = null;
  });

  // Resolve a shared deep link after embedded fonts/layout settle, without
  // taking the viewport away from a reader who has already interacted.
  const initialHash = window.location.hash;
  let initialNavigationInterrupted = false;
  ['pointerdown', 'wheel', 'touchstart', 'keydown'].forEach((event) => {
    window.addEventListener(event, () => { initialNavigationInterrupted = true; }, { once: true, passive: true });
  });
  const alignInitialAnchor = () => {
    const ready = document.fonts?.ready || Promise.resolve();
    ready.then(() => requestAnimationFrame(() => {
      if (!initialHash || initialNavigationInterrupted || window.location.hash !== initialHash) return;
      let id;
      try { id = decodeURIComponent(initialHash.slice(1)); } catch (_) { return; }
      const target = document.getElementById(id);
      if (!target) return;
      const headerHeight = $('.research-masthead')?.getBoundingClientRect().height || 70;
      window.scrollTo({ top: Math.max(0, target.getBoundingClientRect().top + window.scrollY - headerHeight - 24), behavior: 'instant' });
    }));
  };
  if (document.readyState === 'complete') alignInitialAnchor();
  else window.addEventListener('load', alignInitialAnchor, { once: true });

  prepareDataMotion();
  initModelViewSwitchers();
  applyNoteFilter();
  syncMotionUI();
  prepareChartMotion();
  preparePointerDepth();
  applyMotionState();
  updateScroll();
})();

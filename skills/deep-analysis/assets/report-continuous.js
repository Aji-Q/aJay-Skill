/* Functional navigation, evidence depth and reporting tools. No scene switching. */
(() => {
  'use strict';
  const data=JSON.parse(document.getElementById('council-data').textContent);
  const reduced=matchMedia('(prefers-reduced-motion: reduce)').matches;
  const $=(s,root=document)=>root.querySelector(s);
  const $$=(s,root=document)=>Array.from(root.querySelectorAll(s));
  const node=(tag,text,className)=>{const el=document.createElement(tag);if(text!==undefined)el.textContent=String(text);if(className)el.className=className;return el;};
  const dialog=$('#evidence-dialog');let evidenceFocus=null;
  const statusLabel=value=>({available:'输入已记录 · 尚待来源核验',derived:'由记录计算',missing:'缺失 / 未评估',stale:'记录已过期',not_applicable:'不适用'}[value]||value);
  const extraTitles={'0_basic':'基础报价','20_valuation_models':'估值模型输入','21_research_workflow':'研究工作流输入','22_deep_methods':'深度研究方法输入'};
  const safeSource=(value)=>{try{const u=new URL(value);return ['https:','http:'].includes(u.protocol)?u.href:null;}catch(_){return null;}};
  const parseNumericText=(value)=>{
    const text=String(value||'').trim();if(!text||text.length>26||/[年月日时]|(?:19|20)\d{2}[-/]\d/.test(text))return null;
    let compact=text.replace(/[,$¥£€\s]/g,'').replace(/(?:HKD|USD|CNY|RMB|bps)$/i,'').replace(/[％%x×倍]$/i,'');
    const parenthetical=/^\(.+\)$/.test(compact);compact=compact.replace(/^\((.+)\)$/,'-$1');
    if(!/^[+-]?\d+(?:\.\d+)?$/.test(compact))return null;
    const valueNumber=Number(compact);return Number.isFinite(valueNumber)?{value:valueNumber,text,parenthetical}:null;
  };
  function upgradeTable(table){
    if(!table?.parentNode||table.closest('.table-frame'))return;
    table.classList.add('ajay-data-table');const rows=$$('tbody tr',table);const columnMax=[];
    rows.forEach(row=>$$('td',row).forEach((cell,index)=>{const parsed=parseNumericText(cell.textContent);if(parsed)columnMax[index]=Math.max(columnMax[index]||0,Math.abs(parsed.value));}));
    rows.forEach(row=>$$('td',row).forEach((cell,index)=>{const parsed=parseNumericText(cell.textContent);if(!parsed)return;const max=columnMax[index]||1;cell.dataset.cellLevel='true';cell.style.setProperty('--cell-level',Math.max(.06,Math.min(.94,Math.abs(parsed.value)/max)).toFixed(3));if(parsed.value<0||parsed.parenthetical)cell.dataset.signal='negative';else if(/^\+/.test(parsed.text))cell.dataset.signal='positive';else if(/[％%x×倍]$/.test(parsed.text))cell.dataset.signal='emphasis';}));
    const frame=node('div',undefined,'table-frame');table.before(frame);frame.append(table);
  }
  const upgradeTables=(root=document)=>$$('table',root).forEach(upgradeTable);
  function openEvidence(id){
    const e=data.council.evidence[id];const raw=(data.raw.dimensions||{})[id];
    evidenceFocus=document.activeElement;$('#evidence-title').textContent=e?.title||data.analysis.dimension_titles?.[id]||extraTitles[id]||id;
    const body=$('#evidence-content');body.replaceChildren();
    body.append(node('p',`状态：${statusLabel(e?.status||raw?.status)||(raw?'已记录输入，需核验':'缺失 / 未评估')}`));
    body.append(node('p',`来源：${e?.source||raw?.source||'未记录'} · 时期：${e?.date||raw?.data?.period||'未记录'}`));
    body.append(node('p',`采集时间：${e?.collected_at||data.raw.fetched_at||'未记录'}`));
    const source=safeSource(raw?.source_url||raw?.url||raw?.source);if(source){const a=node('a','打开原始来源 ↗');a.href=source;a.target='_blank';a.rel='noopener noreferrer';body.append(a);}
    if(e?.facts?.length){const table=node('table');const head=node('tr');['指标','记录值 / 单位','时期'].forEach(t=>head.append(node('th',t)));table.append(head);e.facts.forEach(f=>{const row=node('tr');[f.label,f.text??`${f.value??'—'} ${f.unit||''}`,f.date||'未记录'].forEach(t=>row.append(node('td',t)));table.append(row);});body.append(table);}
    const details=node('details');details.append(node('summary','完整原始维度数据'));details.append(node('pre',JSON.stringify(raw||{status:'missing'},null,2)));body.append(details);upgradeTables(body);
    dialog.showModal();
  }
  $$('.evidence-link').forEach(b=>b.addEventListener('click',()=>openEvidence(b.dataset.evidence)));
  const dims={...data.analysis.dimension_titles};Object.keys(data.raw.dimensions||{}).forEach(id=>{dims[id] ||= extraTitles[id]||id;});
  Object.entries(dims).forEach(([id,title])=>{const raw=(data.raw.dimensions||{})[id],e=data.council.evidence[id];const card=node('article',undefined,'evidence-record');card.append(node('h3',title));card.append(node('p',`${statusLabel(e?.status)||(raw?'输入已记录':'缺失 / 未评估')} · ${e?.source||raw?.source||'未记录来源'}`));const b=node('button','核对原始记录 ↗','tool-button');b.type='button';b.addEventListener('click',()=>openEvidence(id));card.append(b);$('#evidence-index').append(card);});
  dialog.addEventListener('close',()=>evidenceFocus?.focus({preventScroll:true}));dialog.addEventListener('click',e=>{if(e.target===dialog)dialog.close();});
  $$('[data-open-share]').forEach(b=>b.addEventListener('click',()=>$('#share-overlay')?.showModal()));
  const downloadButton=$('#download-inputs');
  downloadButton.addEventListener('click',()=>{
    downloadButton.classList.add('is-busy');downloadButton.setAttribute('aria-busy','true');downloadButton.textContent='正在准备研究输入';
    requestAnimationFrame(()=>{const blob=new Blob([JSON.stringify({report:'aJay continuous research',raw:data.raw,analysis:data.analysis},null,2)],{type:'application/json'});const url=URL.createObjectURL(blob);const a=node('a');a.href=url;a.download=`aJay-${String(data.raw.ticker||'report').replace(/[^a-zA-Z0-9._-]/g,'_')}-inputs.json`;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);downloadButton.classList.remove('is-busy');downloadButton.removeAttribute('aria-busy');downloadButton.textContent='研究输入已生成';setTimeout(()=>downloadButton.textContent='下载研究输入',1800);});
  });
  $('#expand-research').addEventListener('click',()=>{$$('details.research-category').forEach(d=>d.open=true);$('#expand-research').textContent='全部研究维度已展开';});
  const search=$('#perspective-search'),messages=$$('.chat-msg');
  const availableGroups=new Set(messages.map(message=>message.dataset.group).filter(Boolean));$$('.chat-tab[data-group]').forEach(tab=>{if(tab.dataset.group!=='all'&&!availableGroups.has(tab.dataset.group))tab.hidden=true;});
  function applyNoteFilter(){const group=$('.chat-tab.active')?.dataset.group||'all',q=search.value.trim().toLocaleLowerCase();let count=0;messages.forEach(m=>{const show=(group==='all'||group===m.dataset.group)&&(!q||m.textContent.toLocaleLowerCase().includes(q));m.hidden=!show;m.style.display=show?'':'none';if(show)count++;});$('#perspective-count').textContent=`显示 ${count} / ${messages.length} 条方法记录 · 非真实投资者意见`;}
  search.addEventListener('input',applyNoteFilter);$$('.chat-tab').forEach(t=>t.addEventListener('click',applyNoteFilter));
  // Legacy jump handlers run first; clear the independent search layer as well.
  $$('.seat,#scroll-bull,#scroll-bear').forEach(b=>b.addEventListener('click',()=>{search.value='';applyNoteFilter();}));applyNoteFilter();
  const links=$$('.chapter-nav a'),chapters=links.map(a=>document.querySelector(a.getAttribute('href'))).filter(Boolean);
  const modelLinks=$$('.model-directory a'),modelTargets=modelLinks.map(a=>document.querySelector(a.getAttribute('href'))).filter(Boolean);
  const chapterPosition=$('#chapter-position'),chapterTitle=$('#chapter-title');
  const scenes=$$('.arrival,.shanghai-tower,.model-opening,.market-opening');
  let frame=0;const progress=$('.reading-progress');
  function updateScroll(){frame=0;const y=scrollY+160;let current=chapters[0];chapters.forEach(c=>{if(c.getBoundingClientRect().top+scrollY<=y)current=c;});links.forEach((a,index)=>{if(a.hash==='#'+current?.id){a.setAttribute('aria-current','location');if(chapterPosition)chapterPosition.textContent=`${String(index+1).padStart(2,'0')} / ${String(links.length).padStart(2,'0')}`;if(chapterTitle)chapterTitle.textContent=a.textContent.replace(/^\s*\d+\s*/,'').trim();}else a.removeAttribute('aria-current');});let activeModel=modelTargets[0];modelTargets.forEach(target=>{if(target.getBoundingClientRect().top<=Math.min(190,innerHeight*.3))activeModel=target;});modelLinks.forEach(a=>{if(a.hash==='#'+activeModel?.id)a.setAttribute('aria-current','location');else a.removeAttribute('aria-current');});const max=document.documentElement.scrollHeight-innerHeight;progress.style.transform=`scaleX(${max>0?Math.min(1,scrollY/max):0})`;if(!reduced)scenes.forEach(scene=>{const rect=scene.getBoundingClientRect(),value=Math.max(0,Math.min(1,(innerHeight-rect.top)/(innerHeight+rect.height)));scene.style.setProperty('--scene-progress',value.toFixed(4));});}
  addEventListener('scroll',()=>{if(!frame)frame=requestAnimationFrame(updateScroll);},{passive:true});addEventListener('resize',updateScroll);updateScroll();
  // Reveal editorial hierarchy first. Values stay final; only their visual marks are drawn in.
  if(!reduced&&window.gsap&&'IntersectionObserver' in window){const observer=new IntersectionObserver(entries=>entries.forEach(e=>{if(e.isIntersecting){gsap.fromTo(e.target,{y:14,opacity:.65},{y:0,opacity:1,duration:.7,ease:'power2.out',clearProps:'all'});observer.unobserve(e.target);}}),{threshold:.2});$$('.chapter-heading').forEach(el=>observer.observe(el));}
  if(!reduced&&'IntersectionObserver' in window){document.documentElement.classList.add('motion-ready');const voices=new IntersectionObserver(entries=>entries.forEach(entry=>{if(entry.isIntersecting){entry.target.classList.add('is-revealed');voices.unobserve(entry.target);}}),{rootMargin:'0px 0px -12% 0px',threshold:.08});$$('.method-voice').forEach(voice=>voices.observe(voice));}
  function prepareDataMotion(){
    upgradeTables();
    const revealTargets=$$('.dim-card,.stat-tile,.evidence-record,.model-supplement article,.table-frame');
    revealTargets.forEach((target,index)=>{target.classList.add('data-reveal');target.style.transitionDelay=`${Math.min(index%4,3)*55}ms`;});
    if(reduced||!('IntersectionObserver' in window)){revealTargets.forEach(target=>target.classList.add('is-data-revealed'));return;}
    document.documentElement.classList.add('motion-ready');const revealObserver=new IntersectionObserver(entries=>entries.forEach(entry=>{if(entry.isIntersecting){entry.target.classList.add('is-data-revealed');revealObserver.unobserve(entry.target);}}),{rootMargin:'0px 0px -7% 0px',threshold:.055});revealTargets.forEach(target=>revealObserver.observe(target));
  }
  function prepareChartMotion(){
    if(reduced||!window.gsap||!('IntersectionObserver' in window))return;
    const charts=$$('main svg').filter(svg=>svg.querySelector('path[stroke],polyline[stroke],rect'));
    const chartObserver=new IntersectionObserver(entries=>entries.forEach(entry=>{if(!entry.isIntersecting)return;const svg=entry.target;const lines=$$('path[stroke],polyline[stroke]',svg).filter(mark=>!mark.classList.contains('chart-grid')&&!/^(none|transparent)$/i.test(mark.getAttribute('stroke')||'')&&typeof mark.getTotalLength==='function');const bars=$$('rect',svg).filter(mark=>{const siblings=mark.parentElement?$$('rect',mark.parentElement):[];return siblings.length>=3&&Number(mark.getAttribute('height')||0)>3&&!/^(none|transparent)$/i.test(mark.getAttribute('fill')||'');});lines.forEach(mark=>{try{const length=mark.getTotalLength();if(length<8)return;mark.classList.add('chart-motion-target');gsap.set(mark,{strokeDasharray:length,strokeDashoffset:length});gsap.to(mark,{strokeDashoffset:0,duration:.9,ease:'power2.out',clearProps:'strokeDasharray,strokeDashoffset',delay:.05});}catch(_){}});if(bars.length){bars.forEach(mark=>mark.classList.add('chart-motion-target'));gsap.fromTo(bars,{scaleY:.06,opacity:.28},{scaleY:1,opacity:1,duration:.62,stagger:.025,ease:'power2.out',clearProps:'transform,opacity'});}chartObserver.unobserve(svg);}),{rootMargin:'0px 0px -8% 0px',threshold:.08});charts.forEach(svg=>chartObserver.observe(svg));
  }
  function preparePointerDepth(){
    if(reduced||!matchMedia('(pointer:fine)').matches)return;
    $$('.dim-card,.hero-chart,.evidence-record,.stat-tile,.model-supplement article,.table-frame').forEach(surface=>{surface.classList.add('interactive-surface');surface.addEventListener('pointermove',event=>{const rect=surface.getBoundingClientRect();surface.style.setProperty('--spot-x',`${event.clientX-rect.left}px`);surface.style.setProperty('--spot-y',`${event.clientY-rect.top}px`);},{passive:true});});
  }
  function playArrivalSequence(){
    if(reduced||!window.gsap)return;const targets=$$('.arrival-copy>.eyebrow,.arrival .stock-name,.arrival .stock-code,.arrival .one-liner,.arrival-findings,.arrival .hero-actions,.arrival-routes a');if(!targets.length)return;gsap.fromTo(targets,{y:20,opacity:0},{y:0,opacity:1,duration:.74,stagger:.055,ease:'power3.out',clearProps:'transform,opacity'});
  }
  prepareDataMotion();prepareChartMotion();preparePointerDepth();playArrivalSequence();
  const theme=$('#theme-toggle');function themeLabel(){theme.textContent=document.documentElement.dataset.theme==='dark'?'浅':'深';}theme.addEventListener('click',themeLabel);themeLabel();

  const actionLabels=new Map([['expand-all','展开全部结论'],['collapse-all','收起全部结论'],['scroll-bull','定位最强看多'],['scroll-bear','定位最强看空']]);
  function normalizeActionLabels(){actionLabels.forEach((label,id)=>{const button=$('#'+id);if(button)button.textContent=label;});}
  actionLabels.forEach((_,id)=>$('#'+id)?.addEventListener('click',normalizeActionLabels));normalizeActionLabels();
  // Keep anchored source/closed records reachable; links are still ordinary document navigation.
  $$('a[href="#photography-credits"]').forEach(a=>a.addEventListener('click',()=>$('#photography-credits').open=true));
  let printState=[];addEventListener('beforeprint',()=>{printState=$$('details').map(d=>[d,d.open]);printState.forEach(([d])=>d.open=true);});addEventListener('afterprint',()=>{printState.forEach(([d,open])=>d.open=open);printState=[];});
})();

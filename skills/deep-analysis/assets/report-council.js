(() => {
  'use strict';
  const data = JSON.parse(document.getElementById('council-data').textContent);
  const $ = id => document.getElementById(id);
  const prefersReduced = matchMedia('(prefers-reduced-motion: reduce)');
  const motion = () => window.gsap && !prefersReduced.matches;
  const state = {topic: 0, speaker: 'buffett', city: 0, dossierTab: 'evidence', evidenceIds: null};
  let sceneToken = 0, speechToken = 0, lastFocus = null, speechTimeline = null;
  const text = (node, value) => {node.textContent = value == null ? '未记录' : String(value);};
  const el = (tag, cls, content) => {const n = document.createElement(tag); if(cls) n.className = cls; if(content != null) text(n,content); return n;};
  const icon = name => {const wrap=el('span');wrap.innerHTML=data.icons[name] || '';wrap.setAttribute('aria-hidden','true');return wrap;};
  document.querySelectorAll('[data-icon]').forEach(node=>node.replaceWith(icon(node.dataset.icon)));
  text($('security-ticker'), data.security.ticker);text($('security-name'), data.security.name);
  text($('sample-label'), data.council.is_demo ? 'SYNTHETIC DEMO' : 'RESEARCH SNAPSHOT');
  text($('snapshot-date'), data.security.collected_at ? String(data.security.collected_at).slice(0,16).replace('T',' ') + ' / SNAPSHOT' : '采集日期未记录');
  data.cities.forEach((city,i)=>{const button=el('button','',city.label);button.type='button';button.setAttribute('aria-label',`进入${city.name}场景`);button.setAttribute('aria-pressed',String(i===0));button.addEventListener('click',()=>changeCity(i));$('city-nav').append(button);});
  data.council.topics.forEach((topic,i)=>{const button=el('button','',topic.title);button.type='button';button.setAttribute('aria-pressed',String(i===0));button.addEventListener('click',()=>{state.topic=i;renderVoice(true);});$('agenda').append(button);});
  data.council.profiles.forEach(profile=>{
    const button=el('button','perspective-choice');button.type='button';button.dataset.profile=profile.id;button.setAttribute('aria-label',`听取${profile.name_zh}的模拟方法视角`);button.setAttribute('aria-pressed',String(profile.id===state.speaker));
    const img=el('img');img.src=data.portraits[profile.id];img.alt='';img.decoding='async';button.append(img,el('span','',profile.name_zh.replace(/^.*·/,'')));
    button.addEventListener('click',()=>{state.speaker=profile.id;renderVoice(true);});$('perspective-rail').append(button);
  });
  function currentVoice(){return data.council.topics[state.topic].voices.find(v=>v.id===state.speaker);}
  function updateCopy(){
    const topic=data.council.topics[state.topic],voice=currentVoice(),profile=data.council.profiles.find(p=>p.id===state.speaker);
    text($('question'),topic.question);text($('topic-count'),`${String(state.topic+1).padStart(2,'0')} / 03`);text($('speaker-claim'),voice.claim);text($('speaker-rebuttal'),voice.rebuttal);text($('speaker-method'),`${profile.name_zh} / ${profile.method}`);text($('speaker-english'),profile.name_en);text($('speaker-chinese'),profile.name_zh);text($('speaker-era'),profile.era);
    $('speaker-photo').src=data.portraits[state.speaker];$('speaker-photo').alt=`${profile.name_en} AI 生成肖像，非本人发言或背书`;
    [...$('agenda').children].forEach((b,i)=>b.setAttribute('aria-pressed',String(i===state.topic)));
    [...$('perspective-rail').children].forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.profile===state.speaker)));
    $('briefing-facts').replaceChildren();
    voice.supporting_facts.filter(f=>f.status!=='missing' && !Array.isArray(f.value)).slice(0,3).forEach(f=>{const box=el('div','briefing-fact'),v=el('strong','',f.value==null?'待补充':String(f.value)+(f.unit||''));box.append(el('small','',f.label),v);$('briefing-facts').append(box);});
    text($('announcer'),`${topic.title}，${profile.name_zh}的模拟视角已显示。`);
  }
  async function renderVoice(animate=false){
    const token=++speechToken;
    const targets=['question','speaker-claim','speaker-rebuttal','speaker-method','speaker-english','speaker-chinese','speaker-era'].map($);
    if(speechTimeline){speechTimeline.kill();speechTimeline=null;}
    if(window.gsap)gsap.killTweensOf([...targets,$('speaker-photo')]);
    if(!animate||!motion()){updateCopy();if(window.gsap)gsap.set([...targets,$('speaker-photo')],{opacity:1,x:0,y:0,filter:'none'});return;}
    const incoming=new Image();incoming.src=data.portraits[state.speaker];try{await incoming.decode();}catch(_){}
    if(token!==speechToken)return;
    const tl=speechTimeline=gsap.timeline({defaults:{ease:'power3.out'}});
    tl.to(targets,{opacity:0,y:-5,duration:.17,stagger:.012},0).to($('speaker-photo'),{opacity:0,x:12,duration:.22},0).call(()=>{if(token===speechToken)updateCopy();});
    tl.fromTo($('speaker-photo'),{opacity:0,x:30},{opacity:1,x:0,duration:.8,ease:'power3.out'}).fromTo(targets,{opacity:0,y:12},{opacity:1,y:0,duration:.62,stagger:.035},'<.12');
  }
  async function changeCity(index){
    if(index===state.city&&$('scene-front').src)return;
    const token=++sceneToken,city=data.cities[index];state.city=index;
    [...$('city-nav').children].forEach((b,i)=>b.setAttribute('aria-pressed',String(index===i)));
    text($('room-location'),city.description);$('decision-room').dataset.city=city.id;
    const image=new Image();image.src=city.image;try{await image.decode();}catch(_){}
    if(token!==sceneToken)return;
    if(motion()&&$('scene-front').getAttribute('src')){
      gsap.killTweensOf($('scene-front'));$('scene-back').src=$('scene-front').src;$('scene-front').src=city.image;
      gsap.fromTo($('scene-front'),{opacity:0,scale:1.025},{opacity:1,scale:1,duration:1.15,ease:'power2.inOut',onComplete:()=>{if(token===sceneToken)$('scene-back').removeAttribute('src');}});
    }else{$('scene-front').src=city.image;$('scene-front').style.opacity='1';$('scene-back').removeAttribute('src');}
    text($('announcer'),`场景已切换至${city.name}，研究议题和方法视角保持不变。`);
  }
  function nextSpeaker(){const i=data.council.profiles.findIndex(p=>p.id===state.speaker);state.speaker=data.council.profiles[(i+1)%data.council.profiles.length].id;renderVoice(true);const b=[...$('perspective-rail').children].find(n=>n.dataset.profile===state.speaker);const rail=$('perspective-rail');rail.scrollTo({left:Math.max(0,b.offsetLeft-rail.offsetLeft-rail.clientWidth/2+b.offsetWidth/2),behavior:prefersReduced.matches?'instant':'smooth'});}
  $('next-perspective').addEventListener('click',nextSpeaker);$('rail-next').addEventListener('click',nextSpeaker);
  const statusLabel={available:'输入已记录 · 未独立核实',derived:'由输入计算',missing:'缺失 / 未评估',stale:'记录已过期',not_applicable:'不适用'};
  const labels={roe:'ROE',net_margin:'净利率',revenue_growth:'营收同比',debt_ratio:'资产负债率',close_60d:'历史收盘价',financial_years:'报告期输入',revenue_history:'营收序列',net_profit_history:'净利润序列',financial_health:'财务健康输入',pe:'PE',industry_pe:'行业PE参照',pe_quantile:'PE分位输入',pb:'PB',fcf:'自由现金流',wacc:'WACC',terminal_growth:'永续增长率',intrinsic_value:'内在价值计算值',sensitivity:'敏感性分析',scenario:'情景假设',bull:'乐观情景',base:'基础情景',bear:'悲观情景',source:'来源',as_of:'观测日期',currency:'币种',_note:'说明'};
  function payloadTable(payload,depth=0){
    const box=el('div','payload-table');
    if(payload===null||payload===undefined){box.append(el('p','note','未记录'));return box;}
    if(typeof payload!=='object'){box.append(el('p','',payload));return box;}
    Object.entries(payload).forEach(([key,value])=>{
      if(key.startsWith('_')&&key!=='_note')return;
      const name=labels[key]||key;
      if(value && typeof value==='object' && !Array.isArray(value) && depth<3){const detail=el('details','payload-group');detail.append(el('summary','',name),payloadTable(value,depth+1));box.append(detail);}
      else if(Array.isArray(value)&&value.some(x=>x&&typeof x==='object')){const detail=el('details','payload-group');detail.append(el('summary','',name+' / '+value.length+' 条'));value.forEach((x,i)=>{detail.append(el('h4','',String(i+1)),payloadTable(x,depth+1));});box.append(detail);}
      else{const row=el('div','fact-row');row.append(el('span','',name),el('span','',value==null?'未记录':Array.isArray(value)?value.map(x=>x==null?'缺失':String(x)).join(' · '):typeof value==='object'?JSON.stringify(value):String(value)));box.append(row);}
    });return box;
  }
  function rawRecord(id,dim){const pipeline=dim._pipeline||{};return {id,title:(data.analysis.dimension_titles||{})[id]||id.replace(/^\d+_/,''),status:dim.source==='skip'||dim.applicable===false?'not_applicable':dim.stale||pipeline.stale?'stale':dim.fallback||pipeline.fallback||dim.error||!dim.data||!Object.keys(dim.data).length?'missing':'available',source:dim.source,date:(dim.data||{}).as_of||dim.date,collected_at:pipeline.fetched_at||dim.fetched_at};}
  function recordNode(record,rawPayload){
    const article=el('article','evidence-record'),head=el('div','record-heading');head.append(el('h3','',record.title),el('span','record-status',statusLabel[record.status]||'状态未记录'));article.append(head);
    article.append(el('p','record-meta',`来源：${record.source || '未记录'}\n观测日期：${record.date || '未记录'} · 采集时间：${record.collected_at || data.security.collected_at || '未记录'}`));
    const facts=record.facts||[];
    if(!facts.length&&!rawPayload)article.append(el('p','empty-state','尚无可用于这个问题的完整记录。保留缺口，不以零值代替。'));
    facts.forEach(fact=>{const row=el('div','fact-row');const value=fact.text.startsWith(fact.label+'：')?fact.text.slice(fact.label.length+1):fact.text;row.append(el('span','',fact.label),el('span','',value));article.append(row);});
    if(rawPayload&&Object.keys(rawPayload).length){if(!facts.length)article.append(payloadTable(rawPayload));const detail=el('details'),summary=el('summary','','核对完整原始记录'),pre=el('pre','',JSON.stringify(rawPayload,null,2));detail.append(summary,pre);article.append(detail);}
    return article;
  }
  function renderDossier(){
    const content=$('dossier-content');content.replaceChildren();
    [...document.querySelectorAll('[data-dossier-tab]')].forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.dossierTab===state.dossierTab)));
    const voice=currentVoice();text($('dossier-context'),state.dossierTab==='about'?'影像、模拟方法与原始证据，明确分层。':data.council.topics[state.topic].question);
    if(state.dossierTab==='evidence'){
      const ids=state.evidenceIds||Object.keys({...data.council.evidence,...(data.raw.dimensions||{})});
      ids.forEach(id=>{const dim=(data.raw.dimensions||{})[id]||{};const record=data.council.evidence[id]||rawRecord(id,dim);if(record)content.append(recordNode(record,((data.raw.dimensions||{})[id]||{}).data));});
      if(state.evidenceIds){const button=el('button','text-button','展开全部证据维度');button.addEventListener('click',()=>{state.evidenceIds=null;renderDossier();});content.append(button);}
    }else if(state.dossierTab==='models'){
      content.append(el('p','model-notice','计算模型、规则评分与原始证据分层呈现。规则分不是收益概率；模型输出依赖输入和假设，尚未完成样本外校准。'));
      if(data.analysis.review_skipped)content.append(el('p','model-notice','当前演示跳过自动审阅门槛，不代表真实标的审阅完成。'));
      const models=Object.entries(data.raw.dimensions||{}).filter(([id])=>/^2[012]_/.test(id));
      if(!models.length)content.append(el('p','empty-state','估值模型尚未建立。现金流、折现率、可比公司与情景假设需要补齐；不展示机械价格倍数或默认上涨概率。'));
      models.forEach(([id,dim])=>content.append(recordNode(rawRecord(id,dim),dim.data)));
      const scores=(data.analysis.dimensions||{}).dimensions||{};
      if(Object.keys(scores).length){content.append(el('h3','','分维度规则审阅'));Object.entries(scores).forEach(([id,d])=>{const row=el('div','rules-result');const desc=el('div','',(data.analysis.dimension_titles||{})[id]||id);const valid=d.score_status==='data_backed'&&typeof d.score==='number'&&Number.isFinite(d.score);desc.append(el('small','',valid?'由输入触发的规则分 · 非校准预测':d.score_status==='heuristic'?'定性启发式 · 分数不作测量值':'缺失 / 未评估'));row.append(desc,el('strong','',valid?d.score+' / 10':'—'));content.append(row);});}
    }else{
      const box=el('div','about-copy');
      [['J Trader 私人研究室','J Trader 由 aJay / Aji-Q 维护。城市只改变视觉场景，不改变数据、议题或当前结论。'],['方法，而非人物背书',data.council.disclosure],['证据优先','议题观点由原始输入确定生成，不使用旧 persona 的随机台词，也不把缺失值当成零。规则分、角色一致度与数据覆盖均不是上涨概率；尚未完成样本外校准。'],['图像来源','人物为 AI 生成的编辑肖像。城市图片的具体来源、日期与编辑记录见下方逐图说明。'],['软件来源','J Trader 的新增设计与实现由 aJay 保留署名；MIT 上游作者与贡献历史保存在 LICENSE / NOTICE。GSAP 与 Lucide 依其各自许可使用。']].forEach(([h,p])=>{box.append(el('h3','',h),el('p','',p));});
      data.cities.forEach(city=>{const p=el('p','note',`${city.name}：${city.credit||'场景测试图；非最终摄影选片'}`);if(city.source_url&&/^https:\/\//.test(city.source_url)){const a=el('a','','查看原始摄影作品');a.href=city.source_url;a.target='_blank';a.rel='noopener noreferrer';p.append(document.createTextNode(' '),a);if(city.license_url&&/^https:\/\//.test(city.license_url)){const l=el('a','license-link',city.license);l.href=city.license_url;l.target='_blank';l.rel='noopener noreferrer';p.append(l);}}box.append(p);});
      const link=el('a','','J Trader / GitHub');link.href='https://github.com/Aji-Q/aJay-Skill';link.target='_blank';link.rel='noopener noreferrer';box.append(el('p','note','本报告不构成投资建议。'),link);content.append(box);
    }
    content.scrollTop=0;
  }
  function openDossier(tab='evidence',ids=null){lastFocus=document.activeElement;state.dossierTab=tab;state.evidenceIds=ids;renderDossier();$('dossier').showModal();if(motion())gsap.fromTo($('dossier'),{x:70,opacity:.3},{x:0,opacity:1,duration:.48,ease:'power3.out'});}
  $('view-evidence').addEventListener('click',()=>openDossier('evidence',currentVoice().evidence_ids));$('test-counterpoint').addEventListener('click',()=>openDossier('evidence',currentVoice().evidence_ids));
  document.querySelectorAll('[data-open-dossier]').forEach(b=>b.addEventListener('click',()=>openDossier('evidence')));
  $('open-disclosure').addEventListener('click',()=>openDossier('about'));$('close-dossier').addEventListener('click',()=>$('dossier').close());
  $('dossier').addEventListener('close',()=>{if(lastFocus&&lastFocus.isConnected)lastFocus.focus({preventScroll:true});});
  document.querySelectorAll('[data-dossier-tab]').forEach(b=>b.addEventListener('click',()=>{state.dossierTab=b.dataset.dossierTab;renderDossier();}));
  $('download-inputs').addEventListener('click',()=>{const blob=new Blob([JSON.stringify(data.raw,null,2)],{type:'application/json'}),url=URL.createObjectURL(blob),a=el('a');a.href=url;a.download=`${String(data.security.ticker||'J-Trader').replace(/[^a-zA-Z0-9_.-]/g,'_')}-inputs.json`;document.body.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),1000);});
  $('explore-scene').addEventListener('click',()=>{const city=data.cities[state.city];text($('scene-title'),city.name+' / '+city.label);text($('scene-credit'),city.credit);$('scene-detail').src=city.image;$('scene-detail').alt=city.description+'，AI轻微重构摄影';$('scene-source').href=city.source_url||'#';$('scene-source').hidden=!city.source_url;$('scene-license').href=city.license_url||'#';$('scene-license').hidden=!city.license_url;$('scene-lightbox').showModal();});
  $('close-scene').addEventListener('click',()=>$('scene-lightbox').close());
  $('scene-lightbox').addEventListener('close',()=>$('explore-scene').focus({preventScroll:true}));
  renderVoice();changeCity(0);
  if(motion())gsap.from('.briefing,.speaker-presence,.council-floor',{opacity:0,y:14,duration:.9,stagger:.1,ease:'power3.out',delay:.08});
})();

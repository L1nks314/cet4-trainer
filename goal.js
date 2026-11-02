/* ── 训练页顶部：今天这一页怎么做 ──
   每个训练页只引这一行脚本，步骤与首页 index.html 的排期保持一致，改一处改两处。
   两套：完整版（按音频长度分档 46/54/62/67′）、35 分钟短版（只保核心链，跟读挪到周三）。
   今天走哪套读的是首页同一个键 cet4_tier_YYYY-MM-DD，两边永远一致。 */
(function(){
  var D = new Date();
  var d0 = function(x){ return new Date(x.getFullYear(), x.getMonth(), x.getDate()); };
  var today = d0(D);
  var wd = D.getDay();
  var p = (location.pathname.split('/').pop() || '').toLowerCase();
  var ymd = D.getFullYear() + '-' + String(D.getMonth()+1).padStart(2,'0') + '-' + String(D.getDate()).padStart(2,'0');

  var kind = '';
  if (/section[abc]\.html$/.test(p)) kind = 'listen';
  else if (/^read-/.test(p)) kind = 'read';
  else if (/^matching-/.test(p)) kind = 'match';
  else if (/^write-/.test(p)) kind = 'write';
  else if (/^trans-/.test(p)) kind = 'trans';
  if (!kind) return;                       /* 非训练页直接不挂 */

  /* 周三 + 当前页就是本周一存下的那段 → 复听 */
  if (kind === 'listen' && wd === 3){
    var seg = null;
    try{ seg = JSON.parse(localStorage.getItem('cet4_curseg') || 'null'); }catch(e){}
    if (seg && seg.f && String(seg.f).toLowerCase() === p) kind = 'replay';
  }

  /* 今天走哪套：与首页 getTier() 同源。full=完整，std/min=35 分钟短版 */
  var tier = '';
  try{ tier = localStorage.getItem('cet4_tier_' + ymd) || ''; }catch(e){}
  if (tier !== 'full' && tier !== 'std' && tier !== 'min'){
    tier = 'full';   /* 与首页一致：默认完整版，短版是应急档 */
  }
  var short = (tier !== 'full');

  /* ── 听力按真实音频长度分档：13 套真题中位数 A 6′19″ / B 6′04″ / C 9′14″ ──
     四级卷面只有 A–D 选项，问题在每篇录音末尾才念，所以第一步只能预读选项。 */
  var SEC = /sectionc\.html$/.test(p) ? 'C' : (/sectionb\.html$/.test(p) ? 'B' : 'A');
  var LEN = {
    A:{prep:'4′', blind:'7′', dict:'15′', why:'8′', sh:'12′', total:'约 46 分钟', sent:'5–6 句', aud:'6 分 19 秒', note:'跟 2 遍刚好到点',
       sp:'4′', sb:'7′', sw:'8′', sd:'9′', ssent:'3 句', stotal:'约 30 分钟'},
    B:{prep:'4′', blind:'7′', dict:'15′', why:'8′', sh:'12′', total:'约 46 分钟', sent:'6 句',   aud:'6 分 04 秒', note:'跟 2 遍刚好到点',
       sp:'4′', sb:'7′', sw:'8′', sd:'9′', ssent:'3 句', stotal:'约 30 分钟'},
    C:{prep:'6′', blind:'10′',dict:'20′', why:'10′',sh:'16′', total:'约 62 分钟', sent:'8–10 句',aud:'9 分 14 秒', note:'跟一遍多就到点，别硬凑遍数',
       sp:'5′', sb:'10′', sw:'8′', sd:'11′', ssent:'5 句', stotal:'约 35 分钟'}
  };
  var REP = {
    A:{a:'7′', c:'15′', d:'7′', total:'约 54 分钟', sc:'13′', stotal:'约 30 分钟'},
    B:{a:'7′', c:'15′', d:'7′', total:'约 54 分钟', sc:'13′', stotal:'约 30 分钟'},
    C:{a:'10′',c:'22′', d:'10′',total:'约 67 分钟', sc:'15′', stotal:'约 35 分钟'}
  };
  var L = LEN[SEC], R = REP[SEC];

  var PLANS = {};

  /* ─────────── 听力新段 ─────────── */
  PLANS.listen = { head:'今天 · 听力新段 · Section ' + SEC, total:L.total,
    tip:'做完 ② 马上交卷——交卷才解锁原文和题干；③④⑤ 解锁后再做。', steps:[
    ['横看竖看选项', '四级卷面只有 A–D 选项，问题在录音最后才念。横看：同一题四个选项比一遍，相同部分划掉、不同的那一两个词圈出来，那就是要等的点。竖看：把本段所有选项串一遍，猜这段讲什么。不查词、不看原文', L.prep],
    ['盲听做题', '一遍放完，不暂停、不回放。答案在放音过程中就定，别等问题念完再回想——念完只有 5 秒涂卡。选不出就选最像的，先往下走', L.blind],
    ['逐句听写', '交卷解锁原文后，打开听写模式——它只走清单里标 ★ 的 ' + L.sent + '。听不出就画「—」，绝不留空、绝不猜', L.dict],
    ['对照归因', '只看画「—」的句子，每处标一个原因：连读 / 生词 / 走神', L.why],
    ['跟读', '不看文本，慢半拍跟着念，卡住就退回那句重来。本段 ' + L.aud + '，' + L.note, L.sh]
  ]};

  PLANS.listen_short = { head:'今天 · 听力新段 · Section ' + SEC, total:L.stotal,
    tip:'35 分钟版：砍掉跟读，挪到周三复听一起做。今天只保「听 → 交卷 → 听写 → 归因」这条链。', steps:[
    ['横看竖看选项', '四级卷面只有 A–D 选项，问题在录音最后才念。横看同一题四个选项找差异点，竖看本段选项串话题。不查词、不看原文', L.sp],
    ['盲听做题', '一遍放完，不暂停、不回放。答案在放音中定，别等问题念完再回想。选不出就选最像的', L.sb],
    ['交卷', '点提交。交卷后原文和题干才解锁，后面的听写要用原文对', '1′'],
    ['逐句听写', '打开听写模式，只走标 ★ 的 ' + L.ssent + '。听不出就画「—」，绝不猜。写不满没关系，这是采样不是默写', L.sd],
    ['对照归因', '只看画「—」的句子，每处标一个原因：连读 / 生词 / 走神', L.sw]
  ]};

  /* ─────────── 周三复听 ─────────── */
  PLANS.replay = { head:'今天 · 同一段复听 · Section ' + SEC, total:R.total,
    tip:'这次不换新材料，就吃这一段的漏句。', steps:[
    ['不看书再听一遍', '整段放完，边听边在心里回答：这段讲什么、分几件事。不暂停', R.a],
    ['只看「—」的句子', '翻到周一标出来的漏句，逐句听清每个词。其余部分不看', '10′'],
    ['0.85 倍速跟读 2 遍', '不看文本，慢半拍跟着念。卡住就停在那句，倒回去再跟。慢放会让时间变长，这是正常的', R.c],
    ['1.0 倍速跟读 1 遍', '这次要求跟上。跟丢了就从下一句接上，不许回放', R.d],
    ['再做一遍，对比周一', '清空作答再答一遍，记下这次对几题——差多少就是复听值多少', '15′']
  ]};

  PLANS.replay_short = { head:'今天 · 同一段复听 · Section ' + SEC, total:R.stotal,
    tip:'35 分钟版：只走「重听 → 补漏句 → 慢速跟一遍」。不重做、不上 1.0 倍，那两件攒到周日整套时做。', steps:[
    ['不看书再听一遍', '整段放完，边听边在心里回答：这段讲什么、分几件事。不暂停', R.a],
    ['只看「—」的句子', '翻到周一标出来的漏句，逐句听清每个词。其余部分不看', '10′'],
    ['0.85 倍速跟读 1 遍', '不看文本，慢半拍跟着念。卡住就停在那句，倒回去再跟。慢放拖时间，一个词一个词过', R.sc]
  ]};

  /* ─────────── 阅读 / 匹配 / 写译 ─────────── */
  PLANS.read = { head:'今天 · 仔细阅读', total:'60 分钟', tip:'②做完再对答案，③只记替换，不抄解析。', steps:[
    ['限时做', '12 分钟做完 10 题，不查词、不回看。做完立刻停表', '12′'],
    ['划答案句', '每题回原文划出答案句，别整段翻译，只找那一句', '8′'],
    ['对解析记替换', '逐题看「定位词 → 原文替换词」，只记这一对，不抄解析', '25′'],
    ['收 3 个生词', '从原文里挑 3 个反复出现的词记下来，不背单词书', '15′']
  ]};
  PLANS.read_short = { head:'今天 · 仔细阅读', total:'约 35 分钟', tip:'35 分钟版：砍掉收生词。限时做、划答案句、记替换这三件是命门，不能砍。', steps:[
    ['限时做', '12 分钟做完 10 题，不查词、不回看。做完立刻停表', '12′'],
    ['划答案句', '每题回原文划出答案句，别整段翻译，只找那一句', '8′'],
    ['对解析记替换', '逐题看「定位词 → 原文替换词」，只记这一对，不抄解析。来不及就只做错的题', '15′']
  ]};

  PLANS.match = { head:'今天 · 长篇匹配', total:'60 分钟', tip:'先扫题干关键词，别先读全文。', steps:[
    ['限时做', '15 分钟，10 道题找段落。不查词，凭关键词定位，做完立刻停表', '15′'],
    ['回原文找替换', '逐题回段落里划出对应句，把「题干的词 → 原文的词」这一对写下来', '25′'],
    ['归因', '错题只写一句：是没找到定位，还是替换没认出来。二选一', '20′']
  ]};
  PLANS.match_short = { head:'今天 · 长篇匹配', total:'约 35 分钟', tip:'35 分钟版：归因压到 5 分钟，只写错题的那一句，不逐题复盘。', steps:[
    ['限时做', '15 分钟，10 道题找段落。不查词，凭关键词定位，做完立刻停表', '15′'],
    ['回原文找替换', '逐题回段落里划出对应句，把「题干的词 → 原文的词」写下来。来不及就只做没把握的题', '15′'],
    ['归因', '错题只写一句：是没找到定位，还是替换没认出来。二选一', '5′']
  ]};

  PLANS.write = { head:'今天 · 写作一篇', total:'60 分钟', tip:'写的时候不查词、不停笔，改留到第三步。', steps:[
    ['写', '25 分钟写完，不看范文、不查词。卡住就换一句简单的话说完', '25′'],
    ['自查 3 处', '只看时态、单复数、连接词。三样各挑一处改，不改别的', '10′'],
    ['对范文改', '对完只改 3 句，不重写全篇。把范文里那个句式抄下来', '15′'],
    ['默写句式', '合上范文，把那 1 个句式默写一遍。写不出说明没记住', '10′']
  ]};
  PLANS.write_short = { head:'今天 · 写作一篇', total:'约 35 分钟', tip:'35 分钟版：砍掉默写。写完、自查、对范文改 3 句，这三步保住就够了。', steps:[
    ['写', '25 分钟写完，不看范文、不查词。卡住就换一句简单的话说完', '25′'],
    ['自查 3 处', '只看时态、单复数、连接词。三样各挑一处改，不改别的', '5′'],
    ['对范文改 3 句', '对完只改 3 句，不重写全篇。把范文里那个句式抄下来', '5′']
  ]};

  PLANS.trans = { head:'今天 · 翻译一段', total:'60 分钟', tip:'先断句再译，别一句话读三遍才动笔。', steps:[
    ['译', '25 分钟写完，不看参考、不查词典。卡住就换一句简单的话说完', '25′'],
    ['自查 3 处', '只看时态、单复数、连接词。三样各挑一处改，不改别的', '10′'],
    ['对参考改', '对完只改 3 句，不重写全篇。把参考里那个句式抄下来', '15′'],
    ['默写句式', '合上参考，把那 1 个句式默写一遍。写不出说明没记住', '10′']
  ]};
  PLANS.trans_short = { head:'今天 · 翻译一段', total:'约 35 分钟', tip:'35 分钟版：砍掉默写。译完、自查、对参考改 3 句，这三步保住就够了。', steps:[
    ['译', '25 分钟写完，不看参考、不查词典。卡住就换一句简单的话说完', '25′'],
    ['自查 3 处', '只看时态、单复数、连接词。三样各挑一处改，不改别的', '5′'],
    ['对参考改 3 句', '对完只改 3 句，不重写全篇。把参考里那个句式抄下来', '5′']
  ]};

  var P = short ? (PLANS[kind + '_short'] || PLANS[kind]) : PLANS[kind];
  if (!P) return;

  /* 阶段达标线（与 index.html 的 GOALS 一致） */
  var line;
  if (today <= d0(new Date(2026, 10, 8))) line = '校准期：只测数据，不设线';
  else if (today < d0(new Date(2026, 10, 23))) line = '打底期：听力篇章 ≥5/10 且留白≤5；仔细阅读 ≥82%；匹配 ≥85%；写作进 9 分档';
  else line = '上考场期：整套听力连做 ≥45%；阅读 ≥85%；匹配 ≥90%；模板能默写';

  var examDay = d0(new Date(2026, 11, 12));
  var left = Math.max(0, Math.round((examDay - today) / 86400000));

  var rows = P.steps.map(function(s, i){
    return '<div class="gst"><b>' + (i + 1) + '</b>'
      + '<div class="stx"><i>' + s[0] + '</i><em>' + s[1] + '</em></div>'
      + '<span class="smm">' + s[2] + '</span></div>';
  }).join('');

  var html = '<div id="goalBox">'
    + '<div class="ghd" id="goalHd">'
    +   '<b>' + P.head + ' · ' + P.steps.length + ' 步</b>'
    +   '<span>' + P.total + ' ▾</span>'
    + '</div>'
    + '<div class="gbd">'
    +   rows
    +   '<div class="gfoot">' + P.tip + '<br><span>' + line + '　·　距考试 ' + left + ' 天</span></div>'
    +   '<div class="gsw"><a href="javascript:void(0)" id="goalSw">'
    +     (short ? '今天有整块时间？切完整版 →' : '今天只有半小时？切 35 分钟短版 →')
    +   '</a></div>'
    + '</div>'
    + '</div>';

  var css = ''
    + '#goalBox{margin:12px 0 16px;border:1px solid var(--line,#e5e8ec);border-radius:13px;'
    +   'background:var(--card,#fff);box-shadow:0 1px 2px rgba(16,24,40,.05);overflow:hidden}'
    + '#goalBox .ghd{display:flex;justify-content:space-between;align-items:center;gap:8px;'
    +   'padding:11px 13px;font-size:13px;cursor:pointer;-webkit-tap-highlight-color:transparent}'
    + '#goalBox .ghd b{font-weight:800;color:var(--txt,#1b1e23)}'
    + '#goalBox .ghd span{color:var(--sub2,#8b93a1);font-size:11.5px;white-space:nowrap}'
    + '#goalBox .gbd{padding:0 13px 11px;display:none}'
    + '#goalBox.open .gbd{display:block}'
    + '#goalBox .gst{display:flex;gap:9px;align-items:flex-start;padding:5px 0;'
    +   'border-top:1px solid var(--line2,#f2f4f7)}'
    + '#goalBox .gst:first-child{border-top:0}'
    + '#goalBox .gst b{flex:0 0 18px;height:18px;line-height:18px;text-align:center;border-radius:50%;'
    +   'background:var(--blue,#2563eb);color:#fff;font-size:11px;font-weight:700;margin-top:1px}'
    + '#goalBox .gst .stx{flex:1;min-width:0}'
    + '#goalBox .gst .stx i{display:block;font-style:normal;font-weight:700;font-size:12.5px;'
    +   'color:var(--txt,#1b1e23);line-height:1.5}'
    + '#goalBox .gst .stx em{display:block;font-style:normal;font-size:11.5px;'
    +   'color:var(--sub,#6b7280);line-height:1.55}'
    + '#goalBox .gst .smm{flex:0 0 auto;font-size:11px;color:var(--sub2,#8b93a1);'
    +   'font-variant-numeric:tabular-nums;padding-top:2px}'
    + '#goalBox .gfoot{font-size:11px;color:var(--sub2,#8b93a1);margin-top:8px;line-height:1.6;'
    +   'border-top:1px solid var(--line2,#f2f4f7);padding-top:8px}'
    + '#goalBox .gfoot span{color:#b0b7c3}'
    + '#goalBox .gsw{margin-top:6px;font-size:11.5px}'
    + '#goalBox .gsw a{color:var(--blue,#2563eb);text-decoration:none;'
    +   'border-bottom:1px dashed rgba(37,99,235,.35);padding-bottom:1px}';

  /* 切换：写回首页同一个键，刷新即换整套步骤 */
  function setMode(nextShort){
    try{ localStorage.setItem('cet4_tier_' + ymd, nextShort ? 'std' : 'full'); }catch(e){}
    location.reload();
  }

  function mount(){
    if (document.getElementById('goalBox')) return;
    var h = document.querySelector('header') || document.querySelector('h1');
    if (!h) return;
    var st = document.createElement('style');
    st.textContent = css;
    document.head.appendChild(st);
    if (h.tagName === 'HEADER') h.insertAdjacentHTML('beforeend', html);
    else h.insertAdjacentHTML('afterend', html);
    var box = document.getElementById('goalBox');
    var _v = null;
    try{ _v = localStorage.getItem('cet4_goal_open'); }catch(e){}
    var open = (_v === null) ? true : (_v === '1');   /* 第一次打开默认展开 */
    if (open) box.classList.add('open');
    document.getElementById('goalHd').addEventListener('click', function(){
      box.classList.toggle('open');
      try{ localStorage.setItem('cet4_goal_open', box.classList.contains('open') ? '1' : '0'); }catch(e){}
    });
    var sw = document.getElementById('goalSw');
    if (sw) sw.addEventListener('click', function(e){ e.stopPropagation(); setMode(!short); });
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', mount);
  else mount();
})();

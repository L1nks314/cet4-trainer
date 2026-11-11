/* ── 训练页顶部：今天这一页怎么做 ──
   每个训练页只引这一行脚本，步骤与首页 index.html 的排期保持一致，改一处改两处。
   两套：完整版（听力 C 42′ / A·B 23′ / 阅读 40′ / 匹配 32′ / 写译 38′）、
        35 分钟短版（只保核心链，砍跟读与收生词）。
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

  /* 周三不再是复听：一周两个新段，复听下沉成首页副项的「不看书再听一遍」。 */

  /* 今天走哪套：与首页 getTier() 同源。full=完整，std/min=35 分钟短版 */
  var tier = '';
  try{ tier = localStorage.getItem('cet4_tier_' + ymd) || ''; }catch(e){}
  if (tier !== 'full' && tier !== 'std' && tier !== 'min'){
    tier = 'full';   /* 与首页一致：默认完整版，短版是应急档 */
  }
  var short = (tier !== 'full');

  /* ── 听力按真实音频长度分档：13 套真题中位数 A 6′19″ / B 6′04″ / C 9′14″ ──
     四级卷面只有 A–D 选项，问题在每篇录音末尾才念，所以第一步只能预读选项。
     时长是「做完这一段要多久」，不凑整：C 4+10+1+12+5+10=42′，A/B 3+7+1+7+3+2=23′。 */
  var SEC = /sectionc\.html$/.test(p) ? 'C' : (/sectionb\.html$/.test(p) ? 'B' : 'A');
  var LEN = {
    A:{prep:'3′', blind:'7′', dict:'7′',  why:'3′', sh:'2′',  total:'约 23 分钟', sent:'3 句', aud:'6 分 19 秒', note:'挑 1 句跟到顺就行',
       sp:'3′', sb:'7′', sw:'2′', sd:'5′', ssent:'3 句', stotal:'约 18 分钟'},
    B:{prep:'3′', blind:'7′', dict:'7′',  why:'3′', sh:'2′',  total:'约 23 分钟', sent:'3 句', aud:'6 分 04 秒', note:'挑 1 句跟到顺就行',
       sp:'3′', sb:'7′', sw:'2′', sd:'5′', ssent:'3 句', stotal:'约 18 分钟'},
    C:{prep:'4′', blind:'10′',dict:'12′', why:'5′', sh:'10′', total:'约 42 分钟', sent:'8 句', aud:'9 分 14 秒', note:'跟 2 遍刚好到点',
       sp:'3′', sb:'10′', sw:'4′', sd:'7′', ssent:'5 句', stotal:'约 25 分钟'}
  };
  var L = LEN[SEC];

  var PLANS = {};

  /* ─────────── 听力新段 ─────────── */
  PLANS.listen = { head:'今天 · 听力新段 · Section ' + SEC, total:L.total,
    tip:'做完 ② 马上交卷——交卷才解锁原文和题干；③④⑤ 解锁后再做。', steps:[
    ['横看竖看选项', '四级卷面只有 A–D 选项，问题在录音最后才念。横看：同一题四个选项比一遍，相同部分划掉、不同的那一两个词圈出来，那就是要等的点。竖看：把本段所有选项串一遍，猜这段讲什么。不查词、不看原文', L.prep],
    ['盲听做题', '一遍放完，不暂停、不回放。答案在放音过程中就定，别等问题念完再回想——念完只有 5 秒涂卡。选不出就选最像的，先往下走。做完立刻点交卷', L.blind],
    ['逐句听写', '交卷解锁原文后，打开听写模式——它只走清单里标 ★ 的 ' + L.sent + '。听不出就画「—」，绝不留空、绝不猜', L.dict],
    ['对照归因', '只看画「—」的句子，每处标一个原因：连读 / 生词 / 走神', L.why],
    ['跟读', '不看文本，慢半拍跟着念，卡住就退回那句重来。本段 ' + L.aud + '，' + L.note, L.sh]
  ]};

  PLANS.listen_short = { head:'今天 · 听力新段 · Section ' + SEC, total:L.stotal,
    tip:'35 分钟版：听写降到 ' + L.ssent + '、砍掉跟读。今天只保「听 → 交卷 → 听写 → 归因」这条链。', steps:[
    ['横看竖看选项', '四级卷面只有 A–D 选项，问题在录音最后才念。横看同一题四个选项找差异点，竖看本段选项串话题。不查词、不看原文', L.sp],
    ['盲听做题', '一遍放完，不暂停、不回放。答案在放音中定，别等问题念完再回想。选不出就选最像的', L.sb],
    ['交卷', '点提交。交卷后原文和题干才解锁，后面的听写要用原文对', '1′'],
    ['逐句听写', '打开听写模式，只走标 ★ 的 ' + L.ssent + '。听不出就画「—」，绝不猜。写不满没关系，这是采样不是默写', L.sd],
    ['对照归因', '只看画「—」的句子，每处标一个原因：连读 / 生词 / 走神', L.sw]
  ]};

  /* ─────────── 阅读 / 匹配 / 写译 ─────────── */
  PLANS.read = { head:'今天 · 仔细阅读 1 套（两篇 10 题）', total:'40 分钟', tip:'材料是 46–55 两篇。②做完再对答案，③只记替换，不抄解析。', steps:[
    ['限时做两篇', '15 分钟做完 10 题（46–55），不查词、不回看。考场给两篇就是这个时间，做完立刻停表', '15′'],
    ['划答案句', '每题回原文划出答案句，别整段翻译，只找那一句。五题一段，两段分开划', '8′'],
    ['对替换', '逐题看「定位词 → 原文替换词」，只记这一对。全对的题跳过，别重读', '10′'],
    ['收生词', '只收反复出现的词，最多 3 个。不抄整句、不背单词书', '7′']
  ]};
  PLANS.read_short = { head:'今天 · 仔细阅读 1 套（两篇 10 题）', total:'约 31 分钟', tip:'35 分钟版：砍掉收生词。限时做、划答案句、记替换这三件是命门，不能砍。', steps:[
    ['限时做两篇', '15 分钟做完 10 题（46–55），不查词、不回看。做完立刻停表', '15′'],
    ['划答案句', '每题回原文划出答案句，别整段翻译，只找那一句', '8′'],
    ['对替换', '只看错的题：「定位词 → 原文替换词」，记这一对，不抄解析', '8′']
  ]};

  PLANS.match = { head:'今天 · 长篇匹配 1 篇', total:'32 分钟', tip:'先扫题干关键词，别先读全文。', steps:[
    ['限时做', '15 分钟，10 道题找段落。不查词，凭关键词定位，做完立刻停表', '15′'],
    ['回原文找替换', '逐题回段落里划出对应句，把「题干的词 → 原文的词」这一对写下来', '12′'],
    ['归因', '错题只写一句：是没找到定位，还是替换没认出来。二选一', '5′']
  ]};
  PLANS.match_short = { head:'今天 · 长篇匹配 1 篇', total:'约 26 分钟', tip:'35 分钟版：找替换压到 8 分钟，只做没把握的题；归因只写错题那一句。', steps:[
    ['限时做', '15 分钟，10 道题找段落。不查词，凭关键词定位，做完立刻停表', '15′'],
    ['回原文找替换', '逐题回段落里划出对应句，把「题干的词 → 原文的词」写下来。来不及就只做没把握的题', '8′'],
    ['归因', '错题只写一句：是没找到定位，还是替换没认出来。二选一', '3′']
  ]};

  PLANS.write = { head:'今天 · 写作一篇', total:'38 分钟', tip:'写的时候不查词、不停笔，改留到第三步。', steps:[
    ['写', '25 分钟写完，不看范文、不查词。卡住就换一句简单的话说完', '25′'],
    ['自查 3 处', '只看时态、单复数、连接词。三样各挑一处改，不改别的', '5′'],
    ['对范文改 3 句', '对完只改 3 句，不重写全篇。把范文里那个句式抄下来', '8′']
  ]};
  PLANS.write_short = { head:'今天 · 写作一篇', total:'约 33 分钟', tip:'35 分钟版：对范文只改 3 句、3 分钟收尾。写完、自查两步保住就够了。', steps:[
    ['写', '25 分钟写完，不看范文、不查词。卡住就换一句简单的话说完', '25′'],
    ['自查 3 处', '只看时态、单复数、连接词。三样各挑一处改，不改别的', '5′'],
    ['对范文改 3 句', '对完只改 3 句，不重写全篇。把范文里那个句式抄下来', '3′']
  ]};

  PLANS.trans = { head:'今天 · 翻译一段', total:'38 分钟', tip:'先断句再译，别一句话读三遍才动笔。', steps:[
    ['译', '25 分钟写完，不看参考、不查词典。卡住就换一句简单的话说完', '25′'],
    ['自查 3 处', '只看时态、单复数、连接词。三样各挑一处改，不改别的', '5′'],
    ['对参考改 3 句', '对完只改 3 句，不重写全篇。把参考里那个句式抄下来', '8′']
  ]};
  PLANS.trans_short = { head:'今天 · 翻译一段', total:'约 33 分钟', tip:'35 分钟版：对参考只改 3 句、3 分钟收尾。译完、自查两步保住就够了。', steps:[
    ['译', '25 分钟写完，不看参考、不查词典。卡住就换一句简单的话说完', '25′'],
    ['自查 3 处', '只看时态、单复数、连接词。三样各挑一处改，不改别的', '5′'],
    ['对参考改 3 句', '对完只改 3 句，不重写全篇。把参考里那个句式抄下来', '3′']
  ]};

  var P = short ? (PLANS[kind + '_short'] || PLANS[kind]) : PLANS[kind];
  if (!P) return;

  /* 阶段达标线（与 index.html 的 GOALS 一致） */
  var line;
  if (today <= d0(new Date(2026, 10, 8))) line = '校准期：只测数据，不设线';
  else if (today < d0(new Date(2026, 10, 23))) line = '打底期：整套听力 ≥15/25；仔细阅读 ≥82%；匹配 ≥85%；写作进 9 分档';
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
    +   '<b>今天怎么做 · ' + P.steps.length + ' 步</b>'
    +   '<span>' + P.head.replace(/^今天 · /,'') + '　' + P.total + ' ▾</span>'
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
    /* 默认收起：一进来先看见播放器和题目，要看步骤再点开。
       以前默认展开，一整块 5 步铺满首屏，把播放器推下去 900px，
       人会以为「题还没出来」，直接点播放把整篇 6 分钟放完了。 */
    var open = (_v === '1');
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

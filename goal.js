/* ── 训练页顶部：今天这一页怎么做 ──
   每个训练页只引这一行脚本，步骤与首页 index.html 的排期保持一致，改一处改两处。
   只在训练页挂载（听力/阅读/匹配/写作/翻译），列表页与工具页不挂。 */
(function(){
  var D = new Date();
  var d0 = function(x){ return new Date(x.getFullYear(), x.getMonth(), x.getDate()); };
  var today = d0(D);
  var wd = D.getDay();
  var p = (location.pathname.split('/').pop() || '').toLowerCase();

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

  var PLANS = {
    listen: { head:'今天 · 听力新段', total:'60 分钟', tip:'做完 ③ 就交卷，解析才会解锁；④⑤ 在原文区做。', steps:[
      ['预读', '只看题干和选项，圈出关键词，先别按播放', '5′'],
      ['盲听', '原速整段听一遍，不暂停、不回头、不看文本', '7′'],
      ['听写', '逐句听写，听不清的那句直接标「—」，别猜', '20′'],
      ['归因', '对答案，每题写一句为什么错：替换词 / 连读 / 走神', '10′'],
      ['跟读', '0.85× 跟两遍，再用 1.0× 跟一遍', '15′']
    ]},
    replay: { head:'今天 · 同一段复听', total:'60 分钟', tip:'这次不换新材料，就吃这一段的「—」句。', steps:[
      ['不看书', '整段再听一遍，什么都别翻，只记哪里又卡住', '5′'],
      ['只看「—」', '只处理上次标「—」的句子，一句一句抠', '10′'],
      ['0.85× 跟读', '跟两遍，读到能一口气说完、不用想', '15′'],
      ['1.0× 跟读', '原速跟一遍，卡住就退回上一步', '15′'],
      ['重做对比', '重做一遍题，看错的换没换一批', '15′']
    ]},
    read: { head:'今天 · 仔细阅读', total:'60 分钟', tip:'②做完再对答案，③只记替换，不抄解析。', steps:[
      ['限时做', '10 题 12 分钟，不查词、不回看，做完立刻停表', '12′'],
      ['划答案句', '每题回原文划出答案那一句，别整段翻译', '8′'],
      ['记替换', '逐题抄「定位词 → 原文替换词」，只记这一对', '25′'],
      ['收 3 词', '从原文挑 3 个反复出现的词，不背单词书', '15′']
    ]},
    match: { head:'今天 · 长篇匹配', total:'60 分钟', tip:'先看题干圈人名/术语，别先读全文。', steps:[
      ['限时做', '15 分钟做完 10 题，先扫题干关键词', '15′'],
      ['找替换', '逐题回原文标出对应句，圈出替换词', '25′'],
      ['归因', '记下每题靠什么线索定位：人名 / 数字 / 同义改写', '20′']
    ]},
    write: { head:'今天 · 写作一篇', total:'60 分钟', tip:'写的时候不查词、不停笔，改留到第三步。', steps:[
      ['审题列提纲', '三段式，每段先写一句中心，别写完整句', '10′'],
      ['写', '30 分钟写完 120–140 词，不查词、不停笔', '30′'],
      ['对照改', '对照范文只改三处：开头、连接词、结尾', '20′']
    ]},
    trans: { head:'今天 · 翻译一段', total:'60 分钟', tip:'先断句再译，别一句话读三遍才动笔。', steps:[
      ['拆句', '断句、标主谓，长句拆成两句', '10′'],
      ['译', '一句一句写，不查词典，写完再回头看', '30′'],
      ['对照改', '对照参考译文，记 2 个句式和 3 个词', '20′']
    ]}
  };

  var P = PLANS[kind];
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
    +   '<span>' + P.total + ' · 距考试 ' + left + ' 天 ▾</span>'
    + '</div>'
    + '<div class="gbd">'
    +   rows
    +   '<div class="gfoot">' + P.tip + '<br><span>' + line + '</span></div>'
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
    + '#goalBox .gfoot span{color:#b0b7c3}';

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
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', mount);
  else mount();
})();

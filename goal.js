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
      ['预读选项', '圈出 5 道题里重复出现的名词、数字、人名。不查词，只圈', '5′'],
      ['盲听做题', '一遍放完，不暂停、不回放。选不出来就选最像的那个，先往下走', '7′'],
      ['逐句听写', '只写 8–10 句最难的。听不出就画「—」，绝不留空、绝不猜', '20′'],
      ['对照归因', '只看画「—」的句子，每处标一个原因：连读 / 生词 / 走神', '10′'],
      ['跟读 3 遍', '不看文本，慢半拍跟着念。重点念标出来的连读处', '15′']
    ]},
    replay: { head:'今天 · 同一段复听', total:'60 分钟', tip:'这次不换新材料，就吃这一段的漏句。', steps:[
      ['不看书再听一遍', '整段放完，边听边在心里回答：这段讲什么、分几件事。不暂停', '5′'],
      ['只看「—」的句子', '翻到周一标出来的漏句，逐句听清每个词。其余部分不看', '10′'],
      ['0.85 倍速跟读 2 遍', '不看文本，慢半拍跟着念。卡住就停在那句，倒回去再跟', '15′'],
      ['1.0 倍速跟读 1 遍', '这次要求跟上。跟丢了就从下一句接上，不许回放', '15′'],
      ['再做一遍，对比周一', '清空作答再答一遍，记下这次对几题——差多少就是复听值多少', '15′']
    ]},
    read: { head:'今天 · 仔细阅读', total:'60 分钟', tip:'②做完再对答案，③只记替换，不抄解析。', steps:[
      ['限时做', '12 分钟做完 10 题，不查词、不回看。做完立刻停表', '12′'],
      ['划答案句', '每题回原文划出答案句，别整段翻译，只找那一句', '8′'],
      ['对解析记替换', '逐题看「定位词 → 原文替换词」，只记这一对，不抄解析', '25′'],
      ['收 3 个生词', '从原文里挑 3 个反复出现的词记下来，不背单词书', '15′']
    ]},
    match: { head:'今天 · 长篇匹配', total:'60 分钟', tip:'先扫题干关键词，别先读全文。', steps:[
      ['限时做', '15 分钟，10 道题找段落。不查词，凭关键词定位，做完立刻停表', '15′'],
      ['回原文找替换', '逐题回段落里划出对应句，把「题干的词 → 原文的词」这一对写下来', '25′'],
      ['归因', '错题只写一句：是没找到定位，还是替换没认出来。二选一', '20′']
    ]},
    write: { head:'今天 · 写作一篇', total:'60 分钟', tip:'写的时候不查词、不停笔，改留到第三步。', steps:[
      ['写', '25 分钟写完，不看范文、不查词。卡住就换一句简单的话说完', '25′'],
      ['自查 3 处', '只看时态、单复数、连接词。三样各挑一处改，不改别的', '10′'],
      ['对范文改', '对完只改 3 句，不重写全篇。把范文里那个句式抄下来', '15′'],
      ['默写句式', '合上范文，把那 1 个句式默写一遍。写不出说明没记住', '10′']
    ]},
    trans: { head:'今天 · 翻译一段', total:'60 分钟', tip:'先断句再译，别一句话读三遍才动笔。', steps:[
      ['译', '25 分钟写完，不看参考、不查词典。卡住就换一句简单的话说完', '25′'],
      ['自查 3 处', '只看时态、单复数、连接词。三样各挑一处改，不改别的', '10′'],
      ['对参考改', '对完只改 3 句，不重写全篇。把参考里那个句式抄下来', '15′'],
      ['默写句式', '合上参考，把那 1 个句式默写一遍。写不出说明没记住', '10′']
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

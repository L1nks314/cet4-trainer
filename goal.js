/* ── 训练页顶部：当前阶段目标 ──
   每个训练页只引这一行脚本，阶段与达标线统一在这里维护。
   目标来源与首页 index.html 的 GOALS 保持一致，改一处改两边。 */
(function(){
  var D = new Date();
  var d0 = function(x){ return new Date(x.getFullYear(), x.getMonth(), x.getDate()); };
  var today = d0(D);
  var CALIB_END = d0(new Date(2026, 10, 8));    /* 11/2 – 11/8 校准期 */
  var EXAM_FROM = d0(new Date(2026, 10, 23));   /* 11/23 起上考场期 */
  var isCalib = today <= CALIB_END;
  var isExam  = today >= EXAM_FROM;
  var examDay = d0(new Date(2026, 11, 12));
  var left = Math.max(0, Math.round((examDay - today) / 86400000));

  var G;
  if (isCalib){
    G = { name:"校准期", range:"11/2 – 11/8",
        listen:{ goal:"先测真实水平，别管目标", now:"篇章 20%（6/30）" },
        read:  { goal:"再做 2 篇，把样本补到 20 题", now:"70%（7/10，样本小）" },
        match: { goal:"做 1 篇，把自述变成数字", now:"0 次" },
        write: { goal:"写 1 篇，看模板基础在哪档", now:"58%（8–9/15）" } };
  } else if (isExam){
    G = { name:"上考场期", range:"11/23 – 12/11",
        listen:{ goal:"整套听力连做，中途不停", now:"单段 20–25%" },
        read:  { goal:"仔细阅读 ≥85%，12 分钟/篇", now:"70%" },
        match: { goal:"长篇匹配 ≥90%，15 分钟做完", now:"0 次" },
        write: { goal:"模板默写 + 翻译 20 条句式", now:"写作 58%" } };
  } else {
    G = { name:"打底期", range:"11/9 – 11/22",
        listen:{ goal:"听力篇章 ≥5/10，且留白 ≤5 句", now:"篇章 20%（6/30）" },
        read:  { goal:"仔细阅读 ≥82%", now:"70%（7/10）" },
        match: { goal:"长篇匹配 ≥85%", now:"0 次，还没练过" },
        write: { goal:"写作进 9 分档：三段式 + 2 套模板", now:"58%（8–9/15）" } };
  }

  var p = (location.pathname.split('/').pop() || '').toLowerCase();
  var cur = 'listen';
  if (/^read-/.test(p)) cur = 'read';
  else if (/^matching-/.test(p)) cur = 'match';
  else if (/^(write|trans)-/.test(p)) cur = 'write';

  var ORDER = [['listen','听力'], ['read','阅读'], ['match','匹配'], ['write','写译']];
  var rows = ORDER.map(function(x){
    var g = G[x[0]];
    var on = (x[0] === cur) ? ' on' : '';
    return '<div class="grow'+on+'"><i>'+x[1]+'</i>'
      + '<span class="gt">'+g.goal+'</span>'
      + '<span class="gw">'+g.now+'</span></div>';
  }).join('');

  var html = '<div id="goalBox">'
    + '<div class="ghd" id="goalHd">'
    +   '<b>'+G.name+' · '+G.range+'</b>'
    +   '<span>距考试 '+left+' 天 ▾</span>'
    + '</div>'
    + '<div class="gbd">'
    +   '<div class="gsub">本阶段目标 · 现在的位置</div>'
    +   rows
    +   '<div class="gfoot">这一页的达标线在上面高亮那一行。达不到就同一段再来一遍，不要换新的。</div>'
    + '</div>'
    + '</div>';

  var css = ''
    /* 默认：普通浅色页面（阅读/匹配/写译），挂在 h1 下面 */
    + '#goalBox{margin:12px 0 16px;border:1px solid var(--line,#e5e8ec);border-radius:13px;'
    +   'background:var(--card,#fff);box-shadow:0 1px 2px rgba(16,24,40,.05);overflow:hidden}'
    + '#goalBox .ghd{display:flex;justify-content:space-between;align-items:center;gap:8px;'
    +   'padding:10px 13px;font-size:12.5px;cursor:pointer;-webkit-tap-highlight-color:transparent}'
    + '#goalBox .ghd b{font-weight:700;color:var(--txt,#1b1e23)}'
    + '#goalBox .ghd span{color:var(--sub2,#8b93a1);font-size:11.5px;white-space:nowrap}'
    + '#goalBox .gbd{padding:0 13px 12px;display:none}'
    + '#goalBox.open .gbd{display:block}'
    + '#goalBox .gsub{font-size:11px;color:var(--sub2,#8b93a1);margin:0 0 6px}'
    + '#goalBox .grow{display:flex;gap:7px;align-items:baseline;font-size:12.5px;line-height:1.62;'
    +   'color:var(--sub,#6b7280);padding:1px 0}'
    + '#goalBox .grow i{flex:0 0 34px;font-style:normal;font-weight:700;font-size:11.5px;color:var(--sub2,#8b93a1);white-space:nowrap}'
    + '#goalBox .grow .gt{flex:1;min-width:0}'
    + '#goalBox .grow .gw{flex:0 0 auto;font-size:11px;color:var(--sub2,#8b93a1);font-variant-numeric:tabular-nums;white-space:nowrap;text-align:right}'
    + '#goalBox .grow.on{color:var(--txt,#1b1e23);font-weight:700}'
    + '#goalBox .grow.on i{background:var(--blue,#2563eb);color:#fff;border-radius:5px;padding:0 3px;text-align:center}'
    + '#goalBox .gfoot{font-size:11px;color:var(--sub2,#8b93a1);margin-top:7px;line-height:1.55;'
    +   'border-top:1px solid var(--line2,#eff1f4);padding-top:7px}';

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
    var open = false;
    var _v = null;
    try{ _v = localStorage.getItem('cet4_goal_open'); }catch(e){}
    open = (_v === null) ? true : (_v === '1');   /* 第一次打开默认展开 */
    if (open) box.classList.add('open');
    document.getElementById('goalHd').addEventListener('click', function(){
      box.classList.toggle('open');
      try{ localStorage.setItem('cet4_goal_open', box.classList.contains('open') ? '1' : '0'); }catch(e){}
    });
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', mount);
  else mount();
})();

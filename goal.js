/* ── 训练页顶部：一条横幅，说清「这一页在今天这一套里的哪一步」 ──
   日课顺序只在 index.html 的 renderTasks 里定义一次，这里只做对应、不重排步骤。
   （旧版这张 5 步表写的是「C 42′ / A·B 23′ / 短版 35′」，和首页「整套 37′ 3 步」是两套
     时间表；同一天在两处看到不同的时长，比没有说明更糟。已删。） */
(function(){
  var p = (location.pathname.split('/').pop() || '').toLowerCase();
  var SEC = /sectionc\.html$/.test(p) ? 'C' : (/sectionb\.html$/.test(p) ? 'B' : 'A');
  var t = null;

  if (/section[abc]\.html$/.test(p)){
    t = {
      k: '今天 · 整套听力 · Section ' + SEC,
      r: '整卷里的第 ③ 步 · 约 10 分钟',
      d: 'A→B→C 在「整套听力」页一次连做、一次交卷，25 题一屏。<b>这一页只用来看原文、逐句精听 ' + SEC + ' 段</b>。没做整套就先去做整套——从第一句开始听，等于又变回一天一段。'
    };
  } else if (/^read-/.test(p)){
    t = {
      k: '今天副项 · 仔细阅读 1 套（两篇 10 题）',
      r: '约 25 分钟',
      d: '<b>15′ 限时做</b>（46–55，不查词、不回看）→ <b>8′ 划答案句 + 记替换</b>（每题只找那一句）→ <b>2′ 收生词</b>（最多 3 个）。'
    };
  } else if (/^matching-/.test(p)){
    t = {
      k: '今天副项 · 长篇匹配 1 篇',
      r: '约 20 分钟',
      d: '<b>15′ 限时做</b>（凭关键词定位，不读全文）→ <b>5′ 找替换 + 归因</b>（错题只写「没找到定位」或「替换没认出来」）。'
    };
  } else if (/^write-/.test(p)){
    t = {
      k: '今天副项 · 写作 1 篇',
      r: '约 25 分钟',
      d: '<b>20′ 写完</b>（不看范文、不查词）→ <b>5′ 自查 + 对参考改 3 句</b>（只看时态、单复数、连接词，不重写全篇）。'
    };
  } else if (/^trans-/.test(p)){
    t = {
      k: '今天副项 · 翻译 1 段',
      r: '约 25 分钟',
      d: '<b>20′ 译完</b>（不看参考、不查词典）→ <b>5′ 自查 + 对参考改 3 句</b>（只看时态、单复数、连接词，不重写全篇）。'
    };
  }
  if (!t) return;                          /* 非训练页不挂 */

  var css = '#goalBar{margin:10px 0 14px;padding:10px 12px;border:1px solid var(--line,#e5e8ec);'
    + 'border-left:3px solid var(--blue,#2563eb);border-radius:11px;background:var(--card,#fff);'
    + 'box-shadow:0 1px 2px rgba(16,24,40,.04)}'
    + '#goalBar .gt{display:flex;justify-content:space-between;align-items:baseline;gap:8px}'
    + '#goalBar .gt b{font-size:13px;font-weight:800;color:var(--txt,#1b1e23);line-height:1.4}'
    + '#goalBar .gt span{font-size:11.5px;color:var(--sub2,#8b93a1);white-space:nowrap;flex:0 0 auto}'
    + '#goalBar .gd{margin-top:4px;font-size:12px;color:var(--sub,#6b7280);line-height:1.7}'
    + '#goalBar .gd b{color:var(--txt2,#2b303a);font-weight:700}';

  var html = '<div id="goalBar">'
    + '<div class="gt"><b>' + t.k + '</b><span>' + t.r + '</span></div>'
    + '<div class="gd">' + t.d + '</div>'
    + '</div>';

  function mount(){
    if (document.getElementById('goalBar')) return;
    var h = document.querySelector('header') || document.querySelector('h1');
    if (!h) return;
    var st = document.createElement('style');
    st.textContent = css;
    document.head.appendChild(st);
    if (h.tagName === 'HEADER') h.insertAdjacentHTML('beforeend', html);
    else h.insertAdjacentHTML('afterend', html);
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', mount);
  else mount();
})();

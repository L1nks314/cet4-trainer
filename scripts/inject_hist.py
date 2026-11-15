"""把 hist.js 接进首页和整套页（幂等，可重复跑）。

首页：挂 trend 卡片 + 样式 + renderTrend()
整套页：交卷写一条历史 + 结果卡加一行「最近 N 次平均」
两个页面都引 hist.js?v=1，历史数据只有这一份实现。
"""
import os, re, sys

PUB = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

TREND_CSS = """/* ---------- 听力正确率（最近 6 次）---------- */
#trend .trow{display:flex;justify-content:space-between;align-items:baseline;gap:10px}
#trend .tl{font-size:13px;font-weight:700;color:var(--sub);letter-spacing:.2px}
#trend .tlk{font-size:12.5px;color:var(--blue);text-decoration:none;font-weight:600}
#trend .tbig{display:flex;align-items:baseline;gap:7px;margin:5px 0 0;flex-wrap:wrap}
#trend .tbig b{font-size:29px;font-weight:800;letter-spacing:-1.2px;line-height:1.15}
#trend .tbig span{font-size:12.5px;color:var(--sub)}
#trend .tbig em{margin-left:auto;font-style:normal;font-size:11.5px;font-weight:600;
 padding:2px 9px;border-radius:20px;background:var(--grey);color:var(--sub);white-space:nowrap}
#trend .tbars{display:flex;align-items:flex-end;gap:7px;margin:15px 0 4px}
#trend .tb{flex:1;display:flex;flex-direction:column;align-items:center;justify-content:flex-end;
 gap:4px;min-width:0}
#trend .tn{font-size:11.5px;font-weight:700;color:var(--sub)}
#trend .tb i{display:block;width:100%;max-width:30px;border-radius:6px 6px 3px 3px;
 background:var(--track);opacity:.42}
#trend .tb i.bred{background:var(--red)}
#trend .tb i.bamber{background:var(--amber)}
#trend .tb i.bgreen{background:var(--green)}
#trend .tb i.now{opacity:1}
#trend .td2{font-size:10.5px;color:var(--sub2);white-space:nowrap;overflow:hidden;
 text-overflow:ellipsis;max-width:100%}
#trend .tcol{display:flex;gap:8px;margin:12px 0 0}
#trend .tcell{flex:1;background:var(--soft);border:1px solid var(--line2);border-radius:10px;
 padding:7px 3px;text-align:center}
#trend .tcell span{display:block;font-size:10.5px;color:var(--sub2)}
#trend .tcell b{display:block;font-size:14.5px;font-weight:800;margin-top:1px}
#trend .tcell em{display:block;font-style:normal;font-size:10px;color:var(--sub2);margin-top:1px}
#trend .tft{margin:11px 0 0;font-size:12.5px;line-height:1.75;color:var(--sub)}
#trend .tft b{color:var(--txt2)}
#trend .tft a{color:var(--blue);text-decoration:none;font-weight:600}
"""

TREND_JS = r"""
/* ---------- 听力正确率（数据在 hist.js）----------
   只读 CET4HIST，不在首页算存档；没有记录就整卡不显示。 */
function renderTrend(){
  var el = document.getElementById('trend'); if (!el) return;
  if (!window.CET4HIST){ el.style.display = 'none'; return; }
  var a = CET4HIST.read();
  if (!a.length){ el.style.display = 'none'; return; }

  function tot(x){ return x.v[0] + x.v[1] + x.v[2]; }
  function lvl(n){ return n >= 20 ? 'green' : (n >= 15 ? 'amber' : 'red'); }
  function tag(s){ return s.replace(/^\d{4}-/, '').replace('-', '/'); }

  var last = a.slice(-6), cur = a[a.length - 1], i;
  var h = '<div class="trow"><span class="tl">听力整套 · 最近 ' + last.length + ' 次</span>'
        + '<a class="tlk" href="listen-set.html">再练一套 ›</a></div>'
        + '<div class="tbig"><b style="color:var(--' + lvl(tot(cur)) + ')">' + tot(cur) + '</b>'
        + '<span>/25 · ' + Math.round(tot(cur) / 25 * 100) + '%</span>'
        + '<em>' + tag(cur.s) + '</em></div>';

  if (last.length > 1){
    h += '<div class="tbars">';
    last.forEach(function(x, k){
      var n = tot(x), hh = 8 + Math.round(n / 25 * 44);
      h += '<div class="tb"><span class="tn">' + n + '</span>'
         + '<i class="b' + lvl(n) + (k === last.length - 1 ? ' now' : '') + '" style="height:' + hh + 'px"></i>'
         + '<span class="td2">' + tag(x.s) + '</span></div>';
    });
    h += '</div>';
  }

  var seg = last.slice(-5), n = seg.length, sum = [0, 0, 0], all = 0;
  seg.forEach(function(x){ for (var j = 0; j < 3; j++) sum[j] += x.v[j]; all += tot(x); });
  var den = [7, 8, 10], pc = [0, 1, 2].map(function(j){ return Math.round(sum[j] / (n * den[j]) * 100); });
  var names = ['A 短篇新闻', 'B 长对话', 'C 短文'];

  h += '<div class="tcol">';
  [0, 1, 2].forEach(function(j){
    h += '<div class="tcell"><span>Section ' + 'ABC'[j] + '</span><b>' + pc[j] + '%</b>'
       + '<em>' + sum[j] + '/' + (n * den[j]) + '</em></div>';
  });
  h += '</div>';

  var wi = 0;
  for (i = 1; i < 3; i++) if (pc[i] < pc[wi]) wi = i;
  h += '<p class="tft">近 ' + n + ' 次平均 <b>' + (all / n).toFixed(1) + '/25</b>';
  if (a.length > 1){
    var d = tot(cur) - tot(a[a.length - 2]);
    h += ' · 比上一次 <b>' + (d > 0 ? '+' : '') + d + '</b>';
  }
  if (n >= 2){
    h += '<br>短板 <b>' + names[wi] + '</b>（近 ' + n + ' 次 ' + sum[wi] + '/' + (n * den[wi]) + '）'
       + ' · <a href="' + cur.s + '_Section' + 'ABC'[wi] + '.html?jt=1&st=3">精听 3 句 ›</a>';
  }
  h += '</p>';

  el.innerHTML = h;
  el.style.display = '';
}

if (window.CET4HIST){
  CET4HIST.sync().then(function(){ renderTrend(); });
}
"""


def patch_index(p):
    h = open(p, encoding='utf-8').read()
    n = 0

    if 'hist.js?v=1' not in h:
        old = '<script>\nvar START = new Date(2026,10,2);'
        assert old in h, 'index: 脚本锚点丢了'
        h = h.replace(old, '<script src="hist.js?v=1"></script>\n' + old, 1)
        n += 1

    if 'id="trend"' not in h:
        old = '<div class="card" id="tasks"></div>'
        assert old in h, 'index: tasks 卡片锚点丢了'
        h = h.replace(old, old + '\n<div class="card" id="trend" style="display:none"></div>', 1)
        n += 1

    if '#trend .trow' not in h:
        i = h.index('</style>')
        h = h[:i] + TREND_CSS + h[i:]
        n += 1

    if 'function renderTrend' not in h:
        old = '/* ── 全部训练清单 ── */'
        assert old in h, 'index: 函数插入点丢了'
        h = h.replace(old, TREND_JS.strip() + '\n\n' + old, 1)
        n += 1

    if 'renderTrend();\n' not in h or h.count('renderTrend();') < 2:
        old = 'renderHead();\nrenderTasks();\nrenderList();'
        assert old in h, 'index: 启动块锚点丢了'
        h = h.replace(old, old + '\nrenderTrend();\n'
                      'if (window.CET4HIST) CET4HIST.sync().then(function(){ renderTrend(); });', 1)
        n += 1

    open(p, 'w', encoding='utf-8').write(h)
    return n


HIST_LINE_JS = '''
/* 结果卡里的历史一行：只读 hist.js，没有记录就不显示 */
function histLine(){
  if (!window.CET4HIST) return '';
  var a = CET4HIST.read();
  if (a.length < 2) return '';
  var seg = a.slice(-5), n = seg.length, all = 0;
  seg.forEach(function(x){ all += x.v[0] + x.v[1] + x.v[2]; });
  var d = all / n, cur = a[a.length - 1], prev = a[a.length - 2];
  var dv = (cur.v[0] + cur.v[1] + cur.v[2]) - (prev.v[0] + prev.v[1] + prev.v[2]);
  return '<p class="dim" style="margin:9px 0 0">第 <b>' + a.length + '</b> 次整套听力'
    + ' · 近 ' + n + ' 次平均 <b>' + d.toFixed(1) + '/25</b>'
    + ' · 比上一次 <b>' + (dv > 0 ? '+' : '') + dv + '</b></p>';
}
'''


def patch_listen_set(p):
    h = open(p, encoding='utf-8').read()
    n = 0

    if 'hist.js?v=1' not in h:
        old = "<script>\n(function(){\n'use strict';\n\n/* ===== 整套听力连做 ====="
        assert old in h, 'listen-set: 主脚本锚点丢了'
        h = h.replace(old, '<script src="hist.js?v=1"></script>\n' + old, 1)
        n += 1

    if 'function histLine' not in h:
        old = 'function ls(k, v){'
        assert old in h, 'listen-set: ls 锚点丢了'
        h = h.replace(old, HIST_LINE_JS.strip() + '\n' + old, 1)
        n += 1

    if 'CET4HIST.add(' not in h:
        old = """  ls('cet4_set_' + SID, JSON.stringify({
    d: todayStr(), score: score, a: per, ts: Date.now(),
    used: T0 ? Math.round((Date.now() - T0) / 1000) : 0
  }));"""
        assert old in h, 'listen-set: 成绩写入锚点丢了'
        new = old + """
  /* 成绩存档：同一份数据进历史，首页据此画正确率（hist.js） */
  if (window.CET4HIST){
    CET4HIST.add({d: todayStr(), s: SID, v: per,
      u: T0 ? Math.round((Date.now() - T0) / 1000) : 0, ts: Date.now()});
  }"""
        h = h.replace(old, new, 1)
        n += 1

    if "+ histLine()" not in h:
        old = """    + '<p class="lead">' + tip + '</p>';"""
        assert old in h, 'listen-set: 结果卡锚点丢了'
        h = h.replace(old, """    + '<p class="lead">' + tip + '</p>'
    + histLine();""", 1)
        n += 1

    open(p, 'w', encoding='utf-8').write(h)
    return n


if __name__ == '__main__':
    out = []
    out.append(('index.html', patch_index(os.path.join(PUB, 'index.html'))))
    out.append(('listen-set.html', patch_listen_set(os.path.join(PUB, 'listen-set.html'))))
    for f, c in out:
        print(f, 'patched', c)

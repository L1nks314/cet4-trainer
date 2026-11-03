#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""给 98 个带 penv11 笔迹的页面注入「笔迹随页保存（当天有效）」"""
import glob, io, os, re, sys

INK_MODULE = r"""
  /* ── 笔迹随页保存：同一页当天有效，刷新/重开不丢 ── */
  var INK_KEY = 'cet4ink:v1:' + (location.pathname.split('/').pop() || 'x');
  var INK_DAY = (function(){ var t = new Date();
    return t.getFullYear() + '-' + ('0'+(t.getMonth()+1)).slice(-2) + '-' + ('0'+t.getDate()).slice(-2); })();
  var INK_COL = ['#1b1e23', '#c0392b', '#2563eb', '#0f9d58', '#d97706'];
  var inkT = 0;

  function pathOf(el){
    var out = [];
    while (el && el.parentElement && el !== document.body){
      var i = 0, c = el;
      while ((c = c.previousElementSibling)) if (c.tagName === el.tagName) i++;
      out.unshift(el.tagName.toLowerCase() + ':' + i);
      el = el.parentElement;
    }
    return out.join('/');
  }
  function byPath(p){
    if (!p) return null;
    var el = document.body, parts = p.split('/');
    for (var i = 0; i < parts.length; i++){
      var m = /^([a-z0-9]+):(\d+)$/.exec(parts[i]);
      if (!m || !el) return null;
      var tag = m[1].toUpperCase(), idx = +m[2], n = 0, f = null, kids = el.children;
      for (var k = 0; k < kids.length; k++) if (kids[k].tagName === tag){ if (n === idx){ f = kids[k]; break; } n++; }
      if (!f) return null;
      el = f;
    }
    return el;
  }
  function inkText(el){
    var t = (el.textContent || '').replace(/\s+/g, ' ').trim();
    return t.slice(0, 18);
  }
  function inkFind(r){
    var el = byPath(r.a);
    if (el && (!r.f || inkText(el).indexOf(r.f) === 0 || r.f.indexOf(inkText(el).slice(0, 8)) === 0)) return el;
    if (r.f){                       /* 结构变了：按文本前 18 字在候选锚里找回 */
      var cand = document.querySelectorAll(ANCH_SEL);
      for (var i = 0; i < cand.length; i++){
        if (inkText(cand[i]).indexOf(r.f) === 0) return cand[i];
      }
    }
    return el || null;
  }
  function b64(buf){
    var s = '', CH = 0x8000;
    for (var i = 0; i < buf.length; i += CH) s += String.fromCharCode.apply(null, buf.subarray(i, i + CH));
    return btoa(s);
  }
  function unb64(str){
    var bin = atob(str), n = bin.length, u = new Uint8Array(n);
    for (var i = 0; i < n; i++) u[i] = bin.charCodeAt(i);
    return u;
  }
  /* 点串：首点 x(uint16) y(int16，相对锚顶) w(uint8)；其后 dx,dy(int8) w(uint8)
     相邻点先按 80px 插值补点，保证 delta 落在 int8 内不漂移 */
  function encPts(s){
    var pts = s.pts, y0 = s.anch ? s.anch.y0 : 0, raw = [], prev = null;
    for (var i = 0; i < pts.length; i++){
      var p = pts[i];
      if (prev){
        var ddx = p[0] - prev[0], ddy = p[1] - prev[1];
        var st = Math.ceil(Math.max(Math.abs(ddx), Math.abs(ddy)) / 80);
        for (var k = 1; k < st; k++) raw.push([prev[0] + ddx*k/st, prev[1] + ddy*k/st, p[2]]);
      }
      raw.push([p[0], p[1], p[2]]); prev = p;
    }
    var out = [], px = 0, py = 0;
    for (var j = 0; j < raw.length; j++){
      var q = raw[j];
      var x = Math.max(0, Math.min(65535, Math.round(q[0])));
      var y = Math.max(-32768, Math.min(32767, Math.round(q[1] - y0)));
      var w = Math.max(1, Math.min(15, Math.round(q[2] * 2)));
      if (j === 0){ out.push(x & 255, (x >> 8) & 255, y & 255, (y >> 8) & 255, w); px = x; py = y; }
      else {
        var dx = Math.max(-127, Math.min(127, x - px)), dy = Math.max(-127, Math.min(127, y - py));
        out.push(dx & 255, dy & 255, w); px += dx; py += dy;
      }
    }
    return b64(new Uint8Array(out));
  }
  function decPts(str, y0){
    var u, n, pts = [];
    try{ u = unb64(str); }catch(e){ return pts; }
    n = u.length; if (n < 5) return pts;
    var x = (u[1] << 8) | u[0];
    var y = (u[3] << 8) | u[2]; if (y & 0x8000) y -= 0x10000;
    pts.push([x, y + y0, u[4] / 2]);
    var i = 5;
    while (i + 2 < n){
      var dx = u[i], dy = u[i+1];
      if (dx > 127) dx -= 256; if (dy > 127) dy -= 256;
      x += dx; y += dy;
      pts.push([x, y + y0, u[i+2] / 2]);
      i += 3;
    }
    return pts;
  }
  function inkSave(){
    if (!strokes.length){ try{ localStorage.removeItem(INK_KEY); }catch(e){} return; }
    var arr = [];
    for (var i = 0; i < strokes.length; i++){
      var s = strokes[i];
      if (!s || !s.pts || !s.pts.length) continue;
      var el = (s.anch && s.anch.el) || s.host;
      if (!el) continue;
      arr.push({ a: pathOf(el), f: inkText(el), d: Math.round(s.pts[0][1] - (s.anch ? s.anch.y0 : 0)),
                 e: s.era ? 1 : 0, c: Math.max(0, INK_COL.indexOf(s.color)),
                 cp: s.c ? pathOf(s.c) : '', p: encPts(s) });
    }
    if (!arr.length) return;
    var payload = JSON.stringify({ v: 1, day: INK_DAY, n: arr.length, s: arr });
    try{ localStorage.setItem(INK_KEY, payload); }catch(e){}
  }
  function inkQueue(){ if (inkT) clearTimeout(inkT); inkT = setTimeout(function(){ inkT = 0; inkSave(); }, 250); }
  function inkFlush(){ if (inkT){ clearTimeout(inkT); inkT = 0; } inkSave(); }
  function inkLoad(){
    var raw = null;
    try{ raw = localStorage.getItem(INK_KEY); }catch(e){}
    if (!raw) return;
    var d = null;
    try{ d = JSON.parse(raw); }catch(e){}
    if (!d || d.v !== 1 || !d.s || !d.s.length) return;
    if (d.day !== INK_DAY){ try{ localStorage.removeItem(INK_KEY); }catch(e){} return; }  /* 只留当天 */
    var got = 0;
    for (var i = 0; i < d.s.length; i++){
      var r = d.s[i], el = inkFind(r);
      if (!el) continue;
      var vis = anchVis(el);
      var y0 = vis ? docTopOf(el) : 0;
      var pts = decPts(r.p, y0);
      if (!pts.length) continue;
      var c = r.cp ? byPath(r.cp) : null;
      var s = { pts: pts, color: INK_COL[r.c] || '#1b1e23', era: !!r.e,
                c: c, c0: c ? c.scrollTop : 0,
                host: el.closest('.panel') || el.closest('.card'),
                n: pts.length, mid: [0, 0], bb: null,
                anch: { el: el, y0: y0 } };
      if (!vis) s.needBase = true;
      if (s.era) hasEra = true;
      s.bb = bboxOf(s);
      strokes.push(s); got++;
    }
    if (got) schedule(true);
  }
"""

HOOK_UP = """      var done = cur;
      if (done) done.bb = bboxOf(done);"""
HOOK_UP_NEW = """      var done = cur;
      if (done) done.bb = bboxOf(done);
      inkQueue();                        /* 收笔即落盘（合并 250ms），刷新不丢 */"""

OLD_CLR = """  if (clr) clr.addEventListener('click', function(){
    strokes = []; hasEra = false; cur = null; drawing = false;"""
NEW_CLR = """  if (clr) clr.addEventListener('click', function(){
    if (strokes.length && !confirm('清空本页全部笔迹？')) return;
    strokes = []; hasEra = false; cur = null; drawing = false;
    try{ localStorage.removeItem(INK_KEY); }catch(e){}"""

OLD_TAIL = """      schedule(true);                    /* 收笔后统一重绘一次，保证最终形态完整 */
    }, {capture:true});
  });
})();"""
NEW_TAIL = """      schedule(true);                    /* 收笔后统一重绘一次，保证最终形态完整 */
    }, {capture:true});
  });

  inkLoad();                             /* 页面打开即还原当天笔迹 */
  schedule(true);
  window.addEventListener('pagehide', inkFlush);
  document.addEventListener('visibilitychange', function(){
    if (document.visibilityState === 'hidden') inkFlush();
  });
})();"""

OLD_VAR = "  var strokes = [], cur = null, SC = [];"
NEW_VAR = None  # 动态拼接：变量行 + 模块

ANCH_SHIFT_OLD = """  function anchorShift(s){
    if (!anchVis(s.anch.el)) return 0;
    return docTopOf(s.anch.el) - s.anch.y0;
  }"""
ANCH_SHIFT_NEW = """  function anchorShift(s){
    /* 恢复时锚在隐藏 tab 里定不了基准，等它可见再一次性补正 */
    if (s.needBase){
      if (!anchVis(s.anch.el)) return 0;
      var t0 = docTopOf(s.anch.el);
      for (var i = 0; i < s.pts.length; i++) s.pts[i][1] += t0 - s.anch.y0;
      s.anch.y0 = t0; s.needBase = false; s.bb = bboxOf(s);
    }
    if (!anchVis(s.anch.el)) return 0;
    return docTopOf(s.anch.el) - s.anch.y0;
  }"""

OLD_RST = "    if (!confirm('清空本套作答，重新做一遍？')) return;"
NEW_RST = """    if (!confirm('清空本套作答，重新做一遍？')) return;
    try{ localStorage.removeItem('cet4ink:v1:' + FILE); }catch(e){}"""


def sub1(txt, old, new, name):
    n = txt.count(old)
    if n != 1:
        raise SystemExit('%s: 命中 %d 次（应为 1）' % (name, n))
    return txt.replace(old, new)


def main():
    files = sorted(glob.glob('*.html'))
    done = 0
    for p in files:
        s = open(p, encoding='utf-8').read()
        if '/* penv11 */' not in s or 'cet4ink:v1' in s:
            continue
        s = sub1(s, OLD_VAR, OLD_VAR + INK_MODULE, p + ':var')
        s = sub1(s, ANCH_SHIFT_OLD, ANCH_SHIFT_NEW, p + ':anch')
        s = sub1(s, HOOK_UP, HOOK_UP_NEW, p + ':up')
        s = sub1(s, OLD_CLR, NEW_CLR, p + ':clr')
        s = sub1(s, OLD_TAIL, NEW_TAIL, p + ':tail')
        if OLD_RST in s:
            s = sub1(s, OLD_RST, NEW_RST, p + ':rst')
        open(p, 'w', encoding='utf-8').write(s)
        done += 1
    print('注入页面数', done)


if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    main()

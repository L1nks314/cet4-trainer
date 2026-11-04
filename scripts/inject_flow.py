#!/usr/bin/env python3
# 给 39 个听力页装「单线推进条」：页内就能看到现在第几步，做完一步自动回传首页
import glob, sys, re

BAR = r'''<script>
/* ── 单线推进条：和首页同一套步骤，做完一步自动回传 ── */
(function(){
  var FILE = (location.pathname.split('/').pop() || '');
  if (!/_Section/i.test(FILE)) return;
  var SEC = /SectionC/i.test(FILE) ? 'C' : (/SectionB/i.test(FILE) ? 'B' : 'A');

  function ymd(){
    var d = new Date();
    return d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0');
  }
  function tier(){ try{ return localStorage.getItem('cet4_tier_' + ymd()) || ''; }catch(e){ return ''; } }
  function isShort(){ var t = tier(); return (t === 'std' || t === 'min'); }
  function get(){ try{ return JSON.parse(localStorage.getItem('cet4_steps_' + ymd()) || '{}') || {}; }catch(e){ return {}; } }
  function set(k){
    try{
      var o = get(); o[k] = 1;
      localStorage.setItem('cet4_steps_' + ymd(), JSON.stringify(o));
    }catch(e){}
  }

  function list(){
    var sh = isShort();
    var whyK = (SEC === 'C') ? 's5' : 's4';
    var shK  = (SEC === 'C') ? 's6' : 's5';
    var arr = [
      { k:'s1', t:'横看竖看选项', where:'本页上方' },
      { k:'s2', t:'盲听做题 + 交卷', where:'本页做题区' },
      { k:'s3', t: sh ? '听写 2 句' : '听写 3 句', where:'本页听写清单' }
    ];
    if (SEC === 'C') arr.push({ k:'s4', t: sh ? '音义闪卡 12 词' : '音义闪卡 20 词', where:'闪卡页', go:'soundcard.html?p=' + encodeURIComponent(FILE) + '&n=' + (sh ? 12 : 20) + '&k=s4' });
    arr.push({ k: whyK, t:'对照归因', where:'本页判分区' });
    if (!sh) arr.push({ k: shK, t:'跟读 + 复述', where:'跟读页', go:'shadow.html?p=' + encodeURIComponent(FILE) + '&k=' + shK });
    return arr;
  }

  var box = document.createElement('div');
  box.id = 'flowbar';
  box.innerHTML = '<style>'
    + '#flowbar{position:fixed;left:0;right:0;bottom:0;z-index:80;display:flex;align-items:center;gap:10px;'
    + ' padding:9px 12px calc(9px + env(safe-area-inset-bottom));background:rgba(255,255,255,.97);'
    + ' border-top:1px solid #e5e8ec;box-shadow:0 -2px 10px rgba(16,24,40,.06);'
    + ' font:400 13px/1.4 -apple-system,"PingFang SC","Microsoft YaHei",sans-serif}'
    + '#flowbar .fb{flex:1;min-width:0;color:#6b7280;font-size:12px}'
    + '#flowbar .fb b{display:block;color:#1b1e23;font-size:13.5px;font-weight:700;margin-bottom:1px}'
    + '#flowbar button{border:0;border-radius:10px;padding:10px 15px;background:#2563eb;color:#fff;'
    + ' font:700 13.5px/1.2 inherit;white-space:nowrap}'
    + '#flowbar button.dim{background:#e8ebef;color:#6b7280}'
    + '#flowbar .x{border:0;background:transparent;color:#c3c8d0;font-size:18px;padding:4px 6px;border-radius:8px}'
    + 'body{padding-bottom:80px}'
    /* 底部原有浮动件整体上移，别和进度条抢同一块地方 */
    + '#dictBar{bottom:calc(84px + env(safe-area-inset-bottom)) !important}'
    + '#cloudBar{bottom:calc(146px + env(safe-area-inset-bottom)) !important}'
    + '#ansReset{bottom:calc(146px + env(safe-area-inset-bottom)) !important}'
    + '.segtoast{bottom:calc(84px + env(safe-area-inset-bottom)) !important}'
    + '</style>'
    + '<div class="fb" id="fbTxt"></div>'
    + '<button id="fbGo">做完了 →</button>'
    + '<button class="x" id="fbX" title="收起">×</button>';
  document.body.appendChild(box);

  var elTxt = box.querySelector('#fbTxt'), bGo = box.querySelector('#fbGo'), bX = box.querySelector('#fbX');
  var cur = -1;

  function paint(){
    var L = list(), st = get(), i;
    for (i = 0; i < L.length; i++){ if (!st[L[i].k]){ cur = i; break; } }
    if (i >= L.length){ cur = -1; }
    document.title = document.title.replace(/^\(\d\/\d\)\s*/, '');
    if (cur < 0){
      elTxt.innerHTML = '<b>今天的步骤都走完了</b>回首页看明天';
      bGo.textContent = '回首页';
      bGo.className = '';
      return;
    }
    var s = L[cur];
    elTxt.innerHTML = '<b>第 ' + (cur + 1) + ' / ' + L.length + ' 步 · ' + s.t + '</b>' + s.where;
    bGo.textContent = s.go ? (s.k.indexOf('s4') === 0 ? '去闪卡 →' : '去跟读 →') : '做完了 →';
    bGo.className = '';
  }

  bGo.addEventListener('click', function(){
    var L = list();
    if (cur < 0){ location.href = 'index.html'; return; }
    var s = L[cur];
    if (s.go){ location.href = s.go; return; }
    set(s.k);
    if (cur + 1 >= L.length){ location.href = 'index.html?done=1'; return; }
    paint();
    if (window.__whyOpen && s.k === (SEC === 'C' ? 's5' : 's4')){
      try{ window.__whyOpen(); }catch(e){}
    }
  });

  bX.addEventListener('click', function(){ box.style.display = 'none'; document.body.style.paddingBottom = ''; });

  window.__flowSet = function(k){
    if (!k) return;
    /* 在这一页动过任何一步，就把「今天做这段」钉住，免得首页按历史记录换段 */
    try{
      var cs = JSON.parse(localStorage.getItem('cet4_curseg') || 'null');
      var h1 = document.querySelector('h1');
      var dn = (h1 && h1.textContent ? h1.textContent : document.title).replace(/\s+/g, ' ').trim().slice(0, 40);
      localStorage.setItem('cet4_curseg', JSON.stringify({ f: FILE, d: dn, wk: (cs && cs.wk !== undefined) ? cs.wk : 0 }));
    }catch(e){}
    var L = list(), i;
    /* 交卷/听写发生在某个环节，说明前面的环节已经走过：一并勾上，条子才不会倒退 */
    for (i = 0; i < L.length; i++){ set(L[i].k); if (L[i].k === k) break; }
    paint();
  };
  window.__flowStepKey = function(kind){
    if (kind === 'ans') return 's2';
    if (kind === 'dict') return 's3';
    if (kind === 'why') return (SEC === 'C') ? 's5' : 's4';
    return '';
  };
  paint();
  setTimeout(paint, 400);
})();
</script>
</body>'''

TAIL = '</body>'

def main():
    files = sorted(glob.glob('*_Section*.html'))
    ok = 0
    for f in files:
        s = open(f, encoding='utf-8').read()
        if 'id="flowbar"' in s or 'ID_FLOWBAR' in s:
            print('SKIP', f); continue
        if s.count(TAIL) != 1:
            print('TAIL-MISS', f, s.count(TAIL)); continue
        s = s.replace(TAIL, BAR, 1)

        # 交卷即完成第 ② 步
        old = "    submitted = true;\n"
        new = "    submitted = true;\n    try{ window.__flowSet && window.__flowSet(window.__flowStepKey('ans')); }catch(e){}\n"
        if s.count(old) == 1:
            s = s.replace(old, new, 1)
        else:
            print('ANS-MISS', f, s.count(old))

        # 记下今天该听写的句子，供跟读页复用
        old2 = "    function paintPicks(){"
        new2 = ("    function paintPicks(){\n"
                "      try{ localStorage.setItem('cet4_pick_' + FILE, JSON.stringify(picks)); }catch(e){}\n")
        if s.count(old2) == 1:
            s = s.replace(old2, new2, 1)
        else:
            print('PICK-MISS', f, s.count(old2))

        open(f, 'w', encoding='utf-8').write(s)
        ok += 1
    print('注入完成', ok, '/', len(files))

if __name__ == '__main__':
    main()

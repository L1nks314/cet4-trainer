"""阅读页判分联动注入：错题原地展开已有解析 + 点「定位」在原文句级高亮。

内容不重写——解析 DOM 本来就在 #pN-ana 里，这里只做搬运和联动。
幂等：重复跑会先删掉旧的 READ_ANA_V1 段再写入。
"""
import re
import sys
import glob
import os

PUB = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
S, E = '<!-- READ_ANA_V1_START -->', '<!-- READ_ANA_V1_END -->'

# ── 1) CSS ─────────────────────────────────────────────
CSS = """
/* READ_ANA_V1 阅读解析联动 */
.rmark{font-size:12px;font-weight:700;padding:2px 8px;border-radius:20px;white-space:nowrap}
.rmark.ok{background:var(--green-soft);color:var(--green)}
.rmark.bad{background:var(--red-soft);color:var(--red)}
.anainline{margin:-4px 0 14px}
.anainline .ana{margin:0}
.anainline .ac{font-size:0}
.anainline .ac::before{content:'展开解析';font-size:12.5px}
.anainline.ana[open] .ac::before{content:'收起'}
.amethod{margin:0 0 11px;border:1px dashed var(--line);border-radius:9px;padding:0 10px 2px}
.amethod>summary{padding:8px 0;font-size:12.5px;line-height:1.5;color:var(--sub);cursor:pointer;list-style:none}
.amethod>summary::-webkit-details-marker{display:none}
.amethod>summary::before{content:'▸  ';color:var(--sub2)}
.amethod[open]>summary::before{content:'▾  '}
.amethod .arow{margin:0 0 10px}
.anasect-hint{margin:0 0 10px;padding:8px 10px;font-size:12.5px;line-height:1.6;
  color:var(--blue);background:var(--blue-soft);border-radius:9px}
::highlight(cet4loc){background:#ffe58a;color:#3a2b00}
@media (prefers-color-scheme:dark){::highlight(cet4loc){background:#b8860b;color:#fff}}
"""

# ── 2) JS ──────────────────────────────────────────────
JS = r"""
/* READ_ANA_V1：判分后把解析搬到题下；点定位在原文里高亮那一句 */
(function(){
  var HL = 'cet4loc';

  // 在段落里把指定英文短句高亮（CSS Custom Highlight，不改 DOM，不影响画笔/复制）
  function markSentence(para, sent){
    if (!window.CSS || !CSS.highlights || !sent) return;
    var p = para.querySelector('p.en') || para;
    if (!p) return;
    var walker = document.createTreeWalker(p, NodeFilter.SHOW_TEXT, null);
    var nodes = [], full = '', n;
    while ((n = walker.nextNode())){ nodes.push({n:n, s:full.length}); full += n.nodeValue; }
    var key = sent.slice(0, 26).replace(/\s+/g,' ');
    var idx = full.indexOf(key);
    if (idx < 0){
      // 退一步：用最长的一段词去匹配
      var words = key.split(' ');
      for (var w = 0; w < 3 && idx < 0; w++){
        key = words.slice(w, w + 4).join(' ');
        if (key.length > 12) idx = full.indexOf(key);
      }
    }
    if (idx < 0){ try{ CSS.highlights.delete(HL); }catch(e){} return; }
    var end = Math.min(idx + sent.length, full.length);
    function at(pos){
      for (var k = 0; k < nodes.length; k++){
        var o = nodes[k];
        if (pos <= o.s + o.n.nodeValue.length) return {node:o.n, off:pos - o.s};
      }
      var last = nodes[nodes.length-1];
      return {node:last.n, off:last.n.nodeValue.length};
    }
    try{
      var a = at(idx), b = at(end);
      var r = document.createRange();
      r.setStart(a.node, Math.max(0, a.off));
      r.setEnd(b.node, Math.max(0, b.off));
      CSS.highlights.set(HL, new Highlight(r));
    }catch(e){}
  }

  // 取某题解析里的定位句
  function locOf(qnum){
    var d = document.querySelector('.panel[id$="-ana"] details.ana[data-q="' + qnum + '"]');
    if (!d) return null;
    var len = d.querySelector('.len');
    return len ? len.textContent.trim() : null;
  }

  window.__readAnaAttach = function(box){
    var panel = box.querySelector('.panel[id$="-ana"]');
    if (!panel) return;
    // 清掉上一次的（重做后再交卷）
    Array.prototype.slice.call(document.querySelectorAll('.anainline')).forEach(function(x){
      if (x.parentNode) x.parentNode.removeChild(x);
    });

    var wrong = 0, total = 0;
    box.querySelectorAll('.q').forEach(function(qd){
      var q = qd.dataset.q;
      var src = panel.querySelector('details.ana[data-q="' + q + '"]');
      if (!src) return;
      total++;
      var hit = qd.querySelector('.opt.right[data-pick="1"]');   // 正确项且是自己选的
      var miss = qd.querySelector('.opt.wrong');                  // 自己选错的那项
      var right = !!hit;
      var myKey = miss ? miss.dataset.k : (hit ? hit.dataset.k : '');
      var d = src.cloneNode(true);
      d.classList.add('anainline');
      d.removeAttribute('open');
      d.setAttribute('data-q', q);
      if (!right){ d.setAttribute('open',''); wrong++; }

      // 纠错优先：判型/拆句是方法论，折起来，让定位和错因一屏可见
      var mrows = [];
      Array.prototype.slice.call(d.querySelectorAll('.abody > .arow')).forEach(function(r){
        var tg = r.querySelector('.atag');
        if (tg && (tg.textContent.trim() === '判型' || tg.textContent.trim() === '拆句')) mrows.push(r);
      });
      if (mrows.length){
        var mb = document.createElement('details');
        mb.className = 'amethod';
        var ms = document.createElement('summary');
        ms.textContent = '这题怎么判、怎么拆（方法论）';
        mb.appendChild(ms);
        mrows[0].parentNode.insertBefore(mb, mrows[0]);
        mrows.forEach(function(r){ mb.appendChild(r); });
      }

      var sum = d.querySelector('summary');
      var tag = document.createElement('span');
      tag.className = 'rmark ' + (right ? 'ok' : 'bad');
      tag.textContent = right ? '✓ 选对' : ('✗ 你选 ' + (myKey || '空'));
      var ac = sum.querySelector('.ac');
      if (ac) sum.insertBefore(tag, ac); else sum.appendChild(tag);

      qd.parentNode.insertBefore(d, qd.nextSibling);
    });

    // 解析 tab 顶部加一句：错题已经搬下去了
    var hint = panel.querySelector('.anasect-hint');
    if (!hint){
      hint = document.createElement('p');
      hint.className = 'anasect-hint';
      panel.insertBefore(hint, panel.firstChild);
    }
    hint.textContent = '判分后，错题解析已直接显示在题目下方（' + wrong + ' 题错）。这里保留全量解析，方便按顺序回看。';

    var sc = box.querySelector('.score');
    if (sc && wrong){
      var s = document.createElement('span');
      s.className = 'score-jump';
      s.textContent = ' ↓ 错题已展开解析';
      sc.appendChild(s);
    }
  };

  // 点「定位 P#」：跳段之后，再把那句高亮出来
  document.querySelectorAll('.jump').forEach(function(b){
    b.addEventListener('click', function(){
      var qnum = b.dataset.qnum, go = b.dataset.go;
      if (!qnum || !go) return;
      var para = document.getElementById(go);
      if (!para) return;
      var sent = locOf(qnum);
      if (sent) markSentence(para, sent);
    });
  });
})();
"""

SNIP = '\n%s\n<style>%s</style>\n<script>%s</script>\n%s\n' % (S, CSS, JS, E)


def strip(h):
    return re.sub(r'\n*' + re.escape(S) + r'.*?' + re.escape(E) + r'\n*', '\n', h, flags=re.S)


def patch(path):
    h = open(path, encoding='utf-8').read()
    if 'READ_ANA_V1_START' in h:
        h = strip(h)
    # 判分末尾调用
    old = "    sc.style.color = right/total >= 0.6 ? 'var(--green)' : 'var(--red)';"
    if old not in h:
        return 'skip(no anchor): ' + path
    if '__readAnaAttach' not in h:
        h = h.replace(old, old + "\n    if (window.__readAnaAttach) window.__readAnaAttach(box);", 1)
    # 注入块放 </body> 前
    h = h.replace('</body>', SNIP + '</body>', 1)
    open(path, 'w', encoding='utf-8').write(h)
    return 'ok: ' + path


if __name__ == '__main__':
    files = sys.argv[1:] or sorted(glob.glob(os.path.join(PUB, 'read-*.html')))
    for f in files:
        if not os.path.isabs(f):
            f = os.path.join(PUB, f)
        print(patch(f))

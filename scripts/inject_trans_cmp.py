"""翻译页：交卷后逐句比对采分点 + 15 分制估算。

数据在 explain/trans.js（scripts/gen_trans_pts.py 生成）。
匹配规则与 scripts/check_trans_pts.py 完全一致：小写、去标点、按词前缀匹配。
"""
import re
import sys
import glob
import os

PUB = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
S, E = '<!-- TRANS_CMP_V1_START -->', '<!-- TRANS_CMP_V1_END -->'

CSS = """
/* TRANS_CMP_V1 翻译自评 */
#cmpcard .cmpsum{display:block;margin:2px 0 14px}
#cmpcard .cmpsc{display:block;font-size:30px;font-weight:800;letter-spacing:-.6px;color:var(--blue);line-height:1.1}
#cmpcard .cmpsc i{font-size:13px;font-weight:600;font-style:normal;color:var(--sub2);margin-left:4px;letter-spacing:0}
#cmpcard .cmpnote{display:block;margin-top:7px;font-size:12.5px;line-height:1.65;color:var(--sub)}
#cmpcard .cmpbar{height:6px;border-radius:99px;background:var(--track,#e8ebf0);overflow:hidden;margin:0 0 16px}
#cmpcard .cmpbar>i{display:block;height:100%;border-radius:99px;background:var(--blue)}
.mytrans{margin:9px 0 0;padding:9px 11px;border:1px solid var(--line);border-radius:9px;background:var(--soft)}
.mth{font-size:11px;letter-spacing:.5px;color:var(--sub2);margin-bottom:4px}
.mtt{margin:0 0 8px;font-size:13px;line-height:1.66;color:var(--txt2);
  font-family:Georgia,"Times New Roman",serif;word-break:break-word}
.mtp{display:flex;flex-wrap:wrap;gap:5px}
.pt{font-size:11.5px;line-height:1.5;padding:2px 8px;border-radius:20px;border:1px solid var(--line)}
.pt.ok{background:var(--green-soft);border-color:var(--green-soft);color:var(--green)}
.pt.no{background:var(--red-soft);border-color:var(--red-soft);color:var(--red)}
.pt.ok::before{content:'✓ '}
.pt.no::before{content:'✗ '}
.pt em{font-style:normal;opacity:.72;font-size:11px}
.ptmiss{margin:7px 0 0;font-size:11.5px;line-height:1.6;color:var(--red)}
"""

JS = r"""
/* TRANS_CMP_V1 */
(function(){
  var m = location.pathname.match(/trans-([0-9-]+)\.html/);
  var SID = m ? m[1] : '';
  if (!SID) return;

  function norm(t){
    return (t || '').toLowerCase()
      .replace(/&[a-z]+;|&#\d+;/g, ' ')
      .replace(/<[^>]+>/g, ' ')
      .replace(/[^a-z0-9\u4e00-\u9fa5]+/g, ' ')
      .replace(/\s+/g, ' ').trim();
  }
  // 与 check_trans_pts.py 同一套：先看整体子串，失败再按词前缀顺序匹配
  function hit(text, alt){
    var t = norm(text), a = norm(alt);
    if (!a) return false;
    if (t.indexOf(a) >= 0) return true;
    var tw = t.split(' '), aw = a.split(' '), i = 0;
    for (var k = 0; k < tw.length && i < aw.length; k++){
      var w = aw[i];
      var stem = w.length > 4 ? w.slice(0, Math.max(4, w.length - 2)) : w;
      if (tw[k].indexOf(stem) === 0) i++;
    }
    return i === aw.length;
  }

  // 按英文句末标点切段，用于「你写的」那一行
  function splitEn(t){
    var s = (t || '').replace(/\s+/g, ' ').trim();
    if (!s) return [];
    var parts = s.match(/[^.!?;]+[.!?;]*/g) || [];
    return parts.map(function(x){ return x.trim(); }).filter(function(x){ return x.length > 1; });
  }

  function esc(s){
    return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
  }

  function render(){
    var ta = document.getElementById('wpText');
    var mine = ta ? ta.value : '';
    if (!mine.trim()) return;
    var data = (window.CET4_TRANS || {})[SID];
    var box = document.getElementById('cmpcard');
    if (!data){ return; }

    var sents = document.querySelectorAll('#refcard .sent');
    if (!sents.length) return;

    var myS = splitEn(mine);
    var aligned = myS.length === sents.length;
    var totHit = 0, totPts = 0, missSent = 0;

    for (var i = 0; i < sents.length; i++){
      var pts = data[i] || [];
      var nodes = sents[i].querySelectorAll('.mytrans');
      for (var z = 0; z < nodes.length; z++) nodes[z].parentNode.removeChild(nodes[z]);

      var ok = 0, html = '';
      for (var j = 0; j < pts.length; j++){
        var label = pts[j][0], alts = pts[j][1].split('|');
        var got = false;
        for (var k = 0; k < alts.length; k++){ if (hit(mine, alts[k])){ got = true; break; } }
        if (got){ ok++; totHit++; }
        totPts++;
        html += '<span class="pt ' + (got ? 'ok' : 'no') + '">' + esc(label)
             + (got ? '' : ' <em>' + esc(alts[0]) + '</em>') + '</span>';
      }
      if (ok === 0) missSent++;

      var d = document.createElement('div');
      d.className = 'mytrans';
      var h = '';
      if (aligned && myS[i]) h += '<div class="mth">你写的这一句</div><p class="mtt">' + esc(myS[i]) + '</p>';
      h += '<div class="mth">采分点 ' + ok + '/' + pts.length + '</div><div class="mtp">' + html + '</div>';
      if (ok === 0) h += '<p class="ptmiss">这一句的信息点一个都没匹配上——要么整句没译，要么换了一种说法（关键词匹配认不出同义改写，自己看一眼）。</p>';
      d.innerHTML = h;
      sents[i].appendChild(d);
    }

    // 估分卡
    var cov = totPts ? totHit / totPts : 0;
    var lo = Math.round(15 * cov);
    if (box) box.parentNode.removeChild(box);
    var card = document.createElement('div');
    card.className = 'card';
    card.id = 'cmpcard';
    card.innerHTML =
      '<h2>你的译文自评</h2>'
      + '<div class="cmpsum"><span class="cmpsc">' + lo + '<i>/ 15</i></span>'
      + '<span class="cmpnote">按信息点覆盖折算，<b>不含语法与拼写扣分</b>。'
      + '信息点 ' + totHit + '/' + totPts + (missSent ? ' · 有 ' + missSent + ' 句整句没对上' : '')
      + (aligned ? '' : ' · 你的译文分句与原文不一致，只按全文检查') + '</span></div>'
      + '<div class="cmpbar"><i style="width:' + Math.round(cov * 100) + '%"></i></div>'
      + '<p class="hint" style="margin:0">下面每一句都标了你命中/漏掉的信息点。'
      + '关键词匹配认不出同义改写——漏标不等于你真错了，但<b>标了漏、你又确实没写，那就是真漏</b>。</p>';
    var ref = document.getElementById('refcard');
    ref.parentNode.insertBefore(card, ref);
    return card;
  }

  window.__transCmp = function(scroll){
    function done(){
      var c = render();
      if (c){ if (scroll) c.scrollIntoView({behavior:'smooth', block:'start'}); return; }
      var rc = document.getElementById('refcard');
      if (rc && scroll) rc.scrollIntoView({behavior:'smooth', block:'start'});
    }
    if (window.CET4_TRANS){ done(); return; }
    var sc = document.createElement('script');
    sc.src = 'explain/trans.js';
    sc.onload = done;
    sc.onerror = function(){};
    document.head.appendChild(sc);
  };

  // 刷新后已经提交过：静默补一次自评（不滚动，免得打断）
  window.addEventListener('load', function(){
    setTimeout(function(){
      var rc = document.getElementById('refcard');
      var ta = document.getElementById('wpText');
      if (rc && !rc.classList.contains('lock') && ta && ta.value.trim() && !document.getElementById('cmpcard')){
        window.__transCmp(false);
      }
    }, 400);
  });
})();
"""

SNIP = '\n%s\n<style>%s</style>\n<script>%s</script>\n%s\n' % (S, CSS, JS, E)


def patch(path):
    h = open(path, encoding='utf-8').read()
    h = re.sub(r'\n*' + re.escape(S) + r'.*?' + re.escape(E) + r'\n*', '\n', h, flags=re.S)

    # 提交：解锁后跑自评（原来是 unlock(true) 直接滚到参考）
    old = """    if (window.__markDone) window.__markDone('other');
    unlock(true);"""
    new = """    if (window.__markDone) window.__markDone('other');
    unlock(false);
    if (window.__transCmp) window.__transCmp(true); else unlock(true);"""
    if old in h:
        h = h.replace(old, new, 1)
    elif 'window.__transCmp(true)' not in h:
        return 'skip(no submit anchor): ' + path

    # 刷新后已提交：也补一次
    old2 = """    unlock(false);
    btnS.style.display = 'inline-block';"""
    new2 = """    unlock(false);
    btnS.style.display = 'inline-block';"""
    if old2 in h:
        h = h.replace(old2, new2, 1)

    h = h.replace('</body>', SNIP + '</body>', 1)
    open(path, 'w', encoding='utf-8').write(h)
    return 'ok: ' + path


if __name__ == '__main__':
    files = sys.argv[1:] or sorted(glob.glob(os.path.join(PUB, 'trans-*.html')))
    for f in files:
        if not os.path.isabs(f):
            f = os.path.join(PUB, f)
        print(patch(f))

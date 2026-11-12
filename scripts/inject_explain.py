# -*- coding: utf-8 -*-
"""把某套的解析数据注进三个单段页（幂等，重复跑只会替换自己那段）。

用法：
    python3 scripts/inject_explain.py 2025-12-1

前提：explain/<套号>.js 已由 gen_explain.py 生成。
注入的代码在 <!-- ANA_V1_START --> 里，删掉这一整段即可回退。
"""
import os, re, sys

SID = sys.argv[1] if len(sys.argv) > 1 else '2025-12-1'
PUB = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

TPL = '''
<!-- ANA_V1_START 答题解析：数据在 explain/%(sid)s.js，本段只负责渲染 -->
<script src="explain/%(sid)s.js?v=1"></script>
<script>
(function(){
  var SID='%(sid)s', SEC='%(sec)s';
  var ANA=(window.CET4_ANA||{})[SID];
  if(!ANA||!ANA.secs[SEC]) return;
  var ITEMS=ANA.secs[SEC];
  var DATA=window.DATA||{}, L=DATA.lines||[];

  function esc(s){return String(s==null?'':s).replace(/[&<>"]/g,function(c){
    return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];});}

  function card(it){
    var d=document.createElement('details');
    d.className='ana';
    var h='<summary><b>答案 '+esc(it.ans)+'</b><em></em></summary><div class="ab">';
    h+=(it.loc||[]).map(function(x){
      return '<div class="ar"><span>定位</span><div>'
        +'<button class="apb" data-li="'+x.li+'" type="button">▶ 第 '+(x.li+1)+' 句</button>'
        +'<p class="aen">'+esc(x.en)+'</p><p class="azh">'+esc(x.zh)+'</p></div></div>';
    }).join('');
    if(it.pairs&&it.pairs.length){
      h+='<div class="ar"><span>替换</span><div>'+it.pairs.map(function(p){
        return '<div class="apair"><code>'+esc(p[0])+'</code><code>'+esc(p[1])+'</code></div>';
      }).join('')+'</div></div>';
    }
    if(it.opts){
      h+='<div class="ar"><span>干扰</span><div>'+Object.keys(it.opts).sort().map(function(k){
        var o=it.opts[k];
        return '<div class="aopt"><b>'+k+'</b><em>'+esc(o.kind)+'</em>'+esc(o.why)+'</div>';
      }).join('')+'</div></div>';
    }
    if(it.tip) h+='<p class="atip">'+esc(it.tip)+'</p>';
    d.innerHTML=h+'</div>';
    return d;
  }

  function render(){
    var Q=window.QUIZ||[];
    for(var i=0;i<Q.length;i++){
      var q=Q[i];
      var qEl=document.querySelector('.q[data-q="'+q.id+'"]');
      if(!qEl||qEl.querySelector('.ana')) continue;
      var it=ITEMS[q.id]; if(!it) continue;
      var el=card(it);
      var wrong=qEl.querySelector('.opt.wrong');
      el.open=!!wrong;                    /* 错题默认展开，对题收起 */
      var cause=qEl.querySelector('.cause');
      if(cause) qEl.insertBefore(el,cause); else qEl.appendChild(el);
    }
  }

  /* 判分信号：任一选项拿到 .right 就渲染。判分、恢复判分都会触发，幂等。 */
  var t=null;
  function kick(){ if(t) return; t=setTimeout(function(){ t=null; if(document.querySelector('.opt.right')) render(); },60); }
  var host=document.getElementById('quizCard')||document.body;
  try{
    new MutationObserver(kick).observe(host,{subtree:true,attributes:true,attributeFilter:['class'],childList:true});
  }catch(e){}
  setTimeout(kick,600);
  setTimeout(kick,1800);

  /* 定位句试听：播这一句，到下一句开头停 */
  document.addEventListener('click',function(e){
    var b=e.target.closest?e.target.closest('.apb'):null;
    if(!b) return;
    var li=+b.getAttribute('data-li');
    var A=document.getElementById('audio');
    if(!A||!L[li]||!L[li].tokens||!L[li].tokens[0]) return;
    var s=L[li].tokens[0].s;
    var en=L[li+1]?L[li+1].tokens[0].s:(DATA.dur||s+8);
    try{ A.pause(); }catch(x){}
    A.playbackRate=1;
    try{ A.currentTime=Math.max(0,s-0.15); }catch(x){}
    var f=function(){ if(A.currentTime>=en-0.05){ try{A.pause();}catch(x){} A.removeEventListener('timeupdate',f); } };
    A.addEventListener('timeupdate',f);
    var p=A.play(); if(p&&p.catch)p.catch(function(){});
    var old=b.textContent;
    b.textContent='▶ 播放中';
    setTimeout(function(){ b.textContent=old; },1500);
  },false);
})();
</script>
<!-- ANA_V1_END -->
'''

for k in 'ABC':
    p = os.path.join(PUB, '%s_Section%s.html' % (SID, k))
    if not os.path.exists(p):
        sys.exit('缺少页面：' + p)
    h = open(p, encoding='utf-8').read()
    h = re.sub(r'\n+<!-- ANA_V1_START.*?ANA_V1_END -->\n+', '\n', h, flags=re.S)
    assert '</body>' in h
    h = h.replace('</body>', TPL % {'sid': SID, 'sec': k} + '</body>')
    open(p, 'w', encoding='utf-8').write(h)
    print('injected', p)

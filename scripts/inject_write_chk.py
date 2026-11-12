"""写作页：作文体检 + 四级五档量表。

体检全是确定性规则（词数/段数/连接词/题目词/常见语法错），不调模型，结果可复现。
档位判断是启发式的结构性粗判，页面上必须写明「不等于考场得分」。
"""
import re
import sys
import glob
import os

PUB = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
S, E = '<!-- WRITE_CHK_V1_START -->', '<!-- WRITE_CHK_V1_END -->'

CSS = """
/* WRITE_CHK_V1 作文体检 */
#wcheck .wband{display:flex;align-items:baseline;gap:9px;margin:2px 0 12px;flex-wrap:wrap}
#wcheck .wbnum{font-size:30px;font-weight:800;letter-spacing:-.6px;line-height:1.1;color:var(--blue)}
#wcheck .wbnum i{font-size:13px;font-weight:600;font-style:normal;color:var(--sub2);margin-left:4px;letter-spacing:0}
#wcheck .wbtext{font-size:12.5px;line-height:1.6;color:var(--sub);flex:1;min-width:160px}
.wgrid{display:flex;flex-wrap:wrap;gap:7px;margin:0 0 12px}
.wcell{flex:1 1 44%;min-width:130px;padding:8px 10px;border:1px solid var(--line);border-radius:9px;background:var(--soft)}
.wcell .wl{font-size:11px;color:var(--sub2);letter-spacing:.4px;margin-bottom:2px}
.wcell .wv{font-size:14px;font-weight:700;color:var(--txt)}
.wcell.ok .wv{color:var(--green)}
.wcell.warn .wv{color:var(--amber)}
.wcell.bad .wv{color:var(--red)}
.werr{margin:0;padding:0;list-style:none}
.werr li{position:relative;padding:7px 0 7px 15px;font-size:12.5px;line-height:1.65;color:var(--txt2);
  border-bottom:1px solid var(--line2)}
.werr li:last-child{border-bottom:0}
.werr li::before{content:'';position:absolute;left:0;top:13px;width:5px;height:5px;border-radius:50%;background:var(--red)}
.werr code{background:var(--grey);border-radius:4px;padding:0 4px;font-size:12px}
.werr b{color:var(--red)}
.wbandrow{display:flex;gap:9px;padding:9px 0;border-bottom:1px solid var(--line2);align-items:flex-start}
.wbandrow:last-child{border-bottom:0}
.wbandrow>span{flex:0 0 42px;font-size:13px;font-weight:800;color:var(--sub2);padding-top:1px}
.wbandrow.cur>span{color:var(--blue)}
.wbandrow.cur>div{background:var(--blue-soft);border-radius:7px;margin:-4px -8px;padding:4px 8px}
.wbandrow>div{flex:1;min-width:0;font-size:12.5px;line-height:1.68;color:var(--txt2)}
.wadvice{margin:14px 0 0;padding:9px 11px;font-size:12.5px;line-height:1.7;color:var(--txt2);
  background:var(--blue-soft);border-radius:9px}
.wadvice b{color:var(--blue)}
.wscale{margin:12px 0 0;border:1px solid var(--line);border-radius:9px;padding:0 11px}
.wscale>summary{padding:9px 0;font-size:12.5px;color:var(--sub);cursor:pointer;list-style:none}
.wscale>summary::-webkit-details-marker{display:none}
.wscale>summary::before{content:'▸  ';color:var(--sub2)}
.wscale[open]>summary::before{content:'▾  '}
.wscale[open]>summary{border-bottom:1px solid var(--line2);margin-bottom:2px}
.wscale .wbandrow:last-child{border-bottom:1px solid var(--line2);margin-bottom:10px}
"""

JS = r"""
/* WRITE_CHK_V1 */
(function(){
  var STOP = ('a an the and or but if so than then that this these those it its is are was were be been being ' +
    'am do does did doing have has had having will would shall should can could may might must ' +
    'i you he she they we me my your his her their our us them ' +
    'of in on at to for with by from as into over about after before between during under ' +
    'not no nor too very just only also more most much many some any all both each every ' +
    'write writing written essay words word minutes minute least give your please suppose ' +
    'following direction directions response now they you will university ' +
    'make made take taken give given get got keep kept help helped become came come ' +
    'think thing things way ways want need able well good better best').split(/\s+/);

  var LINK = ['to begin with','first of all','firstly','secondly','thirdly','moreover','furthermore',
    'in addition','besides','however','nevertheless','on the other hand','therefore','thus',
    'consequently','as a result','for example','for instance','in conclusion','to sum up',
    'all in all','last but not least','what is more','in short','above all','first','second','third','finally'];

  function norm(t){
    return (t||'').toLowerCase().replace(/[^a-z0-9' ]+/g,' ').replace(/\s+/g,' ').trim();
  }
  function wc(t){
    var s = (t||'').trim();
    return s ? s.split(/\s+/).length : 0;
  }
  function covers(text, w){
    var t = ' ' + norm(text) + ' ', stem = w.length > 6 ? w.slice(0, w.length - 3) : w;
    return t.indexOf(' ' + stem) >= 0;
  }

  // 本题核心概念：从参考范文里取出现 ≥2 次的实词。
  // 比从 Directions 抽准——题干里全是 collecting / coming / suggesting 这种套话词。
  function topicWords(){
    var ps = document.querySelectorAll('#refcard .essay .en');
    if (!ps.length) return [];
    var cnt = {}, order = [], k;
    Array.prototype.forEach.call(ps, function(p){
      norm(p.textContent).split(' ').forEach(function(w){
        if (w.length < 4 || STOP.indexOf(w) >= 0) return;
        var key = w.length > 5 ? w.slice(0, w.length - 2) : w;
        if (!cnt[key]){ cnt[key] = {n:0, w:w}; order.push(key); }
        cnt[key].n++;
      });
    });
    var out = [];
    order.forEach(function(x){ if (cnt[x].n >= 2) out.push(cnt[x].w); });
    return out.slice(0, 6);
  }

  function check(text){
    var n = wc(text);
    var paras = text.trim().split(/\n\s*\n|\n/).filter(function(x){ return x.trim().length > 10; });
    var low = norm(text);
    var sents = (text.match(/[^.!?]+[.!?]+/g) || []).filter(function(x){ return x.trim().length > 3; });
    var links = LINK.filter(function(l){ return low.indexOf(l) >= 0; });

    var errs = [];
    var m;
    if ((m = text.match(/\bthere\s+(have|has)\b/ig))){
      errs.push('there ' + m[0].split(/\s+/)[1] + ' → 应为 <code>there ' + (/has/i.test(m[0]) ? 'is' : 'are') + '</code>（there be 句型不用 have）');
    }
    if ((m = text.match(/\b(people|students|children|they|we|you)\s+(is|was)\b/ig))){
      errs.push('<code>' + m[0] + '</code> → 主谓不一致，复数主语配 <code>are/were</code>');
    }
    if ((m = text.match(/\b(he|she|it|everyone|everybody|someone|nobody)\s+(are|were|have)\b/ig))){
      errs.push('<code>' + m[0] + '</code> → 主谓不一致，单数主语配 <code>is/was/has</code>');
    }
    if ((m = text.match(/\bmore and more\b/ig)) && m.length >= 3){
      errs.push('<code>more and more</code> 出现 ' + m.length + ' 次 → 换 <code>an increasing number of</code> / <code>a growing proportion of</code>');
    }
    if ((m = text.match(/\b(i think|in my opinion)\b/ig)) && m.length >= 3){
      errs.push('<code>' + m[0] + '</code> 反复出现 ' + m.length + ' 次 → 换成 <code>from my perspective</code> / <code>as far as I am concerned</code>');
    }
    if ((m = text.match(/(^|[.!?]\s+)([a-z])/g)) && m.length > 0){
      var bad = m.filter(function(x){ var c = x.slice(-1); return c !== 'i'; });
      if (bad.length) errs.push('句首字母没大写 ' + bad.length + ' 处 → 每句开头必须大写');
    }
    if (/[，。！？；：、]/.test(text)) errs.push('用了中文标点 → 英文作文里一律换成 <code>, . ! ? ;</code>');
    if ((m = text.match(/\b(\w{3,})\s+\1\b/ig))) errs.push('连续的重复词：<code>' + m[0] + '</code>');

    var tw = topicWords();
    var hit = tw.filter(function(w){ return covers(text, w); });
    return {n:n, paras:paras.length, sents:sents.length, links:links, errs:errs, tw:tw, twHit:hit};
  }

  function band(c){
    // 结构粗判：先看字数，再看段数与错误数，最后看连接词丰富度
    var b;
    if (c.n < 60) b = 2;
    else if (c.n < 90) b = 5;
    else if (c.n < 120) b = 8;
    else b = 11;
    if (c.n >= 120 && c.n <= 180 && c.paras >= 3 && c.errs.length <= 2 && c.links.length >= 3) b = 14;
    else if (c.paras < 3 && b > 8) b = 8;
    else if (c.errs.length >= 4 && b > 5) b = b === 14 ? 11 : Math.max(5, b - 3);
    if (c.n > 200 && b === 14) b = 11;
    return b;
  }

  var BANDS = [
    [14, '切题。表达思想清楚，文字通顺、连贯，基本无语言错误，仅有个别小错。'],
    [11, '切题。表达思想清楚，文字连贯，但有少量语言错误。'],
    [8,  '基本切题。有些地方表达不够清楚，文字勉强连贯，语言错误相当多，其中有一些是严重错误。'],
    [5,  '基本切题。表达思想不清楚，连贯性差，有较多的严重语言错误。'],
    [2,  '条理不清，思路紊乱，语言支离破碎，或大部分句子均有错误且多为严重错误。']
  ];

  function render(){
    var ta = document.getElementById('wpText');
    var text = ta ? ta.value : '';
    if (!text.trim()) return null;
    var c = check(text);
    var b = band(c);

    var old = document.getElementById('wcheck');
    if (old) old.parentNode.removeChild(old);

    var card = document.createElement('div');
    card.className = 'card';
    card.id = 'wcheck';

    var nCls = c.n < 120 ? 'bad' : (c.n > 180 ? 'warn' : 'ok');
    var h = '<h2>你的作文体检</h2>';
    h += '<div class="wband"><span class="wbnum">' + b + '<i>分档</i></span>'
       + '<span class="wbtext">按词数、段数、连接词、错误数做的<b>结构性粗判</b>，'
       + '不等于考场得分。真正的分档看下面那张表，自己对。</span></div>';

    h += '<div class="wgrid">';
    h += '<div class="wcell ' + nCls + '"><div class="wl">词数（要求 120–180）</div><div class="wv">' + c.n + '</div></div>';
    h += '<div class="wcell ' + (c.paras >= 3 ? 'ok' : 'bad') + '"><div class="wl">段落数</div><div class="wv">' + c.paras + '</div></div>';
    h += '<div class="wcell ' + (c.links.length >= 3 ? 'ok' : (c.links.length >= 1 ? 'warn' : 'bad')) + '"><div class="wl">连接词种类</div><div class="wv">' + c.links.length + '</div></div>';
    h += '<div class="wcell ' + (c.errs.length === 0 ? 'ok' : (c.errs.length <= 2 ? 'warn' : 'bad')) + '"><div class="wl">检出的问题</div><div class="wv">' + c.errs.length + '</div></div>';
    h += '</div>';

    if (c.tw.length){
      var miss = c.tw.filter(function(w){ return c.twHit.indexOf(w) < 0; });
      h += '<p class="hint" style="margin:0 0 10px">范文核心概念覆盖 <b>' + c.twHit.length + '/' + c.tw.length + '</b>'
         + (miss.length ? ' · 没提到：<b>' + miss.join(' / ') + '</b>' : ' · 全部提到了')
         + '<br>（同义改写可能认不出，别只看数字。）</p>';
    }

    if (c.errs.length){
      h += '<div class="wl" style="font-size:11px;color:var(--sub2);margin:0 0 2px">可能的问题</div><ul class="werr">';
      c.errs.forEach(function(e){ h += '<li>' + e + '</li>'; });
      h += '</ul>';
    } else {
      h += '<p class="hint" style="margin:0;color:var(--green)">✓ 常见错误一条都没检出。这只覆盖了 7 类高频错，拼写和搭配还得自己过一遍。</p>';
    }

    h += '<p class="wadvice">你落在 <b>' + b + ' 分档</b>：'
       + (b === 14 ? '结构、字数、衔接都合规——接下来拼的是论证具体度和句式变化。'
        : b === 11 ? '结构和字数没问题，差的是理由够不够具体、句式够不够多变。'
        : b === 8 ? '先把字数补到 120 以上、段落分成三段，再看每一段有没有一句明确的主题句。'
        : b === 5 ? '先把话说完整：每段一句完整的主谓宾，比写漂亮句子更重要。'
        : '现在还没成形，照着上面的范文骨架重写一遍。') + '</p>';

    h += '<details class="wscale"><summary>四级写作五档评分标准（官方）· 你在 ' + b + ' 分档</summary>';
    BANDS.forEach(function(x){
      h += '<div class="wbandrow' + (x[0] === b ? ' cur' : '') + '"><span>' + x[0] + ' 分</span><div>' + x[1] + '</div></div>';
    });
    h += '</details>';

    card.innerHTML = h;
    var ref = document.getElementById('refcard');
    ref.parentNode.insertBefore(card, ref);
    return card;
  }

  window.__writeChk = function(scroll){
    var c = render();
    if (c){ if (scroll) c.scrollIntoView({behavior:'smooth', block:'start'}); return; }
    var rc = document.getElementById('refcard');
    if (rc && scroll) rc.scrollIntoView({behavior:'smooth', block:'start'});
  };

  window.addEventListener('load', function(){
    setTimeout(function(){
      var rc = document.getElementById('refcard');
      var ta = document.getElementById('wpText');
      if (rc && !rc.classList.contains('lock') && ta && ta.value.trim() && !document.getElementById('wcheck')){
        window.__writeChk(false);
      }
    }, 400);
  });
})();
"""

SNIP = '\n%s\n<style>%s</style>\n<script>%s</script>\n%s\n' % (S, CSS, JS, E)


def patch(path):
    h = open(path, encoding='utf-8').read()
    h = re.sub(r'\n*' + re.escape(S) + r'.*?' + re.escape(E) + r'\n*', '\n', h, flags=re.S)

    old = """    if (window.__markDone) window.__markDone('other');
    unlock(true);"""
    new = """    if (window.__markDone) window.__markDone('other');
    unlock(false);
    if (window.__writeChk) window.__writeChk(true); else unlock(true);"""
    if old in h:
        h = h.replace(old, new, 1)
    elif '__writeChk(true)' not in h:
        return 'skip(no submit anchor): ' + path

    h = h.replace('</body>', SNIP + '</body>', 1)
    open(path, 'w', encoding='utf-8').write(h)
    return 'ok: ' + path


if __name__ == '__main__':
    files = sys.argv[1:] or sorted(glob.glob(os.path.join(PUB, 'write-*.html')))
    for f in files:
        if not os.path.isabs(f):
            f = os.path.join(PUB, f)
        print(patch(f))

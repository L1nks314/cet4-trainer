/* 听力整套成绩存档（首页 / 整套页共用）
   ------------------------------------------------------------------
   一条 = 一次整套听力交卷：
     {d:'2026-11-15', s:'2022-12-1', v:[A得分,B得分,C得分], u:用时秒, ts:毫秒}
   规则：
     · 同一天同一套重做 → 覆盖（保留最新一次，避免同套留两条把趋势撑歪）
     · 本机最多 40 条，按时间升序
     · 云端另发一条 t:'hist' 消息，不塞进打卡快照——快照要求顶层键是日期，
       混进去首页 pull 会把整条快照判成非打卡数据丢掉
   ntfy 免费 topic 12 小时过期，所以每次打开页面 sync 一次续期；
   过期后远端记录没了，本机还在，下次打开会重新推上去。
*/
(function(){
  var HIST_KEY = 'cet4_hist_v1';
  var SYNC_URL = 'https://ntfy.sh/cet4-718beb5773e8edd9ef48eb651cb1439dd362eb4a8d28f449';
  var MAX = 40;

  function norm(x){
    if (!x || typeof x !== 'object') return null;
    var d = String(x.d || ''), s = String(x.s || ''), v = x.v;
    if (!/^\d{4}-\d{2}-\d{2}$/.test(d) || !s || !v || v.length !== 3) return null;
    var a = [+v[0] || 0, +v[1] || 0, +v[2] || 0];
    if (a[0] > 7 || a[1] > 8 || a[2] > 10) return null;
    var ts = +x.ts || Date.parse(d + 'T12:00:00') || 0;
    return {d: d, s: s, v: a, u: +x.u || 0, ts: ts};
  }

  function keyOf(x){ return x.d + '|' + x.s; }

  function merge(list){
    var m = {}, x, k, i;
    for (i = 0; i < (list || []).length; i++){
      x = norm(list[i]);
      if (!x) continue;
      k = keyOf(x);
      if (!m[k] || x.ts >= m[k].ts) m[k] = x;
    }
    var out = [];
    for (k in m) out.push(m[k]);
    out.sort(function(a, b){ return a.ts - b.ts; });
    return out.slice(-MAX);
  }

  function read(){
    var a;
    try{ a = JSON.parse(localStorage.getItem(HIST_KEY) || '[]'); }catch(e){ a = []; }
    return merge(Array.isArray(a) ? a : []);
  }

  function save(a){
    try{ localStorage.setItem(HIST_KEY, JSON.stringify(a)); }catch(e){}
    return a;
  }

  /* 老数据迁移：以前每套只在本机留一条 cet4_set_<套号>，把它读成历史第一条。
     这套记录本身就是「最后一次」，所以迁移不会重复计数。 */
  function fromSets(){
    var keys = [], i, k, o, out = [];
    try{
      for (i = 0; i < localStorage.length; i++){
        k = localStorage.key(i);
        if (/^cet4_set_/.test(k)) keys.push(k);
      }
    }catch(e){ return out; }
    keys.forEach(function(k){
      try{ o = JSON.parse(localStorage.getItem(k) || 'null'); }catch(e){ o = null; }
      if (!o || !o.a || !o.d) return;
      out.push({d: o.d, s: k.replace(/^cet4_set_/, ''), v: o.a, u: o.used || 0, ts: o.ts || 0});
    });
    return out;
  }

  function pull(){
    if (!window.fetch) return Promise.resolve([]);
    return fetch(SYNC_URL + '/json?poll=1&since=all', {cache: 'no-store'})
      .then(function(r){ return r.ok ? r.text() : ''; })
      .then(function(t){
        var out = [];
        (t || '').trim().split('\n').filter(Boolean).forEach(function(line){
          try{
            var d = JSON.parse(line);
            var p = JSON.parse(d.message || '{}');
            if (p && p.t === 'hist' && p.h && p.h.length) out = out.concat(p.h);
          }catch(e){}
        });
        return out;
      })
      .catch(function(){ return []; });
  }

  function push(list){
    if (!window.fetch) return Promise.resolve(false);
    var body = {t: 'hist', h: list};
    /* ntfy 单条消息上限 4KB：超了就砍最旧的，宁少不丢整条 */
    while (JSON.stringify(body).length > 3800 && body.h.length > 1) body.h.shift();
    return fetch(SYNC_URL, {method: 'POST', body: JSON.stringify(body)})
      .then(function(r){ return r.ok; })
      .catch(function(){ return false; });
  }

  var pending = null;

  /* 合并本机 + 迁移 + 云端，写回本机，再把合并结果推上去。
     连点/多页同时调只跑一次（pending 复用）。 */
  function sync(){
    if (pending) return pending;
    var local = merge(read().concat(fromSets()));
    save(local);
    pending = pull().then(function(remote){
      var all = save(merge(local.concat(remote)));
      return push(all).then(function(){ pending = null; return all; },
        function(){ pending = null; return all; });
    });
    return pending;
  }

  function add(rec){
    var all = save(merge(read().concat(fromSets()).concat([rec])));
    pull().then(function(remote){
      return push(merge(all.concat(remote)));
    });
    return all;
  }

  window.CET4HIST = {
    read: read,
    add: add,
    sync: sync,
    total: function(x){ return x.v[0] + x.v[1] + x.v[2]; }
  };
})();

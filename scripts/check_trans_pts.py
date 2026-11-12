# -*- coding: utf-8 -*-
"""自检：每个采分点的每一种写法，都必须能在参考译文里命中。

命不中说明这个写法学生就算照抄参考译文也判不出来——要么写法写错，要么匹配算法有洞。
"""
import re
import json
import glob
import os
import sys

PUB = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(PUB, 'scripts'))
import gen_trans_pts as G


def norm(t):
    t = re.sub(r'&[a-z]+;|&#\d+;', ' ', t)
    t = re.sub(r'<[^>]+>', ' ', t)
    t = t.lower()
    t = re.sub(r'[^a-z0-9\u4e00-\u9fa5]+', ' ', t)
    return re.sub(r'\s+', ' ', t).strip()


def has(text, alt):
    t, a = norm(text), norm(alt)
    if not a:
        return False
    if a in t:
        return True
    tw, aw = t.split(' '), a.split(' ')
    i = 0
    for k in range(len(tw)):
        if i >= len(aw):
            break
        w = aw[i]
        stem = w[:max(4, len(w) - 2)] if len(w) > 4 else w
        if tw[k].startswith(stem):
            i += 1
    return i == len(aw)


def load_sents():
    out = {}
    for f in sorted(glob.glob(os.path.join(PUB, 'trans-*.html'))):
        sid = os.path.basename(f).replace('trans-', '').replace('.html', '')
        h = open(f, encoding='utf-8').read()
        sents = re.findall(r'<p class="szh">(.*?)</p><p class="sen">(.*?)</p>', h, re.S)
        out[sid] = [b for a, b in sents]
    return out


def main():
    sents = load_sents()
    bad = miss = 0
    tot = 0
    for sid in sorted(G.D):
        ens = sents.get(sid)
        if ens is None:
            print('! 页面不存在', sid)
            bad += 1
            continue
        if len(ens) != len(G.D[sid]):
            print('! 句数不符', sid, '页面', len(ens), '数据', len(G.D[sid]))
            bad += 1
        for i, pts in enumerate(G.D[sid]):
            if i >= len(ens):
                continue
            for z, alts in pts:
                for a in alts.split('|'):
                    tot += 1
                    if not has(ens[i], a):
                        miss += 1
                        print('MISS %-12s 句%d %-14s alt=%r' % (sid, i, z, a))
    print('\n点 %d，命中 %d，未命中 %d，结构问题 %d' % (tot, tot - miss, miss, bad))
    return 0 if miss == 0 and bad == 0 else 1


if __name__ == '__main__':
    sys.exit(main())

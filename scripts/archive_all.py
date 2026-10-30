#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""GitHub Actions 复用：拉取 ntfy 近期消息 → 转存照片到 photos/ + 归档到 records.json。
不需要任何个人 token；提交由 workflow 的 git 步骤完成。
"""
import json
import os
import re
import subprocess
import datetime

TOPIC = "cet4-718beb5773e8edd9ef48eb651cb1439dd362eb4a8d28f449"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PHOTOS = os.path.join(ROOT, "photos")
RECORDS = os.path.join(ROOT, "records.json")


def fetch_msgs():
    r = subprocess.run(
        ["curl", "-sL", "--max-time", "30",
         f"https://ntfy.sh/{TOPIC}/json?poll=1&since=3h"],
        capture_output=True)
    out = []
    for line in r.stdout.decode("utf-8", "ignore").split("\n"):
        line = line.strip()
        if not line:
            continue
        try:
            d = json.loads(line)
            if d.get("event") == "message":
                out.append(d)
        except Exception:
            pass
    return out


def parse_score(text):
    m = re.search(r"结果：(\d+/\d+)", text or "")
    return m.group(1) if m else ""


def main():
    os.makedirs(PHOTOS, exist_ok=True)
    existing = set(os.listdir(PHOTOS))

    arch = {"updated": "", "reps": [], "coaches": [], "photos": [], "prog": {}, "shadow": [], "review": []}
    if os.path.exists(RECORDS):
        try:
            arch = json.load(open(RECORDS, encoding="utf-8"))
        except Exception:
            pass
    for k in ("reps", "coaches", "photos", "shadow", "review"):
        arch.setdefault(k, [])
    arch.setdefault("prog", {})

    # 清掉历史遗留的无效回执（「我选 undefined」）
    arch["reps"] = [r for r in arch["reps"] if "undefined" not in str(r.get("text", "")).lower()]

    rep_keys = {(r.get("date"), r.get("kind"), r.get("page"), r.get("score") or "") for r in arch["reps"]}
    coach_keys = {(c.get("date"), c.get("kind"), c.get("text")) for c in arch["coaches"]}
    shadow_keys = {(x.get("date"), x.get("page"), x.get("mode")) for x in arch["shadow"]}
    photo_keys = {p.get("name") for p in arch["photos"]}
    review_idx = {x.get("id"): i for i, x in enumerate(arch["review"])}
    rv = 0
    ap = ar = ac = pg = 0

    for d in fetch_msgs():
        ts = datetime.datetime.fromtimestamp(d.get("time", 0)).strftime("%Y-%m-%d %H:%M")
        try:
            p = json.loads(d.get("message", "") or "{}")
        except Exception:
            continue
        if not isinstance(p, dict):
            continue
        t = p.get("t")
        att = d.get("attachment") or {}
        name = att.get("name") or ""

        if t == "photo" and name and not name.startswith("test_"):
            if name not in existing:
                dest = os.path.join(PHOTOS, name)
                subprocess.run(["curl", "-sL", "--max-time", "90", "-o", dest, att.get("url", "")],
                               capture_output=True)
                if os.path.exists(dest) and os.path.getsize(dest) > 0:
                    existing.add(name)
                    ap += 1
                elif os.path.exists(dest):
                    os.remove(dest)
            if name not in photo_keys:
                arch["photos"].append({"date": p.get("date"), "kind": p.get("kind"), "page": p.get("page"),
                                       "title": p.get("title", ""), "name": name, "ts": ts})
                photo_keys.add(name)

        elif t == "rep":
            # 无效回执：刷新后选项丢失又点提交 → 「我选 undefined」，不归档
            if "undefined" in str(p.get("text", "")).lower():
                continue
            sc = p.get("score") or parse_score(p.get("text"))
            k = (p.get("date"), p.get("kind"), p.get("page"), sc or "")
            if k not in rep_keys:
                arch["reps"].append({"date": p.get("date"), "kind": p.get("kind"), "page": p.get("page"),
                                     "text": p.get("text", ""), "score": sc, "pct": p.get("pct"), "ts": ts})
                rep_keys.add(k)
                ar += 1

        elif t == "shadow":
            k = (p.get("date"), p.get("page"), p.get("mode"))
            if k not in shadow_keys:
                arch["shadow"].append({"date": p.get("date"), "page": p.get("page"),
                                       "title": p.get("title", ""), "mode": p.get("mode"),
                                       "lines": p.get("lines"), "at": p.get("at"),
                                       "rate": p.get("rate"), "ts": ts})
                shadow_keys.add(k)

        elif t == "review":
            for it in (p.get("items") or []):
                rid = it.get("id")
                if not rid:
                    continue
                rec = {"id": rid, "page": it.get("page"), "title": it.get("title", ""),
                       "li": it.get("li"), "en": it.get("en", ""), "zh": it.get("zh", ""),
                       "stage": it.get("stage", 0), "due": it.get("due"),
                       "last": it.get("last", ""), "stuck": it.get("stuck", 0),
                       "done": it.get("done", 0), "ts": ts}
                i = review_idx.get(rid)
                if i is None:
                    review_idx[rid] = len(arch["review"])
                    arch["review"].append(rec)
                    rv += 1
                else:
                    arch["review"][i] = rec
                    rv += 1

        elif t == "coach":
            k = (p.get("date"), p.get("kind"), p.get("text"))
            if k not in coach_keys:
                arch["coaches"].append({"date": p.get("date"), "kind": p.get("kind"),
                                        "text": p.get("text", ""), "ts": ts})
                coach_keys.add(k)
                ac += 1

        elif not t:
            # 打卡快照：形如 {"2026-10-17":{"l":1,"o":1,"r":1}}
            for dk, dv in p.items():
                if len(dk) != 10 or dk.count("-") != 2 or not isinstance(dv, dict):
                    continue
                cur = arch["prog"].get(dk, {})
                changed = False
                for f in ("l", "o", "r"):
                    if dv.get(f) and not cur.get(f):
                        cur[f] = 1
                        changed = True
                if changed or dk not in arch["prog"]:
                    arch["prog"][dk] = cur
                    if changed:
                        pg += 1

    if ar or ac or ap or pg or rv:
        arch["updated"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        with open(RECORDS, "w", encoding="utf-8") as f:
            json.dump(arch, f, ensure_ascii=False, indent=2)
        print(f"照片+{ap} 回执+{ar} 批改+{ac} 打卡+{pg} 回炉{rv}")
    else:
        print("无新增，跳过写入")


if __name__ == "__main__":
    main()

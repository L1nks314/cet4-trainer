#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""从 ntfy 拉取近 3 小时的手写照片，保存到 photos/（由 GitHub Actions 定时执行）。
用法：python3 scripts/save_photos.py
"""
import json
import os
import subprocess

TOPIC = "cet4-718beb5773e8edd9ef48eb651cb1439dd362eb4a8d28f449"
PHOTOS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "photos")


def fetch_attachments():
    r = subprocess.run(
        ["curl", "-sL", "--max-time", "25",
         f"https://ntfy.sh/{TOPIC}/json?poll=1&since=3h"],
        capture_output=True)
    txt = r.stdout.decode("utf-8", "ignore")
    out = []
    for line in txt.split("\n"):
        line = line.strip()
        if not line:
            continue
        try:
            d = json.loads(line)
            if d.get("event") != "message":
                continue
            att = d.get("attachment") or {}
            if att.get("url") and att.get("name"):
                out.append(att)
        except Exception:
            pass
    return out


def main():
    os.makedirs(PHOTOS, exist_ok=True)
    existing = set(os.listdir(PHOTOS))
    n = 0
    for att in fetch_attachments():
        name, url = att["name"], att["url"]
        if name in existing:
            continue
        if not name.lower().endswith((".jpg", ".jpeg", ".png", ".webp", ".heic")):
            continue
        dest = os.path.join(PHOTOS, name)
        subprocess.run(["curl", "-sL", "--max-time", "90", "-o", dest, url],
                       capture_output=True)
        if os.path.exists(dest) and os.path.getsize(dest) > 0:
            n += 1
            print(f"✓ {name}")
        else:
            print(f"✗ {name}（下载失败，可能已过期）")
    print(f"本次新增 {n} 张")


if __name__ == "__main__":
    main()

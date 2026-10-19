#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hearthstone Card Art Downloader / Extractor
炉石传说卡牌原画下载与提取工具

该工具用于为离线版补全或下载全部卡牌原画 WebP 文件。
原画来自 HearthstoneJSON CDN (https://art.hearthstonejson.com/v1/512x/{cardId}.webp)。
亦支持从本地完整版 APK 中快速提取 22,000+ 原画。
"""

import os
import sys
import json
import zipfile
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ART_DIR = os.path.join(BASE_DIR, "art")
MANIFEST_PATH = os.path.join(BASE_DIR, "data", "art-manifest.json")
CDN_BASE = "https://art.hearthstonejson.com/v1/512x"

def extract_from_apk(apk_path):
    if not os.path.exists(apk_path):
        print(f"[-] APK 文件未找到: {apk_path}")
        return False
    print(f"[+] 正在从 APK 提取原画: {apk_path} ...")
    os.makedirs(ART_DIR, exist_ok=True)
    count = 0
    with zipfile.ZipFile(apk_path, 'r') as z:
        for info in z.infolist():
            if info.filename.startswith("assets/art/") and info.filename.endswith(".webp"):
                fname = os.path.basename(info.filename)
                target = os.path.join(ART_DIR, fname)
                if not os.path.exists(target):
                    with open(target, 'wb') as f:
                        f.write(z.read(info.filename))
                    count += 1
    print(f"[+] 提取完成！新增提取 {count} 张原画至 {ART_DIR}")
    return True

def download_card_art(card_id):
    target = os.path.join(ART_DIR, f"{card_id}.webp")
    if os.path.exists(target) and os.path.getsize(target) > 0:
        return True
    url = f"{CDN_BASE}/{card_id}.webp"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = resp.read()
            with open(target, 'wb') as f:
                f.write(data)
        return True
    except Exception:
        return False

def download_missing(max_workers=16):
    if not os.path.exists(MANIFEST_PATH):
        print(f"[-] 未找到原画清单文件: {MANIFEST_PATH}")
        return
    with open(MANIFEST_PATH, 'r', encoding='utf-8') as f:
        manifest = json.load(f)
    os.makedirs(ART_DIR, exist_ok=True)
    card_ids = list(manifest.keys())
    missing = [cid for cid in card_ids if not os.path.exists(os.path.join(ART_DIR, f"{cid}.webp"))]
    print(f"[+] 清单共有 {len(card_ids)} 张卡牌，缺失 {len(missing)} 张原画待下载...")
    if not missing:
        print("[+] 所有原画均已就绪！")
        return

    success, failed = 0, 0
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(download_card_art, cid): cid for cid in missing}
        for i, fut in enumerate(as_completed(futures), 1):
            if fut.result():
                success += 1
            else:
                failed += 1
            if i % 100 == 0 or i == len(missing):
                print(f"[*] 进度: {i}/{len(missing)} (成功: {success}, 失败: {failed})", end='\r')
    print(f"\n[+] 下载结束: 成功 {success}, 失败 {failed}")

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1].endswith('.apk'):
        extract_from_apk(sys.argv[1])
    else:
        apk_candidates = [
            os.path.join(os.path.dirname(BASE_DIR), "HSO1.5.6b.apk"),
            os.path.join(os.path.dirname(BASE_DIR), "HearthstoneOffline.apk"),
        ]
        extracted = False
        for apk in apk_candidates:
            if os.path.exists(apk):
                extracted = extract_from_apk(apk)
                break
        if not extracted:
            print("[*] 未找到本地 APK，准备从 CDN 下载缺失原画...")
            download_missing()

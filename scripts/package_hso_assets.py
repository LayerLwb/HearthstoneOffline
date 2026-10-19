#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hearthstone Offline - Package Art Assets into HSO.zip
将完整卡牌美术原画（22,000+ 卡牌 WebP）从 APK 提取并打包为 HSO.zip。
放置在手机 Download 目录下供游戏自动识别和加载。
"""

import os
import sys
import zipfile
import time

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_APK = os.path.join(BASE_DIR, "HSO1.5.6b.apk")
OUTPUT_ZIP = os.path.join(BASE_DIR, "HSO.zip")

def package_assets(apk_path=DEFAULT_APK, output_zip=OUTPUT_ZIP):
    if not os.path.exists(apk_path):
        print(f"[-] Error: Source APK not found at {apk_path}")
        sys.exit(1)

    print(f"[*] Packaging art assets from {apk_path} into {output_zip}...")
    start_time = time.time()
    count = 0

    with zipfile.ZipFile(apk_path, 'r') as src:
        with zipfile.ZipFile(output_zip, 'w', compression=zipfile.ZIP_DEFLATED) as dst:
            for info in src.infolist():
                if info.filename.startswith('assets/art/'):
                    rel_path = info.filename[len('assets/'):]
                    data = src.read(info.filename)
                    dst.writestr(rel_path, data)
                    count += 1
                    if count % 2000 == 0:
                        print(f"[*] Packed {count} files...", end='\r')

    elapsed = time.time() - start_time
    size_mb = os.path.getsize(output_zip) / (1024 * 1024)
    print(f"\n[+] Successfully created {output_zip}: {count} files, {size_mb:.2f} MB in {elapsed:.2f}s")

if __name__ == "__main__":
    apk = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_APK
    out = sys.argv[2] if len(sys.argv) > 2 else OUTPUT_ZIP
    package_assets(apk, out)

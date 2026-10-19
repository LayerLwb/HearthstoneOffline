#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hearthstone Offline APK CI/CD Build & Signing Script
炉石传说单机版 CI/CD 自动化构建与签名脚本

功能：
1. 校验运行环境与 JDK jarsigner。
2. 自动检查或从 Release 缓存下载基础原画完整包（包含 22,000+ 卡牌原画 WebP）。
3. 注入最新的 Web 核心引擎代码（index.html, index.js, ai.worker.js, index.css, data 等）。
4. 使用与既有版本完全一致的签名证书（androiddebugkey, SHA256: 61:95:63:01:...）进行签名。
5. 验证 APK 签名有效性，确保可以完美覆盖安装！
"""

import os
import sys
import zipfile
import subprocess
import argparse
import urllib.request

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_KEYSTORE = os.path.join(BASE_DIR, "android", "keystore", "hso.keystore")
DEFAULT_BASE_APK_URL = "https://github.com/LayerLwb/HearthstoneOffline/releases/download/v1.5.7/HearthstoneOffline-v1.5.7.apk"

def download_base_apk(target_path, url):
    print(f"[*] Base APK not found locally. Downloading from {url}...")
    os.makedirs(os.path.dirname(target_path), exist_ok=True)
    
    def report_progress(block_num, block_size, total_size):
        downloaded = block_num * block_size
        if total_size > 0:
            percent = downloaded * 100 / total_size
            mb = downloaded / (1024 * 1024)
            total_mb = total_size / (1024 * 1024)
            if block_num % 1000 == 0 or downloaded >= total_size:
                print(f"[*] Downloading: {mb:.1f}MB / {total_mb:.1f}MB ({percent:.1f}%)", end='\r')
    
    urllib.request.urlretrieve(url, target_path, reporthook=report_progress)
    print(f"\n[+] Base APK downloaded successfully ({os.path.getsize(target_path):,} bytes).")

def build_apk(version, output_apk, keystore, storepass, keypass, keyalias, base_apk):
    # Ensure keystore exists
    if not os.path.exists(keystore):
        print(f"[-] Error: Keystore not found at {keystore}")
        sys.exit(1)

    # Ensure base APK exists or download
    if not os.path.exists(base_apk):
        print(f"[*] Base APK {base_apk} does not exist.")
        download_base_apk(base_apk, DEFAULT_BASE_APK_URL)

    os.makedirs(os.path.dirname(os.path.abspath(output_apk)), exist_ok=True)
    unsigned_apk = output_apk + ".unsigned"

    print(f"[*] Packaging new APK for version {version}...")
    web_dir = os.path.join(BASE_DIR, "web")
    
    # File mapping: destination path inside APK -> local source path
    injections = {
        "assets/index.html": os.path.join(web_dir, "index.html"),
        "assets/assets/index-CU9H2UDJ.js": os.path.join(web_dir, "assets", "index-CU9H2UDJ.js"),
        "assets/assets/index.js": os.path.join(web_dir, "assets", "index.js"),
        "assets/assets/index-CTplPp4x.css": os.path.join(web_dir, "assets", "index-CTplPp4x.css"),
        "assets/assets/index.css": os.path.join(web_dir, "assets", "index.css"),
        "assets/assets/ai.worker-Yhf24pzo.js": os.path.join(web_dir, "assets", "ai.worker-Yhf24pzo.js"),
        "assets/assets/ai.worker.js": os.path.join(web_dir, "assets", "ai.worker.js"),
        "assets/assets/mobile-layout.js": os.path.join(web_dir, "assets", "mobile-layout.js"),
        "assets/assets/mobile-layout.css": os.path.join(web_dir, "assets", "mobile-layout.css"),
    }

    # Add data files
    data_dir = os.path.join(web_dir, "data")
    if os.path.exists(data_dir):
        for df in os.listdir(data_dir):
            if df.endswith(".json"):
                injections[f"assets/data/{df}"] = os.path.join(data_dir, df)

    with zipfile.ZipFile(base_apk, 'r') as src_zip:
        with zipfile.ZipFile(unsigned_apk, 'w', compression=zipfile.ZIP_DEFLATED) as dst_zip:
            for item in src_zip.infolist():
                # Strip old signature
                if item.filename.startswith("META-INF/"):
                    continue
                # Replace updated web engine files
                if item.filename in injections and os.path.exists(injections[item.filename]):
                    dst_zip.write(injections[item.filename], item.filename)
                else:
                    data = src_zip.read(item.filename)
                    dst_zip.writestr(item, data)

    print(f"[+] Unsigned APK packaged: {os.path.getsize(unsigned_apk):,} bytes")

    # Sign APK with jarsigner
    print(f"[*] Signing APK with jarsigner using {keystore} (alias: {keyalias})...")
    sign_cmd = [
        "jarsigner",
        "-keystore", keystore,
        "-storepass", storepass,
        "-keypass", keypass,
        "-signedjar", output_apk,
        unsigned_apk,
        keyalias
    ]
    res = subprocess.run(sign_cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print("[-] Signing failed:", res.stderr)
        if os.path.exists(unsigned_apk):
            os.remove(unsigned_apk)
        sys.exit(1)

    # Clean up unsigned APK
    if os.path.exists(unsigned_apk):
        os.remove(unsigned_apk)

    # Verify signature
    print("[*] Verifying signed APK...")
    verify_cmd = ["jarsigner", "-verify", output_apk]
    verify_res = subprocess.run(verify_cmd, capture_output=True, text=True)
    if verify_res.returncode != 0:
        print("[-] Signature verification failed:", verify_res.stderr)
        sys.exit(1)

    print(f"[+] Success! APK created and verified: {output_apk}")
    print(f"[+] Final file size: {os.path.getsize(output_apk):,} bytes")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Hearthstone Offline APK CI Builder")
    parser.add_argument("--version", default="v1.5.7", help="Version string")
    parser.add_argument("--output", default=os.path.join(BASE_DIR, "dist", "HearthstoneOffline-latest.apk"), help="Output APK path")
    parser.add_argument("--keystore", default=DEFAULT_KEYSTORE, help="Keystore file path")
    parser.add_argument("--storepass", default="android", help="Keystore password")
    parser.add_argument("--keypass", default="android", help="Key password")
    parser.add_argument("--alias", default="androiddebugkey", help="Key alias")
    parser.add_argument("--base-apk", default=os.path.join(BASE_DIR, "HSO1.5.6b.apk"), help="Base APK path")

    args = parser.parse_args()
    build_apk(
        version=args.version,
        output_apk=args.output,
        keystore=args.keystore,
        storepass=args.storepass,
        keypass=args.keypass,
        keyalias=args.alias,
        base_apk=args.base_apk
    )

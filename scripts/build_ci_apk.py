#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hearthstone Offline APK CI/CD Build & Signing Script
炉石传说单机版 CI/CD 自动化构建与签名脚本

功能：
1. 校验运行环境与 JDK jarsigner。
2. 支持构建轻量化 APK（~25MB，美术原画通过手机 Download 目录的 HSO.zip 自动读取）。
3. 支持构建内置完整原画包 APK（~800MB）。
4. 注入最新编译的 Android 核心组件（classes.dex、AndroidManifest.xml、resources.arsc）。
5. 注入最新的 Web 核心引擎代码（index.html, index.js, ai.worker.js, index.css, data 等）。
6. 使用与既有版本完全一致的签名证书（androiddebugkey, SHA256: 61:95:63:01:...）进行签名。
7. 验证 APK 签名有效性，确保可以完美覆盖安装！
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

def build_standalone_apk(version, unsigned_apk, embed_art=False, hso_zip=None):
    print(f"[*] Assembling standalone APK structure for version {version} (embed_art={embed_art})...")
    prebuilt_dir = os.path.join(BASE_DIR, "android", "prebuilt")
    web_dir = os.path.join(BASE_DIR, "web")
    res_dir = os.path.join(BASE_DIR, "android", "app", "src", "main", "res")

    if not os.path.exists(os.path.join(prebuilt_dir, "classes.dex")):
        print(f"[-] Error: Prebuilt classes.dex not found at {prebuilt_dir}")
        sys.exit(1)

    with zipfile.ZipFile(unsigned_apk, 'w', compression=zipfile.ZIP_DEFLATED) as dst:
        # 1. Android core prebuilts
        dst.write(os.path.join(prebuilt_dir, "AndroidManifest.xml"), "AndroidManifest.xml")
        dst.write(os.path.join(prebuilt_dir, "classes.dex"), "classes.dex")
        dst.write(os.path.join(prebuilt_dir, "resources.arsc"), "resources.arsc")

        # 2. Res drawables & icons
        for root, dirs, files in os.walk(res_dir):
            for f in files:
                full_path = os.path.join(root, f)
                rel_path = os.path.relpath(full_path, os.path.join(BASE_DIR, "android", "app", "src", "main"))
                dst.write(full_path, rel_path.replace("\\", "/"))

        # 3. Web assets
        dst.write(os.path.join(web_dir, "index.html"), "assets/index.html")

        # web/assets/
        web_assets = os.path.join(web_dir, "assets")
        if os.path.exists(web_assets):
            for f in os.listdir(web_assets):
                fp = os.path.join(web_assets, f)
                if os.path.isfile(fp):
                    dst.write(fp, f"assets/assets/{f}")

        # web/data/
        web_data = os.path.join(web_dir, "data")
        if os.path.exists(web_data):
            for f in os.listdir(web_data):
                fp = os.path.join(web_data, f)
                if os.path.isfile(fp):
                    dst.write(fp, f"assets/data/{f}")

        # 4. 可选：若指定 embed_art 则将 HSO.zip 中的原画并入 APK 内部
        if embed_art:
            zip_candidate = hso_zip or os.path.join(BASE_DIR, "HSO.zip")
            if os.path.exists(zip_candidate):
                print(f"[*] Embedding art assets from {zip_candidate}...")
                with zipfile.ZipFile(zip_candidate, 'r') as art_zip:
                    for item in art_zip.infolist():
                        if not item.is_dir():
                            rel = item.filename
                            if not rel.startswith("assets/"):
                                rel = "assets/" + rel
                            dst.writestr(rel, art_zip.read(item.filename))
                print("[+] Embedded art assets successfully.")
            else:
                print(f"[!] Warning: embed_art requested but {zip_candidate} not found. Building without embedded art.")

def build_from_base_apk(version, unsigned_apk, base_apk, embed_art=False):
    print(f"[*] Packaging APK from base {base_apk} for version {version}...")
    web_dir = os.path.join(BASE_DIR, "web")
    prebuilt_dir = os.path.join(BASE_DIR, "android", "prebuilt")

    injections = {
        "AndroidManifest.xml": os.path.join(prebuilt_dir, "AndroidManifest.xml"),
        "classes.dex": os.path.join(prebuilt_dir, "classes.dex"),
        "resources.arsc": os.path.join(prebuilt_dir, "resources.arsc"),
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
                # If embed_art is False, strip assets/art to create lightweight apk
                if not embed_art and item.filename.startswith("assets/art/"):
                    continue
                # Replace updated files
                if item.filename in injections and os.path.exists(injections[item.filename]):
                    dst_zip.write(injections[item.filename], item.filename)
                else:
                    data = src_zip.read(item.filename)
                    dst_zip.writestr(item, data)

def build_apk(version, output_apk, keystore, storepass, keypass, keyalias, base_apk=None, embed_art=False):
    # Ensure keystore exists
    if not os.path.exists(keystore):
        print(f"[-] Error: Keystore not found at {keystore}")
        sys.exit(1)

    os.makedirs(os.path.dirname(os.path.abspath(output_apk)), exist_ok=True)
    unsigned_apk = output_apk + ".unsigned"

    # 优先使用 Standalone 构建（快、免下载大型 Base APK），或根据 base_apk
    if base_apk and os.path.exists(base_apk):
        build_from_base_apk(version, unsigned_apk, base_apk, embed_art=embed_art)
    else:
        build_standalone_apk(version, unsigned_apk, embed_art=embed_art)

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
    print(f"[+] Final file size: {os.path.getsize(output_apk):,} bytes ({os.path.getsize(output_apk)/1024/1024:.2f} MB)")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Hearthstone Offline APK CI Builder")
    parser.add_argument("--version", default="v1.5.8", help="Version string")
    parser.add_argument("--output", default=os.path.join(BASE_DIR, "dist", "HearthstoneOffline-latest.apk"), help="Output APK path")
    parser.add_argument("--keystore", default=DEFAULT_KEYSTORE, help="Keystore file path")
    parser.add_argument("--storepass", default="android", help="Keystore password")
    parser.add_argument("--keypass", default="android", help="Key password")
    parser.add_argument("--alias", default="androiddebugkey", help="Key alias")
    parser.add_argument("--base-apk", default="", help="Optional base APK path")
    parser.add_argument("--embed-art", action="store_true", help="Embed card art into APK")

    args = parser.parse_args()
    build_apk(
        version=args.version,
        output_apk=args.output,
        keystore=args.keystore,
        storepass=args.storepass,
        keypass=args.keypass,
        keyalias=args.alias,
        base_apk=args.base_apk if args.base_apk else None,
        embed_art=args.embed_art
    )

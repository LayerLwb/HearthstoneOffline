#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hearthstone Offline APK CI/CD Build & Signing Script
炉石传说单机版 CI/CD 自动化构建与签名脚本

功能：
1. 校验运行环境、zipalign 与 apksigner。
2. 支持构建轻量化 APK（~25MB，美术原画通过手机 Download 目录的 HSO.zip 自动读取）。
3. 支持构建内置完整原画包 APK（~800MB）。
4. 注入最新编译的 Android 核心组件（classes.dex、AndroidManifest.xml、resources.arsc）。
5. 注入最新的 Web 核心引擎代码（index.html, index.js, ai.worker.js, index.css, data 等）。
6. 使用 zipalign 4 字节对齐。
7. 使用与既有版本完全一致的签名证书（androiddebugkey, SHA256: 61:95:63:01:...），
   并通过 apksigner 强制启用 v1 + v2 + v3 签名方案，确保 Android 11+ (API 34) 完美解析并支持覆盖安装！
"""

import os
import sys
import zipfile
import subprocess
import argparse
import shutil
import urllib.request

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_KEYSTORE = os.path.join(BASE_DIR, "android", "keystore", "hso.keystore")
DEFAULT_BASE_APK_URL = "https://github.com/LayerLwb/HearthstoneOffline/releases/download/v1.5.7/HearthstoneOffline-v1.5.7.apk"

def find_tool(name):
    """
    智能寻找 Android SDK 构建工具（zipalign、apksigner 等）
    """
    # 1. 优先从系统 PATH 检索
    p = shutil.which(name)
    if p:
        return p

    # 2. 从可能存在的 Android SDK 及预装路径检索
    sdk_roots = [
        os.environ.get("ANDROID_HOME", ""),
        os.environ.get("ANDROID_SDK_ROOT", ""),
        os.path.expanduser("~/Android/Sdk"),
        "/usr/local/lib/android/sdk",
        r"C:\Users\NULL\AppData\Local\Android\Sdk",
        r"C:\ApkTool1.0\tool",
        os.path.join(BASE_DIR, "tools")
    ]

    for root in sdk_roots:
        if not root or not os.path.exists(root):
            continue
        # 扫描 build-tools 目录
        bt = os.path.join(root, "build-tools")
        if os.path.exists(bt):
            for v in sorted(os.listdir(bt), reverse=True):
                for ext in ["", ".bat", ".exe"]:
                    c = os.path.join(bt, v, name + ext)
                    if os.path.exists(c):
                        return c
                jar = os.path.join(bt, v, "lib", name + ".jar")
                if os.path.exists(jar):
                    return jar
        for ext in ["", ".bat", ".exe", ".jar"]:
            c = os.path.join(root, name + ext)
            if os.path.exists(c):
                return c
    return None

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

def sign_and_align_apk(unsigned_apk, output_apk, keystore, storepass, keypass, keyalias):
    """
    使用 zipalign 4 字节对齐并使用 apksigner 赋予 v1 + v2 + v3 完整签名
    """
    zipalign_bin = find_tool("zipalign")
    apksigner_bin = find_tool("apksigner")

    aligned_apk = output_apk + ".aligned.apk"
    if os.path.exists(aligned_apk):
        os.remove(aligned_apk)

    # 1. 运行 zipalign 对齐
    source_to_sign = unsigned_apk
    if zipalign_bin:
        print(f"[*] Running zipalign (4-byte alignment) with {zipalign_bin}...")
        align_cmd = [zipalign_bin, "-p", "-f", "4", unsigned_apk, aligned_apk]
        res = subprocess.run(align_cmd, capture_output=True, text=True)
        if res.returncode == 0 and os.path.exists(aligned_apk):
            print(f"[+] APK successfully aligned ({os.path.getsize(aligned_apk):,} bytes).")
            source_to_sign = aligned_apk
        else:
            print(f"[!] Warning: zipalign returned code {res.returncode}: {res.stderr}")
    else:
        print("[!] Note: zipalign not found, proceeding with unaligned package.")

    # 2. 运行 apksigner 签名 (v1 + v2 + v3)
    signed_ok = False
    if apksigner_bin:
        print(f"[*] Signing APK with apksigner (v1+v2+v3) using {keystore} (alias: {keyalias})...")
        if apksigner_bin.endswith(".jar"):
            cmd_sign = ["java", "-jar", apksigner_bin, "sign"]
        elif apksigner_bin.endswith(".bat"):
            sibling_jar = os.path.join(os.path.dirname(apksigner_bin), "lib", "apksigner.jar")
            if os.path.exists(sibling_jar):
                cmd_sign = ["java", "-jar", sibling_jar, "sign"]
            else:
                cmd_sign = [apksigner_bin, "sign"]
        else:
            cmd_sign = [apksigner_bin, "sign"]

        cmd_sign.extend([
            "--ks", keystore,
            "--ks-key-alias", keyalias,
            "--ks-pass", f"pass:{storepass}",
            "--key-pass", f"pass:{keypass}",
            "--v1-signing-enabled", "true",
            "--v2-signing-enabled", "true",
            "--v3-signing-enabled", "true",
            "--out", output_apk,
            source_to_sign
        ])

        res = subprocess.run(cmd_sign, capture_output=True, text=True)
        if res.returncode == 0 and os.path.exists(output_apk):
            signed_ok = True
            print("[+] APK signed successfully with apksigner (v1+v2+v3 enabled).")

            # 验证签名方案
            print("[*] Verifying APK signature schemes...")
            if apksigner_bin.endswith(".jar") or (apksigner_bin.endswith(".bat") and os.path.exists(os.path.join(os.path.dirname(apksigner_bin), "lib", "apksigner.jar"))):
                jar_path = apksigner_bin if apksigner_bin.endswith(".jar") else os.path.join(os.path.dirname(apksigner_bin), "lib", "apksigner.jar")
                verify_cmd = ["java", "-jar", jar_path, "verify", "-v", output_apk]
            else:
                verify_cmd = [apksigner_bin, "verify", "-v", output_apk]

            vres = subprocess.run(verify_cmd, capture_output=True, text=True)
            for line in vres.stdout.splitlines():
                if "Verified using" in line or "Verifies" in line:
                    print("    ", line)
        else:
            print("[-] apksigner failed:", res.stderr)

    # 3. 若无 apksigner 则保底使用 jarsigner (仅 v1)
    if not signed_ok:
        print("[!] Warning: Falling back to jarsigner (v1 scheme only)...")
        shutil.copyfile(source_to_sign, output_apk)
        sign_cmd = [
            "jarsigner",
            "-keystore", keystore,
            "-storepass", storepass,
            "-keypass", keypass,
            output_apk,
            keyalias
        ]
        res = subprocess.run(sign_cmd, capture_output=True, text=True)
        if res.returncode != 0:
            print("[-] jarsigner failed:", res.stderr)
            sys.exit(1)

    # 清理中间临时文件
    if os.path.exists(aligned_apk):
        os.remove(aligned_apk)

def build_apk(version, output_apk, keystore, storepass, keypass, keyalias, base_apk=None, embed_art=False):
    # Ensure keystore exists
    if not os.path.exists(keystore):
        print(f"[-] Error: Keystore not found at {keystore}")
        sys.exit(1)

    os.makedirs(os.path.dirname(os.path.abspath(output_apk)), exist_ok=True)
    unsigned_apk = output_apk + ".unsigned.apk"
    if os.path.exists(unsigned_apk):
        os.remove(unsigned_apk)

    # 构建未签名 APK
    if base_apk and os.path.exists(base_apk):
        build_from_base_apk(version, unsigned_apk, base_apk, embed_art=embed_art)
    else:
        build_standalone_apk(version, unsigned_apk, embed_art=embed_art)

    print(f"[+] Unsigned APK packaged: {os.path.getsize(unsigned_apk):,} bytes")

    # 对齐与签名
    sign_and_align_apk(unsigned_apk, output_apk, keystore, storepass, keypass, keyalias)

    # 清理 unsigned 文件
    if os.path.exists(unsigned_apk):
        os.remove(unsigned_apk)

    print(f"[+] Build Complete! Signed APK: {output_apk}")
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

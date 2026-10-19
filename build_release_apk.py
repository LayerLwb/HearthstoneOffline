import os
import sys
import zipfile
import subprocess
import shutil

BASE_DIR = r"C:\HearthstoneOffline"
ORIGINAL_APK = os.path.join(BASE_DIR, "HSO1.5.6b.apk")
UNSIGNED_APK = os.path.join(BASE_DIR, "HSO_unsigned.apk")
SIGNED_APK = os.path.join(BASE_DIR, "HearthstoneOffline-v1.5.7.apk")

SIGN_TOOL = r"C:\ApkTool1.0\tool\signapk.jar"
CERT_PEM = r"C:\ApkTool1.0\tool\testkey.x509.pem"
PRIVATE_KEY = r"C:\ApkTool1.0\tool\testkey.pk8"

print("[*] Building updated Hearthstone Offline APK...")

# Step 1: Copy original APK contents except updated files and signature
print("[*] Packaging updated web assets and files into new APK...")
with zipfile.ZipFile(ORIGINAL_APK, 'r') as src_zip:
    with zipfile.ZipFile(UNSIGNED_APK, 'w', compression=zipfile.ZIP_DEFLATED) as dst_zip:
        for item in src_zip.infolist():
            # Skip old signature files
            if item.filename.startswith("META-INF/"):
                continue
            
            # Replace updated web files
            if item.filename == "assets/index.html":
                print("[+] Injecting updated assets/index.html")
                dst_zip.write(os.path.join(BASE_DIR, "web", "index.html"), item.filename)
            elif item.filename == "assets/assets/index-CU9H2UDJ.js":
                print("[+] Injecting updated assets/assets/index-CU9H2UDJ.js")
                dst_zip.write(os.path.join(BASE_DIR, "web", "assets", "index-CU9H2UDJ.js"), item.filename)
            elif item.filename == "assets/assets/index-CTplPp4x.css":
                dst_zip.write(os.path.join(BASE_DIR, "web", "assets", "index-CTplPp4x.css"), item.filename)
            elif item.filename == "assets/assets/ai.worker-Yhf24pzo.js":
                dst_zip.write(os.path.join(BASE_DIR, "web", "assets", "ai.worker-Yhf24pzo.js"), item.filename)
            else:
                data = src_zip.read(item.filename)
                dst_zip.writestr(item, data)

print(f"[+] Unsigned APK created: {os.path.getsize(UNSIGNED_APK):,} bytes")

# Step 2: Sign APK using JDK jarsigner with debug.keystore
print("[*] Signing APK with jarsigner...")
KEYSTORE = r"C:\ApkTool1.0\tool\debug.keystore"
cmd = [
    "jarsigner",
    "-keystore", KEYSTORE,
    "-storepass", "android",
    "-keypass", "android",
    "-signedjar", SIGNED_APK,
    UNSIGNED_APK,
    "androiddebugkey"
]
res = subprocess.run(cmd, capture_output=True, text=True)
if res.returncode != 0:
    print("[-] Signing failed:", res.stderr)
    sys.exit(1)

print(f"[+] Signed release APK successfully created: {SIGNED_APK}")
print(f"[+] File size: {os.path.getsize(SIGNED_APK):,} bytes")

# Cleanup unsigned temporary apk
if os.path.exists(UNSIGNED_APK):
    os.remove(UNSIGNED_APK)

print("[+] APK Build & Signing complete!")

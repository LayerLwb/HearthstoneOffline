import os
import re
import sys

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX_JS = os.path.join(ROOT_DIR, "web", "assets", "index.js")
INDEX_HASH_JS = os.path.join(ROOT_DIR, "web", "assets", "index-CU9H2UDJ.js")
AI_WORKER_JS = os.path.join(ROOT_DIR, "web", "assets", "ai.worker.js")
AI_WORKER_HASH_JS = os.path.join(ROOT_DIR, "web", "assets", "ai.worker-Yhf24pzo.js")

with open(INDEX_JS, 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Patch Pm(a) to explicitly support Prince Renathal (REV_018 and CORE_REV_018)
pm_needle = 'function Pm(a){const isWhiz=a.cards.some(_=>["BOT_914","DAL_800","TOY_700"].includes(_)),e=a.cards.map(_=>c_(_)?.rule.deckBuild).filter(Boolean),t=[];let s=isWhiz?Math.max(1,a.cards.length):30,r=30,o=0,n=0;'
pm_replace = 'function Pm(a){const isWhiz=a.cards.some(_=>["BOT_914","DAL_800","TOY_700"].includes(_)),hasRenathal=a.cards.some(_=>_==="REV_018"||_==="CORE_REV_018"||(typeof _==="object"&&(_?.id==="REV_018"||_?.id==="CORE_REV_018"))),e=a.cards.map(_=>c_(_)?.rule?.deckBuild).filter(Boolean),t=[];let s=isWhiz?Math.max(1,a.cards.length):(hasRenathal?40:30),r=hasRenathal?40:30,o=0,n=0;'

if pm_needle not in code:
    print("[-] Error: pm_needle not found!")
    sys.exit(1)

code = code.replace(pm_needle, pm_replace, 1)
print("[+] Patched Pm(a) in index.js")

# 2. Patch Ln in hhc (deck builder click to add card)
ln_needle = 'if(F.cards.length>=30){o("卡组已有30张牌，请先移除一张。");return}'
ln_replace = 'const _maxDeck=(F.cards.some(c=>c==="REV_018"||c==="CORE_REV_018")||Ne.id==="REV_018"||Ne.id==="CORE_REV_018"||(typeof Pm==="function"&&Pm(F).deckSize>=40))?40:30;if(F.cards.length>=_maxDeck){o("卡组已有"+_maxDeck+"张牌，请先移除一张。");return}'

if ln_needle not in code:
    print("[-] Error: ln_needle not found!")
    sys.exit(1)

code = code.replace(ln_needle, ln_replace, 1)
print("[+] Patched Ln card addition check in index.js")

# 3. Patch the hardcoded deck validation checks across all rulesets using pure expression
pattern = re.compile(r'\(!a\.cards\.some\(c=>\["BOT_914","DAL_800","TOY_700"\]\.includes\(c\)\)&&a\.cards\.length!==30\)&&([a-zA-Z0-9_$]+)\.push\(`卡组需要30张牌，当前\$\{a\.cards\.length\}张`\);')

def replacer(match):
    arr = match.group(1)
    return f'(!a.cards.some(c=>["BOT_914","DAL_800","TOY_700"].includes(c))&&a.cards.length!==(a.cards.some(c=>c==="REV_018"||c==="CORE_REV_018")?40:30))&&{arr}.push("卡组需要"+(a.cards.some(c=>c==="REV_018"||c==="CORE_REV_018")?40:30)+"张牌，当前"+a.cards.length+"张");'

code, count = pattern.subn(replacer, code)
print(f"[+] Replaced {count} instances of hardcoded deck size validation in index.js")

# 4. Patch iw(a) player health initialization:
iw_needle = 'health:30,maxHealth:30,armor:0,mana:0,maxMana:0,overloaded:0,lockedMana:0,heroAttack:0,heroAttacks:0,heroPowerUsed:!1,heroFrozenUntil:0,weapon:null,deck:Ze(s,o.cards.map(_=>({uid:r.uid(),cardId:_,costChange:0,attackBuff:0,healthBuff:0,originDeck:n})))'
iw_replace = 'health:(o.cards.some(c=>c==="REV_018"||c==="CORE_REV_018")?40:30),maxHealth:(o.cards.some(c=>c==="REV_018"||c==="CORE_REV_018")?40:30),armor:0,mana:0,maxMana:0,overloaded:0,lockedMana:0,heroAttack:0,heroAttacks:0,heroPowerUsed:!1,heroFrozenUntil:0,weapon:null,deck:Ze(s,o.cards.map(_=>({uid:r.uid(),cardId:_,costChange:0,attackBuff:0,healthBuff:0,originDeck:n})))'

if iw_needle in code:
    code = code.replace(iw_needle, iw_replace, 1)
    print("[+] Patched iw(a) player health initialization")

with open(INDEX_JS, 'w', encoding='utf-8') as f:
    f.write(code)

with open(INDEX_HASH_JS, 'w', encoding='utf-8') as f:
    f.write(code)

print("[+] index.js and index-CU9H2UDJ.js successfully updated!")

# 5. Patch ai.worker.js
with open(AI_WORKER_JS, 'r', encoding='utf-8') as f:
    worker_code = f.read()

worker_needle = 'let o=30,t=30,s=0,l=0;for(const A of e){A.deckSize!==void 0&&(o=Math.max(o,A.deckSize))'
worker_replace = 'const hasRenathal=r.cards.some(A=>A==="REV_018"||A==="CORE_REV_018"||(typeof A==="object"&&A?.id==="REV_018"));let o=hasRenathal?40:30,t=hasRenathal?40:30,s=0,l=0;for(const A of e){A.deckSize!==void 0&&(o=Math.max(o,A.deckSize))'

if worker_needle in worker_code:
    worker_code = worker_code.replace(worker_needle, worker_replace, 1)
    with open(AI_WORKER_JS, 'w', encoding='utf-8') as f:
        f.write(worker_code)
    with open(AI_WORKER_HASH_JS, 'w', encoding='utf-8') as f:
        f.write(worker_code)
    print("[+] Patched ai.worker.js and ai.worker-Yhf24pzo.js!")
else:
    print("[*] Note: worker_needle not found or already dynamic")

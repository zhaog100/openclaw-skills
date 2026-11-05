#!/usr/bin/env python3
# Copyright (c) 2026 思捷娅科技 (SJYKJ) | MIT License
"""
make_pkg.py — 固定口径打包脚本（两边共用，保证口径 100% 一致）

用法（在本工作区根目录执行）:
    python3 oil-gold-correlation/packaging/make_pkg.py

输出:
    media/outbound/eo-og-final-<ts>.zip   交付包（含全部代码+配置+数据+运行态）
    media/outbound/MANIFEST-<ts>.json     全文件 md5 清单（用于两边一致性核对）

规则（写死，不留手动空间）:
    强制包含: 全部 .py/.js/.sh/.yaml/.yml/.json/.md/.txt/.html/.css + data/ reports/ 运行态
    强制排除: __pycache__/ *.pyc cache/ logs/ .git/
    打包前跑 verify_pkg.py 全项校验，任一项不过 → 拒绝出包
"""
import os, sys, json, hashlib, zipfile, datetime, re

W = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # workspace 根
sys.path.insert(0, os.path.join(W, "oil-gold-correlation", "packaging"))
from verify_pkg import verify_all, VERIFY_ITEMS

EXC_DIRS = {"__pycache__", "cache", "logs", ".git"}
OUT = os.path.join(W, "media", "outbound")

# ① 先校验，不过不出包
report = verify_all(W)
print("=== 打包前校验 ===")
allpass = True
for it, ok, detail in report:
    mark = "✅" if ok else "❌"
    print(f"  {mark} {it}: {detail}")
    if not ok:
        allpass = False
if not allpass:
    print("\n❌ 校验未全过，拒绝出包。修复后重跑。")
    sys.exit(1)
print("✅ 校验全过，开始打包")

# ② 收集文件
pairs = [
    (os.path.join(W, "oil-gold-correlation"), "oil-gold-correlation"),
    (os.path.join(W, "skills", "economic-outlook"), "economic-outlook"),
]
files = []
for base, arc in pairs:
    for root, dirs, fnames in os.walk(base):
        dirs[:] = [d for d in dirs if d not in EXC_DIRS]
        for f in fnames:
            if f.endswith(".pyc"):
                continue
            p = os.path.join(root, f)
            files.append((p, os.path.join(arc, os.path.relpath(p, base))))

ts = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
outzip = os.path.join(OUT, f"eo-og-final-{ts}.zip")
outman = os.path.join(OUT, f"MANIFEST-{ts}.json")
os.makedirs(OUT, exist_ok=True)

manifest = []
with zipfile.ZipFile(outzip, "w", zipfile.ZIP_DEFLATED) as z:
    for p, rel in files:
        z.write(p, rel)
        h = hashlib.md5(open(p, "rb").read()).hexdigest()
        manifest.append({"path": rel, "md5": h, "size": os.path.getsize(p)})

# 附打包说明（若存在）
doc = os.path.join(W, "media", "outbound", "打包说明-本包为何含这些文件.md")
if os.path.isfile(doc):
    with zipfile.ZipFile(outzip, "a") as z:
        z.write(doc, "打包说明-本包为何含这些文件.md")
        manifest.append({"path": "打包说明-本包为何含这些文件.md",
                         "md5": hashlib.md5(open(doc, "rb").read()).hexdigest(),
                         "size": os.path.getsize(doc)})

man = {
    "built_at": ts,
    "file_count": len(manifest),
    "verify_items": {it: (bool(o)) for it, o, _ in report},
    "files": manifest,
}
with open(outman, "w") as f:
    json.dump(man, f, ensure_ascii=False, indent=2)

print(f"\n✅ 出包 {os.path.basename(outzip)} ({os.path.getsize(outzip)}B, {len(manifest)} 文件)")
print(f"✅ MANIFEST {os.path.basename(outman)}")
print("\n=== 两边一致性核对方法 ===")
print("  对方解压包后执行: python3 verify_pkg.py --manifest <你发的MANIFEST-<ts>.json>")
print("  输出 'N 文件全 md5 一致' 才算收到同版。")
print(f"\n交付包: {outzip}")
print(f"清单: {outman}")

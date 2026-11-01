#!/usr/bin/env python3
# 版权: MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""黄金盯价自定义消息推送（复用 send_qq_gw.py 的 Gateway 推送，但发临时消息）"""
import sys, os, tempfile, importlib.util
msg = sys.argv[1] if len(sys.argv) > 1 else ""
if not msg:
    sys.exit(0)
# 复用 send_qq_gw 的推送通道：写临时文件再调
tmp = tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, dir=".")
tmp.write(msg + "\n\n⚠️ 区间参考，不构成投资建议"); tmp.close()
spec = importlib.util.spec_from_file_location("gw", os.path.join(os.getcwd(), "scripts", "..", "..", "oil-gold-correlation", "scripts", "send_qq_gw.py"))
try:
    gw = importlib.util.module_from_spec(spec); spec.loader.exec_module(gw)
    gw.send_report(tmp.name) if hasattr(gw, "send_report") else None
except Exception as e:
    print(f"push helper err: {e}")
os.unlink(tmp.name)

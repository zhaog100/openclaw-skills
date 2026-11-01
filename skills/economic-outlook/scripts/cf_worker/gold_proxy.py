#!/usr/bin/env python3
# 版权: MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
# 国内小主机转发脚本: 新加坡机直连东财 502(海外IP风控), 走这台国内机转发
# 部署: 国内主机装 python3, 跑 `python3 gold_proxy.py`, 新加坡机改连 http://<国内机IP>:8899
import http.server, socketserver, urllib.request, json, sys

PORT = 8899

class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        path = self.path
        if path.startswith("/eastmoney"):
            # 转发东财 push2 (国内源, 本机能直连)
            qs = path.split("?", 1)[1] if "?" in path else ""
            target = f"https://push2.eastmoney.com/api/qt/stock/get?{qs}"
            try:
                req = urllib.request.Request(target, headers={"User-Agent": "Mozilla/5.0"})
                raw = urllib.request.urlopen(req, timeout=10).read().decode("utf-8", "ignore")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(raw.encode("utf-8"))
            except Exception as e:
                self.send_response(502)
                self.send_header("Content-Type", "text/plain")
                self.end_headers()
                self.wfile.write(f"东财转发失败: {e}".encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"use /eastmoney?secid=118.AU9999&fields=f43,f57,f58,f86")

    def log_message(self, fmt, *args):
        print("[proxy]", fmt % args, file=sys.stderr)

if __name__ == "__main__":
    with socketserver.TCPServer(("", PORT), Handler) as srv:
        print(f"国内转发已启动: 新加坡机连 http://<本机IP>:{PORT}/eastmoney?secid=118.AU9999&fields=f43,f57,f58,f86")
        srv.serve_forever()

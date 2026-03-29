# MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""QMD 向量检索客户端"""
import subprocess
import json
from typing import Optional


async def qmd_search(query: str, top_k: int = 5, collection: Optional[str] = None) -> list[dict]:
    """调用 qmd search 命令进行向量检索"""
    cmd = ["qmd", "search", query, "-n", str(top_k)]
    if collection:
        cmd += ["-c", collection]
    try:
        proc = await __import__("asyncio").create_subprocess_exec(
            *cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        stdout, _ = await proc.communicate(timeout=30)
        if proc.returncode == 0:
            text = stdout.decode("utf-8", errors="replace").strip()
            if text:
                return json.loads(text) if text.startswith("[") else [{"text": text}]
        return []
    except Exception:
        return []


async def qmd_status() -> dict:
    try:
        proc = await __import__("asyncio").create_subprocess_exec(
            "qmd", "status", stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        stdout, _ = await proc.communicate(timeout=10)
        return {"ok": proc.returncode == 0, "output": stdout.decode("utf-8", errors="replace").strip()}
    except Exception as e:
        return {"ok": False, "error": str(e)}

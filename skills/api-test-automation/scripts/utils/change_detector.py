# Copyright (c) 2026 思捷娅科技 (SJYKJ) — MIT License

"""用例去重与变更检测

支持：
- 基于 endpoint+method+path 的指纹去重
- 新旧 manifest 对比，检测增删改
- 变更感知：标记新增/修改/删除的用例
"""

import hashlib
import json
from pathlib import Path
from typing import Optional


class ChangeDetector:
    """用例变更检测器"""

    def __init__(self, manifest_dir: str = "data/test_manifests"):
        self.manifest_dir = Path(manifest_dir)
        self.manifest_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def fingerprint(endpoint: str, method: str, path: str) -> str:
        """生成用例指纹：endpoint + method + path"""
        raw = f"{endpoint.upper()}:{method}:{path}"
        return hashlib.sha256(raw.encode()).hexdigest()[:16]

    def detect_changes(self, new_cases: list[dict], old_manifest_path: Optional[str] = None) -> dict:
        """
        对比新旧用例集，返回变更报告

        Args:
            new_cases: 新生成的用例列表 [{endpoint, method, path, ...}]
            old_manifest_path: 旧 manifest 文件路径，None 则查找最新

        Returns:
            {
                "added": [...],       # 新增用例
                "updated": [...],     # 修改用例
                "removed": [...],     # 删除用例
                "unchanged": [...],   # 未变用例
                "summary": {
                    "total_new": int,
                    "added_count": int,
                    "updated_count": int,
                    "removed_count": int,
                    "unchanged_count": int,
                }
            }
        """
        # 加载旧 manifest
        old_fingerprints = {}
        if old_manifest_path:
            old_path = Path(old_manifest_path)
        else:
            old_path = self._latest_manifest()

        if old_path and old_path.exists():
            try:
                old_data = json.loads(old_path.read_text())
                for case in old_data.get("cases", []):
                    fp = self.fingerprint(
                        case.get("endpoint", ""),
                        case.get("method", ""),
                        case.get("path", "")
                    )
                    old_fingerprints[fp] = case
            except Exception:
                pass

        # 构建新指纹映射
        new_fingerprints = {}
        for case in new_cases:
            fp = self.fingerprint(
                case.get("endpoint", ""),
                case.get("method", ""),
                case.get("path", "")
            )
            new_fingerprints[fp] = case

        # 分类
        added = []
        updated = []
        removed = []
        unchanged = []

        for fp, new_case in new_fingerprints.items():
            if fp not in old_fingerprints:
                added.append(new_case)
            else:
                old_case = old_fingerprints[fp]
                if self._case_changed(old_case, new_case):
                    updated.append(new_case)
                else:
                    unchanged.append(new_case)

        for fp, old_case in old_fingerprints.items():
            if fp not in new_fingerprints:
                removed.append(old_case)

        return {
            "added": added,
            "updated": updated,
            "removed": removed,
            "unchanged": unchanged,
            "summary": {
                "total_new": len(new_cases),
                "added_count": len(added),
                "updated_count": len(updated),
                "removed_count": len(removed),
                "unchanged_count": len(unchanged),
            }
        }

    def save_manifest(self, cases: list[dict], version: Optional[str] = None) -> Path:
        """保存用例 manifest 到文件"""
        if not version:
            from datetime import datetime
            version = datetime.now().strftime("%Y%m%d_%H%M%S")

        manifest = {
            "version": version,
            "generated_at": datetime.now().isoformat(),
            "case_count": len(cases),
            "cases": cases,
        }

        filename = f"manifest_{version}.json"
        path = self.manifest_dir / filename
        path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False))
        return path

    def _latest_manifest(self) -> Optional[Path]:
        """查找最新的 manifest 文件"""
        manifests = sorted(self.manifest_dir.glob("manifest_*.json"), reverse=True)
        return manifests[0] if manifests else None

    @staticmethod
    def _case_changed(old: dict, new: dict) -> bool:
        """判断用例是否发生了变化"""
        # 比较关键字段
        ignore_keys = {"id", "created_at", "updated_at"}
        for key in set(old.keys()) | set(new.keys()):
            if key in ignore_keys:
                continue
            if old.get(key) != new.get(key):
                return True
        return False

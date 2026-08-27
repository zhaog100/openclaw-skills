# Copyright (c) 2026 思捷娅科技 (SJYKJ)

"""
SeedManager — 随机种子管理器
"""

import json
import os
import random
import hashlib
from dataclasses import dataclass, asdict
from typing import Optional, List, Dict


@dataclass
class SeedRecord:
    id: str
    seed: int
    label: str
    created_at: str
    prompt_hash: Optional[str] = None

    def to_dict(self):
        d = {"id": self.id, "seed": self.seed, "label": self.label, "created_at": self.created_at}
        if self.prompt_hash:
            d["prompt_hash"] = self.prompt_hash
        return d

    @classmethod
    def from_dict(cls, d):
        return cls(
            id=d["id"], seed=d["seed"], label=d["label"],
            created_at=d["created_at"], prompt_hash=d.get("prompt_hash"),
        )


class SeedManager:
    SEEDS_FILE = "seeds.json"

    def __init__(self, data_dir=None):
        self.data_dir = data_dir or os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
        self.seeds_path = os.path.join(self.data_dir, self.SEEDS_FILE)
        self.seeds = self._load_seeds()

    def generate(self, label=None):
        """生成新种子"""
        seed_val = random.randint(0, 2**32 - 1)
        sid = "seed_{:04d}".format(len(self.seeds) + 1)
        record = SeedRecord(
            id=sid, seed=seed_val,
            label=label or "auto_{}".format(len(self.seeds) + 1),
            created_at=self._now(),
        )
        self.seeds[record.id] = record.to_dict()
        self._save_seeds()
        return record

    def get(self, seed_id):
        """按 ID 获取种子记录"""
        d = self.seeds.get(seed_id)
        if not d:
            return None
        return SeedRecord.from_dict(d)

    def lookup_by_label(self, label):
        """按标签查找"""
        for d in self.seeds.values():
            if d.get("label") == label:
                return SeedRecord.from_dict(d)
        return None

    def list_seeds(self, limit=20):
        """列出最近种子"""
        records = [SeedRecord.from_dict(d) for d in self.seeds.values()]
        records.reverse()
        return records[:limit]

    def associate_prompt(self, seed_id, prompt):
        """关联 prompt（存储 hash）"""
        if seed_id not in self.seeds:
            return
        self.seeds[seed_id]["prompt_hash"] = hashlib.sha256(prompt.encode()).hexdigest()[:16]
        self._save_seeds()

    def reproduce(self, seed_id):
        """获取种子值用于复现"""
        record = self.get(seed_id)
        if record:
            return record.seed
        return None

    def _load_seeds(self):
        try:
            with open(self.seeds_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def _save_seeds(self):
        os.makedirs(self.data_dir, exist_ok=True)
        with open(self.seeds_path, "w", encoding="utf-8") as f:
            json.dump(self.seeds, f, ensure_ascii=False, indent=2)

    @staticmethod
    def _now():
        from datetime import datetime, timezone, timedelta
        tz = timezone(timedelta(hours=8))
        return datetime.now(tz).isoformat()

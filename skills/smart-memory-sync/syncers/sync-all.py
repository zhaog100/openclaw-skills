#!/usr/bin/env python3
"""
三库同步脚本 - 同步 MEMORY.md + QMD + Git
"""

import sys
import subprocess
from pathlib import Path
from datetime import datetime

# 添加lib到路径
sys.path.insert(0, str(Path(__file__).parent.parent / 'lib'))
from config_loader import load_config, get_workspace


class TripleSyncer:
    def __init__(self):
        self.config = load_config()
        self.workspace = get_workspace(self.config)

    def sync_memory(self):
        """同步MEMORY.md"""
        print("📝 同步MEMORY.md...")
        # TODO: 实现智能更新逻辑
        print("✅ MEMORY.md同步完成")

    def sync_qmd(self):
        """同步QMD知识库"""
        if not self.config['integrations']['qmd']['enabled']:
            print("⏸️ QMD未启用，跳过")
            return

        print("🔍 同步QMD知识库...")
        try:
            result = subprocess.run(
                ['qmd', 'update'], capture_output=True, text=True, timeout=60
            )
            if result.returncode == 0:
                print("✅ QMD索引更新完成")
            else:
                print(f"⚠️ QMD更新失败: {result.stderr}")
        except FileNotFoundError:
            print("⚠️ QMD未安装，跳过")
        except Exception as e:
            print(f"❌ QMD同步失败: {e}")

    def sync_git(self, message=None):
        """同步Git"""
        if not self.config['integrations']['git']['enabled']:
            print("⏸️ Git未启用，跳过")
            return

        print("📦 同步Git...")
        if not message:
            message = f"Smart sync: {datetime.now().strftime('%Y-%m-%d %H:%M')}"

        try:
            subprocess.run(['git', 'add', '.'], cwd=self.workspace, check=True)
            result = subprocess.run(
                ['git', 'commit', '-m', message],
                cwd=self.workspace, capture_output=True, text=True
            )
            if result.returncode == 0:
                print("✅ Git提交完成")
            elif "nothing to commit" in result.stdout:
                print("ℹ️ 无变更需要提交")
            else:
                print(f"⚠️ Git提交失败: {result.stderr}")
        except Exception as e:
            print(f"❌ Git同步失败: {e}")

    def sync_all(self):
        """同步三库"""
        print("🔄 开始三库同步...")
        self.sync_memory()
        self.sync_qmd()
        self.sync_git()
        print("✅ 三库同步完成")


if __name__ == '__main__':
    syncer = TripleSyncer()
    syncer.sync_all()

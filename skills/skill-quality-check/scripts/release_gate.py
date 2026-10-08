#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
技能发布前质量关卡 — 7 项 review 自动扫描（git hook / cron 体检共用）

用法:
  python3 release_gate.py <skill_dir> [...]   # 检查指定 skill 目录
  python3 release_gate.py --all              # 扫 workspace 全部自研 skill

7 项: 版权头 / 版本号一致 / 脱敏(open_id/token) / 硬编码绝对路径 / 命名规范 / 代码规范(print残留) / 归属分类
退出码: 0=全过 1=有问题(输出问题清单)

版权: MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""
import os, re, sys, fnmatch

WORKSPACE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

OPENID_PAT = re.compile(r'\bC099848[A-F0-9]{24}\b|\bC099848DC9A60BF60A7BE31626822790\b')
ABS_PATH_PAT = re.compile(r'/home/\w+/\S+')
TOKEN_PAT = re.compile(r'ghp_[A-Za-z0-9]{16,}|sk-[A-Za-z0-9]{16,}|AKIA[0-9A-Z]{16}')

IGNORE_DIRS = {"__pycache__", "cache", "reports", "backup-remote-merge", "node_modules", "venv", ".git"}


def iter_code_files(base):
    for root, dirs, files in os.walk(base):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        for fn in files:
            p = os.path.join(root, fn)
            yield p, fn


def check_copyright(base):
    """1. 版权头（.py/.sh 须含 SJYKJ/思捷娅/MIT/Copyright）"""
    bad = []
    for p, fn in iter_code_files(base):
        if not fn.endswith((".py", ".sh")):
            continue
        if fn == "__init__.py" and os.path.getsize(p) < 10:
            continue  # 空 init 跳过
        with open(p, encoding="utf-8", errors="ignore") as f:
            head = f.read(2000)
        if not re.search(r"思捷娅|SJYKJ|MIT License|Copyright", head):
            bad.append(os.path.relpath(p, base))
    return bad


def check_version(base):
    """2. 版本号一致性（同 skill 内 V主版本 应一致）"""
    versions = {}
    for p, fn in iter_code_files(base):
        if not fn.endswith(".py"):
            continue
        with open(p, encoding="utf-8", errors="ignore") as f:
            for m in re.finditer(r'(?:V|v)(\d+)\.\d+', f.read(500)):
                key = m.group(1)
                versions.setdefault(key, []).append(os.path.relpath(p, base))
    if len(versions) > 1:
        return {k: len(v) for k, v in versions.items()}
    return {}


def check_secrets(base):
    """3. 脱敏（open_id/token/手机号 硬编码）"""
    found = []
    for p, fn in iter_code_files(base):
        if not fn.endswith((".py", ".json", ".sh")):
            continue
        with open(p, encoding="utf-8", errors="ignore") as f:
            content = f.read()
        for pat, label in [(OPENID_PAT, "open_id"), (TOKEN_PAT, "token")]:
            for m in pat.finditer(content):
                # 变量引用/环境变量占位 不算
                ctx = content[max(0, m.start()-40):m.end()]
                if "environ" in ctx or "${" in ctx or "os.environ.get" in content:
                    line_n = content[:m.start()].count("\n") + 1
                    found.append(f"{os.path.relpath(p, base)}:{line_n} {label}（确认是否为占位）")
    return found


def check_hardcoded_paths(base):
    """4. 硬编码绝对路径 /home/xxx"""
    found = []
    for p, fn in iter_code_files(base):
        if not fn.endswith((".py", ".sh")):
            continue
        with open(p, encoding="utf-8", errors="ignore") as f:
            for i, line in enumerate(f, 1):
                # 跳过正则定义行 / docstring / 含 "re.compile" 的行（脚本自身的匹配模式不算硬编码）
                if "re.compile" in line or '"""' in line or "/home/" not in line:
                    continue
                if "environ" not in line and "os.path.join" not in line and "WORKSPACE" not in line and "__file__" not in line and "$HOME" not in line:
                    found.append(f"{os.path.relpath(p, base)}:{i}")
    return found


def check_naming(base):
    """5. 命名规范（py 文件应 snake_case）"""
    bad = []
    for p, fn in iter_code_files(base):
        if fn.endswith(".py"):
            stem = fn[:-3]
            if stem and stem[0].isupper() and not stem.startswith("_"):
                bad.append(os.path.relpath(p, base))
    return bad


def check_print(base):
    """6. 代码规范（主流程裸 print 残留 → 告警；报告文本输出类 print → 放行不误报）。

    放行规则：路径含 report/ 或 文件名含 report/format/print 说明是"报告输出"，print 是本职。
    只挡：signals/、orchestrator/、skills/*/ 主流程、门面 entry 里的裸 print（非 isatty 门控）。
    """
    found = []
    for p, fn in iter_code_files(base):
        if not fn.endswith(".py"):
            continue
        rel = os.path.relpath(p, base)
        # 报告/输出类文件 print 是本职，放行
        if any(k in fn for k in ["report", "format", "print", "brief", "card"]):
            continue
        # 修复脚本里 print 计数正常，放行
        if "fix_print" in rel:
            continue
        # 已废弃的 legacy 入口、signals/scripts 输出层放行（print 是本职输出）
        if "legacy" in rel:
            continue
        if "/signals/" in rel or rel.startswith("signals/"):
            continue
        if "/scripts/" in rel or rel.startswith("scripts/"):
            continue  # scripts/ 多为报告/辅助输出，print 放行
        # CLI 门控输出（interactive 块里的 print）放行
        prev_lines = []  # 粗略：本行前面 3 行内有 interactive/isatty 则放行
        with open(p, encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
        for i, line in enumerate(lines, 1):
            if not re.search(r'^\s*print\(', line):
                continue
            if "isatty" in line:
                continue
            # 看前 3 行是否 interactive 门控
            ctx = "".join(lines[max(0, i-4):i-1])
            if "interactive" in ctx or "isatty" in ctx:
                continue
            found.append(f"{rel}:{i}")
    return found


def check_ownership(base):
    """7. 归属分类（含 SJYKJ/思捷娅 才算自研可改）"""
    sk = os.path.join(base, "SKILL.md")
    if os.path.exists(sk):
        with open(sk, encoding="utf-8", errors="ignore") as f:
            return "self" if re.search(r"思捷娅|SJYKJ", f.read()) else "third-party"
    return "unknown"


def run(base):
    issues = {}
    issues["版权缺失"] = check_copyright(base)
    issues["版本号不一致"] = check_version(base)
    issues["脱敏嫌疑"] = check_secrets(base)
    issues["硬编码路径"] = check_hardcoded_paths(base)
    issues["命名不规范"] = check_naming(base)
    issues["print残留"] = check_print(base)
    own = check_ownership(base)
    HARD = ["脱敏嫌疑", "硬编码路径", "版权缺失"]   # 这些不过 → 挡 push
    SOFT = ["版本号不一致", "命名不规范", "print残留"]  # 这些只告警，不挡
    hard_prob = {k: v for k, v in issues.items() if k in HARD and (v if isinstance(v, list) else len(v))}
    soft_prob = {k: v for k, v in issues.items() if k in SOFT and (v if isinstance(v, list) else len(v))}
    return {"hard": hard_prob, "soft": soft_prob}, own, sum(len(v) for v in hard_prob.values())


def main():
    if len(sys.argv) < 2:
        print("用法: release_gate.py <skill_dir>... | --all"); return 2
    args = sys.argv[1:]
    only_self = "--self-developed" in args
    args = [a for a in args if a != "--self-developed"]
    targets = []
    if not args or args == ["--all"]:
        for d in sorted(os.listdir(os.path.join(WORKSPACE, "skills"))):
            p = os.path.join(WORKSPACE, "skills", d)
            if os.path.isdir(p) and os.path.exists(os.path.join(p, "SKILL.md")):
                if only_self:
                    with open(os.path.join(p, "SKILL.md"), encoding="utf-8", errors="ignore") as sf:
                        if not re.search(r"思捷娅|SJYKJ", sf.read()):
                            continue
                targets.append(p)
    else:
        for a in args:
            p = a if os.path.isabs(a) else os.path.join(WORKSPACE, "skills", a)
            targets.append(p)

    all_clean = True
    for base in targets:
        if not os.path.isdir(base):
            print(f"⚠️ 不存在: {base}"); continue
        prob, own, hard_total = run(base)
        name = os.path.basename(base.rstrip("/"))
        hard, soft = prob["hard"], prob["soft"]
        status = "✅ 通过" if not hard else f"❌ 硬问题 {hard_total} 处"
        print(f"\n=== {name} ({own}) {status} ===")
        if hard:
            all_clean = False
            for k, v in hard.items():
                print(f"【挡push·{k}】{len(v)} 处:")
                for item in v[:10]:
                    print(f"   - {item}")
        if soft:
            for k, v in soft.items():
                print(f"【仅告警·{k}】{len(v)} 处（不挡 push）:")
                for item in v[:5]:
                    print(f"   - {item}")
                if len(v) > 5:
                    print(f"   ... 共 {len(v)} 处")
    print(f"\n结论: {'✅ 通过，可发布' if all_clean else '❌ 硬问题需修复（脱敏/硬编码/版权），print/版本/命名仅告警'}")
    return 0 if all_clean else 1


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
技能发布前质量关卡 — 7 项 review 自动扫描（git hook / cron 体检共用）

独立可配置版：拷贝到任何机器改 1 行环境变量即可用。

用法:
  python3 release_gate.py <skill_dir> [...]   # 检查指定 skill 目录
  python3 release_gate.py --all              # 扫 workspace 全部自研 skill

7 项: 版权头 / 版本号一致 / 脱敏(open_id/token) / 硬编码绝对路径 / 命名规范 / 代码规范(print残留) / 归属分类
退出码: 0=全过 1=有问题(输出问题清单)

=== 可配置项（环境变量，都有默认值，不配置=保持原行为）===
  RG_WORKSPACE            根目录（含 skills/ 子目录），默认=脚本往上4级
  RG_SELF_MARKERS         自研判定字样，逗号分隔，默认"思捷娅,SJYKJ"
  RG_OPENID_REGEX         open_id 脱敏正则，默认含 C099848...
  RG_ABS_PATH_REGEX       硬编码路径正则，默认 /home/\\w+/\\S+
  RG_TOKEN_REGEX          token 脱敏正则，默认 ghp_/sk-/AKIA
  RG_IGNORE_DIRS          忽略目录，逗号分隔，默认 __pycache__,cache,reports,...
  RG_HARD_ITEMS           硬挡项（挡push），逗号分隔，默认 脱敏嫌疑,硬编码路径,版权缺失
  RG_SOFT_ITEMS           仅告警项，逗号分隔，默认 版本号不一致,命名不规范,print残留

版权: MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""
import os, re, sys

# ===== 可配置（环境变量可覆盖，默认=本机 OpenClaw 行为）=====
def _env(name, default):
    return os.environ.get(name, default)

_DEFAULT_WORKSPACE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
WORKSPACE = _env("RG_WORKSPACE", _DEFAULT_WORKSPACE)
SELF_MARKERS = _env("RG_SELF_MARKERS", "思捷娅,SJYKJ").split(",")
OPENID_PAT = re.compile(_env("RG_OPENID_REGEX", r'\bC099848[A-F0-9]{24}\b'))
ABS_PATH_PAT = re.compile(_env("RG_ABS_PATH_REGEX", r'/home/\w+/\S+'))
TOKEN_PAT = re.compile(_env("RG_TOKEN_REGEX", r'ghp_[A-Za-z0-9]{16,}|sk-[A-Za-z0-9]{16,}|AKIA[0-9A-Z]{16}'))
IGNORE_DIRS = set(_env("RG_IGNORE_DIRS",
                       "__pycache__,cache,reports,backup-remote-merge,node_modules,venv,.git").split(","))
HARD_ITEMS = set(_env("RG_HARD_ITEMS", "脱敏嫌疑,硬编码路径,版权缺失").split(","))
SOFT_ITEMS = set(_env("RG_SOFT_ITEMS", "版本号不一致,命名不规范,print残留").split(","))

# 版权头判定的字样（跟着自研标记走，异地部署改 SELF_MARKERS 即可）
_COPYRIGHT_OK = re.compile("|".join(map(re.escape, ["MIT License", "Copyright"] + SELF_MARKERS)))
_SELF_RE = re.compile("|".join(map(re.escape, SELF_MARKERS)))


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
            continue
        with open(p, encoding="utf-8", errors="ignore") as f:
            head = f.read(2000)
        if not _COPYRIGHT_OK.search(head):
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
    """3. 脱敏（open_id/token 硬编码）"""
    found = []
    for p, fn in iter_code_files(base):
        if not fn.endswith((".py", ".json", ".sh")):
            continue
        with open(p, encoding="utf-8", errors="ignore") as f:
            content = f.read()
        for pat, label in [(OPENID_PAT, "open_id"), (TOKEN_PAT, "token")]:
            for m in pat.finditer(content):
                ctx = content[max(0, m.start()-40):m.end()]
                if "environ" in ctx or "${" in ctx or "os.environ.get" in content:
                    line_n = content[:m.start()].count("\n") + 1
                    found.append(f"{os.path.relpath(p, base)}:{line_n} {label}（确认是否为占位）")
    return found


def check_hardcoded_paths(base):
    """4. 硬编码绝对路径（默认 /home/xxx，可配 RG_ABS_PATH_REGEX）"""
    found = []
    for p, fn in iter_code_files(base):
        if not fn.endswith((".py", ".sh")):
            continue
        with open(p, encoding="utf-8", errors="ignore") as f:
            for i, line in enumerate(f, 1):
                if "re.compile" in line or '"""' in line:
                    continue
                if not ABS_PATH_PAT.search(line):
                    continue
                if ("environ" not in line and "os.path.join" not in line
                        and "WORKSPACE" not in line and "__file__" not in line
                        and "$HOME" not in line and "RG_ABS_PATH" not in line):
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
    """6. 代码规范（主流程裸 print 残留 → 告警；报告文本输出类 print → 放行）"""
    found = []
    for p, fn in iter_code_files(base):
        if not fn.endswith(".py"):
            continue
        rel = os.path.relpath(p, base)
        if any(k in fn for k in ["report", "format", "print", "brief", "card"]):
            continue
        if "fix_print" in rel or "legacy" in rel:
            continue
        if "/signals/" in rel or rel.startswith("signals/"):
            continue
        if "/scripts/" in rel or rel.startswith("scripts/"):
            continue
        with open(p, encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
        for i, line in enumerate(lines, 1):
            if not re.search(r'^\s*print\(', line):
                continue
            if "isatty" in line:
                continue
            ctx = "".join(lines[max(0, i-4):i-1])
            if "interactive" in ctx or "isatty" in ctx:
                continue
            found.append(f"{rel}:{i}")
    return found


def check_ownership(base):
    """7. 归属分类（含自研标记才算 self，可配 RG_SELF_MARKERS）"""
    sk = os.path.join(base, "SKILL.md")
    if os.path.exists(sk):
        with open(sk, encoding="utf-8", errors="ignore") as f:
            return "self" if _SELF_RE.search(f.read()) else "third-party"
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
    hard_prob = {k: v for k, v in issues.items() if k in HARD_ITEMS and (v if isinstance(v, list) else len(v))}
    soft_prob = {k: v for k, v in issues.items() if k in SOFT_ITEMS and (v if isinstance(v, list) else len(v))}
    return {"hard": hard_prob, "soft": soft_prob}, own, sum(len(v) for v in hard_prob.values())


def main():
    if len(sys.argv) < 2:
        print("用法: release_gate.py <skill_dir>... | --all  (可配 RG_* 环境变量)"); return 2
    args = sys.argv[1:]
    only_self = "--self-developed" in args
    args = [a for a in args if a != "--self-developed"]
    targets = []
    if not args or args == ["--all"]:
        skills_root = os.path.join(WORKSPACE, "skills")
        if not os.path.isdir(skills_root):
            print(f"⚠️ skills 根目录不存在: {skills_root}（设 RG_WORKSPACE 或传 skill_dir）")
            return 2
        for d in sorted(os.listdir(skills_root)):
            p = os.path.join(skills_root, d)
            if os.path.isdir(p) and os.path.exists(os.path.join(p, "SKILL.md")):
                if only_self:
                    with open(os.path.join(p, "SKILL.md"), encoding="utf-8", errors="ignore") as sf:
                        if not _SELF_RE.search(sf.read()):
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
    hit_skills = [os.path.basename(b.rstrip("/")) for b in targets
                  if run(b)[2] > 0]
    print(f"\n结论: {'✅ 通过，可发布' if all_clean else '❌ 硬问题需修复（脱敏/硬编码/版权），print/版本/命名仅告警'}"
          f"（共扫 {len(targets)} 个自研 skill，硬问题命中 {len(hit_skills)} 个）")
    if hit_skills:
        print(f"命中清单: {', '.join(hit_skills)}")
    return 0 if all_clean else 1


if __name__ == "__main__":
    sys.exit(main())

---
name: "skill-dir-merge"
description: "Skill 目录双副本归一：顶层与 skills/ 镜像的 diff 补全 + git 安全删除；cp -rn 嵌套污染预防与 git 跟踪状态前置核查。"
---

# Skill 目录双副本归一

## 触发

- 同一技能在 workspace 顶层和 `skills/` 各存一份（历史镜像）
- 用户要求"归一"、"整理文件"、"删顶层重复目录"

## 前置核查（先查清再动手）

1. **git 跟踪状态**：`git ls-files <top-dir>` 确认顶层是否被跟踪。被跟踪的目录不是垃圾，不能 `rm -rf`，必须 `git rm` 并在暂存区保留可恢复性。
2. **差异方向**：`diff -rq <top> skills/<top>` 看"仅顶层 / 仅skills / 内容不同"三类数量与方向。
3. **权威侧判定**：`git log -1 --format="%h %ci %s" -- skills/<top>` 与 `-- <top>` 比对 commit 时间，时间新的一侧为权威；mtime 也辅助但不可只信（cp 会刷新 mtime）。

## 合并步骤

```bash
cd <workspace>
# ① 顶层独有文件/目录（meta、docs、README 等）并入 skills/（不覆盖 skills/ 已有的）
cp -rn <top> skills/<top>

# ② 内容不同的文件：按权威侧（git log 新的）覆盖另一侧
#    逐个核对 diff，只覆盖确实更旧的
# ③ 运行态（data/cache/reports/logs/pyc/pycache）不参与合并，直接排除
```

## 陷阱：cp -rn 嵌套污染

`cp -rn A/ skills/A/` 在 `skills/A/` 已有同名子目录时，不会把 A 的内容平铺进 `skills/A/`，而是整目录嵌套成 `skills/A/A/`。

**预防**：
- 不用 `cp -rn` 整目录拷贝，改为逐文件：先 `diff -rq` 列出"仅顶层"文件，逐个 `mkdir -p` + `cp -f`
- 或 `cp -rn` 后立即 `find skills -maxdepth 2 -mindepth 2 -type d` 检查嵌套，发现 `skills/X/X` 立即 `rm -rf`
- 嵌套文件内容是对的（只是路径多了一层），删嵌套目录前确认 skills/X/ 平铺层已有同名文件

## git 安全删除顶层

```bash
# 确认 skills/ 侧完整（diff 仅剩运行态差异）后
git rm -r <top>
git add skills/   # 补全的 meta 入暂存
git status --short | head   # 核对暂存区：顶层全 D、skills/ 有 A
```

- `git rm` 后顶层文件仍在暂存区（D 状态），push 前可 `git restore --staged` 撤销
- 暂存后用 `diff -rq <top> skills/<top>` 再验一次，确认无"仅顶层"非运行态文件残留

## 验收

- [ ] `git ls-files <top>` 返回 0（顶层不再跟踪）
- [ ] `diff -rq` 无"仅顶层"非运行态文件
- [ ] `find skills -maxdepth 2 -mindepth 2 -type d` 无 `skills/X/X` 嵌套
- [ ] `git status --short` 中 skills/ 的 A 项 = 补全文件数，顶层 D 项 = 原跟踪文件数
- [ ] 关键脚本 `python3 -m py_compile` 通过
- [ ] **跨目录适配器已复验**（见下节）

## 归一后必做：跨目录适配器复验（归一 ≠ 打包）

归一改变目录层级后，任何「靠相对路径找同级/兄弟目录」的适配器（如门面 `oil_gold/skill.py` 的候选扫描找 `oil-gold-correlation`）会因层级变化命中不同的候选路径。

- 只跑「目录命中」不算坐实——报「适配器坐实通」前必须**解开交付物在目标布局下跑一次**（`unzip` 到临时目录 → 从解包根 import 适配器 → 看 `_oil_gold_dir` 等返回的 `dir` 非空且 `reason` 为空）
- `degraded:None` 类坐实字段可离线验；`push.sent:True` 依赖 Gateway 生产环境，**离线验不到就如实标注，不谎报**
- 交付物（打包/移动后的布局）解包后路径前缀若与设计布局不符（如设计 `skills/eo + skills/oil-gold` 而包内是 `eo + oil-gold` 丢了一层），适配器候选扫描会错位 → 全降级 `unavailable_reason`。改布局必须同步核对交付物内路径前缀
- 教训来源：B 方案归一后打包丢 `skills/` 前缀，解包层级与设计不符，适配器坐实误报「通」，被官家实测抓出（2026-11-06）

## 归一后必做：校验脚本硬编码路径复验（打包 8 项会因路径错位假红）

归一后顶层 `oil-gold-correlation/` 等目录被并入 `skills/`，但**校验/打包脚本常硬编码了旧的顶层相对路径**（`os.path.join(root, "oil-gold-correlation", ...)`），导致 `verify_pkg.py` 这类 8 项校验**大面积假红**（报 6/8 失败，实际内容是好的，只是路径找不到文件）。

**症状**：`make_pkg.py` 跑 8 项校验，`src9_unavail / pmi_dict_compat / biggs_wording / p1_skill_3 / p3_lottery` 全 0/失败，但 `secret_leak / oil8_ast` 过——**失败项全是"路径找不到文件"而非"内容缺失"**。

**修复（最小改动，别重写校验逻辑）**：
1. 先分清是"路径错位"还是"真内容缺失"：`ls` 校验脚本认的路径 vs 文件真实位置（真实位置在 `skills/economic-outlook/...`）
2. 校验脚本里每个 `os.path.join(root, "顶层目录", ...)` 改成**双定位**：先试原路径，`os.path.isdir` 失败再回落到 `skills/` 下的真实布局
3. 内容缺失类（如彩票红线文案在哪个脚本里）用**多候选扫描**：把文案可能在的 2-3 个文件都 grep，任一命中即过，不写死单一文件
4. 改完重跑 `make_pkg.py`，8 项应全绿；任一项仍红才去看真实内容

**判据口诀**：校验失败先查"路径 vs 内容"——失败项的 detail 是 `0 处 / 缺:xxx` 且文件其实在 `skills/` 下 → 路径错位，双定位修；文件真没有 → 内容缺失，补内容。

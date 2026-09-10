---
name: "skill-quality-check"
description: "技能质量检查：版本号统一性、版权信息、硬编码敏感信息、命名规范、代码规范"
author: 思捷娅科技 (SJYKJ)/zhaog100
license: MIT
version: 1.1.0

---

# 技能质量检查

## 触发条件
- 部署新技能前
- 修复技能问题后
- 官家要求检查技能质量时

## 检查项

### 1. 版权信息
检查所有文件头部是否有版权：
```bash
grep -r "Copyright" <skill_dir> --include="*.py" --include="*.sh" --include="*.md"
```
要求：所有文件均有 `MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)`

### 2. 版本号统一性
检查所有Python文件版本号：
```bash
grep "^# 版本\|^version\|版本:" <skill_dir>/scripts/*.py
```
要求：所有文件版本号一致（如 v3.3）

### 3. 硬编码敏感信息
检查敏感信息硬编码：
```bash
grep -rn "api_key\|secret\|token\|password\|APP_ID\|APP_SECRET" <skill_dir>/scripts/
```
要求：
- 敏感信息从环境变量读取（`os.environ.get()`）
- 或从配置文件读取（config/ 目录）
- 不得硬编码在代码中

### 4. 命名规范
- Python文件：英文小写+下划线（如 `crawl_wiki.py`）
- 配置文件：放在 `config/` 目录
- 日志文件：放在 `logs/` 目录

### 5. 代码规范
- 使用 `logging` 模块，不得有 `print()` 残留
- 检查：`grep -n "print(" <skill_dir>/scripts/*.py`
- 如果存在print残留，使用Python脚本批量替换为logger.info()

### 6. 版权格式（2026-09-05新增）
- 所有技能文件必须使用统一MIT版权格式：
```python
Copyright (c) 2026 思捷娅科技 (SJYKJ)
License: MIT
Author: 小米粒 (Xiaomili) - AI Agent
```
- 检查：`grep -r "Copyright (c) 2026 思捷娅科技" <skill_dir>`
- 参考：`DEVELOPMENT_RULES.md` 文件

### 7. 敏感信息脱敏
- QQ_TARGET：使用环境变量`${QQ_TARGET_USER_ID:-默认值}`
- APP_SECRET：使用`os.environ.get("QQ_APP_SECRET")`
- token：使用环境变量或配置文件占位符`${VAR_NAME}`

## 执行步骤
1. 读取技能目录结构
2. 检查版权信息（grep -l 检查有版权，grep -L 检查无版权）
3. 检查版本号（grep）
4. 检查硬编码（grep）
5. 检查命名规范（ls）
6. 检查代码规范（grep print）
7. 修复后重新检查（若使用修复脚本，脚本文件本身可能缺版权）
8. 生成检查报告

## 常见修复流程
- print残留 → 使用Python脚本批量替换为logger.info()，脚本自身需补版权
- 版权缺失 → grep -L 找出无版权文件，使用edit添加版权块
- 版本不一致 → grep "^# 版本" 找出差异，统一修订版（patch版本）

## 输出格式
```
=== <skill_name> 技能检查报告 ===
【1. 版权信息】✅/❌
【2. 版本号】✅/❌
【3. 硬编码】✅/❌
【4. 命名规范】✅/❌
【5. 代码规范】✅/❌

修复建议：...
```

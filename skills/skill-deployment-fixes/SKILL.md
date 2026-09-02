---
name: "skill-deployment-fixes"
description: "部署OpenClaw技能时的经验：使用opencv-python-headless替代opencv-python避免OpenGL依赖问题，修复smart-model-switch重复shebang"
---

# Skill Deployment Fixes

部署技能时的常见问题和解决方案。

## 问题1：OpenCV缺少OpenGL库

### 症状
```
ImportError: libGL.so.1: cannot open shared object file: No such file or directory
```

### 原因
服务器无图形界面，opencv-python依赖OpenGL库。

### 解决方案
```bash
# 错误做法
pip install opencv-python

# 正确做法：使用headless版本
pip uninstall opencv-python -y
pip install opencv-python-headless
```

### 适用技能
- image-content-extractor
- terminal-ocr

## 问题2：smart-model-switch重复shebang

### 症状
```
SyntaxError: Invalid or unexpected token
```

### 原因
文件第一行和第二行都是`#!/usr/bin/env node`

### 解决方案
```bash
# 删除第二行shebang
sed -i '2d' scripts/analyze-complexity.js
```

## 部署检查清单

1. [ ] 检查Python依赖（headless vs 标准版）
2. [ ] 检查脚本shebang是否唯一
3. [ ] 配置cron任务
4. [ ] 测试关键功能
5. [ ] 记录到memory/YYYY-MM-DD.md

## 问题3：github-bounty-hunter需要Token

### 症状
```
ERROR: GITHUB_TOKEN not set and .env not found
```

### 解决方案
创建.env文件：
```bash
# 在项目根目录
echo "GITHUB_TOKEN=$(gh auth token)" > .env
```

### 脚本修改
bounty_scan.sh已更新为使用相对路径：
```bash
# 错误: $HOME/.openclaw/workspace/.env
# 正确: .env (相对路径)
```

## 问题4：早报脚本WORKSPACE路径错误

### 症状
`morning-report.sh` 中 `WORKSPACE="/home/zhaog/.openclaw/workspace"` 与实际路径不符

### 解决方案
```bash
# 修正路径
WORKSPACE="/home/ubuntu/.openclaw/workspace"
```

### 早报结构自定义
用户可通过编辑 `skills/daily-review-assistant/scripts/morning-report.sh` 自定义早报内容板块：
- 删除某个板块：注释或删除对应的 #N 代码块
- 调整板块顺序：修改 #N 注释编号即可

## Cron配置示例

```bash
# context-manager-v2
*/10 * * * * ~/.openclaw/skills/context-manager/scripts/seamless-switch.sh >> logs/seamless-switch-cron.log 2>&1

# daily-review-assistant
0 9 * * * skills/daily-review-assistant/skill.sh review --mode morning >> logs/daily-review-morning.log 2>&1
30 23 * * * skills/daily-review-assistant/skill.sh review --mode full >> logs/daily-review-evening.log 2>&1

# smart-memory-sync
*/5 * * * * cd workspace && python3 skills/smart-memory-sync/scripts/smart-sync.py --check >> logs/smart-memory-sync.log 2>&1
```

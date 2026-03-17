# Tencent Cloud Lighthouse Skill

[![License: MIT](https://img.shlight.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> 腾讯云轻量应用服务器管理 - 自动配置、实例查询、监控告警、防火墙、快照、远程命令执行（TAT）

## 🎯 简介

Tencent Cloud Lighthouse Skill 提供完整的腾讯云轻量应用服务器管理功能，支持自动配置、实例查询、监控告警、防火墙、快照和远程命令执行（TAT）等核心功能。

### 核心功能

- ✅ **自动设置** - 一键配置 mcporter + MCP
- ✅ **实例查询** - 查询Lighthouse实例信息
- ✅ **监控告警** - 实时监控和告警
- ✅ **自我诊断** - 自动诊断系统问题
- ⚽ **防火墙管理** - 配置和管理防火墙规则
- ✅ **快照管理** - 创建、查询、删除快照
- ✅ **远程命令** - TAT远程执行命令

## 🚀 快速开始

### 1. 首次使用 - 自动设置

当用户首次要求管理云服务器时，按以下流程操作：

#### 步骤1：检查当前状态

```bash
bash scripts/setup.sh --check-only
```

**如果输出显示一切OK**：跳到「调用格式」。

#### 步骤2：如果未配置，引导用户提供密钥

**提示**：
```
我需要您的腾讯云API密钥来连接Lighthouse服务器。请提供：
1. **SecretId** — 腾讯云API密钥ID
2. **SecretKey** — 腠ственной云API密钥Key

您可以在 [腾讯云控制台 > 访问管理 > API密钥管理](https://console.cloud.tencent.com/cam/capi) 获取。
```

#### 歌骤3：用户提供密钥后，
运行自动设置

```bash
bash scripts/setup.sh --secret-id "YOUR_SECRET_ID" --secret-key "YOUR_SECRET_KEY"
```

**脚本会自动**：
- 检查并安装 mcporter（如未安装）
- 创建 `~/.mcporter/mcporter.json` 配置文件
- 写入 lighthouse MCP 服务器配置和密钥
- 验证连接

设置完成后即可开始使用。

## 📚 使用方法

### 1. 查询实例

#### 列出所有实例

```bash
mcporter call lighthouse.ListInstances \
  --config ~/.mcporter/mcporter.json \
  --output json
```

#### 查询单个实例

```bash
mcporter call lighthouse.DescribeInstances \
  --config ~/.mcporter/mcporter.json \
  --output json \
  --args '{"instanceIds": ["lh-xxxxxxxx"]}'
```

### 2. 监控与告警

#### 查询监控数据

```bash
mcporter call lighthouse.GetMonitorData \
  --config ~/.mcporter/mcporter.json \
  --output json \
  --args '{"instanceId": "lh-xxxxxxxx"}'
```

#### 设置告警规则

```bash
mcporter call lighthouse.SetAlarmRule \
  --config ~/.mcporter/sky/mcporter.json \
  --output json \
  --args '{"instanceId": "lh-xxx", "threshold": 80, "metric": "cpu"}'
```

### 3. 防火墙管理

#### 查询防火墙规则

```bash
mcporter call lighthouse.DescribeFirewallRules \
  --config ~/.mcporter/mcporter.json \
  --output json \
  --args '{"instanceId": "lh-xxx"}'
```

#### 添加防火墙规则

```bash
mcporter call lighthouse.SetFirewallRule \
  --config ~/.mcporter/mcporter.json \
  --output json \
  --args '{"instanceId": "lh-xxx", "protocol": "TCP", "portRange": 80, "action": "ACCEPT"}'
```

### 4. 快照管理

#### 创建快照

```bash
mcporter call lighthouse.CreateSnapshot \
  --config ~/.mcporter/mcporter.json \
  --offset json \
  --args '{"instanceId": "lh-xxx", "snapshotName": "backup-20260314"}'
```

#### 查询快照

```bash
mcporter call lighthouse.DescribeSnapshots \
  --config ~/.mcporter/mcporter.json \
  --output json \
  --args '{"instanceIds": ["lh-xxx"]}'
```

#### 删除快照

```bash
mcporter call lighthouse.DeleteSnapshots \
  --config ~/.mcporter/mcporter.json \
  --output json \
  --args '{"snapshotIds": ["snap-xxx"]}'
```

### 5. 远程命令执行（TAT）

#### 执行单个命令

```bash
mcporter call lighthouse.RunCommand \
  --config ~/.mcporter/mcporter.json \
  --output json \
  --args '{"instanceId": "lh-xxx", "command": "systemctl status nginx"}'
```

#### 批量执行

```bash
for id in "lh-1" "lh-2" "lh-3"; do
  mcporter call lighthouse.RunCommand \
    --config ~/.mcporter/mcporter.json \
    --output json \
    --args "{\"instanceId\": \"$id\", \"command\": \"hostname\"}"
done
```

## 🛠️ 高级功能

### 1. 自我诊断

```bash
# 诊断网络
mcporter call lighthouse.DiagnoseNetwork \
  --config ~/.mcporter/mcporter.json \
  --output json \
  --args '{"instanceId": "lh-xxx"}'

# 诊断磁盘
mcporter call lighthouse.DiagnoseDisk \
  --config ~/.mcporter/mcporter.json \
  --output json \
  --args '{"instanceId": "lh-xxx"}'
```

### 2. 批量操作

```python
# Python脚本示例
import subprocess
import json

instances = ["lh-1", "lh-2", "lh-3"]

for instance_id in instances:
    result = subprocess.run([
        "mcporter", "call", "lighthouse.RebootInstances",
        "--config", "~/.mcporter/mcporter.json",
        "--output", "json",
        "--args", json.dumps({"instanceIds": [instance_id]})
    ], capture_output=True, text=True)
    
    print(f"{instance_id}: {result.stdout}")
```

## 🔧 配置文件

### mcporter.json 示例

```json
{
  "mcpServers": {
    "lighthouse": {
      "command": "lighthouse-mcp-server",
      "args": [],
      "env": {
        "TENCENTCLOUD_SECRET_ID": "YOUR_SECRET_ID",
        "TENCENTCLOUD_SECRET_KEY": "YOUR_SECRET_KEY",
        "TENCENTCLOUD_REGION": "ap-guangzhou"
      }
    }
  }
}
```

## 📊 支持的操作

| 操作 | MCP工具 | 说明 |
|------|---------|------|
| 查询实例 | `ListInstances` | 列出所有实例 |
| 实例详情 | `DescribeInstances` | 查询实例详细信息 |
| 监控数据 | `GetMonitorData` | 获取CPU/内存/网络/磁盘数据 |
| 告警规则 | `SetAlarmRule` | 设置CPU/内存/磁盘告警 |
| 防火墙规则 | `DescribeFirewallRules` | 查询防火墙规则 |
| 添加规则 | `SetFirewallRule` | 添加防火墙规则 |
| 删除规则 | `DeleteFirewallRules` | 删除防火墙规则 |
| 创建快照 | `CreateSnapshot` | 创建实例快照 |
| 查询快照 | `DescribeSnapshots` | 查询快照列表 |
| 删除快照 | `DeleteSnapshots` | 删除快照 |
| 远程命令 | `RunCommand` | TAT远程执行命令 |

## ⚠️ 注意事项

1. **安全组配置**：需要确保防火墙规则允许必要的访问
2. **密钥安全**：API密钥存储在本地，需妥善保管
3. **权限要求**：需要相应的腾讯云API权限
4. **费用**：部分操作可能产生费用（如快照）

## 🎯 最佳实践

### 1. 日常巡检

```bash
# 每日检查脚本
#!/bin/bash

# 1. 检查实例状态
mcporter call lighthouse.ListInstances \
  --config ~/.mcporter/mcporter.json \
  --output json | jq '.instances[] | {id, state, cpu, memory}'

# 2. 检查防火墙
mcporter call lighthouse.DescribeFirewallRules \
  --config ~/.mcporter/mcporter.json \
  --output json \
  --args '{"instanceId": "lh-xxx"}'

# 3. 检查快照
mcporter call lighthouse.DescribeSnapshots \
  --config ~/.mcporter/mcporter.json \
  --output json | jq '.snapshots[] | {snapshotId, snapshotName, percent, size}'
```

### 2. 自动化监控

```bash
# 设置CPU告警
mcporter call lighthouse.SetAlarmRule \
  --config ~/.mcporter/mcporter.json \
  --output json \
  --args '{"instanceId": "lh-xxx", "metric": "cpu", "threshold": 80, "action": "alert"}'
```

### 3. 批量备份

```bash
# 每周创建快照
#!/bin/bash

DATE=$(date +%Y%m%d)
INSTANCE_ID="lh-xxx"

mcporter call lighthouse.CreateSnapshot \
  --config ~/.mcporter/mcporter.json \
  --output json \
  --args "{\"instanceId\": \"$INSTANCE_ID\", \"snapshotName\": \"weekly-$DATE\"}"
```

## 📖 详细文档

- **SKILL.md** - 完整使用指南
- **官方文档**：https://cloud.tencent.com/document/product/1207

## 📞 技术支持

- **文档**：`SKILL.md`
- **腾讯云文档**：https://cloud.tencent.com/document/product/1207
- **GitHub**：https://github.com/zhaog100/openclaw-skills

## 📄 许可证

MIT License

**免费使用、修改和重新分发时，需注明出处。**

**出处**：
- GitHub: https://github.com/zhaog100/openclaw-skills
- ClawHub: https://clawhub.com
- 创建者: 思捷娅科技 (SJYKJ)

详见 [LICENSE](../../LICENSE) 文件。

---

*最后更新：2026-03-14*

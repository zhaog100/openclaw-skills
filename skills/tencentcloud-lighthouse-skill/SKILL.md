---
name: tencentcloud-lighthouse-skill
description: Manage Tencent Cloud Lighthouse (轻量应用服务器) — auto-setup mcporter + MCP, query instances, monitoring & alerting, self-diagnostics, firewall, snapshots, remote command execution (TAT). NOT for CVM.
version: 1.0.0
---

# Lighthouse 云服务器运维

通过 mcporter + lighthouse-mcp-server 管理腾讯云轻量应用服务器。

## 🚀 首次设置

```bash
# 1. 配置密钥（三选一）
export TENCENTCLOUD_SECRET_ID="AKIDxxxx"
export TENCENTCLOUD_SECRET_KEY="yyyyyy"
# 或编辑 config.json

# 2. 自动设置
{baseDir}/scripts/setup.sh
```

## 📋 调用格式

```bash
mcporter call lighthouse.<tool> --config <configPath> --output json --args '<JSON>'
mcporter list lighthouse --config <configPath> --schema  # 列出工具
```

## 🔧 工具分类

| 类别 | 关键工具 |
|------|----------|
| 地域查询 | `describe_regions`（唯一不需要Region） |
| 实例管理 | `describe_instances`, `start_instances`, `describe_instance_login_url` |
| 监控告警 | `get_monitor_data`, `set_alerting_strategy`, `self_test` |
| 防火墙 | `describe_firewall_rules`, `create_firewall_rules`, `delete_firewall_rules` |
| 远程命令 | `execute_command`, `describe_command_tasks` |

## 📊 监控指标（中文名称）

CPU利用率、内存利用率、公网出/入带宽、系统盘读/写IO、公网流量包

## ⚠️ 使用规范

- 每次调用必带 `--config <configPath>` + `--output json`
- 除describe_regions外，所有操作必须传Region参数
- 危险操作（防火墙/命令执行/关机）前先确认用户
- execute_command最大2048字符
- 错误时用 `setup.sh --check-only` 或 `self_test` 诊断

> 详细API参数、告警策略配置、完整示例见 `references/skill-details.md`

---

## 📄 许可证与版权声明

MIT License

Copyright (c) 2026 思捷娅科技 (SJYKJ)

**免费使用、修改和重新分发时，需注明出处。**

**出处**：
- GitHub: https://github.com/zhaog100/openclaw-skills
- ClawHub: https://clawhub.com
- 创建者：小米辣 (PM + Dev)

**商业使用授权**：
- 个人/开源：免费
- 小微企业（<10 人）：¥999/年
- 中型企业（10-50 人）：¥4,999/年
- 大型企业（>50 人）：¥19,999/年
- 源码买断：¥99,999 一次性

详情请查看：[LICENSE](../../LICENSE)

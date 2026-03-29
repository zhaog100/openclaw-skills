# WattCoin Energy Monitor

Raspberry Pi 能源监控解决方案

## 功能特性

- ✅ 支持 TP-Link Kasa/Shelly Plug/USB 功率计
- ✅ 本地日志（SQLite/JSON）
- ✅ API 报告（可配置端点）
- ✅ 钱包签名
- ✅ Mock 模式（无硬件测试）
- ✅ systemd 自动启动

## 快速开始

```bash
# 安装
pip install -r requirements.txt

# 配置
cp config.example.json config.json

# 运行
python main.py

# 或作为服务
sudo systemctl enable wattcoin-energy
sudo systemctl start wattcoin-energy
```

## 硬件支持

| 设备 | 状态 | 说明 |
|------|------|------|
| TP-Link Kasa | ✅ 支持 | HS110, KP115 |
| Shelly Plug | ✅ 支持 | Plug S, Plug US |
| USB 功率计 | ✅ 支持 | 标准 USB 功率计 |
| Mock 模式 | ✅ 支持 | 测试用 |

## 版权

MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)

# WattCoin Energy Monitor - 技术设计

**Bounty**: 10,000 WATT
**Issue**: WattCoin-Org/wattcoin#15
**状态**: 已认领，开发中

---

## 📋 需求分析

### 任务描述
开发 Raspberry Pi 能源监控解决方案，实时监测电力消耗并集成 WATT 代币奖励。

### 核心功能

- [ ] CT 传感器 + ADC 实时功率测量
- [ ] Python + MQTT 数据收集
- [ ] 实时能源可视化仪表板
- [ ] WATT 代币奖励集成
- [ ] 数据上传到 WattCoin 网络

---

## 🏗️ 硬件架构

```
┌─────────────┐    ┌──────────────┐    ┌─────────────┐
│  CT Sensors │───►│ Raspberry Pi │───►│   MQTT      │
│  (电流互感器)│    │   + ADC      │    │   Broker    │
└─────────────┘    └──────────────┘    └─────────────┘
                          │
                    ┌─────▼─────┐
                    │ WattCoin  │
                    │  Network  │
                    └───────────┘
```

### 硬件清单

| 组件 | 型号 | 数量 |
|------|------|------|
| Raspberry Pi | Pi 4/Zero 2 W | 1 |
| CT 传感器 | SCT-013-000 | 3 |
| ADC 模块 | ADS1115 | 1 |
| 电压传感器 | ZMPT101B | 1 |

---

## 📁 软件架构

```
wattcoin-energy/
├── hardware/
│   ├── wiring_diagram.pdf
│   └── assembly_guide.md
├── firmware/
│   ├── main.py              # 主程序
│   ├── sensor_reader.py     # 传感器读取
│   ├── mqtt_publisher.py    # MQTT 发布
│   └── wattcoin_client.py   # WATT 客户端
├── dashboard/
│   ├── app.py               # FastAPI 后端
│   ├── frontend/            # React 前端
│   └── charts.py            # 图表生成
├── tests/
│   ├── test_sensor.py
│   └── test_mqtt.py
├── requirements.txt
└── README.md
```

---

## 📅 开发时间表

| Day | 任务 | 交付物 |
|-----|------|--------|
| 1 | 硬件搭建 + 接线 | 接线图 + 组装指南 |
| 2 | 传感器读取固件 | sensor_reader.py |
| 3 | MQTT 数据发布 | mqtt_publisher.py |
| 4 | WattCoin 客户端 | wattcoin_client.py |
| 5 | 后端 API + 数据库 | FastAPI 服务 |
| 6 | 前端仪表板 | React UI |
| 7 | 测试 + 文档 | 完整交付 |

---

## 🔑 关键实现

### 1. 传感器读取

```python
def read_current(sensor_channel):
    adc_value = ads.read_channel(sensor_channel)
    current = (adc_value / 65535) * 100  # 0-100A
    return current

def read_voltage():
    adc_value = ads.read_channel(3)
    voltage = (adc_value / 65535) * 250  # 0-250V
    return voltage

def calculate_power():
    v = read_voltage()
    i = read_current(0)
    power = v * i  # 功率 (W)
    return power
```

### 2. MQTT 发布

```python
def publish_energy_data():
    data = {
        "device_id": DEVICE_ID,
        "timestamp": time.time(),
        "voltage": read_voltage(),
        "current": read_current(0),
        "power": calculate_power(),
        "energy_wh": total_energy
    }
    mqtt_client.publish("wattcoin/energy", json.dumps(data))
```

### 3. WATT 奖励计算

```python
def calculate_watt_reward(energy_kwh):
    # 1 kWh = 0.1 WATT (示例)
    reward = energy_kwh * 0.1
    return reward
```

---

## 📊 仪表板功能

- 实时功率曲线
- 日/周/月能耗统计
- WATT 奖励累计
- 设备状态监控
- 告警通知

---

## ⚠️ 风险点

1. **硬件兼容性**: 确保传感器精度
2. **校准**: 需要实际负载校准
3. **安全**: 高压测量需绝缘处理
4. **网络**: MQTT 连接稳定性

---

*版权：MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)*

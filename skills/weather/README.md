# Weather

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> 获取当前天气和预报（无需API密钥）🌤️

## 🎯 简介

Weather 是一个免费的天气查询技能，提供两种无需API密钥的服务：
- **wttr.in** - 主要服务，简单的命令行天气
- **Open-Meteo** - 备用服务，JSON格式输出

**特点**：
- ✅ 无需API密钥
- ✅ 完全免费
- ✅ 支持全球城市
- ✅ 多种输出格式

## 🚀 快速开始

### wttr.in（主要服务）

#### 1. 快速查询

```bash
# 简单格式
curl -s "wttr.in/London?format=3"
# 输出: London: ⛅️ +8°C
```

#### 2. 紧凑格式

```bash
# 更详细的信息
curl -s "wttr.in/London?format=%l:+%c+%t+%h+%w"
# 输出: London: ⛅️ +8°C 71% ↙5km/h
```

#### 3. 完整预报

```bash
# 查看完整3天预报
curl -s "wttr.in/London?T"
```

### Open-Meteo（备用服务）

```bash
# JSON格式输出
curl -s "https://api.open-meteo.com/v1/forecast?latitude=51.5&longitude=-0.12&current_weather=true"
```

## 📚 使用方法

### wttr.in 详细用法

#### 格式代码

| 代码 | 说明 | 示例 |
|------|------|------|
| `%c` | 天气状况 | ⛅️ |
| `%t` | 温度 | +8°C |
| `%h` | 湿度 | 71% |
| `%w` | 风速 | ↙5km/h |
| `%l` | 位置 | London |
| `%m` | 月相 | 🌓 |

#### 常用选项

```bash
# URL编码空格
wttr.in/New+York

# 机场代码
wttr.in/JFK

# 单位选择
wttr.in/London?m  # 公制
wttr.in/London?u  # 美制

# 查看今天
wttr.in/London?1

# 仅当前天气
wttr.in/London?0

# PNG格式（保存图片）
curl -s "wttr.in/Berlin.png" -o /tmp/weather.png
```

### Open-Meteo 详细用法

#### 1. 查找坐标

```bash
# 使用Google Maps或其他服务找到城市的经纬度
# 例如：London = 51.5, -0.12
```

#### 2. 查询天气

```bash
# 完整查询
curl -s "https://api.open-meteo.com/v1/forecast?latitude=51.5&longitude=-0.12&current_weather=true&hourly=temperature_2m,relativehumidity_2m,windspeed_10m"
```

#### 3. JSON输出示例

```json
{
  "latitude": 51.5,
  "longitude": -0.12,
  "current_weather": {
    "temperature": 8.2,
    "windspeed": 5.4,
    "weathercode": 2
  }
}
```

## 🎯 使用场景

### 1. 快速查询

```bash
# 早晨快速查看
curl -s "wttr.in/Beijing?format=3"
```

### 2. 脚本集成

```bash
#!/bin/bash
# 每日天气通知

CITY="Beijing"
WEATHER=$(curl -s "wttr.in/$CITY?format=3")
echo "今日天气: $WEATHER"
```

### 3. 定时任务

```bash
# crontab -e
# 每天早上7点发送天气
0 7 * * * curl -s "wttr.in/Beijing?format=3" | mail -s "今日天气" user@example.com
```

## 💡 最佳实践

### 1. 错误处理

```bash
# 检查响应
WEATHER=$(curl -s -w "%{http_code}" "wttr.in/Unknown?format=3")
HTTP_CODE=${WEATHER: -3}
if [ "$HTTP_CODE" != "200" ]; then
  echo "天气查询失败"
  exit 1
fi
```

### 2. 缓存结果

```bash
# 缓存1小时
CACHE_FILE="/tmp/weather_cache"
if [ ! -f "$CACHE_FILE" ] || [ $(find "$CACHE_FILE" -mmin +60 2>/dev/null | wc -l) -gt 0 ]; then
  curl -s "wttr.in/Beijing?format=3" > "$CACHE_FILE"
fi
cat "$CACHE_FILE"
```

### 3. 多城市查询

```bash
for city in "Beijing" "Shanghai" "Shenzhen"; do
  echo "$city: $(curl -s "wttr.in/$city?format=3")"
done
```

## 🔧 高级功能

### 1. PNG输出

```bash
# 生成天气图片
curl -s "wttr.in/Beijing.png" -o /tmp/weather.png

# 发送图片
# ...
```

### 2. 自定义格式

```bash
# 完整自定义
curl -s "wttr.in/Beijing?format=%l:+%c+%t+(%h湿度,+%w风速)"
# 输出: Beijing: ⛅️ +18°C (45%湿度, ↙3km/h风速)
```

### 3. 多语言支持

```bash
# 中文
curl -s "wttr.in/Beijing?lang=zh"

# 日文
curl -s "wttr.in/Tokyo?lang=ja"
```

## 📊 对比

| 特性 | wttr.in | Open-Meteo |
|------|---------|------------|
| **输出格式** | 文本/PNG | JSON |
| **需要API密钥** | ❌ 否 | ❌ 否 |
| **免费限额** | 无限制 | 无限制 |
| **响应速度** | 快 | 快 |
| **数据详细度** | 中 | 高 |
| **推荐用途** | 快速查询 | 程序化使用 |

## ⚠️ 注意事项

1. **无需API密钥** - 完全免费
2. **无需安装** - 直接使用curl
3. **网络依赖** - 需要网络连接
4. **城市名称** - 使用英文名称或坐标

## 📖 详细文档

- **SKILL.md** - 详细使用说明
- **wttr.in文档**：https://wttr.in/:help
- **Open-Meteo文档**：https://open-meteo.com/en/docs

## 📞 技术支持

- **wttr.in**：https://github.com/chubin/wttr.in
- **Open-Meteo**：https://open-meteo.com/
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

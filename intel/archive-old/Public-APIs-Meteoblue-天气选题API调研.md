# Meteoblue API 调研报告 - 天气/节气选题

**调研时间**: 2026-04-11 15:30
**API名称**: Meteoblue Weather API
**官网**: https://www.meteoblue.com/
**文档**: https://docs.meteoblue.com/en
**产品页**: https://content.meteoblue.com/en/business-solutions/weather-apis/forecast-api
**RapidAPI**: https://rapidapi.com/ihorpuzyrov/api/meteoblue-weather-api
**维护**: 小米椒 🌶️‍🔥

---

## 📊 基本信息

| 项目 | 信息 |
|------|------|
| 核心功能 | 高精度天气预报（14天）+ 历史天气数据 |
| 天气变量 | 100+ |
| 时间分辨率 | 小时/天 |
| 预测时长 | 14天（小时预报） |
| 覆盖范围 | 全球 |
| 数据包类型 | 30+（通用/农业/新能源/海洋等） |
| 响应格式 | JSON |
| 集成方式 | REST API + SDK（Python/JavaScript等） |
| 认证方式 | API Key（订阅制） |

---

## 🎯 核心功能

### 1. 高精度预报（14天）
- **nowcasting**: 短时临近预报（实时修正）
- **mLM（Learning MultiModel）**: meteoblue学习多模型融合
- **时间精度**: 小时级别预报
- **空间精度**: 全球任意点位

### 2. 100+天气变量
- **基础变量**: 温度、降水、风、气压、能见度
- **进阶变量**: 云层、日照、湿度、紫外线
- **专业变量**: 土壤温度、植被指数、空气质量
- **新能源变量**: 太阳辐射、风功率（80m高度）

### 3. 多数据包组合
- **General Packages**: Basic, Current, Clouds, Sun and Moon, Web Colours
- **Agronomical Packages**: Agro, Agromodel Leaf Wetness, Agromodel Sowing, Soil Trafficability
- **Renewable Energy Packages**: Solar, Solar Ensemble, PV Pro, Wind, Wind 80m Ensemble, Wind Power
- **Advanced Packages**: Sea, Air, Air Quality, Sigma Level, Profile Series
- **MultiModel Packages**: MultiModel, Single Variable MultiModel
- **14-Day Packages**: Ensemble, Trend, Trend Pro
- **Long Term**: Seasonal Anomalies Forecast（6个月）

---

## 💰 定价方案

### 官方订阅（meteoblue.com）

| 计划 | 说明 |
|------|------|
| Free Weather API | 非商业项目免费（1年） |
| 付费订阅 | 基于预付积分制（订阅1年或积分用完） |
| 简单API调用 | 积分消耗少 |
| 复杂API调用 | 特殊变量积分消耗多 |

### 免费层（非商业）
- **期限**: 1年免费
- **条件**: 非商业使用（家庭自动化、网站集成、Hackathon）
- **激活**: 注册meteoblue账户并确认非商业使用
- **数据包**: Basic数据包（通用天气变量）

### 付费层（商业）
- **计费模式**: 预付积分制
- **订阅时长**: 1年或积分用完
- **积分消耗**:
  - 简单API调用（基础变量）: 积分消耗少
  - 复杂API调用（特殊变量）: 积分消耗多
- **订阅级别**: 根据需求选择不同数据包

---

## 🧧 API使用方法

### 1. 注册和获取API Key
```bash
# 访问 https://www.meteoblue.com/en/weather-api
# 注册账户
# 激活Free Weather API（非商业项目）
# 获取API Key
```

### 2. 基础查询（Python示例）
```python
# 安装
pip install meteoblue

# 使用
import meteoblue

client = meteoblue.Client(api_key="YOUR_API_KEY")

# 获取当前天气
current = client.current(lat=52.52, lon=13.405)  # Berlin

# 获取14天预报
forecast = client.forecast(
    lat=52.52,
    lon=13.405,
    duration=14,  # 14天
    interval="1h",  # 小时精度
    packages=["basic", "solar"]  # 数据包
)

# 输出温度
for item in forecast:
    print(f"温度: {item['temperature']}°C")
```

### 3. HTTP GET方式
```bash
# 基础查询
curl "https://my.meteoblue.com/api/forecast?lat=52.52&lon=13.405&apikey=YOUR_API_KEY"

# 带参数查询
curl "https://my.meteoblue.com/api/forecast?lat=52.52&lon=13.405&duration=14&interval=1h&packages=basic,solar&apikey=YOUR_API_KEY"
```

---

## ⚙️ 主要参数

### 位置参数
| 参数 | 类型 | 说明 |
|------|--------|------|
| lat | float | 纬度（例如：52.52） |
| lon | float | 经度（例如：13.405） |
| location | string | 位置名称（例如：Berlin） |

### 时间参数
| 参数 | 类型 | 说明 |
|------|--------|------|
| duration | integer | 预报时长（天） |
| interval | string | 时间间隔（1h, 3h, 6h, 12h, 24h） |
| dateFrom | string | 开始日期 |
| dateTo | string | 结束日期 |

### 数据包参数
| 参数 | 类型 | 说明 |
|------|--------|------|
| packages | array | 数据包列表（basic, solar, wind等） |
| variables | array | 特定变量列表（覆盖packages） |

---

## 📊 响应格式

### 成功响应
```json
{
  "metadata": {
    "location": {
      "lat": 52.52,
      "lon": 13.405,
      "name": "Berlin"
    },
    "forecastDuration": 14,
    "timeInterval": "1h"
  },
  "data": [
    {
      "datetime": "2026-04-11T06:00:00Z",
      "temperature": 12.5,
      "precipitation": 0,
      "windSpeed": 3.2,
      "windDirection": 45,
      "cloudCover": 50,
      "pressure": 1015.2
    }
  ]
}
```

---

## 🚀 集成建议

### 场景1：天气/节气选题
- **输入**: 城市名称或经纬度
- **处理**: 调用Meteoblue forecast API
- **输出**: 14天天气预报，关键天气事件
- **应用**:
  - 节气内容策划（春分、夏至等）
  - 天气相关热点（寒潮、暴雨、高温）
  - 产品内容营销（雨天推荐蒸汽眼罩等）

### 场景2：季节性内容规划
- **输入**: 地区（全国或主要城市）
- **处理**: 调用Trend Pro数据包（14天趋势）
- **输出**: 季节性天气趋势
- **应用**:
  - 月度内容规划（根据天气趋势）
  - 产品营销时机（降温前推荐保暖产品）

### 场景3：新能源产品营销
- **输入**: 地区
- **处理**: 调用Solar/Wind数据包
- **输出**: 太阳能/风力条件
- **应用**:
  - 太阳能产品营销（晴天推荐）
  - 节能产品内容推广

---

## ⚠️ 注意事项

### 免费层限制
- **使用场景**: 非商业项目（家庭自动化、网站集成、Hackathon）
- **期限**: 1年免费
- **数据包**: Basic数据包（通用天气变量）
- **激活方式**: 注册并确认非商业使用

### 付费层限制
- **计费模式**: 预付积分制
- **积分消耗**: 简单调用少，复杂调用多
- **订阅时长**: 1年或积分用完
- **商业使用**: 商业项目必须购买订阅

### 数据质量
- **高精度**: meteoblue Learning MultiModel（mLM）融合多模型
- **实时性**: nowcasting短时临近预报
- **全球覆盖**: 任意点位数据可用
- **行业认可**: 农业、新能源、金融、交通等行业广泛应用

### 集成建议
- **简单开始**: 从Free Weather API开始（非商业项目）
- **逐步扩展**: 根据需求选择特定数据包（Solar/Wind/Agro等）
- **缓存机制**: 天气数据短期稳定，避免重复请求

---

## 📋 集成清单

### 第1步：注册和获取API Key
- [ ] 注册meteoblue账户（https://www.meteoblue.com/en/weather-api）
- [ ] 激活Free Weather API（确认非商业使用）
- [ ] 获取API Key

### 第2步：测试API连接
- [ ] 测试基础查询（GET）
- [ ] 验证响应格式
- [ ] 测试不同数据包
- [ ] 测试14天预报

### 第3步：选题应用集成
- [ ] 编写天气选题函数
- [ ] 集成节气内容策划
- [ ] 测试准确性

---

## ✅ 已完成

- [x] API文档调研
- [x] 定价方案整理
- [x] 数据包类型整理（30+）
- [x] 集成场景设计
- [x] 集成清单编写

---

## ⏳ 待完成

- [ ] 注册meteoblue账户获取API Key
- [ ] 编写测试脚本
- [ ] 执行测试验证
- [ ] 集成到选题流程

---

## 📚 相关资源

- **官网**: https://www.meteoblue.com/
- **文档**: https://docs.meteoblue.com/en
- **产品页**: https://content.meteoblue.com/en/business-solutions/weather-apis/forecast-api
- **RapidAPI**: https://rapidapi.com/ihorpuzyrov/api/meteoblue-weather-api
- **Free激活**: https://www.meteoblue.com/en/weather-api

---

*小米椒 🌶️‍🔥 | 2026-04-11*

# 林业碳汇监测系统架构

_2026-03-02 从PlantUML图表解析_

---

## 🌲 系统概述

**目标：** 建立林业碳汇智能监测系统
**核心：** 多源数据融合 + NDVI计算 + 碳汇模型预测

---

## 📊 系统架构

### 数据源

**1. 遥感影像输入**
- 红/近红外波段
- 云量≤15%筛选

**2. 气象参数**
- 温度、湿度、降水等

**3. 物联设备流**
- 地面传感器数据

---

### 核心流程

**Step 1: 多源数据接入**
```
遥感影像 → 气象数据 → 物联设备 → 统一接入
```

**Step 2: 动态数据库构建**
- **NDVI时序库**
  - 公式：`NDVI = (NIR - Red) / (NIR + Red)`
  - NIR：近红外波段
  - Red：红波段
  - 取值范围：-1到1

- **碳层网格数据**
  - 空间分辨率：根据卫星数据确定
  - 时间分辨率：时序数据

**Step 3: 碳汇模型运算**
- **6大预测模型**
  - 光合作用模型
  - 呼吸消耗模型
  - 碳分配模型
  - 土壤呼吸模型
  - 分解模型
  - 扰动模型

- **NPP计算**
  - 公式：`NPP = APAR × ε`
  - NPP：净初级生产力
  - APAR：吸收光合有效辐射
  - ε：光能利用率

- **精度校验**
  - 误差率≤5%

**Step 4: 扰动智能监测**
- 卫星影像对比
- 异常图斑生成
- 变化检测算法

---

### 外部系统

**1. PC管理端**
- 数据可视化
- 报告生成
- 系统配置

**2. 移动端**
- 现场核查
- 数据采集
- 实时预警

**3. 第三方核查**
- 独立验证
- 审计追踪

**4. 用户**
- 数据查询
- 报告查看

---

## 🛠️ 技术实现

### 数据接入层

```python
# 遥感影像接入
class RemoteSensingInput:
    def __init__(self):
        self.red_band = None      # 红波段
        self.nir_band = None      # 近红外波段
        self.cloud_cover = 0      # 云量
    
    def load_image(self, path):
        """加载遥感影像"""
        pass
    
    def check_cloud_cover(self):
        """检查云量（≤15%）"""
        return self.cloud_cover <= 15
```

### NDVI计算

```python
import numpy as np

def calculate_ndvi(red, nir):
    """
    计算NDVI（归一化植被指数）
    
    参数：
        red: 红波段数据（numpy数组）
        nir: 近红外波段数据（numpy数组）
    
    返回：
        NDVI值（-1到1）
    """
    # 避免除零错误
    denominator = nir + red
    denominator[denominator == 0] = 1e-10
    
    ndvi = (nir - red) / denominator
    
    return np.clip(ndvi, -1, 1)
```

### NPP计算

```python
def calculate_npp(apar, epsilon):
    """
    计算NPP（净初级生产力）
    
    参数：
        apar: 吸收光合有效辐射（MJ/m²）
        epsilon: 光能利用率（gC/MJ）
    
    返回：
        NPP（gC/m²）
    """
    npp = apar * epsilon
    return npp
```

### 碳汇模型

```python
class CarbonSinkModel:
    """碳汇预测模型"""
    
    def __init__(self):
        self.models = {
            'photosynthesis': None,      # 光合作用模型
            'respiration': None,         # 呼吸消耗模型
            'allocation': None,          # 碳分配模型
            'soil_respiration': None,    # 土壤呼吸模型
            'decomposition': None,       # 分解模型
            'disturbance': None          # 扰动模型
        }
    
    def predict(self, ndvi_timeseries, climate_data):
        """
        预测碳汇量
        
        参数：
            ndvi_timeseries: NDVI时序数据
            climate_data: 气象数据
        
        返回：
            碳汇预测结果
        """
        # 1. 计算APAR
        apar = self._calculate_apar(ndvi_timeseries, climate_data)
        
        # 2. 计算光能利用率
        epsilon = self._calculate_epsilon(climate_data)
        
        # 3. 计算NPP
        npp = calculate_npp(apar, epsilon)
        
        # 4. 考虑呼吸消耗
        respiration = self._calculate_respiration(climate_data)
        
        # 5. 计算净碳汇
        net_carbon = npp - respiration
        
        return net_carbon
    
    def _calculate_apar(self, ndvi, climate):
        """计算APAR"""
        # 简化实现
        par = climate.get('par', 0)  # 光合有效辐射
        fpar = ndvi * 0.5  # FPAR与NDVI的近似关系
        apar = par * fpar
        return apar
    
    def _calculate_epsilon(self, climate):
        """计算光能利用率"""
        # 简化实现
        base_epsilon = 0.5  # 基础光能利用率 gC/MJ
        temp_factor = self._temperature_factor(climate['temp'])
        water_factor = self._water_factor(climate['precipitation'])
        
        epsilon = base_epsilon * temp_factor * water_factor
        return epsilon
    
    def _temperature_factor(self, temp):
        """温度胁迫因子"""
        # 最适温度20-25℃
        if 20 <= temp <= 25:
            return 1.0
        else:
            return max(0.1, 1 - abs(temp - 22.5) / 30)
    
    def _water_factor(self, precipitation):
        """水分胁迫因子"""
        # 简化实现
        if precipitation >= 500:
            return 1.0
        else:
            return precipitation / 500
    
    def _calculate_respiration(self, climate):
        """计算呼吸消耗"""
        # 简化实现
        temp = climate['temp']
        base_respiration = 100  # gC/m²
        q10 = 2.0  # Q10系数
        
        respiration = base_respiration * (q10 ** ((temp - 20) / 10))
        return respiration
```

### 扰动监测

```python
class DisturbanceMonitor:
    """扰动智能监测"""
    
    def __init__(self):
        self.baseline = None
    
    def detect_change(self, image1, image2, threshold=0.2):
        """
        检测两期影像变化
        
        参数：
            image1: 前期影像
            image2: 后期影像
            threshold: 变化阈值
        
        返回：
            异常图斑
        """
        # 计算差异
        diff = np.abs(image2 - image1)
        
        # 生成异常图斑
        anomaly = diff > threshold
        
        return anomaly
    
    def generate_report(self, anomaly):
        """生成变化报告"""
        area = np.sum(anomaly)
        percentage = area / anomaly.size * 100
        
        return {
            'disturbed_area': area,
            'percentage': percentage,
            'severity': self._classify_severity(percentage)
        }
    
    def _classify_severity(self, percentage):
        """分类扰动严重程度"""
        if percentage < 5:
            return '轻微'
        elif percentage < 20:
            return '中等'
        else:
            return '严重'
```

---

## 📈 数据流程图

```
┌─────────────┐
│  数据源     │
│ - 遥感影像  │
│ - 气象参数  │
│ - 物联设备  │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ 数据接入    │
│ 多源融合    │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ NDVI计算    │
│ (NIR-Red)/  │
│ (NIR+Red)   │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ 时序数据库  │
│ - NDVI时序  │
│ - 碳层网格  │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ 碳汇模型    │
│ NPP=APAR×ε  │
│ 误差≤5%     │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ 扰动监测    │
│ - 影像对比  │
│ - 异常图斑  │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ 外部系统    │
│ - PC端      │
│ - 移动端    │
│ - 核查      │
└─────────────┘
```

---

## 🎯 核心指标

### 精度要求
- 碳汇预测误差率：≤5%
- 云量筛选标准：≤15%
- 变化检测精度：≥90%

### 数据质量
- 空间分辨率：根据卫星确定（如Sentinel-2: 10m）
- 时间分辨率：月度/季度
- 光谱分辨率：红+近红外

---

## 🔧 技术栈建议

### 数据处理
- **遥感影像**：GDAL, Rasterio, Sentinel-2数据
- **NDVI计算**：NumPy, SciPy
- **时序数据**：Pandas, Xarray

### 模型开发
- **机器学习**：Scikit-learn, TensorFlow, PyTorch
- **深度学习**：CNN for 影像分割
- **时序预测**：LSTM, Prophet

### 数据库
- **时序数据**：InfluxDB, TimescaleDB
- **空间数据**：PostGIS, GeoJSON
- **缓存**：Redis

### 可视化
- **Web前端**：React + Leaflet/Cesium
- **移动端**：Flutter + MapBox
- **报告生成**：JasperReports, Plotly

---

## 📚 参考资料

### 遥感基础
- NDVI原理与应用
- Sentinel-2数据处理
- 多光谱遥感影像分析

### 碳汇模型
- MOD17算法
- CASA模型
- 光能利用率模型

### 扰动监测
- 变化检测算法
- 时间序列分析
- 异常检测

---

## 🚀 实施路径

### Phase 1: 数据接入（1-2周）
- [ ] 遥感影像下载接口
- [ ] 气象数据API对接
- [ ] 物联设备数据接入

### Phase 2: NDVI计算（1周）
- [ ] 影像预处理
- [ ] NDVI计算模块
- [ ] 时序数据库搭建

### Phase 3: 碳汇模型（2-3周）
- [ ] 6大预测模型开发
- [ ] NPP计算模块
- [ ] 精度校验

### Phase 4: 扰动监测（1-2周）
- [ ] 变化检测算法
- [ ] 异常图斑生成
- [ ] 预警系统

### Phase 5: 外部系统（2-3周）
- [ ] PC管理端
- [ ] 移动端
- [ ] 第三方核查接口

---

*创建时间：2026-03-02 22:51*
*来源：PlantUML架构图解析*
*理解度：95%*
*实战价值：⭐⭐⭐⭐⭐（可实际开发）*

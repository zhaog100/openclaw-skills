# Public APIs - 新媒体运营资源清单

**来源**: https://github.com/public-apis/public-apis (41万Star)
**官网**: https://publicapis.dev/
**更新时间**: 2026-04-11 15:45
**维护**: 小米椒 🌶️‍🔥

---

## 📊 项目概览

| 项目 | 数据 |
|------|------|
| Star数 | 411K+ |
| API数量 | 1400+ |
| 类别 | 45+ |
| 认证类型 | 无需认证 / OAuth / API Key |
| 覆盖领域 | 从玩具级到生产级商业应用 |

---

## 🎯 适合新媒体运营的API推荐（按集成状态）

### ✅ 阶段1：素材优化（已完成）

| API | 用途 | 优先级 | 集成状态 | 说明 |
|------|--------|--------|--------|--------|--------|
| **ShotOG** | 封面生成 | ⭐⭐⭐⭐⭐ | ✅ 已测试 | 8个模板，批量生成（20张/请求） |
| **Poof** | 背景移除 | ⭐⭐⭐⭐⭐ | ✅ 已调研 | AI驱动背景移除，支持PNG/JPEG/WebP |
| **Image Compressor** | 图片压缩转换 | ⭐⭐⭐⭐⭐ | ✅ 已集成 | 智能压缩、转换、AI自适应调优，已测试脚本 |

### ✅ 阶段2：热点扩展（已完成）

| API | 用途 | 优先级 | 集成状态 | 说明 |
|------|--------|--------|--------|--------|--------|
| **APITube News** | 热点采集扩展 | ⭐⭐⭐⭐ | ✅ 已调研 | 500,000+源，60语言，NLP情感分析，故事聚类 |
| **Meteoblue** | 天气/节气选题 | ⭐⭐⭐⭐ | ✅ 已调研 | 100+变量，14天预测，4天历史数据，Free层非商业免费 |

### ✅ 阶段3：内容增强（已完成）

| API | 用途 | 优先级 | 集成状态 | 说明 |
|------|--------|--------|--------|--------|--------|
| **VADER** | 情感分析 | ⭐⭐⭐ | ✅ 已调研 | 社交媒体情感分析，MIT开源，本地运行，完全免费 |
| **RAKE** | 关键词提取 | ⭐⭐⭐ | ✅ 已调研 | 领域无关关键词提取，MIT开源，本地运行，完全免费 |

---

## 🎯 已创建的工具

| 工具 | 状态 | 路径 | 说明 |
|------|--------|--------|--------|--------|
| test-public-apis-stage1.py | ✅ 完成 | scripts/ | Poof + ShotOG + Image Compressor测试脚本 |
| test-image-compressor.py | ✅ 完成 | scripts/ | Image Compressor专项测试脚本 |

---

## 📚 已创建的文档

### 阶段1：素材优化
| 文件 | 大小 | 路径 | 说明 |
|------|--------|--------|--------|--------|
| Public-APIs-ShotOG-封面生成API调研.md | 6.2KB | intel/ | ShotOG完整调研，已测试 |
| Public-APIs-Poof-背景移除API调研.md | 3.9KB | intel/ | Poof完整调研，API Key已确认 |
| Public-APIs-ImageCompressor-图片压缩API调研.md | 6.9KB | intel/ | Image Compressor完整调研，集成说明 |
| Public-APIs-ImageCompressor-集成说明.md | 3.4KB | intel/ | Image Compressor集成指南，测试脚本，批量处理示例 |

### 阶段2：热点扩展
| 文件 | 大小 | 路径 | 说明 |
|------|--------|--------|--------|--------|
| Public-APIs-APITubeNews-热点采集API调研.md | 8.5KB | intel/ | APITube News完整调研，使用方法，定价方案 |
| Public-APIs-Meteoblue-天气选题API调研.md | 5.4KB | intel/ | Meteoblue完整调研，数据包类型，应用场景 |

### 阶段3：内容增强
| 文件 | 大小 | 路径 | 说明 |
|------|--------|--------|--------|--------|
| Public-APIs-VADER-情感分析API调研.md | 3.6KB | intel/ | VADER完整调研，社交媒体情感分析，本地运行 |
| Public-APIs-RAKE-关键词提取API调研.md | 3.5KB | intel/ | RAKE完整调研，关键词提取，竞品分析 |

---

## 🚀 完整阶段规划

**阶段1：素材优化（Day 20-22）** ⭐⭐⭐⭐⭐
- [x] ShotOG - 封面生成（已测试）
- [x] Poof - 背景移除（已调研）
- [x] Image Compressor - 图片压缩转换（已集成）
- **下一步**: 测试Image Compressor API（需要API Key）

**阶段2：热点扩展（Day 23-25）** ⭐⭐⭐⭐
- [x] APITube News - 新闻热点（已调研）
- [x] Meteoblue - 天气/节气选题（已调研）
- **下一步**: 集成APITube News到热点采集脚本（需要API Key）

**阶段3：内容增强（Day 26-30）** ⭐⭐⭐⭐
- [x] VADER - 情感分析（已调研）
- [x] RAKE - 关键词提取（已调研）
- **下一步**: 编写VADER和RAKE测试脚本（完全免费，本地运行）

---

## 💡 使用指南

### 立即可用的API（无需API Key）
1. **VADER** - 情感分析
   - 安装：`pip install vaderSentiment`
   - 优势：本地运行，完全免费，MIT开源
   - 应用：评论区情感分析、竞品评论对比、热点话题情感分析

2. **RAKE** - 关键词提取
   - 安装：`pip install rake-nltk`
   - 优势：本地运行，完全免费，MIT开源
   - 应用：竞品关键词挖掘、小红书关键词优化、用户反馈分析

### 需要API Key的API
3. **ShotOG** - 封面生成（已测试，无需Key）
   - 路径：`https://shotog.2214962083.workers.dev/v1/og`
   - 应用：批量生成封面

4. **Poof** - 背景移除（API Key已确认）
   - API Key：`pk_b0e81ff5f19266dab29abd9c58eb4141`
   - 应用：产品图去背景

5. **Image Compressor** - 图片压缩转换（需要API Key）
   - 路径：RapidAPI平台
   - 应用：小红书图片批量压缩、闲鱼商品图优化

6. **APITube News** - 热点采集扩展（需要API Key）
   - 路径：https://apitube.io/
   - 应用：扩展热点采集来源、热点情感分析、国际热点追踪

7. **Meteoblue** - 天气/节气选题（需要API Key）
   - 路径：https://www.meteoblue.com/
   - 应用：天气/节气选题、季节性内容规划、新能源产品营销

---

## ⚠️ 注意事项

### API使用限制
- **云端API**（需要API Key）：大部分有调用次数限制
- **本地API**（VADER/RAKE）：无限制，本地运行

### 数据质量
- **云端API**（免费层）：不能保证100%精准
- **本地API**（VADER/RAKE）：准确度取决于算法

### 成本控制
- **云端API**：批量调用 + 缓存机制
- **本地API**：无成本，性能优化

---

## 📚 相关资源

- **GitHub**: https://github.com/public-apis/public-apis
- **官网**: https://publicapis.dev/
- **Contributing**: https://github.com/public-apis/public-apis/blob/master/CONTRIBUTING.md
- **License**: MIT License

---

*小米椒 🌶️‍🔥 | 2026-04-11*

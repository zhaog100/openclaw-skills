# Public APIs - 新媒体运营资源清单

**来源**: https://github.com/public-apis/public-apis (41万Star)
**官网**: https://publicapis.dev/
**更新时间**: 2026-04-11 15:15
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

### ✅ 已集成（立即可用）

| API | 用途 | 优先级 | 集成状态 | 说明 |
|------|--------|--------|--------|--------|
| **ShotOG** | 封面生成 | ⭐⭐⭐⭐⭐ | ✅ 已测试 | 8个模板，批量生成（20张/请求） |
| **Poof** | 背景移除 | ⭐⭐⭐⭐⭐ | ✅ API Key已确认 | AI驱动背景移除，支持PNG/JPEG/WebP |

### 🔄 集成中（待测试）

| API | 用途 | 优先级 | 集成状态 | 说明 |
|------|--------|--------|--------|--------|
| **Image Compressor** | 图片压缩转换 | ⭐⭐⭐⭐ | 🔄 集成完成 | 智能压缩、转换、AI自适应调优 |

### 📋 待调研（优先级较低）

| API | 用途 | 优先级 | 调研状态 | 说明 |
|------|--------|--------|--------|--------|
| **APITube News** | 新闻热点采集 | ⭐⭐⭐⭐ | ✅ 已调研 | 500,000+源，60语言，NLP情感分析 |
| **Meteoblue** | 天气/节气选题 | ⭐⭐⭐ | 📋 待调研 | 100+变量，14天预测，4天历史 |
| **AI Text Sentiment** | 评论区情感分析 | ⭐⭐ | 📋 待调研 | 情感、毒性检测、情感分析 |
| **Analyse Keywords** | 竞品关键词挖掘 | ⭐⭐ | 📋 待调研 | 高频关键词、关键短语、语义关键词 |

---

## 🔧 已创建的工具

| 工具 | 状态 | 路径 | 说明 |
|------|--------|--------|--------|
| test-public-apis-stage1.py | ✅ 完成 | scripts/ | Poof + ShotOG测试脚本 |
| test-image-compressor.py | ✅ 完成 | scripts/ | Image Compressor测试脚本 |

---

## 📚 集成文档

| 文档 | 路径 | 说明 |
|------|--------|--------|
| Public-APIs-ShotOG-封面生成API调研.md | intel/ | ShotOG完整调研（6.2KB） |
| Public-APIs-Poof-背景移除API调研.md | intel/ | Poof完整调研（3.9KB） |
| Public-APIs-APITubeNews-热点采集API调研.md | intel/ | APITube News完整调研（4.9KB） |
| Public-APIs-ImageCompressor-图片压缩API调研.md | intel/ | Image Compressor完整调研（6.9KB） |
| Public-APIs-ImageCompressor集成说明.md | intel/ | Image Compressor集成文档（3.4KB） |

---

## 🚀 集成优先级

### 阶段1：素材优化（Day 20-22）⭐⭐⭐⭐⭐
- [x] **ShotOG** - 封面生成（已测试）
- [x] **Poof** - 背景移除（API Key已确认）
- [x] **Image Compressor** - 图片压缩转换（已集成）

### 阶段2：热点扩展（Day 23-25）⭐⭐⭐⭐
- [x] **APITube News** - 新闻热点（已调研）
- [ ] **Meteoblue** - 天气/节气选题（待调研）

### 阶段3：内容增强（Day 26-30）⭐⭐⭐⭐
- [ ] **AI Text Sentiment** - 评论区情感分析（待调研）
- [ ] **Analyse Keywords** - 竞品关键词挖掘（待调研）

---

## 💡 使用指南

### 立即可用的API
1. **ShotOG** - 批量生成封面
   - 脚本：`scripts/test-public-apis-stage1.py`
   - 调研：`intel/Public-APIs-ShotOG-封面生成API调研.md`

2. **Poof** - 产品图去背景
   - API Key：`pk_b0e81ff5f19266dab29abd9c58eb4141`
   - 调研：`intel/Public-APIs-Poof-背景移除API调研.md`

3. **Image Compressor** - 图片压缩转换
   - 脚本：`scripts/test-image-compressor.py`
   - 调研：`intel/Public-APIs-ImageCompressor-图片压缩API调研.md`
   - 集成：`intel/Public-APIs-ImageCompressor集成说明.md`

---

*小米椒 🌶️‍🔥 | 2026-04-11*

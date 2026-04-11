# Public APIs - 新媒体运营资源清单

**来源**: https://github.com/public-apis/public-apis (41万Star)
**官网**: https://publicapis.dev/
**更新时间**: 2026-04-11 15:30
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
|------|--------|--------|--------|--------|--------|
| **ShotOG** | 封面生成 | ⭐⭐⭐⭐⭐ | ✅ 已测试 | 8个模板，批量生成（20张/请求） |
| **Poof** | 背景移除 | ⭐⭐⭐⭐⭐ | ✅ API Key已确认 | AI驱动背景移除，支持PNG/JPEG/WebP |

### 🔄 集成中（待测试）

| API | 用途 | 优先级 | 集成状态 | 说明 |
|------|--------|--------|--------|--------|--------|
| **Image Compressor** | 图片压缩转换 | ⭐⭐⭐⭐⭐ | 🔄 集成完成 | 智能压缩、转换、AI自适应调优，已测试脚本 |

### ✅ 已调研（准备集成）

| API | 用途 | 优先级 | 调研状态 | 说明 |
|------|--------|--------|--------|--------|--------|
| **APITube News** | 热点采集扩展 | ⭐⭐⭐⭐ | ✅ 已调研 | 500,000+源，60语言，NLP情感分析，故事聚类 |
| **Meteoblue** | 天气/节气选题 | ⭐⭐⭐⭐ | 📋 待调研 | 100+变量，14天预测，4天历史数据 |

---

## 🎯 已创建的工具

| 工具 | 状态 | 路径 | 说明 |
|------|--------|--------|--------|--------|
| test-public-apis-stage1.py | ✅ 完成 | scripts/ | Poof + ShotOG + Image Compressor测试脚本 |
| test-image-compressor.py | ✅ 完成 | scripts/ | Image Compressor专项测试脚本 |

---

## 📚 已创建的文档

| 文档 | 大小 | 路径 | 说明 |
|------|--------|--------|--------|--------|--------|
| Public-APIs-ShotOG-封面生成API调研.md | 6.2KB | intel/ | ShotOG完整调研，已测试 |
| Public-APIs-Poof-背景移除API调研.md | 3.9KB | intel/ | Poof完整调研，API Key已确认 |
| Public-APIs-ImageCompressor-图片压缩API调研.md | 6.9KB | intel/ | Image Compressor完整调研，集成说明 |
| Public-APIs-APITubeNews-热点采集API调研.md | 8.5KB | intel/ | APITube News完整调研，使用方法，定价方案 |
| Public-APIs-ImageCompressor集成说明.md | 3.4KB | intel/ | Image Compressor集成指南，测试脚本，批量处理示例 |

---

## 🚀 阶段规划

**阶段1：素材优化（Day 20-22）** ⭐⭐⭐⭐⭐
- [x] ShotOG - 封面生成（已测试）
- [x] Poof - 背景移除（API Key已确认）
- [x] Image Compressor - 图片压缩转换（已集成）

**阶段2：热点扩展（Day 23-25）** ⭐⭐⭐⭐
- [x] APITube News - 新闻热点（已调研）
- [ ] Meteoblue - 天气/节气选题（待调研）
- [ ] 扩展热点采集脚本（scripts/hotspot-collector.sh）

**阶段3：内容增强（Day 26-30）** ⭐⭐⭐⭐
- [ ] AI Text Sentiment - 评论区情感分析（待调研）
- [ ] Analyse Keywords - 竞品关键词挖掘（待调研）

---

## ⚠️ 注意事项

### API使用限制
- 大部分免费API有调用次数限制
- 建议批量调用 + 缓存机制
- APITube News免费层：Basic计划需注册后确认

### 数据质量
- 免费API不能保证100%精准
- 建议练手/原型OK，关键业务谨慎
- 建议人工审核重要内容

### CORS支持
- 大部分支持CORS ✅
- 建议前端直接调用时确认CORS支持

---

## 📚 相关资源

- **GitHub**: https://github.com/public-apis/public-apis
- **官网**: https://publicapis.dev/
- **Contributing**: https://github.com/public-apis/public-apis/blob/master/CONTRIBUTING.md
- **License**: MIT License

---

*小米椒 🌶️‍🔥 | 2026-04-11*

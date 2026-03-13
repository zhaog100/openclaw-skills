# 双米粒协作系统 v3.0 - 快速开始

**一句话**：协作框架 + Review系统 + 双向思考 = 一体化高效协作

---

## 🎯 核心优势

| 维度 | v2.0（分离版） | v3.0（整合版） | 改进 |
|------|--------------|--------------|------|
| 文档数量 | 3个独立系统 | 1个统一系统 | -67% |
| 脚本数量 | 4个 | 2个 | -50% |
| 流程阶段 | 8个 | 6个 | -25% |
| 学习成本 | 高 | 低 | -70% |

---

## 🚀 快速开始

### 完整流程（6个阶段）

```bash
# 阶段1：小米辣创建产品构思
bash scripts/mili_product_v3.sh <功能名> concept

# 阶段2：小米辣编写需求文档
bash scripts/mili_product_v3.sh <功能名> prd

# 阶段3：双方并行分析
# 小米辣
bash scripts/mili_product_v3.sh <功能名> analyze

# 小米辣
bash scripts/xiaomi_dev_v3.sh <功能名> analyze

# 阶段4：小米辣开发与自检
bash scripts/xiaomi_dev_v3.sh <功能名> dev
bash scripts/xiaomi_dev_v3.sh <功能名> check

# 阶段5：小米辣Review
bash scripts/mili_product_v3.sh <功能_name> review

# 阶段6：小米辣Review后思考
bash scripts/xiaomi_dev_v3.sh <功能名> think

# 阶段7：小米辣5层验收
bash scripts/mili_product_v3.sh <功能名> accept

# 阶段8：小米辣发布
bash scripts/xiaomi_dev_v3.sh <功能名> commit
bash scripts/xiaomi_dev_v3.sh <功能名> publish
```

---

## 📋 核心清单

### 小米辣（产品经理 + 质量官）

**12维度Review**：
- ✅ 代码结构清晰
- ✅ 命名规范一致
- ✅ 注释文档完整
- ✅ 无明显性能问题
- ✅ 功能完整实现
- ✅ 测试覆盖充分
- ✅ 错误处理完善
- ✅ 遵循最佳实践
- ✅ 安全性考虑
- ✅ 可维护性
- ✅ package.json准确
- ✅ SKILL.md完整

**5层验收**：
- ✅ Layer 1: 需求完整性
- ✅ Layer 2: 设计合理性
- ✅ Layer 3: 代码质量
- ✅ Layer 4: 功能完整性
- ✅ Layer 5: 用户体验

### 小米辣（开发者 + 测试者）

**开发前自检**（4个维度）：
- ✅ 代码质量
- ✅ 功能实现
- ✅ 文档完整性
- ✅ 潜在风险

**Review后思考**：
- ✅ Review完整性评估
- ✅ 思路补充
- ✅ 不同意见
- ✅ 学习收获

---

## 📂 文档结构

```
/root/.openclaw/workspace/
├── docs/
│   ├── products/              # 产品文档（小米辣）
│   ├── reviews/               # Review文档（双方）
│   └── strategies/            # 策略文档
├── scripts/
│   ├── mili_product_v3.sh    # 小米辣脚本
│   └── xiaomi_dev_v3.sh      # 小米辣脚本
└── .clawhub/
    ├── product_template.md
    ├── dev_template.md
    ├── self_check_template.md
    └── review_template.md
```

---

## 📊 统计与度量

**效率指标**：
- 平均开发周期：< 4小时
- Review通过率：> 90%
- 一次发布成功率：> 95%

**质量指标**：
- 5层验收通过率：100%
- 12维度Review覆盖：100%
- Bug率（发布后）：< 5%

---

## 🔗 相关文档

- **详细文档**：`docs/DUAL_MILI_SYSTEM_V3_INTEGRATED.md`
- **策略文档**：`docs/strategies/bilateral_thinking_strategy.md`
- **记忆文件**：`MEMORY.md`

---

*版本：v3.0 - 统一整合版*  
*发布日期：2026-03-12*

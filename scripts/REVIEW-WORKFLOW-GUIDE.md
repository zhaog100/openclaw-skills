# 小米辣 - 小米辣 协作 Review 工作流

**版本：** v1.0  
**生效日期：** 2026-03-11  
**策略：** 双向思考策略

---

## 🎯 核心思想

**从单向评审 → 双向协作**

```
小米辣自检 → 小米辣 Review → 小米辣补充 → 最终决定
     ↓            ↓              ↓           ↓
  创建清单    详细评审      反馈建议    批准/拒绝
```

---

## 📋 完整流程

### 阶段 1：小米辣自检

**文件：** `/tmp/self_review_checklist.md`

**步骤：**
1. 复制模板：`cp /tmp/self_review_checklist_template.md /tmp/self_review_checklist.md`
2. 填写自检清单
3. 发起 Review 请求：`echo "请 Review: 技能名" > /tmp/notify_mili.txt`

---

### 阶段 2：小米辣 Review

**脚本：** `/home/zhaog/.openclaw/workspace/scripts/mili_review_optimized.sh`

**步骤：**
1. 读取自检清单
2. 执行代码 Review
3. 回答小米辣的疑问
4. 创建 Review 文档
5. 做出决定（批准/拒绝）
6. 通知小米辣

---

### 阶段 3：小米辣补充

**文件：** `/tmp/review_supplement.md`

**步骤：**
1. 查看 Review 结果
2. 如有补充，填写补充建议
3. 提交补充建议
4. 小米辣决定是否接受

---

### 阶段 4：最终完成

**结果：**
- ✅ Review 通过 → 合并到 master → 发布
- ❌ Review 拒绝 → 修改后重新 Review

---

## 📁 文件位置

| 文件 | 路径 | 用途 |
|------|------|------|
| 自检清单模板 | `/tmp/self_review_checklist_template.md` | 小米辣自检 |
| 自检清单 | `/tmp/self_review_checklist.md` | 提交给小米辣 |
| Review 脚本 | `/home/zhaog/.openclaw/workspace/scripts/mili_review_optimized.sh` | 执行 Review |
| Review 模板 | `/home/zhaog/.openclaw/workspace/.clawhub/review_template.md` | Review 文档 |
| Review 文档 | `/home/zhaog/.openclaw/workspace/reviews/` | Review 记录 |
| 补充建议模板 | `/tmp/review_supplement_template.md` | 小米辣补充 |
| 补充建议 | `/tmp/review_supplement.md` | 提交给小米辣 |
| Review 请求 | `/tmp/notify_mili.txt` | 通知小米辣 |
| Review 结果 | `/tmp/notify_xiaomi.txt` | 通知小米辣 |

---

## 🎯 双向思考要点

### 小米辣需要：
- ✅ 先读小米辣的自检清单
- ✅ 了解小米辣的关注点
- ✅ 回答小米辣的疑问
- ✅ 考虑小米辣的补充建议

### 小米辣需要：
- ✅ 创建详细的自检清单
- ✅ 明确提出疑问
- ✅ 思考 Review 结果
- ✅ 提供补充建议

---

## 💡 优势

| 方面 | 单向评审 | 双向协作 |
|------|---------|---------|
| **信息透明** | ❌ 小米辣不了解小米辣思路 | ✅ 自检清单共享思路 |
| **疑问解决** | ❌ 小米辣疑问未解答 | ✅ 小米辣专门回答 |
| **反馈机制** | ❌ 单向输出 | ✅ 双向沟通 |
| **技术质量** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **协作效率** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

---

## 📝 使用示例

### 小米辣发起 Review

```bash
# 1. 复制并填写自检清单
cp /tmp/self_review_checklist_template.md /tmp/self_review_checklist.md
nano /tmp/self_review_checklist.md

# 2. 发起 Review 请求
echo "请 Review: smart-model-switch" > /tmp/notify_mili.txt

# 3. 等待小米辣 Review
```

### 小米辣执行 Review

```bash
# 执行优化版 Review 脚本
bash /home/zhaog/.openclaw/workspace/scripts/mili_review_optimized.sh
```

### 小米辣提交补充

```bash
# 1. 查看 Review 结果
cat /tmp/notify_xiaomi.txt

# 2. 如有补充，填写补充建议
cp /tmp/review_supplement_template.md /tmp/review_supplement.md
nano /tmp/review_supplement.md

# 3. 等待小米辣检查
```

---

## 🌟 最佳实践

1. **自检要详细** - 小米辣应该认真填写自检清单
2. **疑问要明确** - 把不确定的地方写清楚
3. **Review 要耐心** - 小米辣要仔细阅读自检清单
4. **补充要具体** - 补充建议要有可操作性
5. **文档要保存** - 所有 Review 文档归档到 reviews/

---

*让协作更高效，让技术更优秀！* 🌾

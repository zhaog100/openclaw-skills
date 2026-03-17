# 技能开发经验教训库

**版本**: v1.0  
**更新时间**: 2026-03-17  
**用途**: Agent 协作开发时自动参考，避免重复踩坑

---

## 🔴 高频问题（子代理必读）

### 1. 子代理交付代码需要人工修复（频率 5/5）
**典型问题**:
- 相对导入 vs 绝对导入 → 统一用 `src.` 前缀或绝对导入
- 路径计算错误 → `Path(x).parent / "src"` vs `Path(x) / "src"` 必须验证
- 类型处理不完整 → JSON 序列化用 `not isinstance(x, str)` 判断
- 空输出/非 JSON 未容错 → 外部 Bash 输出格式不可假设

### 2. pytest 通过 ≠ 功能正确（频率 3/5）
**必须额外做**: 逐个调用公开接口，传入真实参数验证返回值

### 3. ClawHub slug 被占用（频率 3/5）
**解决**: 统一用 `sjykj-` 前缀

### 4. 发布流程（铁律）
**pytest 全绿 → 功能验证 → 发布 → 汇报（附测试数据）**，禁止先发后补

---

## 🟡 各技能具体教训

### ai-deterministic-control
- vote_with_timeout 超时逻辑: `as_completed(timeout=n)` 不会叠加，需单独计时
- 权重设计: `composite_score` 要确保理想情况下能得满分

### test-case-generator
- 数据类命名避免 `Test` 前缀（pytest 会误收集）
- 接口参数类型要在文档中明确说明

### auto-document-generator
- ast 替代 tree-sitter: 零依赖够用时不用外部 C 扩展

### auto-pipeline
- Bash 无法调 sessions_spawn: 复杂自动化需要 Python Agent 层面

### Error Handler
- 删除服务后必须更新所有引用，否则递归调用导致通知风暴

---

*文档路径: docs/products/development-lessons-learned.md（完整版）*
*集成到 agent-collab-platform 供子代理参考*

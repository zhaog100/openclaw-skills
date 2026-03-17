# 技能开发经验教训库（子代理必读）

**版本**: v1.2  
**更新时间**: 2026-03-17 11:50  

---

## ⛔ 官家核心要求（最高优先级）

### 1. 不要产生幻觉，实际完成所有步骤
- 每一个步骤都要实际执行，不能说"应该可以"、"预计能工作"
- 文件写了就实际写入，代码写了就实际运行
- 不能假设某个步骤的结果，必须看到实际输出

### 2. 严格严谨全面测试
- pytest 全部通过是最低要求，不是最终标准
- 必须逐个调用公开接口，传入真实参数，验证返回值
- 边界情况、空输入、异常输出都要测

### 3. 先测后发，不跳步
- 铁律: pytest全绿 → 功能验证 → 发布 → 汇报(附测试数据)
- 禁止先发布后补测试

### 4. 做完再汇报，不要让官家追问
- 测试、验证做完再汇报，汇报必须附带测试数据
- 有问题自己发现并修复，不要等官家指出

### 5. 不确认就当成没说
- 不确定意图时先问清楚，但明确的需求不需要反复确认

---

## 🔴 高频技术问题

### 子代理交付代码几乎都有bug (5/5)
- 相对导入 → 统一绝对导入或 src. 前缀
- 路径拼接 → 实际打印验证
- 类型处理 → not isinstance(x, str) 判断后序列化
- 空输出/非JSON → 检查输出格式再解析
- 数据类命名 → 避免 Test 前缀

### ClawHub slug占用 (3/5)
统一用 sjykj- 前缀

### Bash限制
- 无法调 sessions_spawn
- 字符串拼接注意引号转义

---

## 🟡 各技能教训

- ai-deterministic-control: as_completed timeout不叠加; composite_score需确保满分
- test-case-generator: 接口参数类型必须明确; 数据类避免Test前缀
- auto-document-generator: ast替代tree-sitter; 改造范围最小化
- auto-pipeline: Bash无法spawn; Review评分需量化
- Error Handler: 删除服务后更新所有引用
- agent-collab-platform: Bash输出格式不可假设; git worktree diff需过滤

---

## 🟢 验证标准

1. pytest 全通过(0 failed)
2. 每个公开接口实际调用，传真实参数
3. 边界测试: 空输入、None、异常类型
4. 外部依赖有容错
5. 版权完整(思捷娅科技 SJYKJ)
6. 不修改无关文件
7. 汇报附测试数据

---

## 🔄 改进记录

- v1.2: 文档写了不等于生效，必须在SKILL.md和spawn prompt显式引用
- v1.1: 加入官家5条核心要求
- v1.0: 初始版本

---

*完整版: docs/products/development-lessons-learned.md*

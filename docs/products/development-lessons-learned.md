# 技能开发经验教训库

**版本**: v1.0  
**更新时间**: 2026-03-17 11:35  
**用途**: 每次开发前必读，避免重复踩坑

---

## 🔴 高频问题（几乎每个技能都遇到）

### 1. 子代理交付代码需要人工修复
**频率**: 5/5 次 spawn 子代理  
**典型问题**:
- 相对导入 vs 绝对导入（test-case-generator, agent-collab-platform）
- 路径计算错误（quality_gate.py 的 `parent/src` vs `path/src`）
- 类型处理不完整（list 参数未 JSON 序列化）
- 空输出/非 JSON 输出未容错（status_manager 返回中文而非 JSON）

**规则**: 子代理交付后，必须实际运行每个接口验证，不能只看 pytest

### 2. pytest 通过 ≠ 功能正确
**频率**: 3/5 次  
**案例**:
- ai-deterministic-control: 96 测试全通过，但 vote_with_timeout 超时逻辑有 bug
- test-case-generator: 71 测试通过，但 generate_pytest 接口参数类型错误
- agent-collab-platform: 16 测试通过，但真实调用 review/check_status 报错

**规则**: pytest + 功能验证（逐个调用公开接口）缺一不可

### 3. ClawHub slug 被占用
**频率**: 3 次（error-handler, auto-pipeline, test-case-generator）  
**解决**: 使用 `sjykj-` 前缀

**规则**: 发布前先确认 slug 可用，优先用 `sjykj-` 前缀

### 4. 先发后补测试（2026-03-17 深刻教训）
**案例**: ai-deterministic-control 先发布 v1.1.0 再补测试  
**后果**: 测试不通过时已发布到 ClawHub  
**规则**: pytest 全绿 → 发布 → 汇报（附测试数据），禁止跳过

---

## 🟡 各技能具体教训

### ai-deterministic-control v1.1
| 问题 | 原因 | 教训 |
|------|------|------|
| vote_with_timeout 超时不生效 | `as_completed(timeout=timeout*n)` 当 timeout*n >= 总时间时不超时 | 并发超时逻辑需要单独计时，不能依赖 futures 的 timeout |
| ConsistencyChecker 评分偏低 | composite_score=0.4×char+0.3×semantic+0.3×entropy，完全一致只得 0.7 | 权重设计需考虑理想情况的满分条件 |
| creative_writing 模板太短 | 仅 44 字符 base 部分 | 模板应包含完整的 task_specific 占位符 |

### test-case-generator v1.0
| 问题 | 原因 | 教训 |
|------|------|------|
| 相对导入失败 | 子代理用 `from .module` 但测试用 `sys.path.insert` | 统一用绝对导入或 `src.` 前缀 |
| pytest 收集 dataclass 警告 | `TestPoint` 类名以 `Test` 开头 | 数据类命名避免 `Test` 前缀 |
| generate_pytest 参数错误 | 期望 AnalysisResult 但接口接收 filepath | 接口设计要明确参数类型，子代理文档要写清 |
| 需求分析器提取规则缺失 | PRD 有要求但技术设计描述简略 | 技术设计必须覆盖 PRD 每条验收标准 |

### auto-document-generator v1.1
| 问题 | 原因 | 教训 |
|------|------|------|
| tree-sitter 依赖太重 | C 扩展编译、50MB+、版本兼容差 | ast 零依赖够用时不用 tree-sitter |
| 只改 parser.py | 最小改动原则 | 改造范围最小化，降低回归风险 |

### agent-collab-platform 集成 quality_gate
| 问题 | 原因 | 教训 |
|------|------|------|
| src_dir 路径错误 | `pipeline_path.parent / "src"` → `skills/src` 而非 `skills/auto-pipeline/src` | 路径拼接必须实际验证输出 |
| list 参数未序列化 | `isinstance(x, dict)` 漏了 list | JSON 序列化判断用 `not isinstance(x, str)` |
| status 返回非 JSON | status_manager.sh 输出中文"未找到技能" | 调用外部 Bash 时，输出格式不可假设，需容错 |
| auto-pipeline git diff 误报 | git worktree 环境下相对路径显示上级变更 | 交叉仓库操作时 diff 结果需要过滤 |

### auto-pipeline v2.0
| 问题 | 原因 | 教训 |
|------|------|------|
| Bash 无法调 sessions_spawn | 子代理自动化需 Agent 层面执行 | Bash 技能有天然限制，复杂自动化需要 Python Agent |
| Review 分数波动 | 同一 PRD 不同次评分差异 | 评分标准需要更量化的 checklist |

### Error Handler v1.2
| 问题 | 原因 | 教训 |
|------|------|------|
| 上下文监控通知风暴 | 递归调用 + 飞书删除后监控还在 | 删除服务后必须更新所有引用 |

---

## 🟢 最佳实践（验证有效的）

### 开发流程
1. **PRD → 技术设计 → 核对PRD → 开发 → 测试 → 发布 → 汇报**
2. 技术设计必须逐条核对 PRD 验收标准
3. 冲浪调研找新思路融入设计
4. 零外部依赖优先（标准库够用就行）

### 测试策略
1. pytest + 功能验证（逐接口调用）+ 边界测试
2. 测试数据必须包含真实场景（不是只测正常路径）
3. 外部依赖输出不可假设（非 JSON、空输出、异常格式都要处理）

### Git 流程
1. 个人信息 → xiaomili，公共信息 → origin
2. **禁止 rebase --strategy=ours**：会丢弃本地新 commit
3. 正确做法：rebase 冲突时用 --skip 跳过重复 commit
4. 每次操作后立即 commit + push

### 发布流程
1. pytest 全绿
2. 功能验证通过
3. 发布 ClawHub
4. 更新 PRD 状态
5. Git commit + push（附测试数据）

---

*本文档随每次开发迭代更新*
*最后更新：2026-03-17 12:13*

---

## 🔄 持续改进记录

### v1.2 → v1.3（2026-03-17 12:13）
**新增6条实践教训**：
1. Python ThreadPoolExecutor.result(timeout) 在 3.12 无法中断 sleep → 改用 daemon threads+join(timeout)
2. generate_ascii_chart 必须过滤非数字值（authors值为dict时崩溃）
3. track_issues 返回字段名(open/closed)与文档不一致需统一
4. git rebase --strategy=ours 会丢弃本地新 commit → 改用 --skip
5. ClawHub version already exists → 发布前检查版本号
6. 子代理经常漏交 SKILL.md 和 package.json → 新增交付清单

**新增子代理交付清单**（8项检查）

### v1.1 → v1.2（2026-03-17 11:46）
**新教训**: 文档写了不等于生效
- 经验教训库放在 docs/ 目录，但 SKILL.md 没引用，子代理根本读不到
- **规则**: 重要规范必须写入 SKILL.md 或在 spawn prompt 中显式引用
- **已修复**: agent-collab-platform/SKILL.md 加入"开发规范"章节


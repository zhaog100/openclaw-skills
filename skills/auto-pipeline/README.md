# auto-pipeline

技能自动开发流水线，实现 PRD → Plan预审 → 开发 → Review(12维度) → 修复(≤3轮) → 发布 的全自动化流程。

## 版权

MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)

## 用法

```bash
# 从PRD启动流水线
auto-pipeline run --prd docs/products/2026-03-16_xxx_PRD.md

# 直接指定技能名
auto-pipeline run --skill my-skill --priority P0

# 查看所有流水线状态
auto-pipeline list

# 查看某个技能的详细状态
auto-pipeline status my-skill
```

## 状态流转

```
pending → developing → reviewing → fixing → publishing → completed
                          ↘ escalated
```

## 12维度评分

PRD覆盖度(2x) + 运行测试 + 代码质量 + 文档完整性 + CLI设计 + 错误处理 + 安全性 + 性能 + 可维护性 + 可扩展性 + 测试覆盖 + PRD一致性

满分60分，≥50分通过。

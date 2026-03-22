# 📝 FEEDBACK-LOG.md - 跨代理纠正记录

_记录重复出现的错误和纠正，避免重蹈覆辙_

**版本**: v1.0  
**创建**: 2026-03-22  
**维护**: 小米辣 (PM + Dev) 🌶️

---

## 2026-03-22

### ❌ 命名不一致

**问题**: SOUL.md 和 IDENTITY.md 中名字不统一（小米粒 vs 小米辣）

**纠正**: 统一改为"小米辣"，添加命名历史说明

**预防**: 每次修改 SOUL.md 时同步检查 IDENTITY.md

---

### ❌ 版权声明遗漏

**问题**: 部分文件没有 MIT License 版权声明

**纠正**: 所有核心文件添加版权声明

**预防**: 创建 docs/RECORDING-STANDARD.md，明确规定所有文件必须包含版权声明

---

### ❌ 格式不统一

**问题**: 不同日志文件格式不一致，表格/Emoji 使用混乱

**纠正**: 创建 RECORDING-STANDARD.md 统一格式规范

**预防**: 每次记录前参考格式规范

---

### ❌ GitHub clone 超时

**问题**: VPS 到 GitHub 网络不稳定，git clone 反复超时

**纠正**: 使用 GitHub API 直接创建 blob→tree→commit→ref

**预防**: 封装成脚本，遇到超时时自动切换 API 方式

---

### ❌ JSON Schema oneOf 歧义

**问题**: `oneOf: [{type: array}, {description: "any"}]` 导致 node link 匹配两个分支

**纠正**: 改为 `additionalProperties: true`

**预防**: JSON Schema 设计时避免 oneOf 用于复杂类型

---

### ❌ github-bounty-hunter.sh 语法错误

**问题**: gitcoin) 和 replit) 在 esac 外面

**纠正**: 移到 case 语句内部

**预防**: 提交前运行 `bash -n` 语法检查

---

## 📋 重复错误模式

| 错误类型 | 出现次数 | 根本原因 | 解决方案 |
|----------|----------|----------|----------|
| 命名不一致 | 1 | 文件分散 | 统一修改脚本 |
| 版权声明遗漏 | 多次 | 忘记添加 | 模板化 |
| 格式不统一 | 多次 | 无规范 | RECORDING-STANDARD.md |
| 网络超时 | 多次 | VPS 网络 | GitHub API 备用方案 |

---

## 🎯 改进措施

1. **模板化** - 所有文件使用统一模板
2. **自动化检查** - CI 检查版权声明和格式
3. **单写者规则** - 每个共享文件只有一个写入者
4. **反馈持久化** - 纠正写进文件，不只是聊天

---

*版权：MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)*

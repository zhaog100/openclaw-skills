# 🔒 安全政策

## 报告漏洞

发现安全漏洞，请通过以下方式报告：

- **GitHub Issue**: https://github.com/example-user/openclaw-skills/issues
- **邮件**: security@example.com（待配置）

## 安全最佳实践

### 1. 环境变量
```bash
# ✅ 正确：使用环境变量
export GITHUB_TOKEN='your_token'

# ❌ 错误：硬编码
GITHUB_TOKEN='your_token'  # 不要写在代码里！
```

### 2. 文件权限
```bash
# 设置配置文件权限
chmod 600 .env
chmod 755 *.sh
```

### 3. Token 权限
- 最小权限原则
- 定期轮换
- 泄露立即撤销

### 4. 日志安全
- 不记录敏感信息
- 日志文件权限 600
- 定期清理

## 已知限制

- ⚠️ 自动提交 PR 需要仓库写入权限
- ⚠️ 自动收款需要手动确认
- ⚠️ 多平台 API 限流

---

*最后更新：2026-03-17*
*版权：思捷娅科技*

---

## 🔍 漏洞扫描策略（HackerOne 安全审计）

### 适用场景
当 bounty 任务涉及安全审计、漏洞挖掘、H1 提交时使用。

### 四阶段工作流

#### 阶段 1：攻击面梳理
扫描前必须先映射完整攻击面：
1. **API 端点清单** — `ls app/api/server/v1/*.ts`
2. **无认证端点** — `grep 'authRequired: false'`
3. **DDP Methods** — `find -name "methods.ts" -path "*/server/*"`
4. **DDP Publications** — `grep 'Meteor.publish'`
5. **文件上传/下载路径**
6. **认证机制**（OAuth, LDAP, SAML, TOTP）

输出：攻击面摘要（端点数、认证要求、高价值目标）

#### 阶段 2：OWASP Top 10 系统化扫描
按类别逐项搜索 → 验证 → 确认/排除：

| 类别 | 搜索命令 | 重点 |
|------|----------|------|
| A01 权限绕过 | `grep -c 'hasPermission'` per file | 0权限检查的端点 |
| A02 加密失败 | `grep -rn 'md5\|sha1'` | 安全关键路径 |
| A03 注入 | `grep '$regex'` 无 `escapeRegExp` | NoSQL/SQL/LDAP |
| A04 不安全设计 | `Random.id(N)` N<16 | Token强度 |
| A05 配置错误 | `ALLOW_UNKNOWN_PROTOCOLS\|CORS \*` | DOMPurify/CORS |
| A06 脆弱组件 | `package.json` 版本检查 | 已知CVE |
| A07 认证失败 | 密码重置token可预测性 | State验证 |
| A08 数据完整性 | `JSON.parse.*param\|eval(` | 反序列化 |
| A10 SSRF | 用户可控URL的fetch | 内网IP过滤 |

#### 阶段 3：CVE/GHSA 模式匹配
利用历史安全修复找未修复的同类漏洞：
1. 搜索安全修复：`grep 'Security Hotfix\|CVE-' CHANGELOG.md`
2. 识别修复模式（如添加 `escapeRegExp`）
3. 对比有修复 vs 无修复的文件
```bash
# 有安全修复的文件
grep -rl 'escapeRegExp' app/api/server/v1/*.ts
# 有 $regex 的文件
grep -rl '$regex' app/api/server/v1/*.ts
# 差异 = 未修复漏洞
```

#### 阶段 4：深度验证
每个确认的漏洞：
1. 读上下文（±20行）
2. 追踪输入源 → 汇聚点
3. 验证利用条件（认证？角色？）
4. 评估影响（数据泄露/DoS/RCE）

### 常见漏洞模式对照

| 漏洞 | 危险模式 | 安全模式 |
|------|----------|----------|
| NoSQL注入 | `{ $regex: userInput }` | `escapeRegExp(userInput)` |
| XSS | `dangerouslySetInnerHTML={{ __html: input }}` | `DOMPurify.sanitize(input)` |
| LDAP注入 | `filter: (uid=${username})` | `ldapEscape.filter\`${username}\`` |
| SSRF | `fetch(userControlledUrl)` | 内网IP过滤 |
| IDOR | `findOneById(userProvidedId)` 无归属检查 | 验证 userId 所有权 |

### H1 报告模板

```
标题: [漏洞类型] via [参数] in [端点]

## Summary — 一段话描述
## Vulnerable Component — 文件:行号 + 代码片段
## Steps to Reproduce — 编号步骤
## Proof of Concept — 实际 payload
## Impact — 具体攻击场景 + 影响范围
## Suggested Fix — 代码级修复建议
## Environment — 分支/commit
```

### 核心原则
1. **系统化 > 随机** — 按 OWASP Top 10 顺序
2. **验证一切** — 每个发现必须有确认或排除证据
3. **对比安全模式** — 同一代码库的安全 vs 不安全对比
4. **利用历史CVE** — 过去的修复揭示未修复的模式
5. **只报 Medium+** — 跳过 Low/Informative
6. **代码级证据** — 每个发现需要 file:line + 代码片段

---

## 📊 实战经验教训（2026-04-12 更新）

### 扫描结果统计

| 目标 | 赏金 | 代码量 | 时间 | 结果 | 原因 |
|------|------|--------|------|------|------|
| Rocket.Chat | $3k+ | 50MB | 2h | ✅ 2漏洞 | 代码量适中，安全模式不一致 |
| Nextcloud | $3k+ | 200MB | 10min | ❌ 超时 | 代码量太大 |
| Bitwarden | $5k+ | 84MB | 15min | ❌ 无漏洞 | 代码质量极高，安全防护完善 |
| GitLab | $12k+ | 2GB+ | 10min | ❌ 超时+误报 | 被扫烂了，sanitize 完善 |
| Mergify | - | - | 30min | ❌ 无漏洞 | 安全配置优秀 |
| KOHO | - | - | 20min | ❌ Low | 发现不够 Medium |
| 20+黑盒目标 | 混合 | - | 3h | ❌ 全被WAF挡 | 黑盒远程扫描效率极低 |

### 核心教训

#### 1. 目标选择公式 ⭐⭐⭐
```
最佳目标 = 中等代码量(50-150MB) × 有赏金($1k+) × TypeScript/PHP/Python
避开目标 = 超大代码量(>200MB) × 被扫烂(GitLab/Bitwarden) × C#/Ruby
```

**理由：**
- 50-150MB 代码量可以在 30 分钟内完成 OWASP 扫描
- TypeScript/PHP/Python 项目更容易找到注入和 XSS
- GitLab、Bitwarden 等头部项目有专业安全团队，漏洞早已被扫完

#### 2. 源码审计效率排序
```
阶段 3（CVE模式匹配）> 阶段 2（OWASP）> 阶段 4（深度验证）> 阶段 1（攻击面梳理）
```
**最高效的做法：**
1. 先 grep CHANGELOG 找安全修复历史
2. 找修复模式（如 escapeRegExp, sanitize）
3. 对比有修复 vs 无修复的文件
4. 差异 = 未修复漏洞

**实例：** Rocket.Chat $regex 注入就是这么找到的 — 其他文件有 `escapeRegExp`，但 channels.ts/im.ts/groups.ts 没有。

#### 3. 黑盒扫描 < 源码审计
- 黑盒远程扫描遇到 WAF + Cloudflare 几乎必败
- 源码审计不需要发任何请求，不会被 WAF 挡
- 源码审计能直接看安全 vs 不安全的代码对比

#### 4. 报告要立即准备，不要等
- 发现漏洞后立即写报告并备份到 `data/`
- `/tmp` 会在会话间清除
- 拖延提交 = 被别人抢先的风险

#### 5. 子代理超时设置
- 小项目(< 100MB): 600s 够用
- 大项目(> 200MB): 需要 1200s 或分模块扫描
- 建议拆分为多个子代理，每个扫一个 OWASP 类别

### H1 目标分级（基于实战）

| 分级 | 目标 | 赏金 | 推荐度 | 原因 |
|------|------|------|--------|------|
| ⭐⭐⭐ | Rocket.Chat | $3k+ | 高 | TS项目，安全模式不一致 |
| ⭐⭐⭐ | Mattermost | $1k+ | 高 | Go/TS，中等代码量 |
| ⭐⭐⭐ | Ghost | $1k+ | 高 | JS，小代码量 |
| ⭐⭐ | Nextcloud | $3k+ | 中 | PHP，代码量大需分模块 |
| ⭐⭐ | Moodle | $1.5k+ | 中 | PHP，但需要教师权限 |
| ⭐ | GitLab | $12k+ | 低 | 被扫烂，代码量2GB+ |
| ⭐ | Bitwarden | $5k+ | 低 | 代码质量极高 |

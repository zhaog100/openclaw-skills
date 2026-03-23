# MEMORY-LITE.md - 核心记忆精简版

## 🎯 当前状态（2026-03-22）
- **今日PR**：5个（ComfyUI×4 + RustChain×1），~500行代码
- **Bounty收割**：38+个PR累计，$5,800+
- **Bounty全自动流水线**：12轮迭代，AI读源码+多模型fallback+质量门禁+文件锁
- **ClawHub**：25+个技能已发布
- **版权**：思捷娅科技 (SJYKJ)，MIT许可证
- **Git**：origin + xiaomili 双仓库 | GitHub: zhaog100
- **FinMind/APort旧PR**：已全部closed，0个open

## 🔑 关键教训TOP8
1. **质量第一** — 宁可慢不可烂，自测3遍（官家指令，永久遵守）
2. **Git rebase禁令** — 禁止--strategy=ours，改用--skip
3. **Bounty收割** — 广撒网+低竞争优先+快速提交+`/attempt #N`
4. **敏感信息** — 只存~/.openclaw/secrets/，config.json gitignore
5. **子代理交付** — SKILL.md+pytest+接口验证+边界测试，8项清单
6. **AI读源码再生成** — 不读issue提到的文件就生成=瞎编
7. **多模型fallback必须** — Gateway间歇性超时，glm-5-turbo→glm-5→deepseek
8. **GitHub API直接操作** — clone超时时用blob→tree→commit→ref绕过（3-22教训）

## ⚠️ 紧急待办
- 等待5个新PR review（ComfyUI×4 + RustChain×1）
- QMD 106个pending embedding
- Playwright爬Algora脚本（解锁更多bounty）
- 技能商业化Pro版设计

## 📌 关键决策
- 模型：zai/glm-5 > deepseek > AIHubMix(限流)
- 检索：QMD精准检索，不全量读取MEMORY.md
- Bounty优选：中额(30-75 RTC) > 大额(需要特殊环境)
- ComfyUI默认分支：master不是main

*最后更新：2026-03-22 04:20*

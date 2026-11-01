# 经济分析系统 — 经验总结（按最近使用沉淀，持续追加不删改）

> 发布前 Review 沉淀。每条 = 踩过的坑 + 修正做法。

## 数据源
1. **东财 ETF 行情接口（push2his.eastmoney.com）被云主机 IP 风控**（HTTP 000）→ 回测/信号改用**申万行业指数**（801050 有色 / 801080 机械）替代；"ETF 资金流"因需份额序列暂无免费等价源，**降级标注 neutral**，不硬造。
2. **官方源多被墙/风控而非断网**（NBS/海关/央行/东财行情）→ 排障先分层探活：主站 200 但数据子域 000/412 = 该子域被限，**不是代码 bug**，别为此改代码或加代理硬拉。换国内网络后官方源自动生效。
3. **数据源失败一律降级，禁止硬造数据** → 信号层捕获异常降级 neutral，主流程不崩、周报照常出。
4. **多源采集原则（官家定，永久）**：源只能多不能少、不限制；网站/公众号/官方/研报全铺；单源会滞后+视角单一，多源并行+交叉验证才可靠；不通的源占位保留不删。
5. **JS 渲染源（财联社/东财快讯）纯 requests 抓不到正文** → 用"能直接返回文本"的源（新华社/金十/华尔街见闻/公众号 mp.weixin 直采正文）替代，不硬凑。

## 架构
6. **门面模式**：对外只留 `entry.py` 单入口，内部 orchestrator 组装 18+ 微技能（registry 自动发现 skills/ 下 BaseSkill 子类）。新技能/其他 skill 集成 = 写一个 skill.py 适配器放 skills/ 下即可（石油黄金已这样挂成第 19 个）。
7. **数据源失败隔离**：单微技能失败不影响整体（execute() 包 try/except 返回 SkillResult.error）。

## 合规（发布前必查）
8. **版权头统一**："思捷娅科技 (SJYKJ) | MIT License"，每个 .py 都要有（__init__.py 也容易被漏）。
9. **版本号统一**：同 skill 内版本号必须一致（本次统一 V3.1），散落的旧版本号（V3.4/V3.0/V2.0）是发布前必清项。
10. **脱敏**：open_id/手机号/token 不得硬编码进公开仓库，走环境变量或 config；缺失要**明确报错**不静默兜底。
11. **硬编码绝对路径**：用 `Path(__file__)` 相对定位或环境变量外置，不写死 /home/ubuntu。
12. **命名规范**：模块/文件/变量全 snake_case。

## 推送
13. **openclaw cron delivery=channel last 会 fail-closed 静默失败**（任务跑完推不到人）→ 推送类任务必须**固定 channel+to**（如 qqbot + 官家 open_id），别走 last。
14. **qqbot CLI 发消息有 bug（Unknown channel "qqbot"）** → 走 Gateway REST（send_qq_gw.py）或直接 openclaw cron announce。

## 回测/验证
15. **官方源超时会让全量测试撞 timeout（exit 124）非报错** → 用 mock 信号（不联网）快速验逻辑不崩，再跑全量；别因超时误判为逻辑错。

## 脱敏改动必须同步调用方（2026-09-30 踩坑）
16. **去硬编码 open_id/secret 时，必须同步确认调用方（cron/CI/上游脚本）注入了替代的环境变量或 config**，否则线上直接挂。
    - 实例：run_report.sh 改成"QQ_TARGET_USER_ID 缺失即拒绝推送"（合规正确），但 4 个石油黄金 cron automation 没注入该变量 → 15:00 日盘 exit 1 报告没推。
    - 修法：openclaw cron edit <id> --command-env "QQ_TARGET_USER_ID=..." 给每个 automation 注入（cron 级配置，不进代码仓库，合规不破）。
    - 教训：脱敏是"代码去硬编码 + 调用方注入变量"两件事，缺一即线上故障。改完脱敏必须手动带 env 跑一次全链路验证。

## 脚本执行位（2026-10-10 踩坑）
17. **改 cron 调用的 .sh 时，"临时文件重写 + mv 回去"会丢 +x 执行位** → cron `sh -lc` 执行报 Permission denied (exit 126)。
    - 实例：10-08 补 open_id 脱敏/版权头用 `> tmp && mv tmp f` 重写，重建文件丢可执行位，morning-report.sh 挂 2 天。
    - 修法：批量 `find skills -name "*.sh" -type f ! -perm -u+x | xargs chmod +x`，再用 `sh -lc <脚本>` 模拟 cron 执行验证 exit=0。
    - 教训：改完任何 cron 调用的 .sh，提交前必 `bash -n` + `chmod +x` 复核执行位，别只查内容。

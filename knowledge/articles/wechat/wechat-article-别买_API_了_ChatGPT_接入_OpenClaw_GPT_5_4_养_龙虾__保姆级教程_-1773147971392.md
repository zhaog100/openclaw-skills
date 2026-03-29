# 别买 API 了！ChatGPT 接入 OpenClaw，GPT-5.4 养「龙虾」（保姆级教程）

**作者**: AI信息Gap
**发布时间**: 木易的AI频道
                        木易的AI频道
**原文链接**: https://mp.weixin.qq.com/s/npk--VNdrcAFcDg8X0oPYQ
**抓取时间**: 2026-03-10T13:06:11.392Z

---

**

答应你们的教程，来了。*

你领养了一只 OpenClaw「龙虾」。

但它食量惊人。随便跑个什么，几万 tokens 眨眼就没了。

你同时也在用 ChatGPT。免费或者 Plus、Business、Pro 订阅。

那么，ChatGPT 能不能直接接入 OpenClaw？

包的。

**你的 ChatGPT 订阅自带 Codex 额度，直接喂给龙虾就行。不需要额外买 OpenAI API，不需要花冤枉钱。**

免费用户目前也有 Codex 权限。

Sam Altman 2 月 2 号亲自官宣的。后来他又确认，活动结束后也会保留，只是额度可能降低。*

划重点，**OpenAI 官方明确允许这么用**。

目前零风险，放心用。**
---

在 OpenClaw 的文档里，白纸黑字写了这么一句话。**

OpenAI Codex OAuth is explicitly supported for external tools/workflows like OpenClaw.

翻译一下，OpenAI 明确支持在 OpenClaw 这类外部工具中使用 Codex OAuth 授权。*

Anthropic 和谷歌的态度截然相反。

前者悄悄在服务端做了封锁，后者直接封号。

OpenAI 这边？

OpenClaw 创始人 Peter Steinberger 2 月 14 号官宣加入 OpenAI。Sam Altman 亲自发文欢迎，说他要「推动下一代个人 Agent」。OpenClaw 项目转入开源基金会，OpenAI 持续赞助。

龙虾的亲爹都去了 OpenAI。这只龙虾，已经被「收编」了。

所以，用 ChatGPT 接入 OpenClaw，合情合理。**
---

下面的操作我是在一台云服务器上跑的，本地电脑流程一样。

假设你已经装好了 OpenClaw。没装的可以翻看我[这篇教程](https://mp.weixin.qq.com/s?__biz=MzkwMzYzMTc5NA==&mid=2247511069&idx=1&sn=361e99b74a30f8e94771a7ec4113270b&scene=21#wechat_redirect)。
### 01｜升级 OpenClaw

GPT-5.4 是几天前刚发布的，老版本的 OpenClaw 识别不出这个模型。

亲测 2026.3.2 版本设置 openai-codex/gpt-5.4 直接报错，升级到 2026.3.7 才跑通。

运行下面这个命令升级「龙虾」。

openclaw update**

升级需要几分钟，耐心等待。完成后自动重启 Gateway。*
### 02｜运行 onboarding 向导

先备份一下配置，以防万一。

cp -a ~/.openclaw ~/.openclaw.bak**

然后运行向导。

openclaw onboard --auth-choice openai-codex***

向导会问你几个问题。

「I understand this is personal-by-default...」选 Yes。

「Onboarding mode」选 QuickStart。

「Config handling」选 Use existing values。

注意，第三个选项千万别选 Reset，选了你的设置、记忆、定时任务全没了。Use existing values 只改模型，其他不变。*
### 03｜OAuth 授权

向导走到 OpenAI Codex OAuth 这一步，会给你一个 URL。*

把这个 URL 复制到本地电脑的浏览器里打开，用 ChatGPT 账号登录，点击授权。*

浏览器会跳转到一个 http://localhost:1455/auth/callback?code=... 的地址。

服务器上这个页面打不开，正常。

把浏览器地址栏里的完整 URL 复制下来，粘贴回终端的 Paste the redirect URL 输入框就行。

本地电脑跑 OpenClaw 的，浏览器弹出来，登录授权就行。
### 04｜跳过后续配置

频道选择那里选 Skip for now。

你之前配置好的频道都还在，不需要重新配。*

后面的 skills、hooks 也一路跳过。

Gateway service 选 Restart。*

最后「How do you want to hatch your bot」选 Do this later。

龙虾之前已经配置好了，不需要重来。*
### 05｜设置模型

openclaw models set openai-codex/gpt-5.4**

去 OpenClaw Web 控制台、TUI（终端里运行 openclaw tui）或者你连接的频道发条消息测试。*

openai-codex/gpt-5.4，跑起来了。**
---

额度怎么看？

打开 Codex 网页版（ChatGPT 网页端左侧菜单栏选 Codex），右上角点设置，左侧菜单选 Usage。*

5 小时额度、每周额度和 Code Review 额度。

划重点，**OpenClaw 消耗的是 Codex 额度，跟你平时用 ChatGPT 聊天的额度是分开的。**

两个池子，互不影响。不用白不用。**
---

OpenAI 是目前御三家里唯一明确欢迎接入 OpenClaw 的。

趁现在门还开着，可以冲了。

成功了或者没成功的，评论区说一声。

觉得有用，欢迎点赞转发，让更多人看到。**
---
****

我是木易，Top2 + 美国 Top10 CS 硕，现在是 AI 产品经理。

关注「AI信息Gap」，让 AI 成为你的外挂。**
---
******

---

*本文由 Playwright 自动抓取生成*

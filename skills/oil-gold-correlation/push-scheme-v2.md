石油黄金定时推送方案 v2.0（最终版）
==========================================
日期: 2026-04-14

一、变更说明
----------
放弃图片生成方案（matplotlib间距/字体/兼容性问题多）
改用纯文本+emoji进度条，直接推送，零延迟。

二、报告格式
----------
石油黄金投资参考 (2026-04-14)

>> 关键拐点
消费者信心=57 持续低位
历史上<60连续3月 = 黄金大级别买入信号

投资决策仪表盘

🥇 沪金 $1,043.4  ⚪观望
🟥🟥🟧🟧⬜⬜⬜⬜⬜⬜ 23/100
技术面23 宏观面50 信号灯-1

🛢️ 沪油 $658.0  ⚪观望
🟥🟥🟧🟧🟦🟦⬜⬜⬜⬜ 50/100
技术面45 宏观面56 信号灯+0

🌍 地缘风险 +50/100 极高风险
🟥🟥🟧🟧🟦🟦⬜⬜⬜⬜

宏观信号灯
信心:57 悲极 | VIX:19.2 平静
利差:0.52 正常 | 信用:2.94 宽松

结论: 全部观望不动。消费信心57极低，避险利多黄金但技术面偏空，等信号灯转正。

仅供参考，不构成投资建议

三、进度条颜色规则
----------
每格按位置着色：
🟥 红色（第1-2格，0-25%）→ 强烈回避
🟧 橙色（第3-4格，25-40%）→ 回避
🟦 蓝色（第5-6格，40-60%）→ 观望
🟨 黄色（第7-8格，60-75%）→ 可考虑
🟩 绿色（第9-10格，75-100%）→ 建议买入
⬜ 灰色 → 未填充

四、推送时间（按市场开收盘）
----------
  时段1  10:00  日盘开盘1h后，隔夜数据回顾
  时段2  15:30  中国日盘收盘后，当日数据完整
  时段3  23:00  美股开盘30min后，全球定价确认
          冬令时自动延迟至00:00（oil-gold-us-adapter.sh）

市场时间参考：
  中国期货日盘: 09:00-15:00
  中国期货夜盘: 21:00-次日02:30
  美股夏令时:   21:30-04:00
  美股冬令时:   22:30-05:00

五、Cron配置（6个任务）
----------
  oil-gold-daily          10:00  default bot  180s timeout
  oil-gold-daily-bot2     10:00  bot2         180s timeout
  oil-gold-nightly        15:30  default bot  180s timeout
  oil-gold-nightly-bot2   15:30  bot2         180s timeout
  oil-gold-us-open        23:00  default bot  180s timeout
  oil-gold-us-open-bot2   23:00  bot2         180s timeout

Cron IDs:
  0a4dce3a-43f5-416a-b964-746e3bada784  oil-gold-daily
  4ff30609-8a83-42f1-b5f4-8d4f392469c0  oil-gold-daily-bot2
  10146b3c-4acc-4708-a60a-a0cfea8a0fec  oil-gold-nightly
  03381fd4-0884-4594-81b8-d1c3185a2415  oil-gold-nightly-bot2
  f585c598-cace-44b1-8955-f5c7d9912d81  oil-gold-us-open
  cb74b819-8b6d-4e26-8a13-369df1ca2df3  oil-gold-us-open-bot2

Cron Prompt (统一):
  运行命令 python3 ~/.openclaw/skills/oil-gold-correlation/scripts/report_text.py 并把输出内容完整推送，不需要任何修改。

QQ Bot推送目标:
  default: qqbot:c2c:C099848DC9A60BF60A7BE31626822790
  bot2:    qqbot:c2c:E7331F9772A02575890BBE94E788248A

六、文件清单
----------
新增:
  scripts/report_text.py  — 纯文本报告生成器（主力）
  scripts/report_card.py  — 图片版（保留备用）
  scripts/oil-gold-us-adapter.sh — 冬令时适配

修复:
  scripts/fetch_data.py   — docstring重复SyntaxError

已有(原v1.6.0):
  scripts/advisor.py      — 核心分析引擎
  scripts/geopolitics.py  — 地缘风险评分
  scripts/analysis.py     — 技术指标计算
  scripts/fetch_fred.py   — FRED宏观数据
  scripts/visualize.py    — 可视化
  SKILL.md                — 技能说明

七、数据源
----------
  沪金/沪油: akshare → futures_main_sina (T-1收盘价)
  地缘风险: 多渠道新闻采集 (13个channel)
  宏观指标: FRED (延迟1-3天)
  yfinance: 腾讯云IP被限速，不可用

八、已知限制
----------
  1. akshare只有T-1收盘价，无盘中实时数据
  2. geopolitics采集13个channel，耗时约8-10秒
  3. 完整报告生成约133秒（含数据采集+分析+地缘）
  4. 沪金沪油数据，布油/美元暂未接入（可扩展）

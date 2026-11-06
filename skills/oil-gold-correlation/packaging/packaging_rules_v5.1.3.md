# 门面 + 油金 · 打包规则（v5.1.3 唯一权威版）

> 11-05 定稿，11-06 升 v5.1.2，11-06 再升 v5.1.3。v5 起为唯一权威规则，不再出补丁。
> 基准包：`media/outbound/eo-og-v5-baseline.zip`（v5.1 B方案 `eo-og-v5.1-baseline`，v5.2 彩票 `eo-og-v5.2-lottery`）。
> v5.1.2 新增：第五节「唯一打包源纪律」+ 第六节「打包源前置放行」+ 13.2.1 第4条「本地双副本漂移当打包源」洞实录。
> v5.1.3 新增：第六节「[8] 定时配置在位」（7 项→8 项，schedules.yaml 必含 oil_gold_push + lottery_push、workflows.yaml 必含 lottery_ss，缺任一=未交付）+ 第九节验收 Checklist 补 [8]。
>
> **与 v4.1 的区别**：v4.1 是逐次发现逐次补（data、缓存、彩票 meta、相对路径……），
> v5 一次性把本地全目录扫描出的**所有"不该入包"类型**枚举进来，打包规则写全。

---

## 一、核心原则（一句话）

**"定义层"入包，"运行态/构建残留/密钥"不入包。**
判断口诀：拿不准就先归"定义层"入包；明显是**跑出来的 / 构建残留的 / 带密钥的**就排除。

---

## 二、入包白名单（定义层，强制保留，永不排除）

| 类型 | 例 | 处置 |
|------|----|----|
| 代码 | `.py` / `.sh` / `.js` / `.ts` | ✅ 保留 |
| meta 定义 | `SKILL.md` / `README.md` / `LICENSE` | ✅ 保留 |
| 依赖清单 | `requirements.txt` / `package.json` / `_meta.json` | ✅ 保留 |
| 无密钥配置 | `config/*.yaml`（密钥已走 `${...}` 占位符的） | ✅ 保留 |
| 入口/路由 | `entry.py` / `router.py` / `entry_legacy.py` | ✅ 保留 |
| 测试代码 | `tests/*.py` / `scripts/test_*.py` | ✅ 保留（开发辅助） |
| 审核文档 | `review/*.md` | ✅ 保留 |
| 推送方案 | `push-scheme-*.md`（无 git 冲突标记的保留） | ✅ 保留 |
| 打包工具 | `packaging/make_pkg.py` / `packaging/verify_pkg.py` | ✅ 保留（开发辅助） |
| 一次性迁移/修复脚本 | `scripts/fix_*.py` / `scripts/fix_*.sh` | ✅ 保留（**默认保留**；若想排除见第十节"可选严格模式"） |

> **白名单优先级**：白名单文件即使被黑名单 pattern 命中，也**强制保留**。
> 这是"`zip -x` 全量排除 → `zip -g` 补回白名单"两步的本质：黑名单先全排，白名单再补回，白名单赢。

---

## 三、排除黑名单（v5.1 全量枚举，一次写全）

> 以下 8 类是本地全目录扫描确认的全部"不该入包"类型。

| 类 | 排除 pattern | 实测命中 | 性质 |
|----|-------------|---------|------|
| ① 运行态数据 | `*/data/*` `data/*` | 油金 4 + 门面 3 | 盯价/信号/ETF 实时快照 |
| ② 缓存 | `*/cache/*` `cache/*` `*/__pycache__/*` `*.pyc` | cache/ 22 + __pycache__/ | 运行时缓存(.pkl 宏观快照)/字节码 |
| ③ 输出报告 | `*/reports/*` `reports/*` | 油金 reports/ 1 | 生成的报告 txt |
| ④ 日志 | `*/logs/*` `logs/*` | — | 日志 |

> **pattern 陷阱（v5 实测踩的坑，必须双写）**：`*/cache/*` 里的 `*` 要求**中间还有一层目录**，
> 所以**只匹配 `a/b/cache/x`（中段 cache），匹配不到顶层直属的 `cache/x`**。
> 因此每个目录类 pattern 必须**双写**——`*/cache/*`（中段）+ `cache/*`（顶层）都加，
> 顶层和子目录里的才都排得掉。2026-11-05 首版 v5 只写了 `*/cache/*`，导致顶层 `cache/` 的
> 22 个 pkl + 1 个 reports 漏进包，本轮补全。
| ⑤ **版本控制残留（v5 新增）** | `*/backup-*/*` `backup-*/*` `*.bak` `*.orig` `*.rej` `*.swp` `*.swo` `*~` `*conflict*` | `scripts/backup-remote-merge/` 3 个 | git 合并备份/冲突暂存 |
| ⑥ **含 git 冲突标记的文件（v5 新增）** | 内容含 `^<<<<<<< HEAD` / `^>>>>>>>` / `^=======` 的任意文件 | `backup-remote-merge/history_report.py` `test_report.py` | 未解决冲突的脏文件 |
| ⑦ **明文密钥（v5 新增）** | 内容含 `(open_id|access_token|app_secret|client_secret)\s*[:=]\s*['"]?[0-9A-Za-z]{8,}` 明文字面量 | —（应 0，有则整文件剔除） | 密钥泄露 |
| ⑧ **临时/隐藏文件（v5.1 新增）** | `*.tmp` `*.temp` `tmp/*` `*/tmp/*` `.DS_Store` `Thumbs.db` `.*.swp` `.eslintcache` `.pytest_cache/*` `.git` `*/.git*` `*.gitignore` `.gitignore` `.env` `*.env` `.env.*` `.venv/*` `*/.venv/*` | `.gitignore` 等 | 编辑器/OS/测试框架临时产物 + VCS 配置 + 本地环境 |

> **⑧类 pattern 陷阱（v5.1.1 实测踩过）**：带目录前缀的文件必须用**通配 pattern**——
> `*.gitignore` 才能排掉 `skills/oil-gold-correlation/.gitignore`（带前缀路径）；裸 `-x ".gitignore"` 只匹配包根顶层、匹配不到带前缀的。
> 因此 `.gitignore`/`.env` 这类**文件级** pattern 也要双写：`*.gitignore`（带前缀）+ `.gitignore`（顶层）。
> B 方案（全 skills/ 布局）下包内路径全带 `skills/` 前缀 → `.gitignore` 实际形态是 `skills/x/.gitignore` → **必须加 `*.gitignore`**，否则漏进包。

**通用排除**：`*.log`（散落的日志文件）。

> **关键**：第 ⑤ 类的 `backup-*/*` 同样**必须双写**（`*/backup-*/*` 中段 + `backup-*/*` 顶层），
> 与 ①②③④ 同一 pattern 陷阱——`*` 前缀匹配不到顶层直属目录。

> 口诀：**排除的是"运行产物 / 构建残留 / 密钥"，不是删子目录**。
> 子目录里的 `SKILL.md`/`LICENSE`/`README`/`requirements.txt` 是定义层，**必须保留**（白名单优先于黑名单）。

---

## 四、密钥处置（SecretRefs 范式）

- 包内**永不带明文密钥**。
- 密钥文件一律占位符：`"${QQ_APP_ID}"` / `"${QQ_APP_SECRET}"` / `"${QQ_TARGET_USER_ID}"`。
- 含明文字面量的 `*.yaml`/`*.json` → 整文件剔除，另存 `config/secrets.local.yaml`（gitignore + 本地运行）。

---

## 五、一键打包脚本（v5，两步，可直接执行）

> **🔒 唯一打包源纪律（11-06 补·②类洞堵漏）**
> 1. **唯一打包源 = 已验全绿的基准包**（如 `eo-og-v5.1-baseline`）。给基准包注入新配置（如 `lottery_push`）时，**从基准包解开为工作树再打**，不从本地 workspace 全量打。
> 2. **本地 workspace 存在双副本/合并烂尾（顶层油金 vs `skills/` 油金不一致）时，默认不可作为打包源**；须先跑第六节 7 项必验全绿（含 AST 挂 0 + 冲突标记 0）才可用，否则从权威基准包取干净版覆盖本地脏副本。
> 3. **报"可交付"前必须真跑第六节 7 项 + 端到端，"图快没验"视为②类洞**（13.2 第4条实录）。

```bash
cd /home/zhaog/.openclaw/workspace
OUT=media/outbound/eo-og-v5-baseline.zip
rm -f "$OUT"

# ① 全量排除（黑名单 8 类一次到位；目录类 pattern 全部双写 中段+顶层）
#    B 方案: 打包源全在 skills/ 下（skills/economic-outlook + skills/oil-gold-correlation 平级）
zip -qr "$OUT" \
  skills/economic-outlook skills/oil-gold-correlation \
  -x "*/data/*" -x "data/*" \
  -x "*/cache/*" -x "cache/*" \
  -x "*/reports/*" -x "reports/*" \
  -x "*/logs/*" -x "logs/*" \
  -x "*/__pycache__/*" -x "*.pyc" -x "*.log" \
  -x "*/backup-*/*" -x "backup-*/*" \
  -x "*.bak" -x "*.orig" -x "*.rej" -x "*.swp" -x "*.swo" -x "*~" \
  -x "*.tmp" -x "*.temp" -x "tmp/*" -x "*/tmp/*" -x ".DS_Store" -x "Thumbs.db" \
  -x ".eslintcache" -x ".pytest_cache/*" \
  -x ".git" -x ".git/*" -x ".git/*" -x "*/.git" -x "*/.git/*" \
  -x "*.gitignore" -x ".gitignore" -x "*.env" -x ".env" -x "*.env.*" \
  -x ".venv/*" -x "*/.venv/*" -x "*/config/*secret*" -x "*/config/*key*" \

# ② 补回被误伤的定义层 meta（白名单，防 zip -x 误杀子目录里的 SKILL.md 等；路径全在 skills/ 下）
zip -gq "$OUT" \
  skills/economic-outlook/SKILL.md skills/economic-outlook/README.md \
  skills/economic-outlook/requirements.txt skills/economic-outlook/LICENSE \
  skills/oil-gold-correlation/SKILL.md skills/oil-gold-correlation/README.md \
  skills/oil-gold-correlation/requirements.txt skills/oil-gold-correlation/LICENSE \
  skills/oil-gold-correlation/package.json skills/oil-gold-correlation/_meta.json \
  skills/economic-outlook/skills/lottery_analysis/SKILL.md \
  skills/economic-outlook/skills/lottery_analysis/LICENSE \
  2>/dev/null   # 文件缺失时静默忽略

echo "✅ 打包: $OUT ($(du -h "$OUT" | awk '{print $1}'))"
```

> **B 方案 vs 官家原 v5.1 的脚本差异（仅 2 行路径）**：
> ① 第一行打包源 `skills/economic-outlook oil-gold-correlation` → **`skills/economic-outlook skills/oil-gold-correlation`**
> ② 白名单里 `oil-gold-correlation/...` → **`skills/oil-gold-correlation/...`**
> 其余 8 类黑名单 / 双写 / 密钥 pattern **完全不变**。

> **为什么分两步**：`zip -x` 全量排除可能误伤子目录里的 meta 定义层；`zip -g` 把白名单补回。
> 既保证"运行态/残留/密钥 0 残留"，又保证"定义层完整"。

---

## 六、打包后必验（8 项全过才算可交付）

```bash
Z=media/outbound/eo-og-v5-baseline.zip

# [1] 运行态 0 残留 —— 必须同时查 顶层(cache/data/reports/logs/直接挂包根) + 中段(路径中带/) 两种形态
echo "中段残留: $(unzip -l $Z | grep -cE '/data/|/cache/|/reports/|/logs/|/__pycache__/|\.pyc')"
echo "顶层残留: $(unzip -l $Z | grep -cE '^(economic-outlook|oil-gold-correlation)/?(cache|data|reports|logs)/')"
# 两个都必须 = 0 才算干净；只看中段会漏掉顶层 cache/(.pkl) —— 这是 v5 首版踩的坑

# [2] 版本控制残留 0 残留（v5 新增）
echo "vc残留: $(unzip -l $Z | grep -cE '/backup-|\.bak|\.orig|\.rej|\.swp|\.swo|~$|conflict')"

# [3] 代码 AST 全过（挂 0）
cd /tmp && rm -rf v5chk && mkdir v5chk && cd v5chk && unzip -q "$Z"
for f in $(find . -name "*.py" -not -path "*__pycache__*"); do
  python3 -c "import ast;ast.parse(open('$f').read())" 2>/dev/null || echo "AST FAIL: $f"
done

# [4] 无 git 冲突标记（v5 新增，应 0）
echo "冲突标记: $(grep -rlcE '^<<<<<<< HEAD|^>>>>>>> ' . 2>/dev/null | wc -l)"

# [5] 定义层 meta 白名单在位
unzip -l "$Z" | grep -cE "(SKILL\.md|LICENSE|requirements\.txt|package\.json|README\.md)"

# [6] 密钥 0 明文（应空）—— 命中后必须逐个看上下文判定: 占位符/变量/接口字段名=通过, 字面量=失败
grep -rlnE "(open_id|access_token|app_secret|client_secret)[[:space:]]*[:=][[:space:]]*['\"]?[0-9a-zA-Z]{8,}" . 2>/dev/null

# [7] 临时/隐藏文件 0 残留（v5.1 新增；含 .git/.gitignore/.env/.venv/.pyc）
echo "临时残留: $(unzip -l $Z | grep -cE '\.tmp$|\.temp$|/tmp/|DS_Store|Thumbs\\.db|eslintcache|pytest_cache|/\\.git|\\.gitignore|/\\.env|/\\.venv/|/__pycache__/|\\.pyc$')"

# [8] 定时配置在位（v5.1.3 新增；定时推送是验收第 11 项, 光 skill 实跑≠定时已挂）
# 必含本轮该挂的定时任务: 当前 = oil_gold_push + lottery_push; workflows.yaml 含 lottery_ss
# 缺任一 = 未交付
echo "定时配置在位: $(grep -rlE 'oil_gold_push|lottery_push' $Z 2>/dev/null | wc -l) (该 >=1; 同时 workflows.yaml 含 lottery_ss)"
unzip -p $Z 'skills/economic-outlook/config/schedules.yaml' 2>/dev/null | grep -cE 'oil_gold_push|lottery_push' | xargs echo "  schedules.yaml 定时项数(该含 oil_gold_push + lottery_push):"
unzip -p $Z 'skills/economic-outlook/config/workflows.yaml' 2>/dev/null | grep -c 'lottery_ss' | xargs echo "  workflows.yaml lottery_ss 命中(该 >=1):"
```

**8 项全过（残留 0 / vc 残留 0 / AST 挂 0 / 冲突标记 0 / meta 在位 / 密钥 0 / 临时文件 0 / 定时配置在位）才算可交付基准包。**

> **🔒 打包源前置放行（11-06 补）**：跑第六节前，**打包源自身**须先 `AST 挂 0 + 冲突标记 0` 才放行；若打包源 = 本地双副本树且未全绿，**不得作为打包源**，改从权威基准包解开为工作树再注入/重打。"图快没验 7 项就报重打 OK" = ②类洞（13.2.1 第4条）。

---

## 七、端到端验证（平级解开直接跑通）

```bash
# 解包: 顶层 skills/economic-outlook/ + oil-gold-correlation/ 并排
# 适配器多布局候选扫描，平级解开也能找到油金目录
cd <解包目录>
python3 -c "
import sys, importlib.util
sys.path.insert(0,'skills/economic-outlook')
spec=importlib.util.spec_from_file_location('og','skills/economic-outlook/skills/oil_gold/skill.py')
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
r=m.OilGoldSkill().run({})
import json; print(json.dumps({k:r.get(k) for k in ('success','degraded','error','unavailable_reason','report_generated')},ensure_ascii=False))
print('push:', json.dumps(r.get('push',{}),ensure_ascii=False)[:150])
"
# 期望: success=True, degraded=None, error=None, unavailable_reason=(无)
# 11-06 本机实测(解开 B 方案包真跑): success=True, degraded=None, unavailable_reason=None,
#   report_generated=True, push.sent 视 Gateway 环境(本机在 Gateway 下=可坐实; /tmp 非生产=验不到, 不谎报)
```

**坐实标准**：`success:True` + `degraded:None` + `error:None` + 无 `unavailable_reason`（适配器坐实字段，本机可验）；
`push.sent:True` 需真实 Gateway 环境（部署环境验；本机在 Gateway 下已实测可坐实，/tmp 非生产验不到，不谎报）。

---

## 八、部署解包落地（避免相对路径坑）

油金适配器 `skills/economic-outlook/skills/oil_gold/skill.py` 靠相对路径找油金脚本目录。
`v4-final` 起已改为**多布局候选扫描**（平级顶层 / `workspace/skills` / 内嵌套都认），
找不到时**显式明标 `unavailable_reason`**，不静默降级。

| 布局 | 是否通 | 说明 |
|------|--------|------|
| 平级解开（`skills/economic-outlook/` + `oil-gold-correlation/` 并排） | ✅ | 候选扫描命中 |
| `workspace/skills/economic-outlook` + `workspace/oil-gold-correlation` | ✅ | 候选扫描命中 |
| 找不到油金目录 | ✅（明标不静默） | `degraded: True` + `unavailable_reason: "油金目录不存在(布局不符...)"` |

---

## 九、验收 Checklist（全勾 = 可交付基准）

- [ ] 运行态 0 残留（第六节 [1] 中段 + 顶层 都 =0）
- [ ] 版本控制残留 0（第六节 [2]=0，含 `backup-*` / `*.bak` / 冲突标记）
- [ ] 代码 AST 全过（第六节 [3] 挂 0）
- [ ] 无 git 冲突标记（第六节 [4]=0）
- [ ] 定义层 meta 白名单在位（第六节 [5]）
- [ ] 无密钥明文入包（第六节 [6] 空；命中逐个看上下文判定）
- [ ] 无临时/隐藏文件残留（第六节 [7]=0，含 `.git`/`.gitignore`/`.env`/`.venv`/`.pyc`/`__pycache__`）
- [ ] 双副本仅一套（**B 方案: 全部唯一套在 `skills/` 下，顶层无 oil-gold 副本**）
- [ ] skills/ 平级解开跑通（第七节 `success:True` + `degraded:None`，push.sent 视 Gateway 环境）
- [ ] 包内路径带 `skills/` 前缀（unzip -l 抽查 `skills/economic-outlook` + `skills/oil-gold-correlation`）
- [ ] 定时配置在位（第六节 [8]：schedules.yaml 含 oil_gold_push + lottery_push，workflows.yaml 含 lottery_ss；缺任一=未交付）
- [ ] 双彩种 `combined_ticket.py ssq/dlt` 实跑通过 + 合规 disclaimer 在

**全部勾上 → 该包为可交付部署基准。**

---

## 十、可选严格模式（按需启用，默认关）

默认 v5 规则**保留**开发辅助文件（tests/、review/、packaging/、fix_* 一次性脚本），因为它们**无害**。
若需要"最小部署包"（剔除所有开发辅助，只留运行必需），启用严格模式，在第五节脚本的 `zip -x` 里**额外加**：

```bash
  # 严格模式: 剔除开发辅助(不影响运行)  ← 默认注释掉, 需要时取消注释
  -x "*/tests/*" -x "tests/*" \
  -x "*/review/*" -x "review/*" \
  -x "*/packaging/*" -x "packaging/*" \
  -x "*/scripts/fix_*" -x "scripts/fix_*" \
  -x "*/push-scheme-*"
```

启用后必验同第七节 7 项全过。**严格模式不影响可交付性**（开发辅助文件本就部署方用不到）。

> **注：本文档现版本 = v5.1.3（11-06 唯一打包源纪律 + 打包源前置放行 + 13.2.1 第4条本地双副本漂移洞 + 第六节[8] 定时配置在位 7项→8项 + 第九节验收补[8]）。**

---

## 十一、基准包记录

| 包 | 大小 | 文件数 | 状态 |
|----|------|--------|------|
| `eo-og-v4.1-baseline`（你发的） | 404,663 | 240 | 混入 `backup-remote-merge/` 3 个（含 git 冲突标记，AST 挂 3） |
| **`eo-og-v5-baseline`**（v5.1 规则产出） | 411,412 | 275 | ✅ **最终部署基准**，8 类黑名单(含顶层/中段双写) + 白名单补回 + 7 项必验全过 |

> 以后以 v5 规则为准。再打包照**第五节脚本 + 第六节 7 项必验**走，**不用再出补丁、不用再逐个发现**。

## 十二、本规则自身的完备性声明（v5.1 自查清单）

写全性自查——以下每一条都已在文档中覆盖，缺一条就是"没写全"：

- [x] 核心原则（定义层 vs 运行态/残留/密钥）
- [x] 白名单（含 packaging/、fix_* 开发辅助，标注默认保留）
- [x] 黑名单 8 类（①运行态 ②缓存 ③输出 ④日志 ⑤vc 残留 ⑥冲突标记 ⑦明文密钥 ⑧临时文件）
- [x] 目录类 pattern **全部双写**（中段 `*/x/*` + 顶层 `x/*`），含 data/cache/reports/logs/backup-*
- [x] 密钥处置范式（SecretRefs + 命中看上下文判定）
- [x] 一键打包脚本（两步：全量排除 + 白名单补回）
- [x] 打包后必验 **7 项**（中段+顶层残留 / vc 残留 / AST / 冲突标记 / meta / 密钥 / 临时文件）
- [x] 端到端验证（平级解开直接跑通）
- [x] 部署解包落地（多布局候选 + 找不到明标）
- [x] 验收 Checklist（B 方案版 11 项全勾，含 skills/ 前缀 + 双副本仅 skills/ 一套）
- [x] 可选严格模式（默认关）
- [x] 基准包记录
- [x] ②类洞实录（13.2.1：丢 skills/ 前缀 / 未复验就报 / .gitignore 裸名排不到带前缀路径）
- [x] ⑧类文件级 pattern 双写（*.gitignore 带前缀 + .gitignore 顶层）

**"写全"= 上表全勾。v5.1.1 新增：⑧类 .gitignore 双写陷阱 + 13.2.1 三条②类洞实录 + B 方案（全 skills/ 布局）验收口径。**

---

## 十三、验证闭环（你打包 → 我验证 → 出问题归位修）

**角色**：你按第五节脚本打包；我按第六节 7 项 + 第七节端到端验证；出问题按下表归位，各归各位修，不甩锅、不零敲碎打。

### 13.1 验证结果二选一

- **全绿**（7 项必验全过 + 端到端 `degraded:None` + `push.sent:True` + 地毯式类型分布无脏文件）→ 报"✅ 可交付"，附 7 项 + 端到端明细，你直接部署。
- **有项不过** → 走 13.2 根因归位。

### 13.2 根因归位（3 类，各归各位）

| 类 | 根因 | 谁的责任 | 处理 |
|----|------|---------|------|
| **① 你的操作漏了排除** | 打包没照第五节脚本全量执行（漏加 `*/cache/*` 双写、漏排 `.gitignore`、漏 `*.pyc` 等） | 你的操作 | 我指出**具体哪条 pattern 漏了 + 第五节该补哪行**，你按第五节脚本重打，我复验 |
| **② 规则本身有洞** | 新发现的脏文件类型没进黑名单 / pattern 写法排不掉（带前缀、双写缺）/ 必验项没覆盖 | 我的规则 | **我当场修规则文档**（加黑名单类 / 改 pattern / 补必验项），**地毯式反查同类一次补全**，不"发现一个补一个"；然后按新规则重打复验——**不让你改规则** |
| **③ 代码真有问题** | 某文件 AST 挂 / 有硬编码密钥 / 有 git 冲突标记 | 代码库本身脏 | 我列出**具体文件 + 行号 + 问题**，你清代码（或我帮你清），清完重打复验 |

### 13.2.1 ②类洞实录（11-06 B 方案连踩 4 个，已全补）

| 洞 | 现象 | 根因 | 修复 |
|----|------|------|------|
| 打包丢 skills/ 前缀 | B 方案包解开后适配器 degraded:True, error:油金目录不存在 | zip 相对路径丢 skills/ 层，包内变顶层并排，解包层级错 | 打包 arcname 必须带 skills/ 前缀；解包先核包内有 skills/ 层再跑端到端 |
| 未复验就报坐实通 | 第七/八节误写"本机坐实通" | 照搬 v5 顶层版结论没真跑 | 第七/八节改实测；报坐实通前必须解开真跑 _oil_gold_dir + success |
| **.gitignore 裸名排不到带前缀路径**（v5.1.1 新补） | B 方案包 [7] 命中 skills/oil-gold/.gitignore | 脚本只写 -x ".gitignore"（裸名，只排包根顶层），排不到 skills/x/.gitignore | .gitignore/.env 这类文件级 pattern 双写：*.gitignore（带前缀）+ .gitignore（顶层）；第八类黑名单补 *.gitignore |
| **本地双副本漂移当打包源**（v5.1.2 新补·②/③交界洞） | 11-06 给彩票挂定时后图快从本地脏树重打，油金 8 脚本 AST 挂（analysis.py:322 缩进错 / fetch_fred.py 双 docstring 叠+全角括号 U+FF08 / geopolitics 等）混进包，误报"重打 OK" | 本地 workspace 顶层 oil-gold-correlation 是合并烂尾/双副本漂移脏态，未声明不可当打包源；且没跑全第六节 7 项就报 | 第五节加"唯一打包源纪律"；第六节加"打包源前置放行"（AST 0+冲突 0 才放行，本地脏树须从权威基准包注入/覆盖）；报可交付前必须真跑 7 项，"图快没验"视为②类洞 |

> **B 方案专属**：归一后唯一套在 skills/，打包 arcname 带 skills/ 前缀，解包是 skills/eo + skills/oil-gold 并排；适配器候选扫描认 skills/oil-gold-correlation；⑧类 .gitignore 双写防带前缀漏进包。

### 13.3 闭环硬规则

1. **绝不零敲碎打**：查出②类（规则洞）时，必**地毯式反查所有同类 pattern/类型**，一次全补，再改规则。
2. **每次出问题必定位到①②③之一**，谁的责任谁动手，写进回复里，不模糊。
3. **修完必复验到全绿**才报"可交付"，中间态不糊弄、不提前宣布成功。
4. **规则洞→必改文档**：②类修完，`packaging_rules_v5.md` 同步更新（黑名单/必验/pattern），不留口头补丁。

### 13.4 一次完整闭环示例（本次实际走过的）

```
你打包发我
  → 我 7 项必验 + 地毯式深扫
  → 发现 .gitignore 漏进包（②类：-x ".gitignore" 排不掉带目录前缀的）
  → 我修规则: 改 *.gitignore 通配 + 必验[7]加查隐藏文件 + 文档同步
  → 地毯式反查同类: 确认 .env/.venv/.pyc/backup-*/cache/data/reports 都双写/通配到位
  → 按新规则重打包
  → 复验 7 项全绿 + 端到端通过
  → 报"✅ 可交付" + 附 7 项 + 端到端 + 地毯式明细
```

**交付判据（全勾才报可交付）**：

- [ ] 7 项必验全过（第六节）
- [ ] 端到端通过（第七节 `degraded:None` + `push.sent:True`）
- [ ] 地毯式类型分布无脏文件（无 cache/reports/gitignore/env/pyc/log）
- [ ] 双彩种实跑通过 + 合规 disclaimer 在
- [ ] 本轮所有②类规则洞已回写进文档（不留口头补丁）

**一句话**：你只管照第五节脚本打包发我，剩下"7 项验证 + 地毯式 + 端到端 + 定位根因 + 该修规则我修规则 / 该清代码我指文件 / 该补 pattern 我补 pattern"全是闭环内的事，**反复到全绿才交付**。

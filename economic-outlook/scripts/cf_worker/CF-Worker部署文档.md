# Cloudflare Worker 中转部署文档（黄金 Au9999 行情源）

## 一、背景

- 服务器已换到**新加坡（海外 IP）**。
- 东财 / 上金所 / 腾讯 / 新浪等**国内行情源**，对海外云 IP 做风控：直接返回 502 / 403 / 连接被拒。
- 因此服务器本地"直连"这些国内口**基本拉不到数**。

**解决思路**：部署一个 **Cloudflare Worker（海外 CDN 边缘函数）** 做中转。
Worker 的出口 IP 是 Cloudflare 的，部分国内源对 CF IP 放行 / 风控更松，
把请求先发给 Worker，由 Worker 转发到国内源，再回传数据给服务器。
免费额度 **10 万次/天**，个人监控足够。

---

## 二、前置条件

1. 一个 **Cloudflare 账号**（免费注册：https://dash.cloudflare.com/sign-up）
2. 一台能上网的电脑或手机（只需浏览器，**不需要国内电脑**，全程网页操作）

---

## 三、部署步骤（3 分钟）

### 第 1 步：登录 Cloudflare
- 打开 `https://dash.cloudflare.com`
- 右上角 **Sign in**（登录）

### 第 2 步：创建 Worker
1. 左侧菜单 **Workers & Pages** → **Create**
2. 选 **Create Worker**（或 New Worker）
3. 名字随便填，例如 `gold-proxy`（只能小写字母/数字/连字符）

### 第 3 步：贴代码
- 新建后 CF 会显示一个默认代码编辑器
- **删除默认模板全部内容**，把下面 `worker.js` 的内容整段贴进去

### 第 4 步：部署
- 点 **Save and Deploy**（保存并部署）
- 部署成功后，CF 会显示一个 URL，形如：

```
https://gold-proxy.你的CF账号名.workers.dev
```

把这个 URL 记下来（**这就是要交给盯价系统的中转地址**）。

---

## 四、worker.js（要贴进 Cloudflare 的代码）

```javascript
// Cloudflare Worker: 国内行情源中转（海外服务器无法直连东财/上金所）
// 用法: 请求 https://<你的worker>/eastmoney?path=118.AU9999
// 免费额度: 10万次/天, 个人监控够用
export default {
  async fetch(request) {
    const url = new URL(request.url)

    // ① 东财行情中转: /eastmoney?path=<secid>&fields=<f43,f57,f58,f86>
    //    常见 secid:
    //      118.AU9999 = 上金所 Au9999 现货
    //      113.AUM    = 沪金主力
    //      113.AGM    = 沪银主力
    if (url.pathname === '/eastmoney') {
      const secid = url.searchParams.get('path') || '118.AU9999'
      const fields = url.searchParams.get('fields') || 'f43,f57,f58,f86'
      const target = `https://push2.eastmoney.com/api/qt/stock/get?secid=${secid}&fields=${fields}`
      const resp = await fetch(target)
      const body = await resp.text()
      return new Response(body, {
        status: resp.status,
        headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' }
      })
    }

    // ② 上金所官网行情中转: /sge?page=Au9999
    if (url.pathname === '/sge') {
      const page = url.searchParams.get('page') || 'Au9999'
      const target = `https://www.sge.com.cn/graph/${page}`
      const resp = await fetch(target)
      const body = await resp.text()
      return new Response(body, {
        status: resp.status,
        headers: { 'Content-Type': 'text/plain', 'Access-Control-Allow-Origin': '*' }
      })
    }

    // ③ 根路径说明
    if (url.pathname === '/' || url.pathname === '') {
      return new Response(
        'endpoints: /eastmoney?path=118.AU9999  |  /sge?page=Au9999',
        { status: 200, headers: { 'Content-Type': 'text/plain' } }
      )
    }

    return new Response('not found: use /eastmoney?path=... or /sge?page=...', { status: 404 })
  }
}
```

---

## 五、部署后验证（确认 Worker 通了）

在**任意**能上网的设备（手机浏览器直接输网址）访问：

```
https://gold-proxy.你的账号.workers.dev/eastmoney?path=118.AU9999
```

- **返回一段 JSON 数据**（含 `"f43": ...` 字段）= Worker 通了 ✅
- 返回 `502` / 报错 / 空白 = 该 Worker 到东财这条仍被拒，需换 Worker 节点或走付费源

> 说明：即使 Worker 部署成功，"国内源对 CF IP 是否放行"要实测才知道。
> 通了就直接用；不通就转第六节的付费源方案。

---

## 六、Worker URL 怎么交给盯价系统

把第 3 步拿到的完整 URL 交给盯价系统（形如 `https://gold-proxy.xxx.workers.dev`），
系统会：
1. 拉取时**优先走直连东财**，502/拉空时**自动改走你的 Worker 中转**
2. 仍拿不到 → 静默（不出价、不冒旧值）

即：`Worker URL = 东财 502 时的自动备用通道`。

---

## 七、备选方案（CF Worker 也不通时）

| 方案 | 说明 | 成本 |
|---|---|---|
| 国际金 XAU/USD API + 汇率换算 | 海外友好的免费金价 API，换算成人民币/克作参考 | 零成本，需 API Key（部分） |
| 付费行情 API（QOS / 探数 等） | 专门覆盖上金所 Au9999，海外可访问 | 订阅付费 |
| 你网页报数 | 盯价时你直接看行情软件报一个价，系统据此记录/计算 | 零成本，最稳 |

---

## 八、常见问题

- **Q：要买 CF 付费版吗？** A：不用，免费版（10 万次/天）个人监控足够。
- **Q：Worker 会一直收费吗？** A：CF 免费额度内不收费；超出 10 万次/天或 5GB 出站才计，监控场景远低于此。
- **Q：URL 里的"你的账号名"怎么知道？** A：Worker 部署成功页直接显示完整 URL，照抄即可。
- **Q：Worker 部署了但访问还是 502？** A：说明国内源对 CF IP 也拒，转第六节备选方案。

---

**版权：MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)**

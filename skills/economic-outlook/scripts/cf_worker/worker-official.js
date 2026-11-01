// Cloudflare Worker: 东财行情中转(官家11-01 给的完整官方URL口径, 带ut/cb全字段)
// 部署后: https://<你的worker>/eastmoney?path=118.AU9999
// 说明: 东财对海外/CDN出口IP做风控, 若 Worker 转发仍 502, 是出口IP被拒, 非脚本问题
export default {
  async fetch(request) {
    const url = new URL(request.url)
    if (url.pathname === '/eastmoney') {
      const secid = url.searchParams.get('path') || '118.AU9999'
      // 官家 11-01 给的官方东财取数口径(ut + 全字段 + invt/fltt/dect)
      const target = `https://push2.eastmoney.com/api/qt/stock/get?invt=2&fltt=1&fields=f58,f734,f107,f57,f43,f59,f169,f170,f152,f177,f111,f46,f60,f44,f45,f86,f47,f19,f532,f161,f171,f48,f39,f49,f50&secid=${secid}&ut=fa5fd1943c7b386f172d6893dbfba10b&wbp2u=%7C0%7C0%7C0%7Cweb&dect=1`
      const resp = await fetch(target, { headers: { "User-Agent": "Mozilla/5.0", "Referer": "https://quote.eastmoney.com/" } })
      const body = await resp.text()
      return new Response(body, {
        status: resp.status,
        headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' }
      })
    }
    if (url.pathname === '/') {
      return new Response('endpoint: /eastmoney?path=118.AU9999', { status: 200 })
    }
    return new Response('not found: use /eastmoney?path=118.AU9999', { status: 404 })
  }
}

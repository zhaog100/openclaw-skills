// Cloudflare Worker: 国内行情源中转（新加坡机无法直连东财/上金所）
// 部署后, 把东财请求改走 worker: https://<你的worker>/eastmoney?path=118.AU9999
// 免费额度: 10万次/天, 个人监控够用
export default {
  async fetch(request) {
    const url = new URL(request.url)
    if (url.pathname === '/eastmoney') {
      const secid = url.searchParams.get('path') || '118.AU9999'
      const fields = url.searchParams.get('fields') || 'f43,f57,f58,f86'
      // 转发到东财 push2 (国内源, worker 侧无海外IP风控)
      const target = `https://push2.eastmoney.com/api/qt/stock/get?secid=${secid}&fields=${fields}`
      const resp = await fetch(target)
      const body = await resp.text()
      return new Response(body, {
        status: resp.status,
        headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' }
      })
    }
    if (url.pathname === '/sge') {
      // 上金所官网行情中转
      const page = url.searchParams.get('page') || 'Au9999'
      const target = `https://www.sge.com.cn/graph/${page}`
      const resp = await fetch(target)
      const body = await resp.text()
      return new Response(body, {
        status: resp.status,
        headers: { 'Content-Type': 'text/plain', 'Access-Control-Allow-Origin': '*' }
      })
    }
    return new Response('use /eastmoney?path=118.AU9999 or /sge?page=Au9999', { status: 404 })
  }
}

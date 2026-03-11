/**
 * Multi Search Engine 实用示例
 * 演示如何使用web_fetch访问17个搜索引擎
 */

// ============================================
// 国内搜索引擎（8个）
// ============================================

// 1. 百度搜索
async function baiduSearch(query) {
  const url = `https://www.baidu.com/s?wd=${encodeURIComponent(query)}`;
  return await web_fetch({ url, extractMode: "markdown" });
}

// 2. Bing国内版
async function bingSearch(query) {
  const url = `https://cn.bing.com/search?q=${encodeURIComponent(query)}`;
  return await web_fetch({ url, extractMode: "markdown" });
}

// 3. Bing国际版
async function bingInternationalSearch(query) {
  const url = `https://cn.bing.com/search?q=${encodeURIComponent(query)}&ensearch=1`;
  return await web_fetch({ url, extractMode: "markdown" });
}

// 4. 360搜索
async function soSearch(query) {
  const url = `https://www.so.com/s?q=${encodeURIComponent(query)}`;
  return await web_fetch({ url, extractMode: "markdown" });
}

// 5. 搜狗搜索
async function sogouSearch(query) {
  const url = `https://sogou.com/web?query=${encodeURIComponent(query)}`;
  return await web_fetch({ url, extractMode: "markdown" });
}

// 6. 微信搜索
async function wechatSearch(query) {
  const url = `https://wx.sogou.com/weixin?type=2&query=${encodeURIComponent(query)}`;
  return await web_fetch({ url, extractMode: "markdown" });
}

// 7. 头条搜索
async function toutiaoSearch(query) {
  const url = `https://so.toutiao.com/search?keyword=${encodeURIComponent(query)}`;
  return await web_fetch({ url, extractMode: "markdown" });
}

// 8. 集思录搜索
async function jisiluSearch(query) {
  const url = `https://www.jisilu.cn/search/?q=${encodeURIComponent(query)}`;
  return await web_fetch({ url, extractMode: "markdown" });
}

// ============================================
// 国际搜索引擎（9个）
// ============================================

// 1. Google搜索
async function googleSearch(query) {
  const url = `https://www.google.com/search?q=${encodeURIComponent(query)}`;
  return await web_fetch({ url, extractMode: "markdown" });
}

// 2. Google香港
async function googleHKSearch(query) {
  const url = `https://www.google.com.hk/search?q=${encodeURIComponent(query)}`;
  return await web_fetch({ url, extractMode: "markdown" });
}

// 3. DuckDuckGo（隐私保护）
async function duckduckgoSearch(query) {
  const url = `https://duckduckgo.com/html/?q=${encodeURIComponent(query)}`;
  return await web_fetch({ url, extractMode: "markdown" });
}

// 4. Yahoo搜索
async function yahooSearch(query) {
  const url = `https://search.yahoo.com/search?p=${encodeURIComponent(query)}`;
  return await web_fetch({ url, extractMode: "markdown" });
}

// 5. Startpage（Google结果+隐私）
async function startpageSearch(query) {
  const url = `https://www.startpage.com/sp/search?query=${encodeURIComponent(query)}`;
  return await web_fetch({ url, extractMode: "markdown" });
}

// 6. Brave搜索
async function braveSearch(query) {
  const url = `https://search.brave.com/search?q=${encodeURIComponent(query)}`;
  return await web_fetch({ url, extractMode: "markdown" });
}

// 7. Ecosia（种树公益）
async function ecosiaSearch(query) {
  const url = `https://www.ecosia.org/search?q=${encodeURIComponent(query)}`;
  return await web_fetch({ url, extractMode: "markdown" });
}

// 8. Qwant（欧盟GDPR合规）
async function qwantSearch(query) {
  const url = `https://www.qwant.com/?q=${encodeURIComponent(query)}`;
  return await web_fetch({ url, extractMode: "markdown" });
}

// 9. WolframAlpha（知识计算）
async function wolframAlphaQuery(query) {
  const url = `https://www.wolframalpha.com/input?i=${encodeURIComponent(query)}`;
  return await web_fetch({ url, extractMode: "markdown" });
}

// ============================================
// DuckDuckGo Bangs（快捷指令）
// ============================================

// GitHub搜索
async function githubSearch(query) {
  const url = `https://duckduckgo.com/html/?q=!gh+${encodeURIComponent(query)}`;
  return await web_fetch({ url, extractMode: "markdown" });
}

// Stack Overflow搜索
async function stackOverflowSearch(query) {
  const url = `https://duckduckgo.com/html/?q=!so+${encodeURIComponent(query)}`;
  return await web_fetch({ url, extractMode: "markdown" });
}

// Wikipedia搜索
async function wikipediaSearch(query) {
  const url = `https://duckduckgo.com/html/?q=!w+${encodeURIComponent(query)}`;
  return await web_fetch({ url, extractMode: "markdown" });
}

// YouTube搜索
async function youtubeSearch(query) {
  const url = `https://duckduckgo.com/html/?q=!yt+${encodeURIComponent(query)}`;
  return await web_fetch({ url, extractMode: "markdown" });
}

// ============================================
// 高级搜索技巧
// ============================================

// 站内搜索
async function siteSearch(site, query) {
  const url = `https://www.google.com/search?q=site:${site}+${encodeURIComponent(query)}`;
  return await web_fetch({ url, extractMode: "markdown" });
}

// 文件类型搜索
async function fileTypeSearch(fileType, query) {
  const url = `https://www.google.com/search?q=${encodeURIComponent(query)}+filetype:${fileType}`;
  return await web_fetch({ url, extractMode: "markdown" });
}

// 时间过滤搜索（过去N天）
async function recentSearch(query, days) {
  const url = `https://www.google.com/search?q=${encodeURIComponent(query)}&tbs=qdr:d${days}`;
  return await web_fetch({ url, extractMode: "markdown" });
}

// ============================================
// 使用示例
// ============================================

async function examples() {
  console.log('喏，官家！Multi Search Engine实用示例：\n');

  // 示例1: 技术问题搜索
  console.log('示例1: 在Stack Overflow搜索Python问题');
  const pythonResult = await stackOverflowSearch('python list comprehension');
  console.log(pythonResult);

  // 示例2: GitHub项目搜索
  console.log('\n示例2: 在GitHub搜索React项目');
  const reactResult = await githubSearch('react hooks tutorial');
  console.log(reactResult);

  // 示例3: 学术资料搜索
  console.log('\n示例3: 搜索PDF论文');
  const pdfResult = await fileTypeSearch('pdf', 'machine learning survey');
  console.log(pdfResult);

  // 示例4: 微信公众号文章
  console.log('\n示例4: 搜索微信公众号文章');
  const wechatResult = await wechatSearch('项目管理最佳实践');
  console.log(wechatResult);

  // 示例5: 知识计算
  console.log('\n示例5: WolframAlpha知识计算');
  const calcResult = await wolframAlphaQuery('100 USD to CNY');
  console.log(calcResult);
}

// 运行示例
// examples();

module.exports = {
  // 国内搜索引擎
  baiduSearch,
  bingSearch,
  bingInternationalSearch,
  soSearch,
  sogouSearch,
  wechatSearch,
  toutiaoSearch,
  jisiluSearch,

  // 国际搜索引擎
  googleSearch,
  googleHKSearch,
  duckduckgoSearch,
  yahooSearch,
  startpageSearch,
  braveSearch,
  ecosiaSearch,
  qwantSearch,
  wolframAlphaQuery,

  // DuckDuckGo Bangs
  githubSearch,
  stackOverflowSearch,
  wikipediaSearch,
  youtubeSearch,

  // 高级搜索
  siteSearch,
  fileTypeSearch,
  recentSearch
};

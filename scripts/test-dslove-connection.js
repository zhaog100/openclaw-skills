const https = require('https');

const options = {
  hostname: 'api.dslove.fun',
  port: 10000,
  path: '/',
  method: 'GET',
  rejectUnauthorized: false,
  headers: {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
  }
};

console.log('🔍 测试连接：https://api.dslove.fun:10000/\n');

const req = https.request(options, (res) => {
  console.log(`✅ 状态码: ${res.statusCode}`);
  console.log(`📋 响应头:`, JSON.stringify(res.headers, null, 2));

  let data = '';
  res.on('data', (chunk) => {
    data += chunk;
  });

  res.on('end', () => {
    console.log('\n📝 响应内容:');
    console.log(data.slice(0, 5000));
  });
});

req.on('error', (e) => {
  console.error('❌ 连接错误:', e.message);
});

req.setTimeout(15000, () => {
  console.error('❌ 连接超时（15秒）');
  req.destroy();
});

req.end();

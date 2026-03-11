const AIHubMix_Models = [
  { id: 'coding-glm-5-free', name: 'Coding GLM-5' },
  { id: 'gemini-3.1-flash-image-preview-free', name: 'Gemini Vision' },
  { id: 'gemini-3-flash-preview-free', name: 'Gemini Preview' },
  { id: 'gpt-4.1-free', name: 'GPT-4.1' },
  { id: 'gpt-4.1-mini-free', name: 'GPT-4.1 Mini' },
  { id: 'gpt-4o-free', name: 'GPT-4o' },
  { id: 'glm-4.7-flash-free', name: 'GLM-4.7 Flash' },
  { id: 'coding-glm-4.7-free', name: 'Coding GLM-4.7' },
  { id: 'step-3.5-flash-free', name: 'Step' },
  { id: 'coding-minimax-m2.1-free', name: 'MiniMax M2.1' },
  { id: 'coding-glm-4.6-free', name: 'Coding GLM-4.6' },
  { id: 'coding-minimax-m2-free', name: 'MiniMax M2' },
  { id: 'kimi-for-coding-free', name: 'Kimi' },
  { id: 'mimo-v2-flash-free', name: 'Mimo' }
];

async function testModel(model) {
  const startTime = Date.now();
  try {
    const response = await fetch('https://aihubmix.com/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${process.env.AIHUBMIX_API_KEY}`
      },
      body: JSON.stringify({
        model: `aihubmix/${model.id}`,
        messages: [{ role: 'user', content: '你好，请用一句话介绍自己' }],
        max_tokens: 50
      })
    });

    const elapsed = Date.now() - startTime;

    if (!response.ok) {
      const error = await response.text();
      return {
        model: model.name,
        status: '❌',
        error: response.status === 429 ? '限流' : error,
        elapsed
      };
    }

    const data = await response.json();
    return {
      model: model.name,
      status: '✅',
      response: data.choices[0].message.content.slice(0, 50),
      elapsed
    };
  } catch (error) {
    return {
      model: model.name,
      status: '❌',
      error: error.message,
      elapsed: Date.now() - startTime
    };
  }
}

async function runTests() {
  console.log('📊 AIHubMix 免费模型测试开始\n');
  console.log('测试时间:', new Date().toLocaleString('zh-CN', { timeZone: 'Asia/Shanghai' }));
  console.log('测试模型数:', AIHubMix_Models.length);
  console.log('-----------------------------------\n');

  const results = [];
  let successCount = 0;
  let failCount = 0;

  for (const model of AIHubMix_Models) {
    console.log(`测试 ${model.name}...`);
    const result = await testModel(model);
    results.push(result);

    if (result.status === '✅') {
      successCount++;
      console.log(`✅ ${result.model} - ${result.elapsed}ms - ${result.response}\n`);
    } else {
      failCount++;
      console.log(`❌ ${result.model} - ${result.error}\n`);

      // 如果遇到限流，立即停止
      if (result.error === '限流') {
        console.log('⚠️ 检测到限流，停止测试\n');
        break;
      }
    }

    // 每个测试间隔1秒，避免限流
    await new Promise(resolve => setTimeout(resolve, 1000));
  }

  console.log('-----------------------------------');
  console.log('📊 测试结果统计\n');
  console.log(`✅ 成功: ${successCount}`);
  console.log(`❌ 失败: ${failCount}`);
  console.log(`📊 成功率: ${((successCount / (successCount + failCount)) * 100).toFixed(1)}%\n`);

  console.log('详细结果:');
  results.forEach((r, i) => {
    console.log(`${i + 1}. ${r.status} ${r.model} - ${r.elapsed}ms${r.error ? ' - ' + r.error : ''}`);
  });

  // 保存结果到文件
  const reportPath = '/root/.openclaw/workspace/memory/aihubmix-test-report-' + new Date().toISOString().slice(0, 10) + '.json';
  const fs = require('fs');
  fs.writeFileSync(reportPath, JSON.stringify({
    testTime: new Date().toISOString(),
    totalModels: AIHubMix_Models.length,
    successCount,
    failCount,
    successRate: ((successCount / (successCount + failCount)) * 100).toFixed(1),
    results
  }, null, 2));

  console.log(`\n📄 报告已保存: ${reportPath}`);
}

runTests().catch(console.error);

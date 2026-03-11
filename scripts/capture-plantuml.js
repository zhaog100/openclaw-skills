/**
 * PlantUML图表访问和截图脚本
 */

const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');

async function capturePlantUML() {
  console.log('喏，官家！开始访问PlantUML图表！\n');

  const url = 'http://www.plantuml.com/plantuml/uml/RCf12i9038NXVKyHyG8LTQy8lO22wzY9RMWcKp8PAfvUNJcByk1jll-K7SrBb6RZ8qM2MP2roHFhZ8OH7jXFWwMYuP8a6MoxuszL4UY9HVn6BpyB3nf97VhlaLLLNZWAAjqv-0ZxjbsnBgbV-KsmErIAPcdvqwUqikbDt0pY-9rFOQcAbAWgBsdPTibkr5MgLhb4A2lrr5CQgXvMgRHARti82Qo1y68ha6n2Dc04WIQx1aGena1ywBqVOkMPv_6fNw5ZFKOrIc_n1MlcUMP-_tangu706sYUEaSTDfYmIUrD8EOaMvYgmQmFHoL-VmBfrbfWxxVzXFGgySk-z1b1_Rg_y-htH42IdksiOwM71HrDvP_fnRFGpZfPFnqq96OsGjnIwOUYuw21-j3pOA_C-ngK3kdc_73s3vuiS_qUcZ8Eau74tgxaPYIs-0RJDQQyPRTTGei49MXUK38lQx45BbribUov3XuaXHtC4xnAmSJqm5-xo1vktG3hI1npgcyNeRU--t4Jp_u4iqGHo4OtVdRR57FbhhlUvyjRczjVR2TsLqBks-Vksrn4Om3zGpPJiJuLyNqwOby6tGFObx6ZmTKnjnIcdpt44rvxTaBTM6Hx0issqqZXy5YScIF7uyzVn5zi_tNszv0Yug3YENYt2oET5ULFsMPq2UkQSvFt0tqLb33RSwjsRlAZ6Qkg5DeFHBFv_GOz0imsBY2dyNOACkV_WNdbUPtONRTDrP5Bb2mINV8Ge72Bxxn1WkuOk-MvOte8XW7LUpnLMRc66SNVSjQU49PeU9GeYntd80cZ5XGgzeHSsazxow3SYklmNi6wlB96YfvGYOizk3IfnrXhFK8BM6b7cr0E6WRdx0up0m_yXwsNBq6_i6S5w4vvviOput41rHGOruA6fTiiA_kB_NLGiesSFQqBD3QX-RnS8waVFjX65a_7maw2lo719SKscyBYpNC-_GWrHCjckcrfcEpoL1yh9J_Qqw34hJ9KhsW-U3U9kHQeEQhmPdnZ0vGCnQNYFjZ3S50IZNEd_h13dHSN_PZpGPHlg9rKDRoiYJkU0uPvsbutZxGQZZmL2lneaKXmuTC0fG8MsyJ6UxJ1TuuiOttaD5GQyXMtcEKEPaOk7NqE76tCghets-K1qGcqcCSZI2BXy98GYTIvq_E7Gcbl8Tq1jKFqV5JZnit_ITGrKa8dQ47vn-k0HCzoD1G9Xo9H6Dyvxp9mC5sP7xQgO5xJlf4MTdcCxwq5pRINNjELF7viaLeXXT-FMILFGnyIdIJ5tz8z-g_v5m00';

  const browser = await puppeteer.launch({
    headless: 'new'
  });

  const page = await browser.newPage();

  try {
    // 访问PlantUML页面
    console.log('1. 访问PlantUML图表页面...');
    await page.goto(url, {
      waitUntil: 'networkidle2',
      timeout: 30000
    });

    console.log('✅ 页面加载成功\n');

    // 等待图片生成
    await new Promise(resolve => setTimeout(resolve, 5000));

    // 截图
    console.log('2. 截图PlantUML图表...');
    const screenshotPath = './plantuml-diagram.png';
    await page.screenshot({ path: screenshotPath, fullPage: true });
    console.log(`✅ 截图已保存: ${screenshotPath}\n`);

    // 提取页面信息
    console.log('3. 提取页面信息...');
    const pageInfo = await page.evaluate(() => {
      return {
        title: document.title,
        url: window.location.href,
        hasImage: !!document.querySelector('img'),
        imageCount: document.querySelectorAll('img').length
      };
    });

    console.log('页面标题:', pageInfo.title);
    console.log('包含图片:', pageInfo.hasImage);
    console.log('图片数量:', pageInfo.imageCount);

    // 保存页面信息
    const infoPath = './plantuml-info.json';
    fs.writeFileSync(infoPath, JSON.stringify(pageInfo, null, 2));
    console.log(`\n✅ 页面信息已保存: ${infoPath}`);

    console.log('\n' + '='.repeat(60));
    console.log('PlantUML图表访问完成');
    console.log('='.repeat(60));
    console.log(`📸 截图位置: ${screenshotPath}`);
    console.log(`📄 信息位置: ${infoPath}`);
    console.log('='.repeat(60));

  } catch (error) {
    console.error('❌ 访问失败:', error.message);

    // 保存错误截图
    try {
      await page.screenshot({ path: './plantuml-error.png' });
      console.log('错误截图已保存: ./plantuml-error.png');
    } catch (e) {
      console.log('截图失败');
    }
  } finally {
    await browser.close();
  }
}

// 运行
capturePlantUML().catch(console.error);

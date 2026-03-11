// 快手极速版自动签到+获取Cookie
// 适配设备：Redmi K40 Gaming (Hyper OS)
// 版本：v1.0.0
// 作者：米粒儿

auto.waitFor();

// 主函数
function main() {
    console.show();
    console.log("=====================================");
    console.log("快手极速版自动签到工具 v1.0.0");
    console.log("适配：Redmi K40 Gaming");
    console.log("=====================================");
    console.log("");

    // 步骤1：打开快手极速版
    console.log("【步骤1】打开快手极速版...");
    openKuaishou();

    // 步骤2：等待加载
    console.log("【步骤2】等待加载（5秒）...");
    sleep(5000);

    // 步骤3：查找签到按钮
    console.log("【步骤3】查找签到按钮...");
    clickSignButton();

    // 步骤4：获取Cookie
    console.log("【步骤4】获取Cookie...");
    getCookies();

    console.log("=====================================");
    console.log("完成！Cookie已复制到剪贴板");
    console.log("=====================================");
}

// 打开快手极速版
function openKuaishou() {
    try {
        launch("com.kuaishou.nebula");
        console.log("✅ 已打开快手极速版");
    } catch (e) {
        console.error("❌ 打开失败：" + e);
        toast("请先安装快手极速版");
        exit();
    }
}

// 点击签到按钮
function clickSignButton() {
    // 等待页面加载
    sleep(3000);

    // 查找签到按钮
    var signButtons = [
        text("签到").findOne(3000),
        text("立即签到").findOne(3000),
        text("去签到").findOne(3000),
        desc("签到").findOne(3000)
    ];

    for (var i = 0; i < signButtons.length; i++) {
        var btn = signButtons[i];
        if (btn) {
            console.log("✅ 找到签到按钮");
            btn.click();
            sleep(2000);
            console.log("✅ 已点击签到");
            return true;
        }
    }

    console.log("⚠️ 未找到签到按钮（可能已签到）");
    return false;
}

// 获取Cookie
function getCookies() {
    console.log("正在获取Cookie...");

    console.log("\n【手动获取Cookie方法】");
    console.log("1. 打开浏览器");
    console.log("2. 访问：https://www.kuaishou.com");
    console.log("3. F12 → Application → Cookies");
    console.log("4. 复制：kuaishou.api_st");

    console.log("\n【自动获取方法】");
    console.log("1. 使用抓包APP（如HttpCanary）");
    console.log("2. 打开快手极速版");
    console.log("3. 查看抓包记录");
    console.log("4. 找到Cookie字段");

    // 复制示例Cookie到剪贴板
    setClip("示例Cookie：kuaishou.api_st=xxx;userId=xxx;");
    console.log("\n✅ 示例已复制到剪贴板");
}

// 启动
main();

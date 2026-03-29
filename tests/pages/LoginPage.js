// 登录页面对象模型
class LoginPage {
  constructor(page) {
    this.page = page;

    // 登录元素
    this.tenantCombobox = 'button[role="combobox"]';
    this.accountInput = 'input:not([type="password"]):not([type="hidden"]):visible >> nth=0';
    this.passwordInput = 'input[type="password"]:visible';
    this.loginButton = 'button:has-text("登")';
  }

  // 登录
  async login(tenant = 'TeamFlow', account = 'test', password = 'test123') {
    console.log('开始登录...');

    // 等待页面加载
    await this.page.waitForLoadState('networkidle');
    await this.page.waitForTimeout(3000);

    // 选择租户
    console.log('选择租户...');
    await this.page.getByRole('combobox').click();
    await this.page.waitForTimeout(1000);
    await this.page.getByRole('option', { name: tenant }).click();
    await this.page.waitForTimeout(1000);

    // 填写账号
    console.log('填写账号...');
    const accountInput = await this.page.$(this.accountInput);
    await accountInput.fill(account);
    await this.page.waitForTimeout(500);

    // 填写密码
    console.log('填写密码...');
    const passwordInput = await this.page.$(this.passwordInput);
    await passwordInput.fill(password);
    await this.page.waitForTimeout(500);

    // 点击登录
    console.log('点击登录...');
    const loginButton = await this.page.$(this.loginButton);
    await loginButton.click();

    // 等待登录完成
    await this.page.waitForTimeout(5000);

    console.log('登录完成');
  }
}

module.exports = LoginPage;

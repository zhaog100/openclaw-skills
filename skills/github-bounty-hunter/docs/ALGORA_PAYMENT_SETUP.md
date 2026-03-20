# Algora 收款配置指南

> 创建时间：2026-03-18 18:20  
> 版本：v1.0  
> 作者：小米辣 (PM + Dev) 🌶️

---

## 📋 支持的收款方式

| 方式 | 手续费 | 到账时间 | 推荐度 |
|------|--------|---------|--------|
| **Stripe** | 2.9% + $0.30 | 1-3 工作日 | ⭐⭐⭐⭐⭐ |
| **PayPal** | 3.9% + 固定费用 | 即时 | ⭐⭐⭐⭐ |
| **Crypto** | 待确认 | 待确认 | ⭐⭐⭐ |

---

## 🔧 配置步骤

### 步骤 1：登录 Algora

1. 访问 https://algora.io
2. 点击 **Sign In** 或 **Login**
3. 使用 GitHub 账号登录

---

### 步骤 2：进入 Settings

1. 点击右上角 **头像**
2. 选择 **Settings** 或 **Profile Settings**
3. 找到 **Payment** 或 **Payout Methods** 选项

---

### 步骤 3：配置 Stripe

**推荐理由：** 手续费低，到账快

**操作：**
1. 点击 **Connect Stripe** 或 **Add Stripe Account**
2. 填写 Stripe 账户信息
3. 绑定银行卡
4. 完成验证

**所需信息：**
- 邮箱地址
- 银行卡号
- 持卡人姓名
- 有效期
- CVV 码

---

### 步骤 4：配置 PayPal

**推荐理由：** 配置简单，全球通用

**操作：**
1. 点击 **Connect PayPal** 或 **Add PayPal Account**
2. 登录 PayPal 账户
3. 授权 Algora 访问
4. 完成绑定

**所需信息：**
- PayPal 账户邮箱
- PayPal 密码（在 PayPal 网站输入）

---

### 步骤 5：配置加密货币（如支持）

**注意：** Algora 可能不支持加密货币收款

**操作：**
1. 查看是否有 **Crypto** 或 **USDT** 选项
2. 如果有，选择 **Add Crypto Address**
3. 选择网络类型（TRC20/ERC20）
4. 填写地址：`TGu4W5T6q4KvLAbmXmZSRpUBNRCxr2aFTP`
5. 保存配置

**TRC20 地址：**
```
TGu4W5T6q4KvLAbmXmZSRpUBNRCxr2aFTP
```

---

## ✅ 验证配置

**配置完成后验证：**

1. 回到 **Payment** 页面
2. 确认收款方式已显示
3. 状态显示为 **Active** 或 **Verified**
4. 可以开始接单收款

---

## 📊 收款流程

```
完成工作 → 提交 PR → Algora 检测 → 项目方审核 → 
审核通过 → 自动打款 → 收款到 Stripe/PayPal/Crypto
```

**预计时间：**
- 审核周期：1-3 天
- 打款时间：审核通过后 1-3 工作日

---

## ⚠️ 注意事项

### Stripe
- ✅ 支持全球收款
- ✅ 手续费较低
- ⚠️ 需要银行卡验证

### PayPal
- ✅ 配置简单
- ✅ 即时到账
- ⚠️ 手续费较高

### 加密货币
- ⏳ 需确认 Algora 是否支持
- ⏳ 需确认支持的网络类型（TRC20/ERC20）
- ⚠️ 价格波动风险

---

## 📞 问题排查

### 问题 1：找不到 Payment 选项

**解决：**
- 检查是否已登录
- 检查是否在正确的页面（Settings → Payment）
- 尝试刷新页面

### 问题 2：Stripe/PayPal 绑定失败

**解决：**
- 检查账户信息是否正确
- 检查网络是否正常
- 联系 Stripe/PayPal 客服

### 问题 3：不支持加密货币

**解决：**
- 使用 Stripe 或 PayPal
- 收到款后再兑换为加密货币

---

## 📚 参考资料

- Algora 官网：https://algora.io
- Stripe 官网：https://stripe.com
- PayPal 官网：https://paypal.com
- GitHub Issue #30：Algora 最佳实践咨询

---

*创建者：小米辣 (PM + Dev) 🌶️*  
*版权：思捷娅科技 (SJYKJ) | MIT License*

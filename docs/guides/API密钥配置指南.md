# API密钥配置指南

## 🔑 快速配置API密钥

### 立即配置步骤

#### 1. 获取API密钥
选择一个AI服务提供商：

**推荐选项 (有免费额度):**
1. **OpenAI GPT** - 需要付费，但有免费试用
2. **Zhipu AI** - 有免费额度
3. **Google Gemini** - 有免费额度  
4. **Anthropic Claude** - 有免费额度

**获取方式:**
- 访问对应官网注册
- 获取API密钥
- 充值获得额度

#### 2. 配置环境变量
在PowerShell中执行：

```powershell
# OpenAI API密钥
$env:OPENAI_API_KEY = "sk-your-openai-key-here"

# ZAI API密钥  
$env:ZAI_API_KEY = "sk-your-zai-key-here"

# 永久保存（可选）
[Environment]::SetEnvironmentVariable("OPENAI_API_KEY", "sk-your-openai-key-here", "User")
[Environment]::SetEnvironmentVariable("ZAI_API_KEY", "sk-your-zai-key-here", "User")
```

#### 3. 验证配置
```bash
& "C:\Users\zhaog\AppData\Roaming\npm\pi.ps1" --list-models
```

#### 4. 测试高级功能
```bash
& "C:\Users\zhaog\AppData\Roaming\npm\pi.ps1" "/qmd PMP认证"
& "C:\Users\zhaog\AppData\Roaming\npm\pi.ps1" "/qmd 敏捷方法"
& "C:\Users\zhaog\AppData\Roaming\npm\pi.ps1" "/qmd 测试工具"
```

### 配置文件方式

#### 创建配置文件
```json
# ~/.pi/agent/config.json
{
  "api_key": "sk-your-openai-key-here",
  "provider": "openai",
  "model": "gpt-3.5-turbo"
}
```

### 免费API选项对比

| 服务 | 免费额度 | 质量 | 易用性 | 推荐指数 |
|------|----------|------|--------|----------|
| **OpenAI GPT** | $5免费额度 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Zhipu AI** | 免费额度 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Google Gemini** | 免费额度 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Anthropic Claude** | 免费额度 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |

### 高级功能预期

#### 1. AI增强搜索
- ✅ 智能关键词匹配
- ✅ 语义理解搜索
- ✅ 相关内容推荐
- ✅ 深度内容分析

#### 2. 交互式问答
- ✅ 自然语言查询
- ✅ 智能问答功能
- ✅ 上下文理解
- ✅ 多轮对话

#### 3. 内容生成
- ✅ 自动内容建议
- ✅ 智能摘要生成
- ✅ 相关内容推荐
- ✅ 学习路径规划

### 使用建议

#### 立即可做
1. **配置免费API** - 选择免费额度较多的服务
2. **测试基础功能** - 验证AI增强功能
3. **对比效果** - 测试不同API的效果

#### 中期优化
1. **升级付费版** - 根据使用需求升级
2. **功能调优** - 优化使用体验
3. **成本控制** - 合理控制API使用

### 常见问题解决

#### 问题1: API密钥无效
- **解决**: 检查密钥格式是否正确
- **解决**: 确认账号余额充足
- **解决**: 检查网络连接

#### 问题2: 服务不可用
- **解决**: 尝试不同的API服务
- **解决**: 检查防火墙设置
- **解决**: 使用代理或VPN

#### 问题3: 响应速度慢
- **解决**: 检查网络延迟
- **解决**: 选择更快的API服务
- **解决**: 使用本地缓存

### 配置完成检查清单

- [ ] 获取API密钥
- [ ] 配置环境变量
- [ ] 验证模型列表
- [ ] 测试搜索功能
- [ ] 测试问答功能
- [ ] 测试内容生成
- [ ] 优化使用体验

---

**🎯 目标**: 启用AI增强的高级功能
**🕒 预计时间**: 10-30分钟
**💰 成本**: 免费额度足够测试
**🚀 状态**: 等待用户配置API密钥
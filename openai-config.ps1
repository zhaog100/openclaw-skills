# OpenAI API快速配置脚本

# 立即配置OpenAI API并启用高级功能

Write-Host "🚀 OpenAI API快速配置" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green

Write-Host ""
Write-Host "📋 配置步骤:" -ForegroundColor Yellow
WriteHost "1. 访问: https://platform.openai.com/" -ForegroundColor Cyan
Write-Host "2. 注册账号并验证邮箱" -ForegroundColor Cyan
Write-Host "3. 点击 'API keys' -> 'Create new secret key'" -ForegroundColor Cyan
Write-Host "4. 输入密钥名称: QMD-Knowledge-Base" -ForegroundColor Cyan
Write-Host "5. 复制生成的密钥 (格式: sk-xxxxxxxx)" -ForegroundColor Cyan
Write-Host "6. 在下方粘贴密钥" -ForegroundColor Cyan
Write-Host ""

# 获取用户输入的API密钥
$apiKey = Read-Host -Prompt "请输入您的OpenAI API密钥 (sk-xxxxxxxxxxxxxxxxxxxxx)"

# 验证API密钥格式
if ($apiKey -match "^sk-[a-zA-Z0-9]{48}$") {
    Write-Host "✅ API密钥格式正确" -ForegroundColor Green
    
    # 设置环境变量
    $env:OPENAI_API_KEY = $apiKey
    
    # 永久保存到用户环境变量
    [Environment]::SetEnvironmentVariable("OPENAI_API_KEY", $apiKey, "User")
    
    Write-Host ""
    Write-Host "🔧 环境变量已设置:" -ForegroundColor Green
    Write-Host "OPENAI_API_KEY = $apiKey" -ForegroundColor Cyan
    
    Write-Host ""
    Write-Host "🧪 验证配置..." -ForegroundColor Yellow
    
    # 验证配置
    try {
        $result = & "C:\Users\zhaog\AppData\Roaming\npm\pi.ps1" --list-models 2>&1
        if ($result -match "No models available") {
            Write-Host "❌ 配置验证失败: API密钥可能无效或未正确设置" -ForegroundColor Red
            Write-Host "💡 建议: 检查API密钥是否正确，以及是否已验证邮箱" -ForegroundColor Yellow
        } else {
            Write-Host "✅ 配置验证成功!" -ForegroundColor Green
            Write-Host ""
            Write-Host "🎉 OpenAI API配置完成!" -ForegroundColor Green
            Write-Host ""
            Write-Host "🚀 现在可以测试高级功能:" -ForegroundColor Yellow
            Write-Host "1. 测试AI搜索: pi '/qmd PMP认证'" -ForegroundColor Cyan
            Write-Host "2. 测试智能问答: '如何制定项目计划？'" -ForegroundColor Cyan
            Write-Host "3. 测试内容分析: '分析项目管理的关键成功因素'" -ForegroundColor Cyan
            Write-Host ""
            Write-Host "💰 免费额度: $5免费额度 (约支持500-1000次查询)" -ForegroundColor Cyan
            Write-Host "⏰ 使用监控: 建议定期检查API使用量和余额" -ForegroundColor Cyan
        }
    } catch {
        Write-Host "❌ 配置验证出错: $_" -ForegroundColor Red
    }
} else {
    Write-Host "❌ API密钥格式错误!" -ForegroundColor Red
    Write-Host "正确格式: sk-xxxxxxxxxxxxxxxxxxxxx (48个字符)" -ForegroundColor Yellow
    Write-Host "💡 请检查密钥格式并重新输入" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "📚 更多帮助: 请查看 OpenAI配置指南.md" -ForegroundColor White
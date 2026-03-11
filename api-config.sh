#!/bin/bash

# 配置API密钥的简化方法

echo "🔑 API密钥配置方案"
echo "=================="

echo ""
echo "方法1: 环境变量方式"
echo "-------------------"
echo "在终端中执行:"
echo "export OPENAI_API_KEY='sk-your-key-here'"
echo "export ZAI_API_KEY='sk-your-key-here'"
echo ""

echo "方法2: 配置文件方式"
echo "--------------------"
echo "创建配置文件 ~/.pi/agent/config.json:"
echo '{'
echo '  "api_key": "sk-your-key-here",'
echo '  "provider": "openai"'
echo '}'

echo ""
echo "方法3: 免费API选项"
echo "--------------------"
echo "1. OpenAI GPT (需要付费)"
echo "2. Anthropic Claude (需要付费)"
echo "3. Gemini API (有免费额度)"
echo "4. Hugging Face (有免费模型)"

echo ""
echo "推荐:"
echo "1. 先使用免费额度测试"
echo "2. 成功后再付费升级"
echo "3. 考虑使用本地模型"

echo ""
echo "🚀 立即执行:"
echo "# 查看当前配置"
echo "cat ~/.pi/agent/config.json"
echo ""

echo "✅ 配置完成后重新测试pi功能"
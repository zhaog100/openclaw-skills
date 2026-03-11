# 知识库初始化脚本

# 简化的知识库初始化和测试
echo "🚀 QMD知识库初始化测试"
echo "=========================="

# 测试基本pi功能
echo "1. 测试pi基本功能..."
pi "Hello, this is a test from QMD knowledge base" --print --timeout 10

# 测试文档读取
echo ""
echo "2. 测试文档读取..."
pi "读取 knowledge/README.md 的前5行内容" --print --timeout 10

# 测试内容搜索
echo ""
echo "3. 测试内容搜索..."
pi "在 knowledge 目录中搜索包含'项目'的文档" --print --timeout 10

echo ""
echo "✅ 基础测试完成！"
#!/bin/bash
# OWASP ZAP 安全扫描脚本
# 用于自动扫描 OpenClaw Dashboard 的安全性

set -e

# 配置
API_KEY="changeme"  # 在 ZAP GUI 中获取：Tools → Options → API
BASE_URL="http://127.0.0.1:8090"
TARGET="http://127.0.0.1:18789"
WORKSPACE="/home/zhaog/.openclaw/workspace"
LOGS_DIR="$WORKSPACE/logs"

# 颜色
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "============================================================"
echo "🔒 OWASP ZAP 安全扫描"
echo "============================================================"
echo ""
echo "目标：$TARGET"
echo "ZAP API: $BASE_URL"
echo ""

# 创建日志目录
mkdir -p "$LOGS_DIR"

# 检查 ZAP 是否运行
echo "🔍 检查 ZAP 运行状态..."
if ! curl -s "$BASE_URL" > /dev/null 2>&1; then
    echo -e "${RED}❌ ZAP 未运行${NC}"
    echo ""
    echo "💡 请先启动 ZAP："
    echo "   zaproxy -daemon -port 8090"
    echo ""
    exit 1
fi
echo -e "${GREEN}✅ ZAP 运行中${NC}"
echo ""

# 启动爬取
echo "🕷️  启动自动爬取..."
SPIDER_RESPONSE=$(curl -s "$BASE_URL/JSON/spider/action/scan/?url=$TARGET&apikey=$API_KEY")
echo "$SPIDER_RESPONSE" | jq -r '.message' 2>/dev/null || echo "爬取已启动"
echo ""

# 等待爬取完成
echo "⏳ 等待爬取完成（60 秒）..."
for i in {60..1}; do
    printf "\r   剩余时间：%d秒" $i
    sleep 1
done
echo ""
echo -e "${GREEN}✅ 爬取完成${NC}"
echo ""

# 启动主动扫描
echo "🔍 启动主动扫描..."
ASCAN_RESPONSE=$(curl -s "$BASE_URL/JSON/ascan/action/scan/?url=$TARGET&apikey=$API_KEY")
echo "$ASCAN_RESPONSE" | jq -r '.message' 2>/dev/null || echo "扫描已启动"
echo ""

# 等待扫描完成
echo "⏳ 等待扫描完成（120 秒）..."
for i in {120..1}; do
    printf "\r   剩余时间：%d秒" $i
    sleep 1
done
echo ""
echo -e "${GREEN}✅ 扫描完成${NC}"
echo ""

# 获取警报统计
echo "📊 获取警报统计..."
echo ""

# 高风险警报
HIGH_ALERTS=$(curl -s "$BASE_URL/JSON/core/view/alerts/?apikey=$API_KEY&baseurl=$TARGET" | \
    jq '[.alerts[] | select(.riskcode=="2")] | length' 2>/dev/null || echo "0")

# 中风险警报
MEDIUM_ALERTS=$(curl -s "$BASE_URL/JSON/core/view/alerts/?apikey=$API_KEY&baseurl=$TARGET" | \
    jq '[.alerts[] | select(.riskcode=="1")] | length' 2>/dev/null || echo "0")

# 低风险警报
LOW_ALERTS=$(curl -s "$BASE_URL/JSON/core/view/alerts/?apikey=$API_KEY&baseurl=$TARGET" | \
    jq '[.alerts[] | select(.riskcode=="0")] | length' 2>/dev/null || echo "0")

# 信息提示
INFO_ALERTS=$(curl -s "$BASE_URL/JSON/core/view/alerts/?apikey=$API_KEY&baseurl=$TARGET" | \
    jq '[.alerts[] | select(.riskcode=="-1")] | length' 2>/dev/null || echo "0")

echo "============================================================"
echo "📋 扫描结果"
echo "============================================================"
echo ""
echo -e "  ${RED}高风险漏洞：${HIGH_ALERTS}${NC}"
echo -e "  ${YELLOW}中风险漏洞：${MEDIUM_ALERTS}${NC}"
echo -e "  低风险问题：${LOW_ALERTS}"
echo -e "  信息提示：${INFO_ALERTS}"
echo ""

# 生成报告
echo "📄 生成 HTML 报告..."
REPORT_PATH="$LOGS_DIR/security-report-$(date +%Y-%m-%d).html"
curl -s "$BASE_URL/OTHER/core/other/htmlreport/?apikey=$API_KEY" > "$REPORT_PATH"
echo -e "${GREEN}✅ 报告已保存：$REPORT_PATH${NC}"
echo ""

# 阈值检查
echo "============================================================"
echo "✅ 安全检查"
echo "============================================================"
echo ""

EXIT_CODE=0

if [ "$HIGH_ALERTS" -gt 0 ]; then
    echo -e "${RED}❌ 发现 $HIGH_ALERTS 个高风险漏洞${NC}"
    echo ""
    echo "💡 建议：立即修复以下类型的高风险漏洞："
    echo "   - SQL 注入"
    echo "   - 跨站脚本 (XSS)"
    echo "   - 路径遍历"
    echo "   - 远程代码执行"
    echo ""
    EXIT_CODE=1
else
    echo -e "${GREEN}✅ 无高风险漏洞${NC}"
fi

if [ "$MEDIUM_ALERTS" -gt 5 ]; then
    echo -e "${YELLOW}⚠️  发现 $MEDIUM_ALERTS 个中风险漏洞${NC}"
    echo ""
    echo "💡 建议：尽快修复以下类型的中风险漏洞："
    echo "   - 安全头缺失"
    echo "   - Cookie 安全问题"
    echo "   - 信息泄露"
    echo ""
    EXIT_CODE=2
else
    echo -e "${GREEN}✅ 中风险漏洞在可接受范围内${NC}"
fi

if [ "$EXIT_CODE" -eq 0 ]; then
    echo -e "${GREEN}✅ 安全检查通过！${NC}"
    echo ""
fi

echo "============================================================"
echo ""
echo "💡 下一步："
echo "   1. 在浏览器中查看报告：firefox $REPORT_PATH"
echo "   2. 修复发现的漏洞"
echo "   3. 重新运行扫描验证修复效果"
echo ""

exit $EXIT_CODE

#!/bin/bash
# oil-gold-correlation 跨平台启动脚本 (Linux/macOS)
# 用法: ./run.sh {fetch|analyze|visualize|report|advisor|all}
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# 优先检测 conda 环境
if command -v conda &>/dev/null && [ -d "$HOME/miniconda3/envs/oil-gold" ]; then
    source "$HOME/miniconda3/etc/profile.d/conda.sh"
    conda activate oil-gold
elif command -v python3 &>/dev/null; then
    PYTHON=python3
else
    echo "❌ 需要 Python 3.10+ 环境"
    echo "推荐安装 Miniconda: https://docs.conda.io/en/latest/miniconda.html"
    exit 1
fi

case "${1:-all}" in
    fetch)      python3 "$SCRIPT_DIR/scripts/fetch_data.py" "$@" ;;
    analyze)    python3 "$SCRIPT_DIR/scripts/analysis.py" "$@" ;;
    visualize)  python3 "$SCRIPT_DIR/scripts/visualize.py" "$@" ;;
    report)     python3 "$SCRIPT_DIR/scripts/report.py" "$@" ;;
    advisor)    python3 "$SCRIPT_DIR/scripts/advisor.py" "$@" ;;
    all)        python3 "$SCRIPT_DIR/scripts/main.py" daily ;;
    health)     python3 "$SCRIPT_DIR/scripts/advisor.py" --health-check ;;
    geopolitics) python3 "$SCRIPT_DIR/scripts/geopolitics.py" "$@" ;;
    opportunity) python3 "$SCRIPT_DIR/scripts/opportunity_scanner.py" "$@" ;;
    json) python3 "$SCRIPT_DIR/scripts/report_json.py" "$@" ;;
    *)          echo "用法: $0 {fetch|analyze|visualize|report|advisor|all|health|geopolitics|opportunity|json}"
                echo "示例: ./run.sh fetch 7d"
                echo "      ./run.sh advisor 3"
                echo "      ./run.sh all"
                echo "      ./run.sh geopolitics"
                echo "      ./run.sh json --period 1y"
                echo "      ./run.sh opportunity" ;;
esac
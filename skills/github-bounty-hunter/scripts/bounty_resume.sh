#!/bin/bash
# bounty_resume.sh - 恢复超时中断的开发进度（v3.0）
# 用法：bash bounty_resume.sh <work_dir>
# 特点：自动检测已完成阶段，从中断点继续

set -euo pipefail

WORK_DIR="$1"

if [ ! -d "$WORK_DIR" ]; then
    echo "❌ Error: Work directory not found: $WORK_DIR"
    exit 1
fi

cd "$WORK_DIR"

echo "🔄 Resuming bounty development..."
echo "   Work Dir: $WORK_DIR"
echo ""

# 检测已完成的阶段
PHASE1=[ -f ".phase1_analysis.json" ] && echo "✅" || echo "❌"
PHASE2=[ -f ".phase2_design.json" ] && echo "✅" || echo "❌"
PHASE3=[ -f ".phase3_impl.json" ] && echo "✅" || echo "❌"
PHASE4=[ -f ".phase4_pr.json" ] && echo "✅" || echo "❌"

echo "📊 Progress Status:"
echo "   Phase 1 (Analysis): $PHASE1"
echo "   Phase 2 (Design):   $PHASE2"
echo "   Phase 3 (Impl):     $PHASE3"
echo "   Phase 4 (PR):       $PHASE4"
echo ""

# 读取上下文
if [ -f ".dev_context.json" ]; then
    REPO=$(python3 -c "import json;print(json.load(open('.dev_context.json'))['repo'])")
    ISSUE=$(python3 -c "import json;print(json.load(open('.dev_context.json'))['issue'])")
    BRANCH=$(python3 -c "import json;print(json.load(open('.dev_context.json'))['branch'])")
    
    echo "📋 Context:"
    echo "   Repo: $REPO"
    echo "   Issue: #$ISSUE"
    echo "   Branch: $BRANCH"
    echo ""
fi

# 确定从哪个阶段继续
if [ -f ".phase4_pr.json" ]; then
    echo "✅ All phases complete! Ready to submit PR."
    echo ""
    echo "🎯 Next steps:"
    echo "   1. Review code"
    echo "   2. git push origin $BRANCH"
    echo "   3. Create PR with PR_TEMPLATE.md"
    exit 0
elif [ -f ".phase3_impl.json" ]; then
    echo "⏭️  Resuming from Phase 4 (Testing & PR Prep)..."
    # 执行 Phase 4
    echo "🚀 Phase 4/4: Testing & PR Prep (2 min)..."
    # ... (Phase 4 实现代码)
elif [ -f ".phase2_design.json" ]; then
    echo "⏭️  Resuming from Phase 3 (Implementation)..."
    # 执行 Phase 3
elif [ -f ".phase1_analysis.json" ]; then
    echo "⏭️  Resuming from Phase 2 (Design)..."
    # 执行 Phase 2
else
    echo "⏭️  No phase found. Starting from Phase 1..."
    # 执行 Phase 1
fi

echo ""
echo "💡 Tip: All progress is saved in .phase*.json files"

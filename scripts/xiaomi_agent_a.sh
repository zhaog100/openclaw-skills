#!/bin/bash
# 小米辣工作流程 - ClawHub协作（智能体A）
# 小米辣负责开发技能并提交米粒儿Review

echo "🌾 === 小米辣工作流程（智能体A）==="
echo "我是小米辣，现在开始工作！"

# 步骤1：开发新技能
read -p "请输入技能名称（如：devto-surfer）: " SKILL_NAME
read -p "请输入版本号（如：1.0.0）: " VERSION

git checkout -b feature/$SKILL_NAME
echo "✅ 小米辣创建了分支：feature/$SKILL_NAME"

echo "小米辣正在开发 $SKILL_NAME 技能..."
read -p "开发完成？按回车继续..."

cd /root/.openclaw/workspace/skills/$SKILL_NAME
git add .
git commit -m "feat: 小米辣开发 $SKILL_NAME 技能"
git push origin feature/$SKILL_NAME
echo "✅ 小米辣已推送代码到Git"

echo "$(date) | 小米辣 | 提交PR | $SKILL_NAME | 等待米粒儿Review" > /tmp/notify_mili.txt
echo "✅ 小米辣已通知米粒儿"

read -p "米粒儿Review已通过？(y/n): " REVIEW_OK

if [ "$REVIEW_OK" = "y" ]; then
    git checkout master
    git pull origin master
    git merge feature/$SKILL_NAME
    git push origin master
    echo "✅ 小米辣已合并到master"
    
    cd /root/.openclaw/workspace/skills/$SKILL_NAME
    clawhub publish . --slug $SKILL_NAME --version $VERSION --name "$SKILL_NAME"
    
    echo "$(date) | 小米辣 | 发布 | $SKILL_NAME v$VERSION | 成功" >> /root/.openclaw/workspace/logs/clawhub_operations.log
    git add /root/.openclaw/workspace/logs/clawhub_operations.log
    git commit -m "chore: 小米辣发布 $SKILL_NAME v$VERSION"
    git push origin master
    
    echo "✅ 小米辣发布完成！🌾"
    echo "ClawHub链接：https://clawhub.com/skills/$SKILL_NAME"
else
    echo "❌ Review未通过，小米辣会修改后重新提交"
fi

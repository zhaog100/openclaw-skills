#!/bin/bash
# 语音技能安装提醒脚本
# 执行时间：2026-03-10 09:00

LOG_FILE="/home/zhaog/.openclaw/workspace/logs/voice-reminder.log"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

echo "[$TIMESTAMP] 开始发送语音技能安装提醒..." >> "$LOG_FILE"

# 发送QQ提醒消息
# 使用 openclaw message send 命令
MESSAGE="官家，早安！🌾

⏰ 语音技能安装提醒

昨天您说今天要安装语音技能套装，现在准备好了吗？

📦 安装内容：
1. voice-chat（语音对话，6种方言）
2. voice-wake（语音唤醒，5种唤醒词）
3. talk-mode（持续对话模式）

📋 安装命令：
sudo apt update
sudo apt install -y portaudio19-dev python3-pip
python3 -m pip install openai-whisper pyttsx3 pyaudio webrtcvad

准备好了就告诉我，我来帮您完成安装！🦞"

# 发送消息
openclaw message send --channel qqbot --to "8C21AFD77B89CA793A2AAC9A3ABEEA25" "$MESSAGE" >> "$LOG_FILE" 2>&1

if [ $? -eq 0 ]; then
    echo "[$TIMESTAMP] ✅ 提醒发送成功" >> "$LOG_FILE"
else
    echo "[$TIMESTAMP] ❌ 提醒发送失败" >> "$LOG_FILE"
fi

# 发送完成后删除自己
(crontab -l | grep -v "voice-skill-install-reminder.sh") | crontab -

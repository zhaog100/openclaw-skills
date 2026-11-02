# video-frames 视频抽帧理解技能

> Copyright (c) 2026 思捷娅科技 (SJYKJ) | MIT License
> 版本: v1.0 | 创建: 2026-11-02 | 作者: 小米椒

## 触发条件
用户发来视频（mp4/mov 等）且需要理解内容。OpenClaw 当前模型不支持原生视频读取时，
走本技能：ffmpeg 抽关键帧 → view_image 批量喂帧 → 出结论。

## 步骤

### 1. 探测视频基本信息
```bash
ffprobe -v error -show_entries format=duration,size \
  -show_entries stream=codec_type,width,height -of default=noprint_wrappers=1 <视频路径>
```
拿到时长（duration），决定抽帧数。

### 2. 按时长抽帧（关键帧法）
```bash
mkdir -p /home/ubuntu/.openclaw/workspace/media/frames
# 帧数规则: ≤60s 抽 6 帧, 60-180s 抽 8 帧, >180s 抽 10 帧
# 时间点均匀分布(首/中/尾必含, 避开第 0 秒黑屏, 从 0.5s 起)
ffmpeg -y -loglevel error -ss <t> -i <视频> -frames:v 1 -q:v 3 /home/ubuntu/.openclaw/workspace/media/frames/f<t>.jpg
```
- 帧必须存到 **workspace 允许目录下**（view_image 只读 allowed dirs，/tmp 不行）。
  固定用 `/home/ubuntu/.openclaw/workspace/media/frames/`，存前先删旧帧防串场。
- 抽完逐帧确认文件非 0 字节。

### 3. 图片理解
用 `view_image` 一次喂全部帧（paths 按时间顺序），prompt 要求逐帧描述：
界面类型（终端/网页/软件）、关键数字/文字/图表、报错、操作动作。

### 4. 出结论
- 逐帧简述 + 整体定性（这段视频在干什么）。
- 涉及行情/数据时，数字必须原样引用帧上看到的，不脑补。
- 明确告知：只能看画面，听不到声音；要听声音走语音转写（speech-recognition 技能）。

## 失败降级
- ffmpeg 抽帧失败（文件损坏/编码特殊）→ 报「抽帧失败，视频可能损坏」，别瞎猜内容。
- view_image 读图失败 → 检查路径是否在 allowed dirs，移到 workspace/media/frames 重试一次。

## 验证
抽帧数 = 目标帧数、每帧 jpg 非空、view_image 成功加载全部帧，三项全过才出结论。

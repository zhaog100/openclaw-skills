# FFmpeg 视频处理工具 - 命令行视频编辑器

**调研时间**: 2026-04-11 16:25
**工具名称**: FFmpeg
**官网**: https://ffmpeg.org/
**GitHub**: https://github.com/FFmpeg/FFmpeg
**文档**: https://ffmpeg.org/documentation.html
**维护**: 小米椒 🌶️‍🔥

---

## 📊 基本信息

| 项目 | 信息 |
|------|------|
| 核心功能 | 命令行视频处理工具 |
| 开发方 | FFmpeg社区 |
| 许可证 | GPL-2.0/LGPL-2.1（完全开源） |
| 支持格式 | 几乎所有视频/音频/图片格式 |
| 语言支持 | C（Python可调用） |
| 费用 | 完全免费（开源） |

---

## 🎯 核心功能

### 1. 视频转换
- **格式支持**: MP4, MOV, AVI, FLV, WMV, MKV, WebM等
- **编解码**: H.264, H.265, VP9, AV1等
- **分辨率控制**: 调整分辨率（-s参数）
- **帧率控制**: 调整帧率（-r参数）
- **码率控制**: 调整码率（-b参数）

### 2. 视频剪辑
- **时间裁剪**: 截取指定时间段（-ss/-t参数）
- **合并**: 多个视频合并（-concat参数）
- **提取音频**: 提取音频轨道（-vn参数）
- **静音**: 消除音频（-an参数）

### 3. 视频滤镜
- **裁剪**: crop滤镜
- **缩放**: scale滤镜
- **旋转**: rotate滤镜
- **水印**: overlay滤镜
- **文字**: drawtext滤镜
- **模糊**: blur滤镜
- **亮度**: brightness/contrast滤镜

### 4. 音频处理
- **音量调整**: volume滤镜
- **音频提取**: 提取音频流
- **格式转换**: 音频格式转换

---

## 💰 定价方案

| 计划 | 费用 |
|------|--------|
| Free | 完全免费（GPL开源） |

---

## 🧧 使用方法

### 1. 安装
```bash
# Ubuntu 24.04
sudo apt update
sudo apt install ffmpeg
```

### 2. 命令行基础使用
```bash
# 视频转换
ffmpeg -i input.mov -c:v libx264 -c:a aac output.mp4

# 视频剪辑（截取0-10秒）
ffmpeg -i input.mp4 -ss 00:00:00 -t 00:00:10 -c copy output.mp4

# 视频裁剪
ffmpeg -i input.mp4 -vf "crop=1920:1080:0:0" output.mp4

# 添加水印
ffmpeg -i input.mp4 -i watermark.png -filter_complex "overlay=5:5" output.mp4

# 添加文字
ffmpeg -i input.mp4 -vf "drawtext=text='小米椒':fontsize=24:fontcolor=white:x=10:y=10" output.mp4

# 调整分辨率
ffmpeg -i input.mp4 -vf scale=1920:1080 output.mp4

# 视频合并
ffmpeg -f concat -i filelist.txt -c copy output.mp4
```

### 3. Python集成（使用subprocess）
```python
import subprocess

# 视频转换
cmd = ['ffmpeg', '-i', 'input.mov', '-c:v', 'libx264', '-c:a', 'aac', 'output.mp4']
subprocess.run(cmd, check=True)

# 视频剪辑
cmd = ['ffmpeg', '-i', 'input.mp4', '-ss', '00:00:00', '-t', '00:00:10', '-c', 'copy', 'output.mp4']
subprocess.run(cmd, check=True)

# 添加水印
cmd = ['ffmpeg', '-i', 'input.mp4', '-i', 'watermark.png', '-filter_complex', '[0:v][1:v]overlay=10:10[v]', '-map', '[v]', 'output.mp4']
subprocess.run(cmd, check=True)
```

### 4. 批量处理
```bash
#!/bin/bash
# 批量转换视频格式
for file in *.mov; do
    output="${file%.mov}.mp4"
    ffmpeg -i "$file" -c:v libx264 -c:a aac "$output"
    echo "转换完成: $file -> $output"
done
```

---

## 🚀 集成建议

### 场景1：视频格式统一
- **输入**: 各种格式视频
- **处理**: 使用FFmpeg转换为统一格式（MP4）
- **输出**: 转换后的视频
- **应用**:
  - 产品演示视频格式统一
  - 平台格式适配（小红书/闲鱼）
  - 批量格式转换

### 场景2：视频优化
- **输入**: 原始视频文件
- **处理**: 调整分辨率、码率、帧率
- **输出**: 优化后的视频
- **应用**:
  - 视频文件大小优化
  - 上传速度提升
  - 播放流畅度提升

### 场景3：水印添加
- **输入**: 原始视频 + 水印图片
- **处理**: 使用FFmpeg叠加水印
- **输出**: 带水印的视频
- **应用**:
  - 品牌水印批量添加
  - 版权保护
  - 位置自定义（左上/右上/居中）

### 场景4：GIF生成
- **输入**: 视频片段
- **处理**: 使用FFmpeg转换为GIF格式
- **输出**: GIF文件
- **应用**:
  - 产品演示GIF制作
  - 小红书GIF内容创作
  - 闲鱼产品动图制作

---

## ⚠️ 注意事项

### 命令参数
- **输入输出**: -i输入, -o输出
- **时间控制**: -ss起始时间, -t持续时间
- **滤镜**: -vf视频滤镜, -af音频滤镜
- **覆盖**: -y覆盖输出文件

### 性能优化
- **硬件加速**: 使用GPU加速（-hwaccel参数）
- **线程控制**: 使用多线程（-threads参数）
- **预设**: 使用preset（-preset ultrafast/fast/slow等）

---

## 📋 集成清单

### 第1步：安装FFmpeg
- [ ] 安装ffmpeg工具
- [ ] 测试基础功能

### 第2步：编写视频处理脚本
- [ ] 编写格式转换脚本
- [ ] 编写视频优化脚本
- [ ] 编写水印添加脚本
- [ ] 测试准确性

### 第3步：集成到工作流
- [ ] 集成到视频内容创作流程
- [ ] 集成到产品演示视频制作
- [ ] 测试准确性

---

## ✅ 已完成

- [x] 工具文档调研
- [x] 使用方法整理
- [x] 集成场景设计
- [x] 集成清单编写

---

## ⏳ 待完成

- [ ] 安装ffmpeg工具
- [ ] 编写测试脚本
- [ ] 执行测试验证
- [ ] 集成到工作流

---

## 📚 相关资源

- **官网**: https://ffmpeg.org/
- **GitHub**: https://github.com/FFmpeg/FFmpeg
- **文档**: https://ffmpeg.org/documentation.html
- **Wiki**: https://trac.ffmpeg.org/wiki

---

*小米椒 🌶️‍🔥 | 2026-04-11*

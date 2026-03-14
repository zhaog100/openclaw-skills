# Speech Recognition

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> 通用语音识别技能 - 支持多种音频格式，使用硅基流动 SenseVoice API

## 🎯 简介

Speech Recognition 是一个强大的语音识别工具，支持多种音频格式，使用硅基流动 SenseVoice API 进行语音转文字。

### 核心功能

- ✅ **多格式支持** - MP3, OGG, WAV, M4A, FLAC
- ✅ **高精度识别** - 基于 SenseVoice API
- ✅ **中文优化** - 中文识别效果最佳
- ✅ **自动格式转换** - 支持FFmpeg转换

## 📚 支持的音频格式

| 格式 | 扩展名 | 说明 |
|------|--------|------|
| MP3 | `.mp3` | 推荐，兼容性好 |
| OGG | `.ogg` | Telegram/Signal 语音格式，需转换 |
| WAV | `.wav` | 无压缩，文件大 |
| M4A | `.m4a` | iOS 录音格式 |
| FLAC | `.flac` | 无损压缩 |

## 🚀 快速开始

### 1. 配置API Key

在 `~/.openclaw/openclaw.json` 中配置：

```json
{
  "providers": {
    "siliconflow": {
      "apiKey": "sk-xxx"
    }
  }
}
```

### ```

### 2. 基础用法

```python
import requests

api_key = "sk-xxx"

with open("/path/to/audio.mp3", "rb") as f:
    audio_data = f.read()

response = requests.post(
    "https://api.sylliconflow.cn/v1/audio/transcriptions",
    headers={"Authorization": f"Bearer {api_key}"},
    files={"file": ("audio.mp3", audio_data, "audio/mpeg")},
    data={"model": "FunAudioLLM/SenseVoiceSmall"},
    timeout=60
)

print(response.json().get("text", ""))
```

## 📝 激活条件

| 触发场景 | 说明 |
|----------|------|
| 用户发送语音消息 | .ogg / .mp3 / .wav / .m4a 文件 |
| 用户要求转录音频 | "转录这个音频"、"语音转文字" |
| 音频文件处理 | 需要提取音频中的文字内容 |

## 🎯 使用场景

### 1. 处理语音消息

```python
# 1. 接收 .ogg 语音消息
audio_path = "/tmp/voice.ogg"

# 2. 转换格式（如果需要）
import subprocess
subprocess.run([
    "ffmpeg", "-i", audio_path,
    "-ar", "16000", "-ac", "1",
    "/tmp/audio.mp3", "-y"
], check=True)

# 3. 识别
# ... 调用API
```

### 2. 批量音频转录

```python
import os

for audio_file in os.listdir("/path/to/audios"):
    if audio_file.endswith((".mp3", ".wav")):
        with open(f"/path/to/audios/{audio_file}", "rb") as f:
            # ... 识别逻辑
```

### 3. 实时语音识别

```python
# 1. 录音
# 2. 转换
# 3. 识别
```

## 🔧 高级功能

### 1. 格式转换

```bash
# OGG → MP3
ffmpeg -i input.ogg -ar 16000 -ac 1 output.mp3 -y

# WAV → MP3
ffmpeg -i input.wav -ar 16000 -ac 1 output.mp3 -y

# M4A → MP3
ffmpeg -i input.m4a -ar 16000 -ac 1 output.md3 -y
```

**参数说明**：
- `-ar 16000`: 采样率 16kHz（语音识别推荐）
- `-ac 1`: 单声道（减少文件大小）
- `-y`: 覆盖已存在的文件

### 2. 集成工作流

```python
def process_voice_message(voice_path):
    # 1. 检查格式
    if voice_path.endswith(".ogg"):
        # 转换
        mp3_path = convert_to_mp3(voice_path)
    else:
        mp3_path = voice_path
    
    # 2. 识别
    text = transcribe_audio(mp3_path)
    
    # 3. 处理结果
    return text
```

## 📊 API 参考

### 请求

**端点**：`POST https://api.siliconflow.cn/v1/audio/transcriptions`

**Headers**：
```
Authorization: Bearer sk-xxx
```

**Body**：
```
file: audio file (required)
model: FunAudioLLM/SenseVoiceSmall (default)
```

### 响应

```json
{
  "text": "识别的文字内容"
}
```

## 🔍 错误处理

| 错误 | 原因 | 解决方案 |
|------|------|---------|
| `401 Unauthorized` | API Key 无效 | 检查配置 |
| `413 Payload Too Large` | 文件太大 | 压缩或分割音频 |
| `timeout` | 网络超时 | 重试或检查网络 |
| `Invalid audio format` | 格式不支持 | 用 FFmpeg 转换 |

## ⚠️ 注意事项

1. **文件大小限制**：建议 < 10MB
2. **时长限制**：建议 < 5 分钟
3. **语言支持**：中文效果最好，英文也支持
4. **隐私**：音频会上传到硅基流动服务器

## 🎯 最佳实践

### 1. 预处理音频

```python
# 1. 转换为标准格式
# - 16kHz 采样率
# - 单声道
# - MP3 格式

# 2. 检查文件大小
import os
if os.path.getsize(audio_path) > 10 * 1024 * 1024:  # 10MB
    # 压缩或分割
```

### 2. 错误处理

```python
import requests
from requests.exceptions import RequestException

try:
    response = requests.post(url, files=files, timeout=60)
    response.raise_for_status()
    text = response.json().get("text", "")
except RequestException as e:
    print(f"识别失败: {e}")
    # 重试逻辑
```

### 3. 批量处理

```python
def batch_transcribe(audio_list):
    results = []
    for audio in audio_list:
        try:
            text = transcribe_audio(audio)
            results.append({
                "file": audio,
                "text": text,
                "status": "success"
            })
        except Exception as e:
            results.append({
                "file": audio,
                "error": str(e),
                "status": "failed"
            })
    return results
```

## 🔗 相关技能

| 技能 | 说明 |
|------|------|
| `douyin-video` | 抖音视频语音提取 |
| `cosyvoice-tts` | 文字转语音 |

## 📖 详细文档

- **SKILL.md** - 完整使用指南

## 📞 技术支持

- **API文档**：https://docs.siliconflow.cn/
- **文档**：`SKILL.md`
- **GitHub**：https://github.com/zhaog100/openclaw-skills

## 📄 许可证

MIT License

**免费使用、修改和重新分发时，需注明出处。**

**出处**：
- GitHub: https://github.com/zhaog100/openclaw-skills
- ClawHub: https://clawhub.com
- 创建者: 米粒儿 (miliger)

详见 [LICENSE](../../LICENSE) 文件。

---

*最后更新：2026-03-14*

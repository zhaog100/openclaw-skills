# 本地语音识别部署研究（2026-03-03）

**官家要求：** 尽量实现本地部署，不调用三方协议

---

## 🎯 目标

**完全本地化的语音交互方案：**
- ✅ 语音识别：本地部署
- ✅ 语音合成：本地部署
- ✅ 完全离线运行
- ✅ 无第三方API依赖

---

## 📊 当前状态

**已安装：**
- ✅ Python 3.12
- ✅ ffmpeg（音频处理）
- ⏸️ OpenAI Whisper（未安装）

**环境：**
- ✅ VMware虚拟机
- ✅ CPU模式（无GPU）
- ✅ OpenJDK 21.0.10
- ✅ Node.js v22.22.0

---

## 🔧 方案一：OpenAI Whisper（推荐）

### 优势
- ✅ 开源免费
- ✅ 支持中文
- ✅ 准确率高
- ✅ 多种模型大小

### 安装
```bash
# 安装Whisper
pip install openai-whisper

# 安装ffmpeg（已安装）
sudo apt install ffmpeg
```

### 使用
```python
import whisper

# 加载模型（base/small/medium/large）
model = whisper.load_model("base")

# 识别音频
result = model.transcribe("audio.mp3")
print(result["text"])
```

### 模型选择

**VMware CPU环境推荐：**
- `tiny`：39M，最快，准确率较低
- `base`：74M，平衡，推荐 ✅
- `small`：244M，准确率好
- `medium`：769M，高准确率
- `large`：1550M，最高准确率（太慢）

**推荐：base模型**
- 大小：74MB
- 速度：中等
- 准确率：良好
- CPU友好 ✅

### 测试命令
```bash
# 下载测试音频
wget https://github.com/openai/whisper/raw/main/tests/jfk.flac

# 运行识别
whisper jfk.flac --model base --language Chinese
```

---

## 🔧 方案二：FunASR（阿里开源）

### 优势
- ✅ 阿里达摩院开源
- ✅ 专为中文优化
- ✅ 实时流式识别
- ✅ 工业级应用

### 安装
```bash
pip install funasr
pip install modelscope
```

### 使用
```python
from funasr import AutoModel

# 加载模型
model = AutoModel(model="paraformer-zh")

# 识别音频
result = model.generate(input="audio.wav")
print(result[0]["text"])
```

### 特点
- ✅ 中文识别率高
- ✅ 支持实时流式
- ✅ 自动标点
- ✅ 语音活动检测

---

## 🔧 方案三：Sherpa-ONNX（轻量级）

### 优势
- ✅ 超轻量级
- ✅ CPU友好
- ✅ 跨平台
- ✅ 实时识别

### 安装
```bash
pip install sherpa-onnx
```

### 使用
```python
import sherpa_onnx

# 创建识别器
recognizer = sherpa_onnx.OfflineRecognizer(
    model="path/to/model"
)

# 识别音频
result = recognizer.create_stream()
result.accept_waveform(sample_rate, samples)
text = result.result.text
```

---

## 🎤 语音合成（TTS）本地方案

### 方案一：pyttsx3（推荐）

**优势：**
- ✅ 完全离线
- ✅ 无需网络
- ✅ 跨平台
- ✅ 轻量级

**安装：**
```bash
pip install pyttsx3
```

**使用：**
```python
import pyttsx3

engine = pyttsx3.init()
engine.say("你好，我是米粒儿")
engine.runAndWait()
```

### 方案二：Edge-TTS

**优势：**
- ✅ 高质量中文语音
- ✅ 微软Edge合成
- ✅ 免费使用

**安装：**
```bash
pip install edge-tts
```

**使用：**
```bash
edge-tts --text "你好，我是米粒儿" --write-media hello.mp3
```

---

## 🔄 集成方案

### 完整流程

```
用户语音 → Whisper识别 → 文字处理 → AI回复 → TTS合成 → 语音输出
   ↓            ↓            ↓          ↓         ↓          ↓
  录音      本地识别      本地处理    本地生成   本地合成    QQ发送
```

### QQ Bot集成

**语音消息接收：**
1. 用户发送语音消息
2. QQ Bot接收音频文件
3. 保存为WAV/MP3格式

**语音识别处理：**
1. Whisper识别音频
2. 转换为文字
3. AI处理生成回复

**语音回复发送：**
1. TTS生成语音文件
2. QQ Bot发送语音消息
3. 用户听到回复

---

## 📋 部署计划

### 阶段一：基础部署（1小时）

**步骤：**
1. ✅ 安装OpenAI Whisper
2. ✅ 下载base模型
3. ✅ 测试语音识别
4. ✅ 安装pyttsx3

**命令：**
```bash
# 安装Whisper
pip install openai-whisper

# 测试安装
whisper --help

# 安装TTS
pip install pyttsx3

# 测试TTS
python3 -c "import pyttsx3; print('OK')"
```

### 阶段二：功能测试（30分钟）

**测试：**
1. ✅ Whisper识别测试音频
2. ✅ pyttsx3生成测试语音
3. ✅ 验证中文支持

### 阶段三：QQ Bot集成（1小时）

**集成：**
1. ✅ 研究QQ Bot语音消息API
2. ✅ 实现语音接收
3. ✅ 实现语音发送
4. ✅ 完整测试

---

## 💡 优化建议

### 性能优化

**Whisper优化：**
- 使用base模型（平衡）
- 批量处理音频
- 缓存常用模型

**CPU优化：**
- 使用ONNX Runtime
- 量化模型
- 多线程处理

### 中文优化

**Whisper：**
- 指定language="zh"
- 使用large模型（如果CPU允许）
- 后处理修正

**FunASR：**
- 专为中文优化
- 自动标点
- 语音活动检测

---

## 🎯 推荐方案

**综合考虑（VMware CPU环境）：**

**语音识别：**
- **首选：OpenAI Whisper base模型** ✅
- 备选：FunASR（中文优化）

**语音合成：**
- **首选：pyttsx3** ✅（完全离线）
- 备选：Edge-TTS（高质量）

**理由：**
- ✅ 完全本地部署
- ✅ 无第三方API
- ✅ CPU友好
- ✅ 安装简单
- ✅ 中文支持好

---

## 📝 安装清单

```bash
# 1. 安装Whisper
pip install openai-whisper

# 2. 安装TTS
pip install pyttsx3

# 3. 安装音频处理工具
sudo apt install ffmpeg espeak

# 4. 验证安装
whisper --help
python3 -c "import pyttsx3; print('pyttsx3 OK')"
```

---

## ⏰ 预计时间

**基础部署：** 1小时
**功能测试：** 30分钟
**QQ Bot集成：** 1小时
**总计：** 2.5小时

---

## ✅ 下一步

1. ⏰ 等待官家明天9点后开始
2. ✅ 安装OpenAI Whisper
3. ✅ 测试语音识别
4. ✅ 研究QQ Bot语音API
5. ✅ 完成集成测试

---

**官家，本地部署方案已准备！明天开始实施！** 🌾

---

*创建时间：2026-03-03 00:30*
*方案：完全本地化语音识别*
*推荐：OpenAI Whisper + pyttsx3*

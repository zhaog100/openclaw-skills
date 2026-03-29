# QQ语音消息发送功能需求

## 状态：待开发 ⏳

## 问题描述
QQ Bot插件目前只支持图片发送，不支持语音消息发送。

## 技术细节

### 已完成 ✅
1. **语音识别系统**
   - Medium模型（769MB）
   - 6种方言支持（含四川话）
   - 四川话准确率：80%
   - 语音降噪处理

2. **SILK编码器**
   - silk-python已安装
   - 可生成有效SILK文件（64KB）
   - 符合QQ语音格式要求

### 未完成 ❌
1. **QQ Bot插件扩展**
   - `sendMedia`函数只支持图片
   - 需要添加语音消息发送功能

## 解决方案

### 方案1：扩展sendMedia函数
修改`/home/zhaog/.npm-global/lib/node_modules/openclaw/extensions/qq/src/outbound.ts`

```typescript
// 在sendMedia函数中添加语音支持
const voiceMimeTypes: Record<string, string> = {
  ".silk": "audio/silk",
  ".mp3": "audio/mpeg",
  ".wav": "audio/wav",
};

// 检查文件类型
const ext = path.extname(mediaUrl).toLowerCase();
const isVoice = voiceMimeTypes[ext] !== undefined;

if (isVoice) {
  // 上传语音文件
  const uploadResult = await uploadC2CMedia(
    accessToken,
    openid,
    MediaFileType.VOICE,
    undefined,
    base64Data,
    false
  );
  
  // 发送语音消息
  await sendC2CMediaMessage(
    accessToken,
    openid,
    uploadResult.file_info,
    msgId
  );
}
```

### 方案2：创建独立的sendVoice函数
创建新函数专门处理语音消息发送。

## API参考

### QQ Bot语音消息API
- **上传接口**：`POST /v2/users/{openid}/files`
- **文件类型**：`MediaFileType.VOICE = 3`
- **发送接口**：`POST /v2/users/{openid}/messages`
- **消息类型**：`msg_type: 7`（富媒体消息）

### 文件要求
- **格式**：SILK
- **采样率**：24000Hz
- **声道**：单声道

## 测试用例
1. 生成SILK语音文件
2. 上传到QQ Bot API
3. 获取file_info
4. 发送语音消息
5. 验证用户端显示（浅蓝色圆角矩形，带播放按钮和波形）

## 优先级
⭐⭐⭐⭐⭐ 高优先级（核心功能）

## 预计工作量
- 代码修改：1-2小时
- 测试验证：30分钟
- 文档更新：15分钟

---

**创建时间**：2026-03-03 11:10
**最后更新**：2026-03-03 11:10

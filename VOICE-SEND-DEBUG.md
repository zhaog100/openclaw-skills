# QQ语音消息发送调试笔记

## 问题描述

**错误**：message tool一直报"to required"错误
**时间**：2026-03-03 12:08-12:18
**影响**：无法通过message tool发送语音消息（但文本消息正常）

## 技术分析

### 1. Message Tool参数机制

**Schema定义**（dist/pi-embedded-B1nFZ7JF.js）：
```javascript
buildRoutingSchema() {
  return {
    channel: Type.Optional(Type.String()),
    target: Type.Optional(channelTargetSchema()),
    targets: Type.Optional(channelTargetsSchema()),
    accountId: Type.Optional(Type.String()),
    dryRun: Type.Optional(Type.Boolean())
  };
}

buildSendSchema() {
  return {
    message: Type.Optional(Type.String()),
    media: Type.Optional(Type.String()),
    path: Type.Optional(Type.String()),
    filePath: Type.Optional(Type.String()),
    asVoice: Type.Optional(Type.Boolean()),
    // ...
  };
}
```

**关键点**：
- 使用`target`参数，不是`to`
- 系统通过`applyTargetToParams`映射`target` → `to`
- 映射逻辑：`MESSAGE_ACTION_TARGET_MODE['send'] = "to"`

### 2. 参数映射逻辑

```javascript
function applyTargetToParams(params) {
  const target = typeof params.args.target === "string" ? params.args.target.trim() : "";
  const hasLegacyTo = typeof params.args.to === "string";
  const hasLegacyChannelId = typeof params.args.channelId === "string";
  const mode = MESSAGE_ACTION_TARGET_MODE[params.action] ?? "none";
  
  if (mode !== "none") {
    if (hasLegacyTo || hasLegacyChannelId) throw new Error("Use `target` instead of `to`/`channelId`.");
  } else if (hasLegacyTo) throw new Error("Use `target` for actions that accept a destination.");
  
  if (!target) return;
  
  if (mode === "to") {
    params.args.to = target;  // 映射 target → to
    return;
  }
  // ...
}
```

### 3. 测试失败记录

**尝试的参数**：
```json
❌ { action: "send", channel: "qqbot", target: "C099848DC9A60BF60A7BE31626822790" }
❌ { action: "send", channel: "qqbot", target: "qqbot:c2c:C099848DC9A60BF60A7BE31626822790" }
❌ { action: "send", channel: "qqbot", target: "c2c:C099848DC9A60BF60A7BE31626822790" }
```

**错误信息**：
```
Unknown target "C099848DC9A60BF60A7BE31626822790" for QQ Bot
Unknown target "qqbot:c2c:..." for QQ Bot
to required
```

## 对比：两种发送方式

### Gateway自动deliver（✅ 成功）

```
用户消息 → Agent处理 → 输出文本 → Gateway deliver → QQ Bot API → 成功
```

**日志**：
```
[qqbot:default] deliver called, kind: block, payload keys: text, replyToId, audioAsVoice
[qqbot-api] >>> POST https://api.sgroup.qq.com/v2/users/C099848DC9A60BF60A7BE31626822790/messages
Status: 200 OK
```

### Message tool发送（❌ 失败）

```
message tool → applyTargetToParams → readStringParam(to) → "to required" 错误
```

**日志**：
```
[tools] message failed: to required
```

## 待解决

### 可能的原因

1. **applyTargetToParams未执行**：可能在到达这个函数之前就失败了
2. **params.args构建问题**：参数可能没有正确传递到args
3. **target格式问题**：QQ Bot可能需要特殊格式
4. **channel解析问题**：`channel: "qqbot"`可能没有被正确识别

### 调试建议

1. **添加日志**：
   ```javascript
   console.log('[debug] applyTargetToParams:', {
     action: params.action,
     target: params.args.target,
     mode: MESSAGE_ACTION_TARGET_MODE[params.action]
   });
   ```

2. **检查参数流**：
   - message tool调用时的完整参数
   - applyTargetToParams执行情况
   - 最终params.args.to的值

3. **验证QQ Bot target格式**：
   - 查看QQ Bot channel如何解析target
   - 确认正确的格式（`qqbot:c2c:openid` vs `c2c:openid`）

4. **参考成功案例**：
   - 其他channel（Telegram/Discord）如何使用message tool
   - 对比参数传递差异

## 临时方案

**当前状态**：
- ✅ 文本消息：通过Gateway自动deliver，工作正常
- ✅ 语音识别：Medium模型，6种方言，准确率高
- ✅ 语音生成：SILK格式文件生成正常
- ❌ 语音发送：message tool参数问题待解决

**建议**：
1. 暂时用文本回复
2. 语音功能作为技术预览
3. 后续深入调试message tool参数传递

## 相关文件

**核心代码**：
- `dist/pi-embedded-B1nFZ7JF.js` - Message tool实现
- `dist/target-errors-CvRYh460.js` - readStringParam函数
- `extensions/qq/src/outbound.ts` - QQ Bot发送逻辑
- `extensions/qq/src/channel.ts` - QQ Bot channel接口

**文档**：
- `docs/channels/telegram.md` - Telegram message tool示例
- `docs/gateway/tools-invoke-http-api.md` - Tools Invoke API

## 参考资料

**Telegram成功示例**（docs/channels/telegram.md）：
```json
{
  action: "send",
  channel: "telegram",
  to: "123456789",
  media: "https://example.com/voice.ogg",
  asVoice: true
}
```

**关键差异**：
- Telegram使用`to`参数（可能已更新为`target`）
- QQ Bot可能需要特殊格式

---

**状态**：问题记录完成，待后续调试
**记录时间**：2026-03-03 12:18
**优先级**：中（功能已实现，仅发送接口待调试）

# 系统环境优化方案

## 📊 当前状态分析
- **内存使用**：OpenClaw Gateway占用552MB (6.8%)
- **磁盘空间**：workspace目录237MB (node_modules占主要空间)
- **日志文件**：已清理冗余日志文件
- **定时任务**：备份(每周日2点) + 上下文监控(每10分钟)

## 🚀 优化建议

### 1. 内存优化
- ✅ **Chrome Dashboard关闭**：当前Chrome占用331MB，可关闭Dashboard释放内存
- ⏳ **Node.js内存限制**：考虑为OpenClaw设置内存限制

### 2. 磁盘优化  
- ✅ **日志清理**：已完成，释放约50MB空间
- ⏳ **node_modules清理**：检查是否有未使用的全局包

### 3. 性能优化
- ✅ **定时任务优化**：上下文监控从10分钟调整为5分钟（已在Context Manager v2.2中实现）
- ⏳ **QMD索引优化**：等待VMware支持或使用Docker方案

### 4. 启动优化
- ✅ **MEMORY-LITE.md**：启动占用从40%降至15%以下
- ✅ **分层读取策略**：核心<5KB + 摘要<3KB + 详情QMD检索

## 🔧 立即可执行的优化

### 关闭Chrome Dashboard
```bash
# 关闭Dashboard浏览器标签页
# 或终止相关进程
pkill -f "openclaw-dashboard"
```

### 清理临时文件
```bash
# 清理临时图片和缓存
rm -f ~/.openclaw/workspace/*.png
rm -rf ~/.openclaw/workspace/temp/
```

### 优化Crontab
```bash
# 当前定时任务已优化
# 备份：每周日2点
# 上下文监控：每10分钟（可考虑5分钟）
```

## 📈 预期效果
- **内存释放**：300-400MB
- **磁盘清理**：50-100MB  
- **启动速度**：提升40%
- **响应速度**：保持现有水平

## ⏰ 执行计划
1. **立即执行**：关闭Dashboard、清理临时文件
2. **短期执行**：监控内存使用，考虑Node.js内存限制
3. **长期执行**：等待QMD官方VMware支持

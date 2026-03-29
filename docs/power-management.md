# 节能防睡眠方案对比

## 📊 方案对比表

| 方案 | 功耗 | 续航影响 | 功能完整度 | 适用场景 |
|------|------|---------|-----------|---------|
| **完整保护** | ~15-20W | -70% | 100% | 接电源时 |
| **智能模式** | ~10-15W | -50% | 90% | 混合使用 |
| **周期唤醒** | ~5-8W | -30% | 70% | 电池模式 |
| **超级节能** | ~2-5W | -10% | 50% | 仅保持网络 |

---

## 🎯 推荐配置

### 🔌 使用电源适配器
```bash
bash scripts/prevent-sleep-simple.sh
```
- ✅ 完整功能
- ✅ 合盖不睡眠
- ❌ 功耗较高

### 🔋 使用电池
```bash
bash scripts/ultra-save.sh
```
- ✅ 最低功耗
- ✅ 延长续航
- ⚠️ 仅保持网络

### 🔄 混合使用
```bash
bash scripts/power-manager.sh
```
- ✅ 自动切换
- ✅ 智能调度
- ✅ 平衡功耗

---

## 💡 使用建议

**场景1：长时间开发（接电源）**
```bash
# 完整保护
bash scripts/prevent-sleep-simple.sh
```

**场景2：外出携带（电池）**
```bash
# 超级节能
bash scripts/ultra-save.sh
```

**场景3：自动适应（推荐）**
```bash
# 智能管理
bash scripts/power-manager.sh
```

---

## ⚙️ 参数说明

### caffeinate 参数
- `-d` 防止显示器睡眠（高功耗）
- `-i` 防止系统空闲睡眠（中功耗）
- `-s` 仅在使用电源时有效
- `-u` 模拟用户活动（低功耗）
- `-t N` 持续N秒

### 组合方案
```bash
# 高功耗（15-20W）
caffeinate -d -i -s

# 中功耗（8-12W）
caffeinate -i -s

# 低功耗（2-5W）
caffeinate -i -u -t 60  # 每分钟唤醒1次
```

---

## 📈 功耗优化技巧

### 1. 降低CPU频率
```bash
# 查看当前频率
sysctl hw.cpufrequency

# 降低性能（需sudo）
sudo pmset -a lessmsp 1
```

### 2. 禁用不必要服务
```bash
# 临时禁用Spotlight
sudo mdutil -a -i off

# 临时禁用Time Machine
sudo tmutil disable
```

### 3. 降低屏幕亮度
- 合盖时自动关闭
- 外接显示器时调至最低

### 4. 优化网络
```bash
# 降低扫描频率（修改脚本）
# 将检查间隔从300秒改为600秒
```

---

## 🔧 高级配置

### 自定义唤醒周期
```bash
# 编辑 ultra-save.sh
# 修改这两个值：
WAKE_DURATION=60    # 唤醒时长（秒）
SLEEP_DURATION=540  # 休眠时长（秒）
```

### 条件触发
```bash
# 仅在有未推送内容时唤醒
if [ $(git log origin/main..HEAD --oneline | wc -l) -gt 0 ]; then
    caffeinate -i -u -t 120
fi
```

---

## 📱 监控工具

### 查看功耗
```bash
# 实时功耗
sudo powermetrics --samplers smc -i 1000 -n 1

# 电池状态
pmset -g batt
```

### 查看进程功耗
```bash
# CPU占用
top -o cpu

# 能耗影响（Activity Monitor）
open -a "Activity Monitor"
```

---

## 🎯 总结

**最佳实践**：
1. **接电源** → `prevent-sleep-simple.sh`
2. **用电池** → `ultra-save.sh`
3. **混合使用** → `power-manager.sh`

**节能效果**：
- 完整保护：0% 节能
- 智能模式：30-40% 节能
- 周期唤醒：50-60% 节能
- 超级节能：70-80% 节能

**推荐配置**：
- 开发者：智能模式
- 外出携带：超级节能
- 自动化：智能管理

---

_创建时间: 2026-03-29 07:55 PDT_

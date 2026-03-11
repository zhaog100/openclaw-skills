# 米粒管家自动化工具集

**版本**: v1.0.0
**适配设备**: Redmi K40 Gaming (Hyper OS)

---

## 📦 工具列表

### 1. Auto.js APP + 脚本（推荐）

**优点**：
- ✅ 不需要电脑
- ✅ 不需要Root
- ✅ 手机直接运行
- ✅ 图形化界面

**包含**：
- Auto.js Pro APP（免费版）
- 抖音极速版自动签到脚本
- 快手极速版自动签到脚本

**使用**：
```
1. 安装Auto.js APP
2. 导入脚本
3. 运行 → 复制Cookie
4. 发送给米粒管家
```

---

### 2. Python工具（电脑端）

**优点**：
- ✅ 功能更强大
- ✅ 自动化程度高

**包含**：
- ADB自动化工具
- Cookie提取工具

**使用**：
```
1. 手机连接电脑（USB调试）
2. 运行Python脚本
3. 自动获取Cookie
```

---

## 🚀 快速开始

**手机端（推荐）**：
```bash
1. 下载Auto.js APP
2. 导入脚本
3. 运行获取Cookie
4. 发送给米粒管家
```

**电脑端**：
```bash
1. pip install uiautomator2
2. python3 auto_tool_v1.py
3. 获取Cookie
```

---

## 📂 文件结构

```
tools/
├── autojs-scripts/           # Auto.js脚本
│   ├── douyin_auto_sign.js   # 抖音极速版
│   ├── kuaishou_auto_sign.js # 快手极速版
│   └── README.md             # 使用指南
│
└── device-automation-tool/   # Python工具
    ├── auto_tool_v1.py       # 主程序
    ├── GUIDE.md              # 使用指南
    └── requirements.txt      # 依赖列表
```

---

## 💡 推荐

**手机用户** → Auto.js APP（最简单）
**电脑用户** → Python工具（更强大）

---

**作者**: 米粒儿 🌾
**创建时间**: 2026-03-04
**版本**: v1.0.0

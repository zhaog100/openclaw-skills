# QMD 知识库搜索工具使用指南

## 🎯 功能说明

本地搜索工具，用于在知识库中查找相关文档。

## 📖 使用方法

### 基础搜索
```powershell
.\search-knowledge.ps1 "关键词"
```

### 示例

**1. 搜索项目管理相关内容**
```powershell
.\search-knowledge.ps1 "PMP"
.\search-knowledge.ps1 "敏捷"
.\search-knowledge.ps1 "Scrum"
```

**2. 搜索软件测试相关内容**
```powershell
.\search-knowledge.ps1 "测试"
.\search-knowledge.ps1 "自动化"
.\search-knowledge.ps1 "Selenium"
```

**3. 搜索内容创作相关内容**
```powershell
.\search-knowledge.ps1 "公众号"
.\search-knowledge.ps1 "视频"
.\search-knowledge.ps1 "内容策略"
```

## 📚 知识库结构

```
knowledge/
├── project-management/        # 项目管理
│   ├── pmp-certification/     # PMP认证
│   ├── agile-methodology/     # 敏捷方法
│   └── project-planning/      # 项目规划
├── software-testing/          # 软件测试
│   ├── test-automation/       # 自动化测试
│   ├── test-management/       # 测试管理
│   └── test-tools/            # 测试工具
└── content-creation/          # 内容创作
    ├── wechat-public/         # 公众号运营
    ├── video-creation/        # 视频创作
    └── content-strategy/      # 内容策略
```

## ✅ 当前状态

- ✅ 知识库结构：100%完成
- ✅ 专业文档：9个文档
- ✅ 搜索功能：已启用
- ⏳ AI语义搜索：等待Gateway重启

## 💡 使用建议

1. **精确搜索**：使用具体的专业术语（如"PMP"、"Selenium"）
2. **模糊搜索**：使用通用的概念词（如"管理"、"测试"）
3. **组合搜索**：可以多次搜索不同关键词，交叉验证结果

## 🔧 高级功能（待启用）

- AI语义搜索（需要Gateway重启）
- 智能问答
- 文档关联推荐

---

*创建时间：2026年2月26日*

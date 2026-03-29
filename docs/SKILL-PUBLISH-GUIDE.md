# 技能发布指南

**版本：** v1.0  
**最后更新：** 2026-03-11

---

## 📋 发布前检查

- [ ] SKILL.md 完整（包含 name, description, author）
- [ ] package.json 配置正确（包含版权信息）
- [ ] 代码测试通过
- [ ] README.md 完善
- [ ] 无敏感信息

---

## 🚀 发布流程

### 方法 1：命令行发布（推荐）
```bash
cd /home/zhaog/.openclaw/workspace/skills/skill-name
clawnet publish .
```

### 方法 2：网页上传
```
1. 访问 https://clawhub.ai/publish
2. 上传技能目录或 tar.gz 包
3. 填写发布信息
4. 提交审核
```

---

## ⚠️ 常见问题

### 安全扫描拦截
- 避免使用 `exec()` 改用 `execFile()`
- 避免 curl 管道命令，改为"访问网站下载"

### 服务器错误
- 等待几秒后重试
- 或改用网页上传

---

*让技能发布更顺利！* 🌾

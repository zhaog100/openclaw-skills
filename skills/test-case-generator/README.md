# 测试用例生成器 (test-case-generator)

> 根据源代码自动生成测试用例

---

## 🎯 功能特性

- **代码分析** - 自动识别函数和类
- **测试生成** - 生成正常/边界/异常场景测试
- **多语言支持** - Python/Bash/JavaScript
- **多框架支持** - pytest/unittest/jest

---

## 🚀 快速开始

### 安装

```bash
cd skills/test-case-generator
bash scripts/install.sh
```

### 使用

```bash
# 生成 Python 测试
./skill.sh generate --lang python src/my_module.py

# 生成 Bash 测试
./skill.sh generate --lang bash scripts/

# 生成 JavaScript 测试
./skill.sh generate --lang javascript src/
```

---

## 📊 示例

**输入**:
```python
def add(a, b):
    return a + b
```

**输出**:
```python
def test_add_positive():
    assert add(2, 3) == 5

def test_add_negative():
    assert add(-1, -1) == -2
```

---

## 📝 许可证

MIT License  
Copyright (c) 2026 思捷娅科技 (SJYKJ)

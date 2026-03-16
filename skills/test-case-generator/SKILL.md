---
name: test-case-generator
description: 测试用例生成器 - 根据代码自动生成测试用例
---

# 测试用例生成器 (test-case-generator)

**版本**: v1.0  
**创建时间**: 2026-03-16  
**创建者**: 思捷娅科技 (SJYKJ)  
**用途**: 根据源代码自动生成测试用例

---

## 🎯 核心功能

### 1. 代码分析
- ✅ 支持 Python/Bash/JavaScript
- ✅ 自动识别函数和类
- ✅ 分析输入输出参数

### 2. 测试用例生成
- ✅ 生成正常场景测试
- ✅ 生成边界条件测试
- ✅ 生成异常场景测试

### 3. 测试框架支持
- ✅ pytest (Python)
- ✅ unittest (Python)
- ✅ jest (JavaScript)
- ✅ Bash 测试

---

## 🚀 使用方法

```bash
# 生成 Python 测试用例
./skill.sh generate --lang python src/my_module.py

# 生成 Bash 测试用例
./skill.sh generate --lang bash scripts/my_script.sh

# 生成 JavaScript 测试用例
./skill.sh generate --lang javascript src/my_module.js

# 指定测试框架
./skill.sh generate --lang python --framework pytest src/
```

---

## 📊 输出示例

**输入代码**:
```python
def add(a, b):
    return a + b
```

**生成测试**:
```python
def test_add_positive():
    assert add(2, 3) == 5

def test_add_negative():
    assert add(-1, -1) == -2

def test_add_zero():
    assert add(0, 0) == 0
```

---

## 📝 许可证

MIT License  
Copyright (c) 2026 思捷娅科技 (SJYKJ)

---

*版本：v1.0*  
*最后更新：2026-03-16*  
*创建者：思捷娅科技 (SJYKJ)*

---
name: china-exam-info-core
description: 中国公考信息和企事业单位考试信息获取工具，重点关注四川成都及周边、泸州及周边地区。使用Python标准库实现，零外部依赖。
version: 3.3.0
author: 小米辣 🌶️
lessons_updated: 2026-06-16
---

# 中国公考+国企央企信息获取工具 v3.3

## 功能
- 四川公务员/事业单位考试信息采集
- 成都事业单位招聘采集
- 泸州事业单位招聘采集
- 国企央企招聘信息采集（聚焦四川）

## 使用方法
```bash
cd scripts/
# 四川公务员
python3 get_exam_info.py --region sichuan --no-detail
# 成都事业单位
python3 get_exam_info.py --region chengdu --no-detail
# 泸州事业单位
python3 get_exam_info.py --region luzhou --no-detail
# 国企央企（四川）
python3 get_exam_info.py --soe --region sichuan
```

## 依赖
- Python 3.8+
- requests
- beautifulsoup4

## 版权
MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)

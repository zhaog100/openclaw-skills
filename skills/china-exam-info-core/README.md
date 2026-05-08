# 中国公考信息获取技能

获取中国公考信息和企事业单位考试信息，重点关注四川成都及泸州地区。

## 快速开始

```bash
# 获取所有考试（演示模式，不访问网络）
python3 skills/china-exam-info-core/scripts/get_exam_info.py --demo

# 获取成都地区考试
python3 skills/china-exam-info-core/scripts/get_exam_info.py --demo --region chengdu

# 获取泸州地区考试
python3 skills/china-exam-info-core/scripts/get_exam_info.py --demo --region luzhou

# 组合筛选：成都+本科+18-35岁
python3 skills/china-exam-info-core/scripts/get_exam_info.py --demo --region chengdu --education bachelor --age "18-35"

# 输出为Markdown格式并保存
python3 skills/china-exam-info-core/scripts/get_exam_info.py --demo --format markdown --save exam.md
```

## 功能特性

- 📋 多源数据采集（公务员、事业单位、企业招聘）
- 📍 地区聚焦（成都、泸州及周边城市）
- 📊 分类整理（年龄、学历、工作地点等）
- 📱 多种输出格式（JSON、Markdown、CSV、Text）

## 依赖

仅需Python3标准库，无需安装额外依赖。

## 数据源

- 国家公务员局、四川省公务员考试
- 四川/成都/泸州人事考试网
- 四川/成都人才网站

## 更多信息

详见 [SKILL.md](SKILL.md)
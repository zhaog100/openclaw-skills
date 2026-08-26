# Copyright (c) 2026 思捷娅科技 (SJYKJ) | MIT License

---
name: china-exam-info-core
description: 获取中国公考信息和企事业单位考试信息，重点关注四川成都及周边、泸州及周边地区。使用Python标准库实现，零外部依赖。
homepage: https://www.openclaw.ai
metadata: {"clawdbot":{"emoji":"📚","requires":{"bins":["python3"]}}}
version: 4.0
---

# 中国公考信息获取技能 v4.0

获取中国的公考信息和企事业单位考试信息，重点关注四川成都及周边、泸州及周边地区。

## 功能特点

- 📋 **多源数据采集**：从多个官方考试网站获取信息
- 📍 **地区聚焦**：重点关注四川成都及泸州及周边
- 📊 **分类整理**：按年龄、学历、工作地点等维度分类
- 🔔 **实时更新**：定期获取最新考试信息
- 📱 **多种格式**：支持JSON、Markdown、CSV格式输出
- ⚙️ **零外部依赖**：完全使用Python标准库

## 使用命令

### 基本用法

```bash
# 获取所有考试信息
python3 skills/china-exam-info-core/scripts/get_exam_info.py --all

# 获取成都及周边考试
python3 skills/china-exam-info-core/scripts/get_exam_info.py --region chengdu

# 获取泸州及周边考试
python3 skills/china-exam-info-core/scripts/get_exam_info.py --region luzhou
```

### 按考试类型筛选

```bash
# 公务员考试
python3 skills/china-exam-info-core/scripts/get_exam_info.py --type civil-service

# 事业单位考试
python3 skills/china-exam-info-core/scripts/get_exam_info.py --type public-institution

# 企业招聘
python3 skills/china-exam-info-core/scripts/get_exam_info.py --type enterprise

# 组合筛选
python3 skills/china-exam-info-core/scripts/get_exam_info.py --type civil-service,public-institution
```

### 按条件筛选

```bash
# 按学历要求
python3 skills/china-exam-info-core/scripts/get_exam_info.py --education bachelor

# 按年龄要求
python3 skills/china-exam-info-core/scripts/get_exam_info.py --age "18-35"

# 多条件组合
python3 skills/china-exam-info-core/scripts/get_exam_info.py --age "18-35" --education bachelor
```

### 输出格式

```bash
# JSON格式（默认）
python3 skills/china-exam-info-core/scripts/get_exam_info.py --format json

# Markdown格式
python3 skills/china-exam-info-core/scripts/get_exam_info.py --format markdown

# CSV格式
python3 skills/china-exam-info-core/scripts/get_exam_info.py --format csv

# 简洁文本格式
python3 skills/china-exam-info-core/scripts/get_exam_info.py --format text
```

### 组合使用示例

```bash
# 成都地区公务员+事业单位，学历本科以上，年龄18-35
python3 skills/china-exam-info-core/scripts/get_exam_info.py \
  --region chengdu \
  --type civil-service,public-institution \
  --education bachelor \
  --age "18-35" \
  --format markdown

# 泸州地区所有考试，JSON输出
python3 skills/china-exam-info-core/scripts/get_exam_info.py \
  --region luzhou \
  --format json \
  --save data/exam-luzhou-$(date +%Y%m%d).json
```

## 数据源

### 公务员考试
- 国家公务员局：http://www.scrs.gov.cn/
- 四川省公务员考试：http://rst.sc.gov.cn/

### 事业单位考试
- 四川人事考试网：http://www.scpta.org.cn/
- 成都人事考试网：http://cdpta.cdhrss.chengdu.gov.cn/
- 泸州人事考试网：http://www.lzhrss.gov.cn/

### 企业招聘
- 四川人才网：http://www.scrc.com.cn/
- 成都人才网：http://www.rc114.com/
- 智联招聘：https://www.zhaopin.com/
- 前程无忧：https://www.51job.com/

## 输出字段说明

每个考试信息包含以下字段：

### 基本信息
- **考试名称**：完整考试名称
- **考试类型**：公务员考试/事业单位考试/企业招聘
- **发布机构**：发布公告的机构名称
- **发布时间**：公告发布时间
- **报名截止时间**：报名截止日期
- **考试日期**：笔试/面试日期

### 岗位要求
- **年龄要求**：如"18-35岁"
- **学历要求**：如"本科及以上"
- **专业要求**：所需专业背景
- **工作经验**：工作经验要求
- **政治面貌**：党员/团员/群众等要求

### 工作地点
- **工作地点**：具体工作城市/地区
- **单位性质**：行政机关/事业单位/国有企业/民营企业
- **岗位级别**：科员/副科/正科等

### 报名信息
- **报名方式**：网上报名/现场报名
- **报名网站**：官方报名网址
- **咨询电话**：联系咨询电话
- **报名费用**：考试报名费用

### 考试内容
- **笔试科目**：行测/申论/专业知识等
- **面试形式**：结构化面试/无领导小组讨论等
- **成绩计算**：笔试面试比例

## 示例输出

### JSON格式
```json
{
  "exams": [
    {
      "exam_name": "2024年四川省公务员录用考试",
      "exam_type": "公务员考试",
      "region": "成都",
      "publish_date": "2024-03-15",
      "deadline": "2024-04-15",
      "exam_date": "2024-05-11",
      "requirements": {
        "age": "18-35岁",
        "education": "本科及以上",
        "major": "不限",
        "experience": "不限",
        "politics": "不限"
      },
      "position": {
        "location": "成都市",
        "organization": "成都市某行政机关",
        "level": "科员"
      },
      "registration": {
        "method": "网上报名",
        "website": "http://rst.sc.gov.cn/",
        "phone": "028-86702886",
        "fee": "100元"
      },
      "exam_content": {
        "written_test": "行政职业能力测验、申论",
        "interview": "结构化面试",
        "score_calculation": "笔试60% + 面试40%"
      }
    }
  ]
}
```

### Markdown格式
```markdown
## 2024年四川省公务员录用考试

**基本信息**
- **考试类型**: 公务员考试
- **发布机构**: 四川省人力资源和社会保障厅
- **发布时间**: 2024-03-15
- **报名截止**: 2024-04-15
- **考试日期**: 2024-05-11

**岗位要求**
- **年龄要求**: 18-35岁
- **学历要求**: 本科及以上
- **专业要求**: 不限
- **工作经验**: 不限
- **政治面貌**: 不限

**工作地点**
- **工作地点**: 成都市
- **单位性质**: 行政机关
- **岗位级别**: 科员

**报名信息**
- **报名方式**: 网上报名
- **报名网站**: http://rst.sc.gov.cn/
- **咨询电话**: 028-86702886
- **报名费用**: 100元

**考试内容**
- **笔试科目**: 行政职业能力测验、申论
- **面试形式**: 结构化面试
- **成绩计算**: 笔试60% + 面试40%
```

## 定时任务

### 配置示例
在crontab中添加定时任务：

```bash
# 每天上午9点获取成都和泸州最新考试信息
0 9 * * * cd ~/.openclaw/workspace && python3 skills/china-exam-info-core/scripts/get_exam_info.py --region chengdu,luzhou --format json --save data/exam-$(date +\%Y\%m\%d).json

# 每周一上午10点获取所有考试信息
0 10 * * 1 cd ~/.openclaw/workspace && python3 skills/china-exam-info-core/scripts/get_exam_info.py --all --format markdown --save data/exam-weekly-$(date +\%Y\%m\%d).md
```

## 注意事项

1. **数据准确性**：所有信息均来自官方渠道，但请以官方网站为准
2. **更新频率**：建议每天更新一次获取最新信息
3. **网络要求**：需要稳定的网络连接访问官方网站
4. **存储建议**：建议将结果保存到文件或数据库中便于后续分析
5. **合规使用**：请遵守各网站的使用条款，不要过度频繁访问

## 技术实现

### 零外部依赖
- 使用Python标准库实现所有功能
- urllib.request: HTTP请求
- html.parser: HTML解析
- json: JSON处理
- csv: CSV处理
- re: 正则表达式
- argparse: 命令行参数

### 兼容性
- Python 3.6+
- Linux/macOS/Windows跨平台
- 无需安装额外依赖

## 许可证

# MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)

**免费使用、修改和重新分发时，需注明出处。**

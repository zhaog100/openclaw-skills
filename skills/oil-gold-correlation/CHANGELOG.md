# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [2.1.4] - 2026-05-12

### Updated
- 版本号更新至 2.1.4
- 完善技能仓库地址信息
- 统一所有文件版本号一致性
- 优化版权信息展示

### Fixed
- 修复 README.md 版本号不一致问题
- 完善 SKILL.md 文档结构

## [2.1.0] - 2026-05-09

### Added
- 容错增强：retry_on_failure 指数退避重试
- is_data_valid 数据有效性检查
- fetch_with_fallback 多数据源自动切换
- 过期缓存兜底机制

### Fixed
- 移除数据源硬性偏好，统一为自动检测
- advisor.py 注释已更新为自动选择
- 修复 report_text.py Git 冲突标记

### Changed
- 数据源策略：谁先返回有效数据谁先用
## [2.0.0] - 2026-05-09

### Added
- 多数据源 fallback 机制（akshare / yfinance / FRED）
- 智能建议引擎 v1.3（8品种 × 9指标）
- 地缘政治分析模块
- 定时推送配置（push-config.yaml）
- 夏/冬令时自适应（美盘 22:00/23:00）

### Fixed
- requirements.txt merge conflict
- 清理草稿文件（report_text_v2.0_draft.py）
- 多个脚本 Git 冲突标记

### Changed
- 报告脚本整合为 2 个核心文件
- 数据源从 yfinance 切换到 akshare（避免限流）

## [1.6.0] - 2026-04-XX

### Added
- DCC-GARCH 动态相关分析
- Granger 因果检验
- 可视化图表生成

## [1.5.0] - 2026-03-XX

### Added
- 初始版本
- Pearson/Spearman/Kendall 相关系数
- 基础投资建议
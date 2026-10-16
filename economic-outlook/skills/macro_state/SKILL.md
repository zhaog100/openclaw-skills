# macro_state — 宏观状态向量
## 职责
生成 10 维度宏观状态向量（GDP/CPI/PPI/M1/M2/社融/出口/社零/固投/地产）+ 三情景概率。
## 依赖
无（自动采集官方数据 + akshare 降级）
## 测试
`pytest tests/test_skills.py::test_macro_state -v`

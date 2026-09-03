#!/usr/bin/env python3
"""修复PR清单CSV的付款字段"""

import csv
import os

CSV_PATH = "/home/ubuntu/.openclaw/workspace/PR清单_全量.csv"
WALLET = "RTC2f0e423eafe70cb9394ba929fd11ff4d11bd515d"

# 读取CSV
rows = []
with open(CSV_PATH, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    fieldnames = reader.fieldnames
    for row in reader:
        rows.append(row)

print(f"总行数: {len(rows)}")

# 修复
fixed_count = 0
for row in rows:
    amount = row.get('金额', '').strip()
    status = row.get('状态', '').strip()
    pay_addr = row.get('付款地址', '').strip()
    pay_status = row.get('付款状态', '').strip()
    
    # 如果金额为空，跳过
    if not amount:
        continue
    
    # 如果付款地址为空，填充
    if not pay_addr:
        row['付款地址'] = WALLET
        fixed_count += 1
    
    # 如果付款状态为空，根据状态填充
    if not pay_status:
        if status == 'open':
            row['付款状态'] = '待验收'
        elif status == 'closed':
            row['付款状态'] = '已关闭'
        fixed_count += 1

print(f"修复了 {fixed_count} 行")

# 保存
with open(CSV_PATH, 'w', encoding='utf-8', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print(f"已保存: {CSV_PATH}")

# 验证
with open(CSV_PATH, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    filled = sum(1 for row in reader if row.get('付款地址', '').strip())
    print(f"验证: {filled} 行有付款地址")

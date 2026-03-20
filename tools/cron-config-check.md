# 定时任务配置检查

## 任务列表（7个）

```
1. config-backup（03:00）
   - ID: 1475c2aa-0543-4fd9-8fa8-f69327af202c
   - 状态：ok ✅
   - 下次：3小时后

2. memory-knowledge-noon（12:00）
   - ID: 9f72f785-cbd4-48c7-a39d-3e9941aa29fa
   - 状态：ok ✅
   - 下次：12小时后
   - **需要检查配置** ⚠️

3. 每日回顾与查漏补缺（23:00）
   - ID: fb3f1368-981b-4f84-ba3e-32fc742f0803
   - 状态：ok ✅
   - 下次：23小时后

4. QMD每日更新（23:50）
   - ID: 6b7546ff-0809-4bce-b590-6451614d4dce
   - 状态：ok ✅
   - 配置：channel=qqbot, to=C099848...
   - 下次：24小时后

5. memory-knowledge-evening（23:50）
   - ID: e0cb1a92-0cbc-452a-8744-5703def67e35
   - 状态：running ⏸️
   - 配置：channel=qqbot, to=C099848...
   - 下次：24小时后

6. disk-check（周日09:00）
   - ID: 1bcddf68-7ee9-4701-9de9-efe8183ddfcb
   - 状态：idle ⏸️
   - 下次：3天后

7. model-health-check（周一10:00）
   - ID: ae378b08-6e68-4a5c-8370-f5f931de4a84
   - 状态：idle ⏸️
   - 下次：4天后
```

## 需要检查的任务

**memory-knowledge-noon（12:00）**
- 可能缺少channel/to配置
- 需要添加：channel=qqbot, to=C099848DC9A60BF60A7BE31626822790

## 修复步骤

1. 检查memory-knowledge-noon配置
2. 如果缺少channel/to，添加配置
3. 测试运行
4. 提交Git记录

# tscircuit 生态开发经验

_2026-03-25 | 小米辣 (PM + Dev) 🌶️_

## 代码库结构

| 仓库 | 用途 |
|------|------|
| tscircuit/core | 核心原理图/PCB 引擎 |
| tscircuit/matchpack | 芯片封装布局求解 |
| tscircuit/schematic-trace-solver | 原理图走线求解 |

## core pipeline

- 入口：`createSchematicTraceSolverInputProblem`
- 关键参数：`maxMspPairDistance`（默认 2.4，同网走线断裂问题时需增大到 5）
- 走线断裂表现：同一网络的不同引脚间连线断开

## matchpack

### SingleInnerPartitionPackingSolver
- 主要芯片封装布局求解器
- 去耦电容处理：通过 `isDecouplingCap` 字段识别，特殊处理水平布局

### PartitionInputProblem 类型
```ts
{
  chipMap: Map<string, Chip>
  chipPinMap: Map<string, ChipPin>
  netMap: Map<string, Net>
}
```
- `isDecouplingCap`: 布尔字段，标记去耦电容

### Side 类型系统
```ts
type Side = "x-" | "x+" | "y-" | "y+"
```
- **不是** left/right/top/bottom！
- x- = 左, x+ = 右, y- = 上, y+ = 下

## CI 注意事项

- 上游依赖 `convertCircuitJsonToSchematicSimulationSvg` 可能有问题，导致 CI 失败
- biome 格式化必须通过
- 类型断言用 `as` 而非 `!`，undefined 检查要完整

## PR 标准

- Fork → branch → 提交 PR
- 需要通过所有 CI checks
- Review 周期：通常 1-3 天

---

**MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)**

# Specialized Layout for Decoupling Capacitors

## Summary

This PR implements specialized layout optimization for decoupling capacitors in the `SingleInnerPartitionPackingSolver`. The enhancement forces horizontal orientation for decoupling capacitors with pins on opposite Y sides (y+ and y-), which minimizes loop area and improves high-frequency performance.

## Changes

### Core Algorithm Enhancement
- **Forced Horizontal Orientation**: Decoupling capacitors with 2 pins on y+/y- sides are restricted to 0° and 180° rotations only
- **Loop Area Minimization**: Horizontal placement reduces electromagnetic interference and improves power delivery
- **Gap Optimization**: Respects the `decouplingCapsGap` parameter for tighter spacing between decoupling caps

### Files Modified
- `lib/solvers/PackInnerPartitionsSolver/SingleInnerPartitionPackingSolver.ts`
  - Added logic to detect decoupling capacitors with y+/y- pin arrangement
  - Restrict available rotations to [0, 180] for optimal horizontal placement
  - Maintain existing functionality for non-decoupling components

### Test Coverage
- `tests/SingleInnerPartitionPackingSolver/SingleInnerPartitionPackingSolver01.test.ts`
  - Validates horizontal layout behavior for decoupling capacitors
  - Tests gap parameter handling (0.3 vs 0.6)
  - Verifies placement optimization for high-frequency performance

## Technical Details

### Decoupling Capacitor Detection
```typescript
if (chip.isDecouplingCap && chip.pins.length === 2) {
  const pin1 = this.partitionInputProblem.chipPinMap[chip.pins[0]]
  const pin2 = this.partitionInputProblem.chipPinMap[chip.pins[1]]
  if (pin1 && pin2) {
    const sides = new Set([pin1.side, pin2.side])
    if (sides.has("y+") && sides.has("y-")) {
      availableRotations = [0, 180] // Only horizontal orientations
    }
  }
}
```

### Performance Benefits
- **Reduced Loop Area**: Horizontal placement minimizes current loop area
- **Improved EMI**: Better high-frequency noise filtering
- **Optimized Spacing**: Uses specialized `decouplingCapsGap` (0.3) vs regular `chipGap` (0.6)

## Validation

The solution has been tested with:
- Sample input containing U3 microcontroller and multiple decoupling capacitors (C10, C11)
- Verification of horizontal orientation enforcement
- Gap parameter compliance testing
- Layout optimization validation

## Impact

This enhancement makes the layout "less messy" as requested in issue #15 by:
1. Enforcing optimal horizontal orientation for decoupling capacitors
2. Reducing electromagnetic interference through loop area minimization
3. Improving high-frequency performance of power delivery networks
4. Maintaining clean, organized component placement

The change is backward compatible and only affects components specifically marked as decoupling capacitors with the appropriate pin configuration.
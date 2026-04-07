#!/usr/bin/env python3
"""
PowerPC G4 vs Modern GPU Benchmark
===================================

Hypothesis: Small-scale random memory access with complex branching
favors G4's low-latency cache and branch predictor over GPU kernel overhead.

Task: Hash chain verification with random jumps
- Small dataset (1000 elements)
- Random memory access pattern
- Complex branching logic
- Single-threaded pointer chasing

Expected: G4 wins because:
1. GPU kernel launch overhead (~10-50μs) > compute time
2. PCIe transfer time (~5-10μs) for small data
3. G4's 1.67GHz single-threaded performance + low-latency L1 cache
4. Random memory access hurts GPU coalescing
"""

import hashlib
import time
import random

# Simulate hash chain with random jumps
def verify_hash_chain(data, jumps=1000):
    """
    Verify a hash chain with random jumps.
    This is pointer-chasing heavy with complex branching.
    """
    chain = []
    current_idx = 0
    
    for i in range(jumps):
        # Random jump (bad for GPU coalescing)
        next_idx = (current_idx + data[current_idx]) % len(data)
        
        # Hash computation (AltiVec can accelerate this)
        h = hashlib.sha256()
        h.update(data[current_idx].to_bytes(8, 'little'))
        h.update(data[next_idx].to_bytes(8, 'little'))
        hash_val = int.from_bytes(h.digest()[:8], 'little')
        
        # Complex branching (GPU branch predictor suffers)
        if hash_val % 7 == 0:
            chain.append((current_idx, next_idx, 'A'))
        elif hash_val % 11 == 0:
            chain.append((current_idx, next_idx, 'B'))
        elif hash_val % 13 == 0:
            chain.append((current_idx, next_idx, 'C'))
        else:
            chain.append((current_idx, next_idx, 'D'))
        
        current_idx = next_idx
    
    return chain


def benchmark():
    # Generate small dataset (1KB total)
    data = [random.randint(0, 1000000) for _ in range(1000)]
    
    # Warm up
    verify_hash_chain(data, jumps=100)
    
    # Benchmark
    start = time.perf_counter()
    for _ in range(100):
        chain = verify_hash_chain(data, jumps=1000)
    end = time.perf_counter()
    
    total_ops = 100 * 1000
    elapsed = end - start
    ops_per_sec = total_ops / elapsed
    
    print(f"Total time: {elapsed*1000:.2f}ms")
    print(f"Operations: {total_ops}")
    print(f"Ops/sec: {ops_per_sec:,.0f}")
    print(f"Per operation: {elapsed/total_ops*1_000_000:.2f}μs")
    
    return elapsed


if __name__ == '__main__':
    print("PowerPC G4 Benchmark: Hash Chain Verification")
    print("=" * 50)
    benchmark()

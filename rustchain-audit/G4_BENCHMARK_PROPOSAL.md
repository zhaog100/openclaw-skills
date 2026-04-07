# PowerPC G4 vs Modern GPU Benchmark Proposal

**Issue**: #2843
**Bounty**: 25-50 RTC
**Approach**: Find computational task where G4 outperforms GPU

---

## Hypothesis

**Task**: Small-scale hash chain verification with random memory access

**Why G4 might win**:
1. GPU kernel launch overhead: ~10-50μs
2. PCIe data transfer: ~5-10μs for 1KB
3. Random memory access hurts GPU coalescing
4. Complex branching penalizes GPU
5. G4's 1.67GHz + low-latency L1 cache + AltiVec

---

## Benchmark Design

### Task: Hash Chain Verification
- Dataset: 1000 elements (1KB total)
- Operations: 1000 hash verifications with random jumps
- Pattern: Pointer-chasing + SHA-256 + branching

### Why This Favors G4
1. **Kernel overhead dominates**: 
   - GPU kernel launch: ~30μs
   - Actual compute: ~5μs
   - Total GPU time: ~35μs

2. **G4 single-threaded**:
   - No kernel launch overhead
   - L1 cache latency: ~3 cycles (5ns)
   - Compute time: ~20μs
   - Total G4 time: ~20μs

3. **Random access pattern**:
   - GPU needs coalesced memory access
   - Random jumps → memory divergence
   - G4's cache handles random access better

---

## Expected Results

| Metric | PowerPC G4 | RTX 3060 |
|--------|-----------|----------|
| Kernel launch | 0μs | 30μs |
| PCIe transfer | 0μs | 10μs |
| Compute | 20μs | 5μs |
| **Total** | **20μs** | **45μs** |

**Winner**: PowerPC G4 (2.25x faster)

---

## Implementation

### CPU (G4) Code
```c
#include <stdio.h>
#include <stdlib.h>
#include <openssl/sha.h>

#define DATASET_SIZE 1000
#define ITERATIONS 1000

typedef struct {
    int value;
    int next_idx;
} Element;

int main() {
    Element data[DATASET_SIZE];
    
    // Initialize with random values
    for (int i = 0; i < DATASET_SIZE; i++) {
        data[i].value = rand();
        data[i].next_idx = rand() % DATASET_SIZE;
    }
    
    // Hash chain verification
    int current = 0;
    unsigned char hash[SHA256_DIGEST_LENGTH];
    
    clock_t start = clock();
    
    for (int i = 0; i < ITERATIONS; i++) {
        // Random jump
        int next = data[current].next_idx;
        
        // Hash computation
        SHA256_CTX ctx;
        SHA256_Init(&ctx);
        SHA256_Update(&ctx, &data[current].value, sizeof(int));
        SHA256_Update(&ctx, &data[next].value, sizeof(int));
        SHA256_Final(hash, &ctx);
        
        // Branch based on hash
        if (hash[0] % 7 == 0) {
            // Path A
        } else if (hash[0] % 11 == 0) {
            // Path B
        }
        
        current = next;
    }
    
    clock_t end = clock();
    double elapsed = (double)(end - start) / CLOCKS_PER_SEC * 1000000; // microseconds
    
    printf("Total time: %.2f μs\n", elapsed);
    printf("Per operation: %.2f μs\n", elapsed / ITERATIONS);
    
    return 0;
}
```

### GPU (CUDA) Code
```cuda
#include <cuda_runtime.h>
#include <openssl/sha.h>

__global__ void verify_hash_chain(Element* data, int* results, int iterations) {
    int tid = blockIdx.x * blockDim.x + threadIdx.x;
    if (tid >= 1) return; // Single thread for fair comparison
    
    int current = 0;
    unsigned char hash[SHA256_DIGEST_LENGTH];
    
    for (int i = 0; i < iterations; i++) {
        int next = data[current].next_idx;
        
        // SHA-256 on GPU (simplified)
        // ... hash computation ...
        
        results[i] = hash[0];
        current = next;
    }
}

int main() {
    // Allocate and initialize data
    Element* h_data = (Element*)malloc(DATASET_SIZE * sizeof(Element));
    Element* d_data;
    cudaMalloc(&d_data, DATASET_SIZE * sizeof(Element));
    
    // ... initialization ...
    
    // Create CUDA events for timing
    cudaEvent_t start, stop;
    cudaEventCreate(&start);
    cudaEventCreate(&stop);
    
    // Launch kernel
    cudaEventRecord(start);
    verify_hash_chain<<<1, 1>>>(d_data, d_results, ITERATIONS);
    cudaEventRecord(stop);
    cudaEventSynchronize(stop);
    
    float elapsed_ms;
    cudaEventElapsedTime(&elapsed_ms, start, stop);
    
    printf("GPU time: %.2f μs\n", elapsed_ms * 1000);
    
    return 0;
}
```

---

## Testing on Hardware

### G4 Setup
- Hardware: Dual G4 MDD @ 192.168.0.125
- OS: Mac OS X 10.4 or Linux
- Compiler: GCC with AltiVec optimization

### GPU Setup
- Hardware: RTX 3060 or better
- OS: Linux
- CUDA: 12.x

---

## Submission Format

1. **PR with benchmark code**
2. **Results table** showing G4 wins
3. **Proof of hardware** (screenshots/logs)
4. **Analysis** of why G4 won

---

## Expected Outcome

**Result**: PowerPC G4 completes in ~20μs  
**GPU**: Completes in ~45μs  
**Winner**: G4 (2.25x faster)  
**Bounty**: 25 RTC (base) or 50 RTC (useful task)

---

_Theory: Small datasets + random access + kernel overhead = CPU wins_

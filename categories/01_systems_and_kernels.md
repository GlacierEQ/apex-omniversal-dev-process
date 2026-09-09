# 🛠️ CATEGORY 01: Low-Level Systems & Kernel Engineering

## 1. Scope & Architectural Mandate
Governs high-performance, deterministic, memory-safe, and low-latency systems software interfacing directly with hardware, kernels, or OS primitives.

- **Domains**: Operating system submodules, in-kernel sandboxing (eBPF), zero-copy ring buffers, lock-free queues, custom memory allocators, device drivers, and POSIX/Darwin systems programming.
- **Key Constraints**: Predictable latency (microsecond scale), bounded memory footprint, zero uncaught panics/segfaults, zero memory leaks, thread safety under multi-core concurrency.

---

## 2. Polyglot Technology Stack
- **Primary Languages**: Rust (default for memory safety & concurrency without GC), C/C++ (legacy systems, lock-free ring buffers, SIMD primitives), Zig / Odin (manual memory control), eBPF C (in-kernel tracing & networking).
- **Tooling**: `cargo`, `clang`, `valgrind`, `lldb`, `perf`, `bpftrace`, `cargo-fuzz`.

---

## 3. Core Invariants & Fail-Closed Boundaries
1. **Memory Invariants**:
   - Zero buffer overruns or under-allocations.
   - All pointer arithmetic must have bounds checks or live inside proven unsafe abstractions.
   - Resource Acquisition Is Initialization (RAII) or explicit cleanup destructors on every resource handle.
2. **Concurrency Invariants**:
   - Atomic memory ordering must be explicitly justified (e.g., `Acquire`/`Release` for ring buffers; never casual `SeqCst` where unwarranted).
   - Lock hierarchy must be acyclic to mathematically prevent deadlocks.
3. **Refusal Reason Codes**:
   - `ERR_SYS_BUFFER_OVERFLOW`: Allocation or write exceeds allocated capacity.
   - `ERR_SYS_BUFFER_UNDERFLOW`: Read attempted on empty buffer.
   - `ERR_SYS_OUT_OF_BOUNDS`: Index or pointer offset outside valid memory slice.
   - `ERR_SYS_RESOURCE_EXHAUSTED`: System file descriptors or ring memory exhausted.
   - `ERR_SYS_INVALID_ALIGNMENT`: Memory address does not meet SIMD or hardware alignment constraints.

---

## 4. Stage-by-Stage Implementation Guide

### Stage 0: Contracting
- Specify exact buffer capacities, latency percentiles (p99.99), and supported CPU architectures (`x86_64`, `aarch64` Apple Silicon).
- Define non-goals (e.g., dynamic resizing if deterministic memory is required).

### Stage 1: Design & State Machines
- Draw memory layout diagrams and cache-line alignment plans (64-byte padding to prevent false sharing).
- Specify state transitions for reader and writer pointers.

### Stage 2: Pro-Code Implementation
- Implement with zero stubs.
- Use explicit types (`uint64_t`, `usize`, `int32_t`).
- Prevent compiler undefined behavior (UB) using checked arithmetic or wrapping semantics.

### Stage 3: Adversarial Verification
- Stress test with multi-threaded saturation (16+ concurrent threads).
- Feed zero-byte inputs, misaligned pointers, and overflow boundaries.
- Run address sanitizer (`ASan`), thread sanitizer (`TSan`), and memory sanitizer (`MSan`).

---

## 5. Reference Pattern: Fail-Closed Bounded Ring Buffer
```rust
pub enum SystemsError {
    BufferOverflow { capacity: usize, requested: usize },
    BufferUnderflow,
    OutOfBounds { index: usize, length: usize },
}

pub struct BoundedRingBuffer<T, const N: usize> {
    storage: [Option<T>; N],
    head: usize,
    tail: usize,
    count: usize,
}

impl<T: Copy, const N: usize> BoundedRingBuffer<T, N> {
    pub fn new() -> Self {
        assert!(N > 0, "Capacity must be non-zero");
        Self { storage: [None; N], head: 0, tail: 0, count: 0 }
    }

    pub fn push(&mut self, item: T) -> Result<(), SystemsError> {
        if self.count >= N {
            return Err(SystemsError::BufferOverflow { capacity: N, requested: self.count + 1 });
        }
        self.storage[self.tail] = Some(item);
        self.tail = (self.tail + 1) % N;
        self.count += 1;
        Ok(())
    }

    pub fn pop(&mut self) -> Result<T, SystemsError> {
        if self.count == 0 {
            return Err(SystemsError::BufferUnderflow);
        }
        let item = self.storage[self.head].take().expect("Non-empty buffer must contain element");
        self.head = (self.head + 1) % N;
        self.count -= 1;
        Ok(item)
    }
}
```

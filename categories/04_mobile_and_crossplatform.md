# 📱 CATEGORY 04: Mobile & Cross-Platform Development

## 1. Scope & Architectural Mandate
Governs battery-efficient, offline-first, native and cross-platform mobile experiences on iOS, Android, and spatial environments.

- **Domains**: Swift / SwiftUI (iOS/macOS), Kotlin / Jetpack Compose (Android), Flutter / Dart (cross-platform), CoreData/Room/SQLite local persistence, background synchronization daemons.
- **Key Constraints**: Strict thermal and battery budgets, cold start $< 800\text{ms}$, smooth 120Hz ProMotion rendering, robust offline state recovery, sandboxed keychain security.

---

## 2. Polyglot Technology Stack
- **Languages**: Swift (iOS/visionOS), Kotlin (Android), Dart (Flutter).
- **Architectures**: MVI (Model-View-Intent), MVVM with unidirectional data flow, Clean Architecture with Repository pattern.
- **Storage & Sync**: SQLite via GRDB / Room, Secure Enclave / KeyStore for secrets, WebSockets / SSE for live sync.

---

## 3. Core Invariants & Fail-Closed Boundaries
1. **Offline State Invariant**:
   - The user must never face a blank blocking screen due to network unavailability.
   - Operations performed offline are queued in an append-only transaction ledger and synced idempotently upon reconnection.
2. **Main Thread Non-Blocking**:
   - Zero synchronous disk I/O, heavy JSON parsing, or cryptography on the main UI thread. All heavy computations run on background actor pools.
3. **Refusal Reason Codes**:
   - `ERR_MOB_BIOMETRIC_FAILED`: Local FaceID / biometric authentication rejected.
   - `ERR_MOB_STORAGE_CORRUPTION`: SQLite database checksum failure or migration error.
   - `ERR_MOB_OFFLINE_QUEUE_FULL`: Local pending sync queue capacity reached.
   - `ERR_MOB_DEVICE_INSUFFICIENT_MEMORY`: App received memory warning; non-essential caches must evict.

---

## 4. Stage-by-Stage Implementation Guide

### Stage 0: Contracting
- Specify supported OS versions (e.g., iOS 17+, Android 14+), screen sizes, and dynamic type font scaling.
- Detail offline capabilities and conflict resolution policy (e.g., client-wins vs server-wins).

### Stage 1: Architectural Modeling
- Design state machine for network transitions (Connected, Degraded, Offline, Syncing).
- Specify database schema migrations with automated rollback paths.

### Stage 2: Pro-Code Implementation
- Use Swift Actors or Kotlin Coroutines for safe concurrent state mutations.
- Enforce strict battery optimization: batch background network requests.

### Stage 3: Adversarial Verification
- Simulate airplane mode mid-transaction; verify transaction remains in pending queue.
- Inject corrupted local database files; verify automatic graceful recovery or rebuild.
- Test under low-memory pressure; assert zero OS-forced terminations.

---

## 5. Reference Pattern: Swift Offline Sync Queue Manager
```swift
import Foundation

public enum MobileSyncError: Error {
    case queueFull(capacity: Int)
    case serializationFailed
    case networkUnavailable
}

public struct SyncOperation: Codable, Identifiable {
    public let id: UUID
    public let endpoint: String
    public let payload: Data
    public let timestamp: Date
}

public actor OfflineSyncManager {
    private var pendingQueue: [SyncOperation] = []
    private let maxCapacity: Int

    public init(maxCapacity: Int = 500) {
        self.maxCapacity = maxCapacity
    }

    public func enqueue(endpoint: String, payload: Data) throws -> UUID {
        guard pendingQueue.count < maxCapacity else {
            throw MobileSyncError.queueFull(capacity: maxCapacity)
        }
        let op = SyncOperation(id: UUID(), endpoint: endpoint, payload: payload, timestamp: Date())
        pendingQueue.append(op)
        return op.id
    }

    public func dequeuePending() -> [SyncOperation] {
        let ops = pendingQueue
        pendingQueue.removeAll()
        return ops
    }

    public var queueLength: Int {
        pendingQueue.count
    }
}
```

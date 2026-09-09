# 🚀 CATEGORY 12: Aerospace, Robotics & Mission-Critical Embedded

## 1. Scope & Architectural Mandate
Governs mission-critical embedded control systems, orbital trajectory mechanics, robotic sensor fusion (ROS2), telemetry filtering, and hard real-time execution loops.

- **Domains**: SpaceX-grade mission event buses, orbital mechanics simulators, ROS2 robotics nodes, Kalman sensor fusion, actuator control, telemetry filtering, hardware-in-the-loop (HIL) testing.
- **Key Constraints**: Hard real-time determinism (zero missed deadlines), fail-safe hardware defaults, cosmic radiation single-event-upset (SEU) mitigation, bounded execution time.

---

## 2. Polyglot Technology Stack
- **Languages**: C / C++ (hard real-time controllers, RTOS), Rust (memory-safe robotics & embedded), Python (telemetry analysis & trajectory planning), Ada / SPARK (formal safety verification).
- **Standards & Frameworks**: ROS2 (Robot Operating System), DDS (Data Distribution Service), MISRA C:2012, DO-178C Level A.

---

## 3. Core Invariants & Fail-Closed Boundaries
1. **Missed Deadline Invariant**:
   - If a sensor read or actuator control loop misses its hard real-time deadline ($T_{\text{max}}$), the system must immediately enter an autonomous safe mode and disengage thrusters/actuators.
2. **Sensor Anomaly Rejection**:
   - Sensor inputs outside physical aerodynamic limits must be rejected with explicit telemetry codes; redundant sensor voting (2-out-of-3) is required.
3. **Refusal Reason Codes**:
   - `ERR_AERO_DEADLINE_MISSED`: Control loop computation exceeded maximum real-time period.
   - `ERR_AERO_SENSOR_OUT_OF_ENVELOPE`: Accelerometer or gyro reading exceeded physical flight bounds.
   - `ERR_AERO_ACTUATOR_SATURATION`: Command requested torque/deflection beyond mechanical physical limits.
   - `ERR_AERO_WATCHDOG_TRIP`: Hardware watchdog timer expired without heartbeat.

---

## 4. Stage-by-Stage Implementation Guide

### Stage 0: Contracting
- Define mission envelope: flight phases (Launch, Orbit, Descent, Landing), maximum allowable drift, and fail-safe recovery maneuvers.
- Establish strict DO-178C / MISRA compliance goals.

### Stage 1: Architectural Modeling
- Design dual or triple modular redundancy (TMR) state voting matrices.
- Formulate state estimation algorithms (Extended Kalman Filter - EKF).

### Stage 2: Pro-Code Implementation
- Zero dynamic heap allocation (`malloc`/`free`) after initialization phase. All memory statically allocated.
- Enforce loop bounds: all `for` and `while` loops must have constant maximum iterations.

### Stage 3: Adversarial Verification
- Hardware-in-the-loop (HIL) fault injection: disconnect simulated sensor mid-flight.
- Assert that the voting engine detects sensor loss and falls back to redundant sensors within 1 millisecond.

---

## 5. Reference Pattern: Fail-Safe Real-Time Sensor Voting Matrix
```python
from typing import List, Dict, Any, Optional

class AerospaceSensorVoter:
    def __init__(self, tolerance: float, min_valid: float, max_valid: float):
        self.tolerance = tolerance
        self.min_valid = min_valid
        self.max_valid = max_valid

    def vote_telemetry(self, sensor_readings: List[float]) -> Dict[str, Any]:
        # 1. Filter out readings beyond physical flight envelope
        valid_readings = [r for r in sensor_readings if self.min_valid <= r <= self.max_valid]
        
        if len(valid_readings) < 2:
            return {
                "status": "FAIL_SAFE",
                "code": "ERR_AERO_SENSOR_OUT_OF_ENVELOPE",
                "message": "Fewer than 2 sensors within physical flight envelope; safe mode engaged",
                "actuator_disengaged": True
            }

        # 2. Check pairwise agreement within tolerance
        inliers = []
        for i, val in enumerate(valid_readings):
            agreements = sum(1 for j, other in enumerate(valid_readings) if i != j and abs(val - other) <= self.tolerance)
            if agreements >= 1:
                inliers.append(val)

        if not inliers:
            return {
                "status": "FAIL_SAFE",
                "code": "ERR_AERO_VOTING_DISAGREEMENT",
                "message": "Sensors in envelope disagreed beyond allowable tolerance",
                "actuator_disengaged": True
            }

        consensus_value = sum(inliers) / len(inliers)
        return {
            "status": "NOMINAL",
            "code": "SUCCESS",
            "value": consensus_value,
            "inlier_count": len(inliers),
            "actuator_disengaged": False
        }
```

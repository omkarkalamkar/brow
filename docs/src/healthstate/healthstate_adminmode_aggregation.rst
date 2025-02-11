HealthState Aggregation in Telescope Low
=========================================

Overview
--------

This document explains how **HealthState** aggregation works in the Telescope Low system.  
The overall system state is determined by aggregating the health states of multiple subsystems,  
with **AdminMode** as an input factor.

HealthState Aggregation
-----------------------

Each subsystem reports a **HealthState**, which can be one of:

- **OK** – Fully functional.
- **DEGRADED** – Partially functional with issues.
- **FAILED** – Non-functional.
- **UNKNOWN** – Health state is unavailable.

### Aggregation Rules:

1. If **any subsystem** is in **FAILED**, the system health is **FAILED**.
2. If no subsystems are **FAILED**, but **any subsystem** is **DEGRADED**, the system health is **DEGRADED**.
3. If **all subsystems** are **OK**, the system health is **OK**.
4. If **all subsystems are UNKNOWN**, the system health is **UNKNOWN**.

#### Example:

+---------------+-------------+---------------+
| Subsystem     | HealthState | System Health |
+---------------+-------------+---------------+
| CSP Subarray  | OK          | OK            |
| SDP Subarray  | DEGRADED    | DEGRADED      |
| MCCS Subarray | OK          | DEGRADED      |
+---------------+-------------+---------------+

Effect of AdminMode on HealthState
----------------------------------

Although **AdminMode** is not aggregated separately, it influences HealthState aggregation.

### AdminMode States:

- **ONLINE** – Fully operational and configurable.
- **OFFLINE** – Not available for operations.
- **MAINTENANCE** – Undergoing maintenance.
- **NOT_FITTED** – Not installed or part of the system.
- **STANDBY** – Inactive or low-power state.

### Impact of AdminMode on HealthState:

1. If **AdminMode is OFFLINE**, the subsystem’s HealthState is ignored.
2. If **AdminMode is NOT_FITTED**, the subsystem is excluded from aggregation.
3. If **AdminMode is MAINTENANCE**, HealthState is informative but does not affect system-wide aggregation.
4. Otherwise, HealthState aggregation follows the rules mentioned earlier.

#### Example:

+---------------+------------+-------------+---------------+-------------+
| Subsystem     | AdminMode  | HealthState | System Health | System Mode |
+---------------+------------+-------------+---------------+-------------+
| CSP Subarray  | ONLINE     | OK          | DEGRADED      | ONLINE      |
| SDP Subarray  | ONLINE     | DEGRADED    | DEGRADED      | ONLINE      |
| MCCS Subarray | OFFLINE    | FAILED      | DEGRADED      | OFFLINE     |
+---------------+------------+-------------+---------------+-------------+

🔹 **Note:** Since **MCCS Subarray is OFFLINE**, its **FAILED** state is ignored. The system health is **DEGRADED** instead of **FAILED**.

.. warning::
   Do not use the `SetAdminMode` command directly, as AdminMode is managed internally by the system.

Usage in TMC LOW
-----------------------

- This aggregation logic is applied in **CSP, MCCS, and SDP** for system monitoring.
- Ensures accurate system-wide health representation.
- **AdminMode is used as an input** to HealthState aggregation, preventing unnecessary alerts for offline or maintenance subsystems.

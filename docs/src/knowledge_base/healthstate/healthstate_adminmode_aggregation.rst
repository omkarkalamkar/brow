===========================================
Subarray healthState Aggregation in TMC Low
===========================================

Overview
========

This document explains how TMC performs Subarray healthState aggregation. 
The subarray healthState is determined by aggregating the health states of 
multiple subsystem subarray devices. The **AdminMode** reported by the 
subsystem subarray devices as also a contributing factor.

HealthState Aggregation
-----------------------

Each subsystem subarray device reports an attribute named **healthState**. The 
value can be:

- **OK** – Fully functional.
- **DEGRADED** – Partially functional with issues.
- **FAILED** – Non-functional.
- **UNKNOWN** – Health state is unavailable.

Only a single value can be reported at a time.

Aggregation Rules
------------------

1. If **any subsystem** is in **FAILED**, the system health is **FAILED**.
2. If no subsystems are **FAILED**, but **any subsystem** is **DEGRADED**, the system health is **DEGRADED**.
3. If **all subsystems** are **OK**, the system health is **OK**.
4. If **all subsystems are UNKNOWN**, the system health is **UNKNOWN**.

.. csv-table::  Example
   :file: healthstate_aggregation.csv
   :header-rows: 1

.. note::
   The adminMode is defined in more details in the SKA Control System Guidelines. 
   Please refer the document for additional understanding.

Impact of AdminMode on HealthState
----------------------------------

Although **AdminMode** is not aggregated separately, it influences HealthState aggregation.

AdminMode States:
-----------------

- **ONLINE** – Fully operational and configurable.
- **OFFLINE** – Not available for operations.
- **MAINTENANCE** – Undergoing maintenance.
- **NOT_FITTED** – Not installed or part of the system.
- **STANDBY** – Inactive or low-power state.

Impact of AdminMode on HealthState:
-----------------------------------

1. If **AdminMode is OFFLINE**, the subsystem’s HealthState is ignored.
2. If **AdminMode is NOT_FITTED**, the subsystem is excluded from aggregation.
3. If **AdminMode is MAINTENANCE**, HealthState is informative but does not affect system-wide aggregation.
4. Otherwise, HealthState aggregation follows the rules mentioned earlier.

Impact of AdminMode on command execution:
-----------------------------------------

1. The command invocation is not allowed from TMC CentralNode if the adminMode of any subsystem's controller is  either **OFFLINE or NOT_FITTED**
2. The command invocation is not allowed from TMC SubarrayNode if the adminMode of any subsystem's subarray is  either **OFFLINE or NOT_FITTED**
3. The command invocation will allowed if the adminMode of subsystem is either **ONLINE or ENGINEERING**

Example:
--------

+---------------+------------+-------------+---------------+-------------+
| Subsystem     | AdminMode  | HealthState | System Health | System Mode |
+---------------+------------+-------------+---------------+-------------+
| CSP Subarray  | ONLINE     | OK          | DEGRADED      | ONLINE      |
| SDP Subarray  | ONLINE     | DEGRADED    | DEGRADED      | ONLINE      |
| MCCS Subarray | OFFLINE    | FAILED      | DEGRADED      | OFFLINE     |
+---------------+------------+-------------+---------------+-------------+

🔹 **Note:** Since **MCCS Subarray is OFFLINE**, its **FAILED** state is ignored. The system health is **DEGRADED** instead of **FAILED**.

.. warning::  
   Although TMC devices provide the `SetAdminMode` command to set the `AdminMode` of lower-level devices and subsystems, its usage is discouraged. The functionality is not consistently implemented across all subsystems, and using this command may lead to system inconsistencies. Full implementation of `AdminMode` is expected by the end of PI 27.  

Usage in TMC LOW
-----------------------

- This aggregation logic is applied in **CSP, MCCS, and SDP** for system monitoring.
- Ensures accurate system-wide health representation.
- **AdminMode is used as an input** to HealthState aggregation, preventing unnecessary alerts for offline or maintenance subsystems.

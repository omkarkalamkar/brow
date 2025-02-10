HealthState and AdminMode Aggregation in Telescope Low
============================================================

Overview
--------

This document explains how **HealthState** and **AdminMode** aggregation works in the system. The system's overall state is determined by aggregating the states of multiple devices.

HealthState Aggregation
-----------------------

Each device reports its **HealthState**, which can be one of:

- **OK** - The device is fully functional.
- **DEGRADED** - The device has some issues but can still function.
- **FAILED** - The device is non-functional.
- **UNKNOWN** - The device’s health is not available.

Aggregation Rules:

1. If **any device** is in **FAILED**, the system health is **FAILED**.
2. If **no devices** are in **FAILED**, but **any device** is in **DEGRADED**, the system health is **DEGRADED**.
3. If **all devices are OK**, the system health is **OK**.
4. If **any device is UNKNOWN** and no other states (FAILED, DEGRADED, OK) are present, the system health is **UNKNOWN**.

Example:

+------------+------------+----------------+
| Device     | HealthState | System Health |
+------------+------------+----------------+
| Device A   | OK         | OK             |
| Device B   | DEGRADED   | DEGRADED       |
| Device C   | OK         | DEGRADED       |
+------------+------------+----------------+

---

AdminMode Aggregation
----------------------

Each device has an **AdminMode**, which determines whether it is operational and configurable.

AdminMode states:

- **ONLINE** - The device is operational and can execute commands.
- **OFFLINE** - The device is not available.
- **MAINTENANCE** - The device is under maintenance.
- **NOT_FITTED** - The device is not installed or not part of the system.
- **STANDBY** - The device is in a low-power or inactive state.

Aggregation Rules:

1. If **all devices are ONLINE**, the system is **ONLINE**.
2. If **any device is in OFFLINE**, the system is **OFFLINE**.
3. If **any device is in MAINTENANCE**, the system is **MAINTENANCE**.
4. If **all devices are NOT_FITTED**, the system is **NOT_FITTED**.
5. If **any device is in STANDBY**, but none are in OFFLINE or MAINTENANCE, the system is **STANDBY**.

Example:

+------------+------------+--------------+
| Device     | AdminMode  | System Mode  |
+------------+------------+--------------+
| Device A   | ONLINE     | ONLINE       |
| Device B   | MAINTENANCE| MAINTENANCE  |
| Device C   | ONLINE     | MAINTENANCE  |
+------------+------------+--------------+

---

Combined Aggregation of HealthState and AdminMode
--------------------------------------------------

Since **AdminMode** determines whether devices are operational, it affects how **HealthState** should be considered.

1. If **AdminMode is OFFLINE**, HealthState is ignored.
2. If **AdminMode is NOT_FITTED**, the device is excluded from aggregation.
3. If **AdminMode is MAINTENANCE**, HealthState is informative but does not affect system-wide aggregation.
4. Otherwise, HealthState aggregation follows the rules mentioned earlier.

Example:

+------------+------------+------------+----------------+-------------+
| Device     | AdminMode  | HealthState | System Health | System Mode |
+------------+------------+------------+----------------+-------------+
| Device A   | ONLINE     | OK         | DEGRADED       | ONLINE      |
| Device B   | ONLINE     | DEGRADED   | DEGRADED       | ONLINE      |
| Device C   | OFFLINE    | FAILED     | DEGRADED       | OFFLINE     |
+------------+------------+------------+----------------+-------------+

Since **Device C is OFFLINE**, its **FAILED** state is ignored, so the system health is **DEGRADED** instead of **FAILED**.

---

Implementation in Code
----------------------

A simple Python function to implement this logic:

.. code-block:: python

   def aggregate_health_and_adminmode(devices):
       health_states = []
       admin_modes = []

       for device in devices:
           if device["admin_mode"] == "OFFLINE":
               continue  # Ignore offline devices
           if device["admin_mode"] == "NOT_FITTED":
               continue  # Ignore not fitted devices
           if device["admin_mode"] == "MAINTENANCE":
               continue  # Maintenance mode does not impact health

           health_states.append(device["health_state"])
           admin_modes.append(device["admin_mode"])

       # Aggregate HealthState
       if "FAILED" in health_states:
           system_health = "FAILED"
       elif "DEGRADED" in health_states:
           system_health = "DEGRADED"
       elif all(state == "OK" for state in health_states):
           system_health = "OK"
       else:
           system_health = "UNKNOWN"

       # Aggregate AdminMode
       if "OFFLINE" in admin_modes:
           system_mode = "OFFLINE"
       elif "MAINTENANCE" in admin_modes:
           system_mode = "MAINTENANCE"
       elif all(mode == "ONLINE" for mode in admin_modes):
           system_mode = "ONLINE"
       elif "STANDBY" in admin_modes:
           system_mode = "STANDBY"
       else:
           system_mode = "UNKNOWN"

       return system_health, system_mode

   # Example usage
   devices = [
       {"admin_mode": "ONLINE", "health_state": "OK"},
       {"admin_mode": "ONLINE", "health_state": "DEGRADED"},
       {"admin_mode": "OFFLINE", "health_state": "FAILED"},
   ]
   system_health, system_mode = aggregate_health_and_adminmode(devices)
   print(system_health, system_mode)  # Output: DEGRADED ONLINE

---

Usage in TMC LOW
-----------------------

- This logic is used in `CSP, MCCS and SDP` for high-level system monitoring.
- It ensures that system-wide health is accurately represented.
- The **AdminMode** aggregation prevents unnecessary alerts for offline or maintenance devices.

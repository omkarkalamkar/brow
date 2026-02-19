HealthInfo Reporting
====================

Purpose
-------

**HealthInfo** provides structured, human-readable diagnostic information that explains **why** a component is in its current **HealthState** (OK, DEGRADED, FAILED, or UNKNOWN).

While **HealthState** gives you the high-level status, **HealthInfo** tells you the specific reason(s) — especially useful when troubleshooting failures or degraded behaviour.

Key characteristics:

- Only populated (non-empty) when HealthState is **DEGRADED**, **FAILED**, or **UNKNOWN**
- Empty (``[]``) when everything is **OK**
- Updated in sync with **HealthState** changes
- Published as an *on-change* event


Reporting Format
----------------

**HealthInfo** is a JSON object (dictionary) where:

- **Keys** = Tango device names (leaf nodes)
- **Values** = List of failure/diagnostic messages (strings) indicating the problem

Example — when problems exist:

.. code-block:: json

    {
        "low-tmc/subarray-leaf-node-csp/01": [
            "CSP Subarray Health State: FAILED",
            "Delay Model Exception."
        ],
        "low-tmc/subarray-leaf-node-sdp/01": [
            "Liveliness check failed for SDP"
        ],
        "low-tmc/subarray-leaf-node-mccs/01": [
            "MCCS Subarray Health State: UNKNOWN"
        ]
    }

Example — when no issues:

.. code-block:: json

    []


What You Will See as an Operator
--------------------------------

- **Subarray level** — HealthInfo shows aggregated problems from leaf nodes (CSP, SDP, MCCS) and any TMC-internal issues detected (e.g. liveliness check failure).
- **Leaf node level** — More detailed reasons (available by reading HealthInfo directly from the relevant leaf node device).
- Clear mapping of **which** device/subsystem is affected and **why**.

Use HealthInfo to:

- Quickly identify which subsystem(s) caused a FAILED or DEGRADED HealthState
- Understand whether the issue is external (subsystem) or internal (TMC-detected)
- Guide deeper investigation (e.g. go to the failing subsystem's own HealthInfo or logs)

For diagrams and more detailed system context, see:

`HealthInfo Reporting Mechanism Diagram <https://confluence.skatelescope.org/display/SWSI/HealthInfo+Reporting+Mechanism>`_

.. _`Recovering TMC Low`:

TMC Recovery mechanism in case of subsystem failure
===================================================
- This guide provides instructions to recover TMC Low when it enters the ``FAULT`` observation state.

- The recovery steps involve issuing command-line instructions that can be executed from any Python runtime environment or script.

TMC Low Auto Recovery
=====================

Overview
--------

The **Telescope Monitoring and Control (TMC) Low** system implements an **auto-recovery mechanism** to handle failures
that occur during the ``Configure`` command execution.

When a ``Configure`` command fails, TMC attempts to recover the affected subsystems automatically, depending on their
observation (Obs) states.

---

Auto Recovery Scenarios
-----------------------

1. Configure Command Failure — Subsystems in Recoverable State
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If the ``Configure`` command fails for any reason and the subsystems are in the following states:

+-------------------+-------------------+-------------------+---------------------------------------------------------------+
| **CSP Obs State** | **SDP Obs State** | **MCCS Obs State** | **Auto Recovery Action**                                     |
+===================+===================+===================+===============================================================+
| ``IDLE``          | ``READY``         | ``READY``          | TMC invokes the **End** command on **MCCS** and **SDP**      |
|                   |                   |                   | subarrays to bring them back to ``IDLE``. Once complete, the  |
|                   |                   |                   | **TMC Subarray** also transitions to ``IDLE``.                |
+-------------------+-------------------+-------------------+---------------------------------------------------------------+

**Example**

- **Scenario:**
  The ``Configure`` command fails due to a timeout in MCCS configuration.

- **Subsystem States:**
  - CSP → ``IDLE``
  - SDP → ``READY``
  - MCCS → ``READY``

- **Action Taken:**
  TMC automatically issues ``End`` on SDP and MCCS subarrays, returning all subsystems (and the TMC Subarray)
  to the ``IDLE`` state.

---

2. Successive Configure Command Failure — All Subsystems in READY State
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If a successive ``Configure`` command fails for any reason, and all subsystems remain in the ``READY`` state:

+-------------------+-------------------+-------------------+---------------------------------------------------------------+
| **CSP Obs State** | **SDP Obs State** | **MCCS Obs State** | **Auto Recovery Action**                                     |
+===================+===================+===================+===============================================================+
| ``READY``         | ``READY``         | ``READY``          | TMC re-invokes the **Configure** command **only** on the     |
|                   |                   |                    | failed subsystem, using the **last successful config data**, |
|                   |                   |                    | to restore the **TMC Subarray ObsState** to ``READY``.       |
+-------------------+-------------------+-------------------+---------------------------------------------------------------+

**Example**

- **Scenario:**
  The first ``Configure`` command succeeds. The next ``Configure`` command fails for SDP due to invalid configuration
  parameters.

- **Subsystem States:**
  - CSP → ``READY``
  - SDP → ``READY``
  - MCCS → ``READY``

- **Action Taken:**
  TMC re-invokes ``Configure`` on SDP with the **previous successful configuration data**.
  Once successful, the **TMC Subarray ObsState** transitions back to ``READY``.

---

Summary
-------

+-----------------------------------------+------------------------------------------+-------------------------------------------------------------+
| **Condition**                           | **Subsystem States**                     | **Recovery Action**                                         |
+=========================================+==========================================+=============================================================+
| First ``Configure`` fails               | CSP: ``IDLE``                            | Invoke ``End`` on MCCS and SDP → all subsystems return to   |
|                                         | SDP: ``READY``                           | ``IDLE``.                                                   |
|                                         | MCCS: ``READY``                          |                                                             |
+-----------------------------------------+------------------------------------------+-------------------------------------------------------------+
| Successive ``Configure`` fails          | CSP: ``READY``                           | Re-invoke ``Configure`` on failed subsystem → return to     |
|                                         | SDP: ``READY``                           | ``READY``.                                                  |
|                                         | MCCS: ``READY``                          |                                                             |
+-----------------------------------------+------------------------------------------+-------------------------------------------------------------+

---




TMC Low in FAULT ObsState
-------------------------

- TMC will not get stuck in a particular transitional observation states like for ex. ``RESOURCING``, ``CONFIGURING``, etc.

- Instead it moves to the Observation state ``FAULT`` in the following scenarios.

- To recover from the Observation state ``FAULT``, please follow the steps to recover.

+-----------------------------------+------------------------------------------------------------------------+ 
| Scenario                          |               Steps to recover                                         | 
+===================================+========================================================================+ 
| 1. When a command times out       |- Using Subarray Node                                                   |
| 2. When a command fails on any    |    - Create device proxy of subarray node                              |
|    of the subsystem               |    - When TMC Low is in ObsState.FAULT, execute Restart() command on   |
| 3. When any of the subsystem      |      TMC Subarray Node to bring it back to initial ObsState.EMPTY      |
|    transitions to FAULT ObsState  |    - subarray_node = tango.DeviceProxy("low-tmc/subarray/01")          |
|                                   |    - subarray_node.Restart()                                           |
+-----------------------------------+------------------------------------------------------------------------+


TMC Low not recovering from FAULT obsState
-------------------------------------------

If the ``Restart()`` command fails to transition the TMC Low to the ``EMPTY`` observation state, please follow these steps:

- **Inspect all TMC Low leaf nodes:**  
  Manually visit each leaf node within the TMC Low hierarchy.

- **Identify the faulty subsystem:**  
  Check the ``obsState`` of each node to locate any subsystem that is not in the expected state.

- **Manually reset the faulty subsystem:**  
  Attempt to bring the identified faulty subsystem to the ``EMPTY`` observation state by applying corrective actions or issuing necessary commands.

- **Re-invoke Restart() on the TMC Low Subarray Node:**  
  After all subsystems are in a recoverable state, issue the ``Restart()`` command on the TMC Low Subarray Node to transition the system back to the ``EMPTY`` obsState.
.. _`Recovering TMC Low`:

TMC Recovery mechanism in case of subsystem failure
===================================================
- This guide provides instructions to recover TMC Low when it enters the ``FAULT`` observation state.

- The recovery steps involve issuing command-line instructions that can be executed from any Python runtime environment or script.


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
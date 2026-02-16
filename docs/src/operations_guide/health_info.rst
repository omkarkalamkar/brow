HealthInfo Reporting Mechanism
==============================

Overview
--------

The **HealthInfo** attribute provides structured diagnostic information
explaining the current **HealthState** of a component.

The purpose of this attribute is to provide additional context and diagnostic
information about the cause of failure beyond the existing HealthState.

While ``HealthState`` indicates the overall status
(OK, DEGRADED, FAILED, UNKNOWN), ``HealthInfo`` provides the
reason and context behind that state.

HealthInfo is:

- Reported when a component enters **DEGRADED / FAILED / UNKNOWN**
- Archived as an *on change* event
- Kept in sync with ``HealthState`` updates
- Structured in **JSON format** for consistent and machine-readable reporting

This ensures operators have clear visibility into subsystem failures
and TMC-detected exceptions.

Design Choices
--------------

Separate Attributes
~~~~~~~~~~~~~~~~~~~

Two attributes are maintained:

- ``HealthState`` → Represents the component's current operational state
- ``HealthInfo`` → Provides structured diagnostic details explaining the HealthState

This separation ensures:

- Clean state propagation logic
- Detailed reporting without overloading the state attribute
- Better monitoring and debugging capability


Data Structure
~~~~~~~~~~~~~~

HealthInfo uses **JSON format** for structured reporting.

Example when failures are detected:

.. code-block:: json

    {
        "low-tmc/subarray-leaf-node-csp/01": [
            "CSP Subarray Health State: FAILED"
        ],
        "low-tmc/subarray-leaf-node-sdp/01": [
            "Liveliness check failed for SDP",
        ]
    }

When no issues are present:

.. code-block:: json

    []

This structure ensures:

- Clear mapping between component and failure message
- Extensibility for future diagnostic additions
- Machine-readable format for automated monitoring


HealthInfo Reporting Sources
----------------------------

TMC-Detected Failures
~~~~~~~~~~~~~~~~~~~~~

TMC reports the reason for failure when:

- Internal validation fails
- Subsystem state transitions are invalid

The HealthInfo contains the explicit failure reason.


Subsystem Failures
~~~~~~~~~~~~~~~~~~

When a subsystem reports FAILED / DEGRADED / UNKNOWN:

- The TMC Leaf Node subscribes to the subsystem's ``HealthState``
- The Leaf Node propagates this information upward
- The Subarray Node updates its HealthInfo accordingly

The Subarray HealthInfo reports:

- Subsystem name
- High-level failure reason

Detailed HealthInfo remains available at the subsystem level.


HealthInfo Flow
---------------

Leaf Nodes
~~~~~~~~~~

Each TMC Leaf Node subscribes to the ``HealthState`` of its subsystem.

The Leaf Node:

- Monitors subsystem health
- Updates its own ``HealthState``
- Updates ``HealthInfo`` when necessary
- Propagates health information to the Subarray Node

TMC Internal Exceptions
~~~~~~~~~~~~~~~~~~~~~~~

Internal exceptions affect both HealthState and HealthInfo.

Examples:

- Delay model exceptions
- Failed availability checks

When such exceptions occur:

- ``HealthState`` → FAILED or DEGRADED
- ``HealthInfo`` → Contains exception reason
- Information is propagated to the Subarray Node


Subarray Node Aggregation
~~~~~~~~~~~~~~~~~~~~~~~~~

The Subarray Node derives its ``HealthState`` by aggregating:

- Subsystem HealthState
- TMC Leaf Node HealthState
- Internal TMC exceptions

Aggregation logic examples:

- Any subsystem FAILED → Subarray = FAILED

The Subarray updates its HealthInfo to explain:

- Which subsystem failed
- Whether failure is internal or external
- Any reduced operational capability


Synchronization and Event Handling
-----------------------------------

- HealthInfo is updated whenever HealthState changes.
- HealthInfo is archived as an *on change* event.
- HealthInfo remains synchronized with HealthState at all times.

This guarantees consistency between operational state and diagnostic information.


Operator Visibility
-------------------

HealthInfo provides operators with:

- Clear identification of failing subsystems
- Visibility into TMC-detected internal exceptions
- Structured diagnostics for troubleshooting

Detailed subsystem-specific HealthInfo remains available at the subsystem level.


Reference
---------

For detailed flow diagrams and system-level visualization, refer to:

HealthInfo Reporting Mechanism Diagram
https://confluence.skatelescope.org/display/SWSI/HealthInfo+Reporting+Mechanism
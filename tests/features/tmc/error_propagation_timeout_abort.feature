@XTP-81319 @XTP-28348
Scenario Outline: Error Propagation Reported by TMC Low Abort Command for Defective Subarray
    Given the telescope is in ON state
    And TMC subarray is in initial ObsState for <defective_subsystem>
    When Abort is invoked on a defective subsystem <defective_subsystem>
    Then TMC SubarrayNode obsstate changes to FAULT obsState
    Then the command failure is reported by subarray with error message with <defective_subsystem>

    Examples:
            | defective_subsystem  |
            | CSP                  |
            | SDP                  |
            | MCCS                 |

@XTP-81339 @XTP-28348
Scenario Outline: Timeout Reported by TMC Low Abort Command for Defective Subarray
    Given the telescope is in ON state
    And TMC subarray is in initial ObsState for <defective_subsystem>
    When Abort is invoked on a defective subsystem <defective_subsystem>
    Then TMC SubarrayNode obsstate changes to FAULT obsState
    Then the Timeout is reported by subarray with error message with <defective_subsystem>

    Examples:
            | defective_subsystem  |
            | CSP                  |
            | SDP                  |
            | MCCS                 |

@XTP-81594 @XTP-28348
Scenario Outline: Error Propagation Reported by TMC Low Restart Command for Defective Subarray
    Given the telescope is in ON state
    And TMC subarray is in ABORTED ObsState
    When Restart is invoked on a defective subsystem <defective_subsystem>
    Then the command failure is reported by subarray with error message with <defective_subsystem>

    Examples:
        | defective_subsystem  |
        | SDP                  |
        | CSP                  |
        | MCCS                 |


@XTP-81466 @XTP-28348
Scenario Outline: Timeout Reported by TMC Low Reset Command for Defective Subarray
    Given the telescope is in ON state
    And TMC subarray is in ABORTED ObsState
    When Restart is invoked on a defective subsystem <defective_subsystem>
    Then the Timeout is reported by subarray with error message with <defective_subsystem>

    Examples:
            | defective_subsystem  |
            | SDP                  |
            | CSP                  |
            | MCCS                 |
@XTP-81319 @XTP-28348
Scenario Outline: Error Propagation Reported by TMC Low Abort Command for Defective Subarray
    Given the telescope is in ON state
    And TMC subarray is in initial ObsState for <defectiveSubsystem>
    When Abort is invoked on a defective subsystem <defectiveSubsystem>
    Then TMC SubarrayNode obsstate changes to FAULT obsState
    Then the command failure is reported by subarray with error message with <defectiveSubsystem>

    Examples:
            | defectiveSubsystem   |
            | CSP                  |
            | SDP                  |
            | MCCS                 |

@XTP-81339 @XTP-28348
Scenario Outline: Timeout Reported by TMC Low Abort Command for Defective Subarray
    Given the telescope is in ON state
    And TMC subarray is in initial ObsState for <defectiveSubsystem>
    When Abort is invoked on a defective subsystem <defectiveSubsystem>
    Then TMC SubarrayNode obsstate changes to FAULT obsState
    Then the Timeout is reported by subarray with error message with <defectiveSubsystem>

    Examples:
            | defectiveSubsystem   |
            | CSP                  |
            | SDP                  |
            | MCCS                 |

@XTP-28348
Scenario Outline: Error Propagation Reported by TMC Low Restart Command for Defective Subarray
    Given the telescope is in ON state
    And TMC subarray is in ABORTED ObsState
    When Restart is invoked on a defective subsystem <defectiveSubsystem>
    Then the command failure is reported by subarray with error message with <defectiveSubsystem>

    Examples:
        | defectiveSubsystem   |
        | CSP                  |
        | SDP                  |
        #| MCCS                 |


@XTP-81466 @XTP-28348
Scenario Outline: Timeout Reported by TMC Low Reset Command for Defective Subarray
    Given the telescope is in ON state
    And TMC subarray is in ABORTED ObsState
    When Restart is invoked on a defective subsystem <defectiveSubsystem>
    Then the Timeout is reported by subarray with error message with <defectiveSubsystem>

    Examples:
            | defectiveSubsystem   |
            | CSP                  |
            | SDP                  |
            | MCCS                 |
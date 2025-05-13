@XTP-28348
Scenario Outline: Error Propagation Reported by TMC Low Abort Command for Defective Subarray
    Given the telescope is in ON state
    And TMC subarray is in ObsState IDLE
    When Abort is invoked on a defective subsystem <defectiveSubsystem>
    Then TMC SubarrayNode obsstate changes to FAULT obsState
    Then the command failure is reported by TMC SubarrayNode with error message

    Examples:
            | defectiveSubsystem   |
            | CSP                  |
            | SDP                  |

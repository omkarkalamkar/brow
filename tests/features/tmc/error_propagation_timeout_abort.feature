@XTP-28348
Scenario Outline: Error Propagation Reported by TMC Low Abort Command for Defective Subarray
    Given the telescope is in ON state
    And the TMC subarray is in the IDLE observation state
    When Abort is invoked on a defective subsystem
    Then the command failure is reported by subarray with an appropriate error message

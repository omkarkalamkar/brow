@XTP-28348
Scenario Outline: Error Propagation Reported by TMC Low Abort Command for Defective Subarray
    Given the telescope is in ON state
    And TMC subarray is in ObsState EMPTY
    And I issue the AssignResources command to the TMC
    And the CSP subarray is in an abnormal state
    When I invoke abort command on defective system
    Then the command failure is reported by TMC SubarrayNode with error message
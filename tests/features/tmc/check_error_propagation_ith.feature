Scenario Outline: TMC subarray reports errors during interactions with MCCS subarray
    Given the telescope is in ON state
    And TMC subarray is in ObsState EMPTY
    When the MCCS controller is in an abnormal state    
    And I issue the AssignResources command to the TMC
    Then the Error is reported by the TMC
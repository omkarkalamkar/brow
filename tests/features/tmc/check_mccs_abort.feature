Scenario: Verify Abort in Resourcing
    Given a TMC
    And central node is busy assigning resources
    And mccsleafnode node is in observation state ObsState.RESOURCING
    When I invoke abort on subarray node
    Then MCCS subarray transitions to observation state ObsState.EMPTY
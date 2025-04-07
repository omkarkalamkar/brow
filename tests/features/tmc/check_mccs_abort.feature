Scenario: Verify Abort in Resourcing
    Given a TMC
    And central node is busy assigning resources
    And mccsleafnode node is in observation state ObsState.RESOURCING
    When I invoke abort on subarray node
    When MCCS subarray transitions to Obsstate EMPTY
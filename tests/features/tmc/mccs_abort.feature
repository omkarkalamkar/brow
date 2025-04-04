Scenario: Verify Abort in Resourcing
    Given a TMC
    And central node is busy assigning resources
    And mccsleafnode node is in observation state RESOURCING
    When I invoke abort on subarray node
    MCCS subarray transitions to Obsstate EMPTY
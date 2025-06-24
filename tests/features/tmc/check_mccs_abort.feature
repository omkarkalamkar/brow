@XTP-29003
Scenario: Verify Abort in Resourcing
    Given a TMC
    And central node is busy assigning resources
    And mccs subarray leafnode node is in observation state ObsState.RESOURCING
    When I invoke abort on subarray node
    Then mccs master leafnode result to aborted
    And the Subarray node transitions to observation state ObsState.ABORTED
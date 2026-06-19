Feature: Skb 1158

@XTP-96989 @XTP-28348
Scenario: Verify SKB-1158
    Given a TMC
    And central node is busy assigning resources
    And subarray node is in observation state RESOURCING
    When I invoke abort on subarray node
    Then subarray Node is transitioned to observation state ABORTED
    And central node receives AssignResources longrunningcommandresult with message `Command has been aborted`
    
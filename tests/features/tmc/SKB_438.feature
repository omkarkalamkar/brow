@XTP-58039 @XTP-28348
Scenario: Verify SKB-438
    Given a TMC
    And central node is busy assigning resources
    And subarray node is in observation state RESOURCING
    When I invoke abort on subarray node
    Then central node receives longrunningcommandresult with message `Command has been aborted`
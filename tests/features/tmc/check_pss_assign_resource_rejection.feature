Feature: Check Pss Assign Resource Rejection

@XTP-98756 @XTP-98925 @XTP-28348 @TEAM_HIMALAYA
Scenario: Verify for PSS scan integration with shared beam rejection
    Given the telescope is in the ON state
    And subarray 1 and 2 are in the EMPTY ObsState
    When I assign resources with shared PSS beams to both subarrays simultaneously
    Then the first assignment succeeds with OK result
    And the second assignment fails with PSS beam conflict error
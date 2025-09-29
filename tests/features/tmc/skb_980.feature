@SKA_low
Scenario: Verify SKB-980 for assign resources flow
    Given the telescope is in the ON state
    And subarray 1 and 2 are in the EMPTY ObsState
    When I assign resources from the both the subarrays simultaneously
    Then the TMC central node long running command results for both subarrys are OK
    And the TMC, CSP, SDP, and MCCS subarray 1 transition to the IDLE obsState
    And the TMC, CSP, SDP, and MCCS subarray 2 transition to the IDLE obsState

@SKA_low
Scenario: Verify SKB-980 for release resources flow
    Given the telescope is in the ON state
    And subarray 1 and 2 are in the IDLE ObsState
    When I release resources from the both the subarrays simultaneously
    Then the TMC central node long running command results for both subarrys are OK
    And the TMC, CSP, SDP, and MCCS subarray 1 transition to the EMPTY obsState
    And the TMC, CSP, SDP, and MCCS subarray 2 transition to the EMPTY obsState
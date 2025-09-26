@skb_1051
Scenario: Verify SKB_1051
    Given the telescope is in the ON state
    And subarray 1 and 2 are in the IDLE ObsState
    When I release resources from the both the subarrays
    Then the TMC, CSP, SDP, and MCCS subarray 1 transition to the EMPTY obsState
    And the TMC, CSP, SDP, and MCCS subarray 2 transition to the EMPTY obsState

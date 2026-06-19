Feature: Skb 1051

#This test verifies the behaviour of Release Resources on TMC with multiple subarrays.
@XTP-90244 @XTP-28348 @SKA_low
Scenario: Verify SKB-1051
    Given the telescope is in the ON state
    And subarray 1 and 2 are in the IDLE ObsState
    When I release resources from both the subarrays
    Then the TMC, CSP, SDP, and MCCS subarray 1 and 2 transition to the EMPTY obsState

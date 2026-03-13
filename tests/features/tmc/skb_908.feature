#This test verifies Assign Resources flow with multiple subarrays
@XTP-90283 @XTP-28348 @SKA_low
Scenario: Verify SKB-908 for assign resources flow
    Given the telescope is in the ON state
    And subarray 1 and 2 are in the EMPTY ObsState
    When I assign resources to both the subarrays simultaneously
    Then the TMC central node long running command results for both subarrys are OK
    And the TMC, CSP, SDP, and MCCS subarray 1 and 2 transition to the IDLE obsState

#This test verifies Release Resources flow with multiple subarrays
@XTP-90284 @XTP-28348 @SKA_low
Scenario: Verify SKB-908 for release resources flow
    Given the telescope is in the ON state
    And subarray 1 and 2 are in the IDLE ObsState
    When I release resources from both the subarrays simultaneously
    Then the TMC central node long running command results for both subarrys are OK
    And the TMC, CSP, SDP, and MCCS subarray 1 and 2 transition to the EMPTY obsState


@XTP-77663 @XTP-64112 @XTP-28348 @SKA_low
    Scenario: Execute Scans on two Low telescope subarrays using TMC
        Given a Low telescope
        And telescope is in ON state
        And I assign station 1 to subarray 1 and station 1 to subarray 2
        And I configure the two subarrays for scan
        When I invoke scan command on two subarrays
        Then the TMC, CSP, SDP and MCCS subarrays transition to SCANNING obsState
        And after the scan duration they transition back to READY obsState
Scenario: Release resources from Low subarray
    Given a Low telescope
    And telescope is in the ON state
    And subarray is in the IDLE obsState
    When I release all resources assigned to it
    Then the TMC, CSP, SDP, and MCCS subarrays transition to EMPTY obsState
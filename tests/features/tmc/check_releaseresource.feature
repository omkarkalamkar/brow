Scenario: Release resources from Low subarray
    Given the telescope is in the ON state
    And subarray is in the IDLE obsState
    When I release all resources assigned to it
    Then the TMC, CSP, SDP, and MCCS subarrays transition to the EMPTY obsState
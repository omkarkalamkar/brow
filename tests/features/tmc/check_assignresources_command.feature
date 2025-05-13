Scenario: Assign resources to Low subarray
    Given the telescope is in the ON state
    And subarray is in EMPTY ObsState
    When I assign resources to the subarray
    Then the TMC, CSP, SDP, and MCCS subarrays transition to RESOURCING obsState
    And the TMC, CSP, SDP, and MCCS subarrays transition to IDLE obsState
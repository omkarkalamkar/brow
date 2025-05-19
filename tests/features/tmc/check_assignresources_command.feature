Scenario: Assign resources to Low subarray
    Given the telescope is in the ON state
    And subarray is in the EMPTY ObsState
    When I assign resources to the subarray
    Then the TMC, CSP, SDP, and MCCS subarrays transition to the RESOURCING obsState
    And the TMC, CSP, SDP, and MCCS subarrays transition to the IDLE obsState
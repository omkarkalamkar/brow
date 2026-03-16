@XTP-98746 @XTP-98925 @XTP-28348 @TEAM_SAHYADRI
Scenario Outline: Execute observations simultaneously on four subarrays
    Given the telescope is in the ON state
    And all the subarrays are in the EMPTY ObsState
    And I Assign subarray 1 with station beam <station_beam_subarray1>, subarray 2 with station beam <station_beam_subarray2>, subarray 3 with pst beam <pst_beam_subarray3> and subarray 4 with pst beam <pst_beam_subarray4>
    And I configure all the subarrays
    And the Subarrays are configured successfully
    When I start scan on all the subarrays
    Then the subarrays transition to READY on scan completion
    And I end the observations on all the Subarrays
    And I release resources from all the subarrays

    Examples:
      | station_beam_subarray1 | station_beam_subarray2  | pst_beam_subarray3 | pst_beam_subarray4 |
      | 1                      | 2                       | 1                  | 2                  |

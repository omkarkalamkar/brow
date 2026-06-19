Feature: Tmc Pss Beams Two Subarray

@XTP-98746 @XTP-98925 @XTP-28348 @TEAM_HIMALAYA
Scenario Outline: Execute two observations simultaneously where two subarrays are allocated PSS beams without sharing in TMC Low
    Given the telescope is in the ON state
    And subarray 1 and 2 are in the EMPTY ObsState
    When I Assign subarray 1 with pss beams <pss_beams_subarray1> and subarray 2 with pss beams <pss_beams_subarray2>
    Then invoking Configure command on both subarrays TMC moves to CONFIGURING
    And the Subarray is configured successfully
    And CSPSLN generates updated delay model for pss beams

    Examples:
      | pss_beams_subarray1 | pss_beams_subarray2  |
      | 1-15                | 16-30                |

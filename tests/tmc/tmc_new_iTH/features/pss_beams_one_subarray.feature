Feature: Multiple pss beams one subarray

@XTP-98755 @XTP-98925 @XTP-28348 @TEAM_HIMALAYA
Scenario Outline: Execute observation where a subarray is allocated 30 PSS beams in TMC Low
    Given subarray in EMPTY ObsState
    When I Assign subarray with 30 pss beams
    Then invoking Configure command on subarray TMC moves to CONFIGURING
    And the Subarray is configured successfully
    And CSPSLN generates updated delay model for pss beams

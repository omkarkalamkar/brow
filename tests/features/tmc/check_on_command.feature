@XTP-64114 @XTP-28348 
Scenario: Starting up low telescope
    Given a Low telescope
    When I invoke the ON command on the telescope
    Then the SDP, CSP and MCCS go to the ON state
    And the telescope go to the ON state


@XTP-84024 @XTP-83574 @TEAM_HIMALAYA
Scenario: Starting up low telescope if one subsystem in adminmode ENGINEERING
    Given a Low telescope
    And MCCS controller is in adminmode ENGINEERING
    When I invoke the ON command on the telescope
    Then the SDP, CSP and MCCS go to the ON state
    And the telescope go to the ON state
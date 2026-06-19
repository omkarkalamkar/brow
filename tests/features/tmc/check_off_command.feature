@XTP-64122 @XTP-28348 
Scenario: Switch off the low telescope
    Given a Low telescope
    And the telescope is in the ON state
    When I invoke the OFF command on the telescope
    Then the CSP, SDP and MCCS go to the OFF state
    And the telescope go to the OFF state
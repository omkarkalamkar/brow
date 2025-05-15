Scenario: Switch off the low telescope
    Given a Low telescope
    And the telescope is in the ON state
    When I invoke the OFF command on the telescope
    Then the CSP, SDP and MCCS goes to OFF state
    And the telescope goes to OFF state
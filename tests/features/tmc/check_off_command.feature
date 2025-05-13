Scenario: Switch off the low telescope
    Given a Low telescope
    And the telescope is in the ON state
    When I invoke the OFF command on the telescope
    Then the SDP and MCCS go to OFF state
    And the CSP remains in ON state
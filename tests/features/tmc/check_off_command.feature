Scenario: Switch off the low telescope
    Given a Low telescope
    And a Telescope consisting of SDP, CSP and MCCS that is ON
    When I invoke the OFF command on the telescope
    Then the SDP and MCCS go to OFF state
    And the CSP remains in ON state
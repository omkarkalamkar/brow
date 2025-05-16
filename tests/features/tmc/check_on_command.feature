Scenario: Starting up low telescope
    Given a Low telescope
    When I invoke the ON command on the telescope
    Then the SDP, CSP and MCCS goes to the ON state
    And the telescope goes to the ON state
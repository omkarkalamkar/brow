Feature: StartUp Telescope with TMC and MCCS devices	
    @XTP-33991 @XTP-73593 @XTP-28348 @XTP-30488 @Team_HIMALAYA
    Scenario: StartUp Telescope with TMC and MCCS devices
        Given a Telescope consisting of TMC,MCCS,simulated SDP and simulated CSP
        When I startup the telescope
        Then the MCCS should transition to ON state
        And the telescope state should change to ON
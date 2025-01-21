Feature: Default

	#This BDD test performs TMC-SDP pairwise testing to verify StartUp command flow.
    @XTP-29228 @XTP-73593 @XTP-28348 @XTP-28347 @XTP-29227
    Scenario: Start up the telescope having TMC and SDP subsystems
        Given a Telescope consisting of TMC, SDP, simulated CSP and simulated MCCS
        When I start up the telescope
        Then the SDP must go to ON state
        And telescope state is ON
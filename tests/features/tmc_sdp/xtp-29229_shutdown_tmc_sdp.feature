Feature: Default

	#This BDD test performs TMC-SDP pairwise testing to verify Shutdown command flow.
    @XTP-29229 @XTP-29227 @XTP-73593
    Scenario: Switch off the telescope having TMC and SDP subsystems 
        Given a Telescope consisting of TMC and SDP that is in ON State
        And  simulated CSP and MCCS in ON States
        And telescope state is ON
        When I switch off the telescope
        Then the sdp must go to OFF State
        And telescope state is OFF
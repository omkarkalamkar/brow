@XTP-29685 @XTP-29682 @XTP-73593
Scenario: Start up the telescope having TMC and CSP subsystems
	Given a Telescope consisting of TMC,CSP,simulated SDP and simulated MCCS
	When I start up the telescope
	Then the CSP must go to ON state
	And telescope state is ON
@XTP-29686 @XTP-28348 @XTP-73593 @XTP-29682
Scenario: Standby the telescope having TMC and CSP subsystems
	Given a Telescope consisting of TMC,CSP,simulated SDP and simulated MCCS 
	And telescope state is ON
	When I invoke TelescopeStandby command  
	Then telescope state is STANDBY
	And the csp subarray and controller stays in ON state
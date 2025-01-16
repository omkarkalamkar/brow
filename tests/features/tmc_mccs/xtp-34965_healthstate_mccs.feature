	@XTP-34965 @XTP-73574 @XTP-28348 @XTP-34276 @XTP-73574
	Scenario Outline: Verify CentralNode TelescopeHealthState
		Given a Telescope consisting of TMC, MCCS, emulated SDP and emulated CSP 
		And the Telescope is in ON state
		When The <devices> health state changes to <health_state> 
		Then the telescope health state is <telescope_health_state>
		Examples:
		| devices                           | health_state               | telescope_health_state |
		| mccs controller                   | DEGRADED                   |   DEGRADED             |
		| mccs controller,sdp master        | DEGRADED,DEGRADED          |   DEGRADED             |
		| mccs controller,csp master        | DEGRADED,DEGRADED          |   DEGRADED             |
		| mccs controller,sdp master        | DEGRADED,OK                |   DEGRADED             |
		| mccs controller,csp master        | DEGRADED,OK                |   DEGRADED             |
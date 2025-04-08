@XTP-
Scenario: Successful Configuration of Low Telescope Subarray with Only MCCS in TMC
	Given a TMC
	Given a subarray in the IDLE obsState
	When I configure subarray with only MCCS
	Then the MCCS is in the READY obsState
	And the SDP and CSP remains in the IDLE obsState
	And the subarray is in the READY obsState

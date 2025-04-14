@XTP-
Scenario: Successful Configuration of Low Telescope Subarray with Only MCCS in TMC
	Given the telescope is in ON state
	And TMC subarray in the IDLE obsState
	When I configure TMC subarray with MCCS only configuration
	Then the MCCS subarray and MCCS subarray leafnode are in the READY obsState
	And the SDP and CSP subarray and subarray leafnodes remains in the IDLE obsState
	And the TMC subarray is in the READY obsState

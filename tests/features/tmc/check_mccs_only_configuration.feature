Feature: Check Mccs Only Configuration

@XTP-78908
Scenario: Successful Configuration of Low Telescope Subarray with Only MCCS in TMC
	Given the telescope is in the ON state
	And TMC subarray in the IDLE obsState
	When I configure TMC subarray with MCCS only configuration
	Then the MCCS subarray and MCCS subarray leafnode are in the READY obsState
	And the SDP, CSP subarray and subarray leafnodes remain in the IDLE obsState
	And the TMC subarray is in the READY obsState

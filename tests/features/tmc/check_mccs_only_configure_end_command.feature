Scenario: Successful Execution of End Command on Low Telescope Subarray with MCCS-Only Configuration in TMC
	Given the telescope is in ON state
	And the TMC subarray is in the IDLE obsState
	And I configure TMC subarray with MCCS only configuration
	And the TMC subarray transitions to the READY obsState
	When I invoke End command on the TMC subarray
    then the TMC Subarray is in the IDLE obsState


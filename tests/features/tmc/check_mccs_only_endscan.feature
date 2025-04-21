@XTP-79504
Scenario: Successful Execution of the EndScan Command on a Low Telescope Subarray with an MCCS-Only subsystem
	Given the telescope is in the ON state
	And the TMC subarray is in the IDLE obsState
	And I configure the TMC subarray with an MCCS-only configuration
	And the TMC subarray is in the READY obsState
	And I invoke the Scan command on the TMC subarray
	And the TMC subarray is in the SCANNING obsState
	When I invoke the EndScan command on the TMC subarray
	Then the TMC subarray transitions to the READY obsState
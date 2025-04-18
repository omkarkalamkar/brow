Scenario: Successful Execution of the Scan Command on a Low Telescope Subarray with an MCCS-Only subsystem
	Given the telescope is in the ON state
	And the TMC subarray is in the IDLE obsState
	And I configure the TMC subarray with an MCCS-only configuration
	And the TMC subarray is in the READY obsState
	When I invoke the Scan command on the TMC subarray for a given period
	Then the TMC subarray is in the SCANNING obsState
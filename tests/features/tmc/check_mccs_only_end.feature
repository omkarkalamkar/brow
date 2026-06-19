Feature: Check Mccs Only End

@XTP-79501
Scenario: Successful Execution of the End Command on a Low Telescope Subarray with an MCCS-Only subsystem
	Given the telescope is in the ON state
	And the TMC subarray is in the IDLE obsState
	And I configure the TMC subarray with an MCCS-only configuration
	And the TMC subarray is in the READY obsState
	When I invoke the End command on the TMC subarray
	Then the TMC subarray is in the IDLE obsState
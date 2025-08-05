Feature: SP-5340

	#This test covers the flow of restart command when only TMC subarray observation state is FAULT, it will able to only recover TMC subarray to observation state EMPTY. This will also test the partial success scenario of Restart Command.
	@SKA_tmc_low_restart @XTP-82857 @XTP-82736 @TEAM_HIMALAYA
	Scenario: Test Restart Command flow when TMC Subarray observation state is FAULT and subsystems are EMPTY
		Given a TMC Subarray transitioned from RESOURCING to FAULT observation state after command failure
		And CSP,SDP and MCCS in observation state EMPTY,EMPTY and IDLE
		And MCCS resources are released directly using MCCS Controller
		When I invoke Restart Command on the TMC Subarray
		Then TMC subarray transitions to observation state EMPTY
Feature: SP-5340

	#This test covers scenarios where user invokes Restart command as TMC Subarray Node is in FAULT observation state to recover system.
	@XTP-82861 @XTP-82747 @TEAM_HIMALAYA
	Scenario: Test Restart Command when TMC subarray transitions to FAULT observation state
		Given a TMC Subarray transitioned from RESOURCING to FAULT observation state
		And CSP,SDP and MCCS in observation state EMPTY
		When I invoke Restart Command on the TMC Subarray
		Then TMC subarray transitions to observation state EMPTY
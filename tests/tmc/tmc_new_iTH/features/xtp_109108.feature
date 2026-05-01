Feature: Default

	#This tests verify the bug related to observation state transition from EMPTY to FAULT during execution of restart command on TMC Subarray when there is an error in any one of the subsystems.
	@XTP-109108 @XTP-28348
	Scenario: Verify SKB-1326
		Given TMC Subarray in observation state RESTARTING
		And SDP Subarray leaf node in Observation state EMPTY
		When CSP subarray leaf node raises error and transitions to observation state EMPTY
		Then the TMC subarray aggregates to observation state EMPTY
		And the TMC subarray reports failure on LongRunningCommandResult attribute
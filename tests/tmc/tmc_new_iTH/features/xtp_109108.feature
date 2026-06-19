Feature: SKB-1326

	#This tests verify the bug related to observation state transition from EMPTY to FAULT during execution of restart command on TMC Subarray when there is an error in any one of the subsystems.
	@XTP-109108 @XTP-28348
	Scenario Outline: Verify SKB-1326
		Given <subsystem3> subarray as defective device
		And TMC Subarray in observation state RESTARTING
		And <subsystem1> subarray leaf node in Observation state EMPTY
		And <subsystem2> subarray leaf node in Observation state EMPTY
		When <subsystem3> subarray leaf node raises error and transitions to observation state EMPTY
		Then the TMC subarray reports failure on LongRunningCommandResult attribute
		And the TMC subarray aggregates to observation state EMPTY
		Examples:
		    |subsystem1 | subsystem2 | subsystem3|
		    | SDP       | MCCS       | CSP       |
		    | SDP       | CSP        | MCCS      |
		    | MCCS      | CSP        | SDP       |
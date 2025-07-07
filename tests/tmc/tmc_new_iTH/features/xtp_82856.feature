Feature: SP-5340

	#This test covers scenarios where user invokes Restart command as TMC Subarray Node is in FAULT observation state to recover system.
	@XTP-82856 @XTP-82736 @SKA_tmc_low_restart
	Scenario Outline: Test Restart Command when TMC subarray transitions to FAULT observation state
	Given CSP,SDP and MCCS in observation states <csp_obsstate>,<sdp_obsstate> and <mccs_obsstate> after <command>
	And TMC Subarray in observation state FAULT
	When I invoke restart command on the TMC Subarray
	Then SDP,CSP and MCCS transitions to observation state EMPTY
	And TMC subarray transitions to observation state EMPTY
	Examples:
		| command         | csp_obsstate | sdp_obsstate     | mccs_obsstate |
		| AssignResources | FAULT        | IDLE             | IDLE          |
		| AssignResources | FAULT        | IDLE             | RESOURCING    |
		| AssignResources | FAULT        | IDLE             | FAULT         |
		| AssignResources | FAULT        | RESOURCING       | IDLE          |
		| AssignResources | FAULT        | RESOURCING       | RESOURCING    |
		| AssignResources | FAULT        | RESOURCING       | FAULT         |
		| AssignResources | IDLE         | FAULT            | IDLE          |
		| AssignResources | IDLE         | FAULT            | RESOURCING    |
		| AssignResources | IDLE         | FAULT            | FAULT         |
		| AssignResources | RESOURCING   | FAULT            | IDLE          |
		| AssignResources | RESOURCING   | FAULT            | RESOURCING    |
		| AssignResources | RESOURCING   | FAULT            | FAULT         |
		| AssignResources | RESOURCING   | IDLE             | IDLE          |
		| AssignResources | RESOURCING   | IDLE             | RESOURCING    |
		| AssignResources | RESOURCING   | IDLE             | FAULT         |
		| AssignResources | RESOURCING   | RESOURCING       | RESOURCING    |
		| AssignResources | IDLE         | RESOURCING       | IDLE          |
		| AssignResources | IDLE         | RESOURCING       | RESOURCING    |
		| AssignResources | IDLE         | RESOURCING       | FAULT         |
		| Configure       | FAULT        | READY            | READY         |
		| Configure       | FAULT        | READY            | CONFIGURING   |
		| Configure       | FAULT        | READY            | FAULT         |
		| Configure       | FAULT        | CONFIGURING      | READY         |
		| Configure       | FAULT        | CONFIGURING      | CONFIGURING   |
		| Configure       | FAULT        | CONFIGURING      | FAULT         |
		| Configure       | READY        | FAULT            | READY         |
		| Configure       | READY        | FAULT            | CONFIGURING   |
		| Configure       | READY        | FAULT            | FAULT         |
		| Configure       | CONFIGURING  | FAULT            | READY         |
		| Configure       | CONFIGURING  | FAULT            | CONFIGURING   |
		| Configure       | CONFIGURING  | FAULT            | FAULT         |
		| Configure       | CONFIGURING  | READY            | READY         |
		| Configure       | CONFIGURING  | READY            | CONFIGURING   |
		| Configure       | CONFIGURING  | READY            | FAULT         |
		| Configure       | CONFIGURING  | CONFIGURING      | READY         |
		| Configure       | CONFIGURING  | CONFIGURING      | CONFIGURING   |
		| Configure       | CONFIGURING  | CONFIGURING      | FAULT         |
		| Configure       | READY        | CONFIGURING      | READY         |
		| Configure       | READY        | CONFIGURING      | CONFIGURING   |
		| Configure       | READY        | CONFIGURING      | FAULT         |
		| Scan            | SCANNING     | READY            | READY         |
		| Scan            | SCANNING     | READY            | SCANNING      |
		| Scan            | SCANNING     | READY            | FAULT         |
		| Scan            | READY        | SCANNING         | READY         |
		| Scan            | READY        | SCANNING         | SCANNING      |
		| Scan            | FAULT        | SCANNING         | READY         |
		| Scan            | FAULT        | SCANNING         | SCANNING      |
		| Scan            | FAULT        | SCANNING         | FAULT         |
		| Scan            | SCANNING     | FAULT            | SCANNING      |
		| Scan            | SCANNING     | FAULT            | FAULT         |
		| Scan            | SCANNING     | SCANNING         | READY         |
		| Scan            | SCANNING     | SCANNING         | FAULT         |
	    | ReleaseResources| FAULT        | IDLE             | IDLE          |
		| ReleaseResources| IDLE         | FAULT            | IDLE          |
		| ReleaseResources| IDLE         | FAULT            | FAULT         |
		| ReleaseResources| FAULT        | FAULT            | IDLE          |
    	| ReleaseResources| FAULT        | IDLE             | FAULT         |
		| ReleaseResources| FAULT        | IDLE             | RESOURCING    |
		| ReleaseResources| RESOURCING   | FAULT            | IDLE          |
		| ReleaseResources| RESOURCING   | RESOURCING       | FAULT         |
		| ReleaseResources| FAULT        | FAULT            | RESOURCING    |
		| ReleaseResources| FAULT        | RESOURCING       | FAULT         |
		| EndScan         | FAULT        | READY            | READY         |
		| EndScan         | READY        | FAULT            | READY         |
		| EndScan         | READY        | READY            | FAULT         |
		| EndScan         | READY        | FAULT            | FAULT         |
		| EndScan         | FAULT        | FAULT            | READY         |
		| EndScan         | FAULT        | READY            | FAULT         |
		| End             | FAULT        | IDLE             | IDLE          |
		| End             | IDLE         | FAULT            | IDLE          |
		| End             | IDLE         | IDLE             | FAULT         |
		| End             | IDLE         | FAULT            | FAULT         |
		| End             | FAULT        | FAULT            | IDLE          |
		| End             | FAULT        | IDLE             | FAULT         |	
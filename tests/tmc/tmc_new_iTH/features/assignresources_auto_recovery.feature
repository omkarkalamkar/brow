Scenario: TMC Perform Auto Recovery when AssignResources Failed
	Given a subarray is in the EMPTY obsState
	When I AssignResources to subarray with defective <failed_devices>
	Then AssignResources command fails on <failed_devices> Subarray Leaf Node
	And a subarray perform auto recovery and transition Subarray Obs State to EMPTY
	And <failed_devices> Failure is reported on Long Running Command Result
	Examples:
	| failed_devices  |
	| SDP             |

Scenario: TMC Auto Recovery Failed
	Given a subarray is in the EMPTY obsState
	When I AssignResources to subarray with defective <failed_devices>
	Then AssignResources command fails on <failed_devices> Subarray Leaf Node
	And auto recovery fails due to <auto_recovery_failed_devices> failure
	And TMC Subarray Obs State transition to FAULT Obs State
	Examples:
	| failed_devices  | auto_recovery_failed_devices |
	| SDP             | MCCS                         |

Scenario: Succesive AssignResources command execution after recovery
	Given a subarray is in the EMPTY obsState
	And failed AssignResources is successfully recovered with <failed_devices>
	When I invoke second AssignResources command on subarray
	Then AssignResources command is executed successfully
	Examples:
	| failed_devices  |
	| SDP             |


Scenario: TMC Perform Auto Recovery when AssignResources Failed CSP EMPTY
	Given a subarray is in the EMPTY obsState
	When I AssignResources to subarray with defective <failed_devices> EMPTY
	Then AssignResources command fails on <failed_devices> Subarray Leaf Node
	And a subarray perform auto recovery and transition Subarray Obs State to EMPTY
	And <failed_devices> Failure is reported on Long Running Command Result
	Examples:
	| failed_devices  |
	| CSP             |
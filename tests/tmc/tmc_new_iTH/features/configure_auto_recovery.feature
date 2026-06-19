Feature: Configure auto recovery

@XTP-91743 @XTP-91746 @XTP-28348 @Team_HIMALAYA
Scenario: TMC Perform Auto Recovery when Configure Failed
	Given a subarray is in the IDLE obsState
	When I configure it for a scan with defective <failed_devices>
	Then configure failed on <failed_devices> Subarray Leaf Node
	And a subarray perform auto recovery and transition Subarray Obs State to IDLE
	And <failed_devices> Failure is reported on Long Running Command Result
	Examples:
	| failed_devices  |
	| SDP             |

@XTP-91744 @XTP-91746 @XTP-28348 @Team_HIMALAYA
Scenario: TMC Perform Auto Recovery when Successive Configure Failed
	Given a subarray is in the READY obsState
	When I configure it for a scan with defective <failed_devices>
	Then configure failed on <failed_devices> Subarray Leaf Node
	And a subarray perform auto recovery and transition Subarray Obs State to READY
	And <failed_devices> Failure is reported on Long Running Command Result
	Examples:
	| failed_devices  |
	| CSP             |

@XTP-91745 @XTP-91746 @XTP-28348 @Team_HIMALAYA
Scenario: TMC Auto Recovery Failed
	Given a subarray is in the IDLE obsState
	When I configure it for a scan with defective <failed_devices>
	Then configure failed on <failed_devices> Subarray Leaf Node
	And auto recovery failed due to <auto_recovery_failed_devices> failure
	And TMC Subarray Obs State transition to FAULT Obs State
	Examples:
	| failed_devices  | auto_recovery_failed_devices |
	| SDP             | MCCS                         |
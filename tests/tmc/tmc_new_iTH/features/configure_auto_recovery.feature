Scenario: TMC Perform Auto Recovery when Configure Failed
	Given a subarray is in the IDLE obsState
	When I configure it for a scan with defective <failed_devices>
	Then configure failed on <failed_devices> Subarray Leaf Node
	And a subarray perform auto recovery and transition Subarray Obs State to IDLE
	And <failed_devices> Failure is reported on Long Running Command Result
	Examples:
	| failed_devices  |
	| SDP             |

Scenario: TMC Perform Auto Recovery when Successive Configure Failed
	Given a subarray is in the READY obsState
	When I configure it for a scan with defective <failed_devices>
    Then configure failed on <failed_devices> Subarray Leaf Node
	And a subarray perform auto recovery and transition Subarray Obs State to READY
    And <failed_devices> Failure is reported on Long Running Command Result
	Examples:
	Examples:
	| failed_devices  |
	| SDP             |

Scenario: TMC Auto Recovery Failed
	Given a TMC
	And a subarray is in the IDLE obsState
	When I configure it for a scan
    Then configure failed on SDP Subarray Leaf Node
    And SDP Subarray Leaf Node transition to IDLE Obs state
	And a subarray perform auto recovery
    And auto recovery failed due to <failed_device> failure
    And TMC Subarray Obs State transition to FAULT Obs State
	And Configure command failure, auto recovery failure reported on LRCR
	Examples:
	| failed_device  |
	| CSP            |
	| SDP            |
	| MCCS           |
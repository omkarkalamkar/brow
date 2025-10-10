Scenario: TMC Perform Auto Recovery when Configure Failed
	Given a subarray is in the IDLE obsState
	When I configure it for a scan with defective <failed_devices>
    Then configure failed on <failed_devices> Subarray Leaf Node
    And <failed_devices> Subarray Leaf Node transition to IDLE Obs state
	And a subarray perform auto recovery and transition Subarray Obs State to IDLE
	Examples:
	| failed_devices  |  success_devices |
	| CSP             |  SDP,MCCS        |
	| SDP             |  CSP,MCCS        |
    | MCCS            |  CSP,SDP         |
	| CSP,SDP         |  MCCS            |
	| MCCS,SDP        |  CSP             |

Scenario: TMC Perform Auto Recovery when Successive Configure Failed
	Given a TMC
	And a subarray is in the READY obsState
	When I configure it for a scan
    Then configure failed on <failed_devices> Subarray Leaf Node
    And <failed_devices> Subarray Leaf Node transition to READY Obs state
	And a subarray perform auto recovery and transition Subarray Obs State to READY
    And <failed_devices> Failure is reported on Long Running Command Result
    And <success_devices> Obs State is in READY Obs State
	Examples:
	| failed_devices  |  success_devices |
	| CSP             |  SDP,MCCS        |
	| SDP             |  CSP,MCCS        |
    | MCCS            |  CSP,SDP         |
	| CSP,SDP         |  MCCS            |
	| MCCS,SDP        |  CSP             |

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
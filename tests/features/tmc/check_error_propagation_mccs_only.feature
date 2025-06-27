@SKA_low @XTP- @XTP-
	Scenario Outline: Error Propagation Reported by TMC Low EndScan/Scan Commands for Defective MCCS Subarray
		Given the telescope is in the ON state
		And the TMC subarray is in the <obsState> observation state
		When <command> is invoked on a defective MCCS subarray
		Then the command failure is reported by subarray with error message
		Then the TMC SubarrayNode transitions to FAULT obsState
		Examples:
		            |obsState  | command |
		            |SCANNING         | ENDSCAN |
		            |SCANNING         | ENDSCAN |
		            |READY            | SCAN    |
		            |READY            | SCAN    |
		            |SCANNING         | ENDSCAN |
		            |READY            | SCAN    |


@SKA_low @XTP-73592 @XTP-84145
	Scenario Outline: Error Propagation Reported by TMC Low Configure/End/EndScan/Scan Commands for Defective MCCS Subarray
		Given the telescope is in the ON state
		And the TMC subarraynode is in the <obsState> observation state
		When <command> is invoked on a defective MCCS subarray
		Then the command failure is reported by subarray with error message
		Then the TMC SubarrayNode transitions to FAULT obsState
		Examples:
		            |obsState  | command |
		            |SCANNING         | ENDSCAN |
		            |READY            | SCAN    |
		            |IDLE            | CONFIGURE    |
		            |READY            | END    |

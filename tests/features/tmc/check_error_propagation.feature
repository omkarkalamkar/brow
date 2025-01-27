@SKA_low @XTP-73592 @XTP-73766
	Scenario Outline: Error Propagation Reported by TMC Low End/EndScan/Scan Commands for Defective Subarray
		Given the telescope is is ON state
		And the TMC subarray is in the <initialObsState> observation state
		When <command> is invoked on a <defectiveSubsystem> Subarray
		Then the command failure is reported by subarray with appropriate error message
		Then the TMC SubarrayNode remains in <stuck> obsState
		Examples:
		            |initialObsState  | command | defectiveSubsystem  |stuck|
		            |READY            | END     | CSP                  | READY |
		            |READY            | END     | MCCS                 | READY |
		            |SCANNING         | ENDSCAN | CSP                  | SCANNING |
		            |SCANNING         | ENDSCAN | MCCS                 | SCANNING |
		            |READY            | SCAN    | CSP                  | SCANNING |
		            |READY            | SCAN    | MCCS                 | SCANNING |
		            |READY            | END     | SDP                  | READY|
		            |SCANNING         | ENDSCAN | SDP                  | SCANNING|
		            |READY            | SCAN    | SDP                  | SCANNING|



@SKA_low @XTP-73592 @XTP-74764
	Scenario Outline: TimeOut Reported by TMC Low End/EndScan/Scan Commands for Defective Subarray
		Given the telescope is is ON state
		And the TMC subarray is in the <initialObsState> observation state
		When <command> is invoked on a <defectiveSubsystem> Subarray
		Then the command failure is reported by subarray with appropriate error message
		Then the TMC SubarrayNode remains in <stuck> obsState
		Examples:
		            |initialObsState  | command | defectiveSubsystem  |stuck|
		            |READY            | END     | CSP                  | READY |
		            |READY            | END     | MCCS                 | READY |
		            |SCANNING         | ENDSCAN | CSP                  | SCANNING |
		            |SCANNING         | ENDSCAN | MCCS                 | SCANNING |
		            |READY            | SCAN    | CSP                  | SCANNING |
		            |READY            | SCAN    | MCCS                 | SCANNING |
		            |READY            | END     | SDP                  | READY|
		            |SCANNING         | ENDSCAN | SDP                  | SCANNING|
		            |READY            | SCAN    | SDP                  | SCANNING|
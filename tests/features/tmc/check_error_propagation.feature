@SKA_low @XTP-73592 @XTP-73766
	Scenario Outline: Error Propagation Reported by TMC Low End/EndScan/Scan Commands for Defective Subarray
		Given the telescope is is ON state
		And the TMC subarray is in the <initialObsState> observation state
		When <command> is invoked on a defectiveSubsystem <defectiveSubsystem>
		Then the command failure is reported by subarray with error message
		Then the TMC SubarrayNode transitions to FAULT obsState
		Examples:
		            |initialObsState  | command | defectiveSubsystem  |
		            |READY            | END     | CSP                  |
		            |READY            | END     | MCCS                 |
		            |READY            | END     | SDP                  |
		            |IDLE             | CONFIGURE | CSP                |
                    |IDLE             | CONFIGURE | MCCS               |
                    |IDLE             | CONFIGURE | CSP                | 





@SKA_low @XTP-73592 @XTP-74764
	Scenario Outline: TimeOut Reported by TMC Low End/EndScan/Scan Commands for Defective Subarray
		Given the telescope is is ON state
		And the TMC subarray is in the <initialObsState> observation state
		When <command> is invoked on a <defectiveSubsystem> Subarray
		Then the command failure is reported by subarray with appropriate error message
		Then the TMC SubarrayNode transitions to FAULT obsState
		Examples:
		            |initialObsState  | command | defectiveSubsystem  |
		            |READY            | END     | CSP                  |
		            |READY            | END     | MCCS                 |
		            |READY            | END     | SDP                  |
		            |IDLE             | CONFIGURE | CSP                |
                    |IDLE             | CONFIGURE | MCCS               |
                    |IDLE             | CONFIGURE | CSP                |

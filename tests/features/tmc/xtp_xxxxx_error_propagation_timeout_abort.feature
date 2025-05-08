@XTP-28348
Scenario Outline: Error Propagation Reported by TMC Low Abort Command for Defective Subarray
    Given the telescope is in ON state
    And the TMC subarray is in the <initialObsState> observation state
    When Abort is invoked on a defective subsystem <defectiveSubsystem>
    Then the command failure is reported by subarray with an appropriate error message


Examples:
        |initialObsState  | command | defectiveSubsystem  
        |IDLE             | ABORT   | CSP                 
        |IDLE             | ABORT   | SDP               
        |READY            | ABORT   | MCCS                
        |ABORTED          | RESTART | CSP                
        |ABORTED          | RESTART | RESTART                  

@XTP-28348
Scenario Outline: TimeOut Reported by TMC Low Abort Command for Defective Subarray
		Given the telescope is is ON state
		And the TMC subarray is in the <initialObsState> observation state
		When Abort is invoked on a defective subsystem <defectiveSubsystem>
		Then the command failure is reported by subarray with appropriate error message
		
		Examples:
        | initialObsState | defectiveSubsystem |
        | IDLE            | CSP                |
        | READY           | MCCS               | 
        | IDLE            | SDP                |
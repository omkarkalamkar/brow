@XTP-73592 @XTP-73766  @tmc @Team_Sahydri
Scenario: Error Propagation Reported by TMC Low End/EndScan/Scan Commands for Defective Subarray

Given the telescope is is ON state
And the TMC subarray is in the <initialObsState> observation state
When <command> is invoked on a <defectiveSubsystem> Subarray
Then the command failure is reported by subarray with appropriate error message
Then the TMC SubarrayNode remains in <Intermediate> obsState
Examples:
            |initialObsState  | command | defectiveSubsystem  |Intermediate|
            |READY            | END     | CSP                  | READY |
            |READY            | END     | MCCS                 | READY |
            |SCANNING         | ENDSCAN | CSP                  | SCANNING |
            |SCANNING         | ENDSCAN | MCCS                 | SCANNING |
            |READY            | SCAN    | CSP                  | SCANNING |
            |READY            | SCAN    | MCCS                 | SCANNING |


Scenario: TimeOut Reported by TMC Low End/EndScan/Scan Commands for Defective Subarray

Given the telescope is is ON state
And the TMC subarray is in the <initialObsState> observation state
When <command> is invoked on a <defectiveSubsystem> Subarray
Then the command failure is reported by subarray with appropriate error message
Then the TMC SubarrayNode remains in <Intermediate> obsState
Examples:
            |initialObsState  | command | defectiveSubsystem  |Intermediate|
            |READY            | END     | CSP                  | READY |
            |READY            | END     | MCCS                 | READY |
            |SCANNING         | ENDSCAN | CSP                  | SCANNING |
            |SCANNING         | ENDSCAN | MCCS                 | SCANNING |
            |READY            | SCAN    | CSP                  | SCANNING |
            |READY            | SCAN    | MCCS                 | SCANNING |
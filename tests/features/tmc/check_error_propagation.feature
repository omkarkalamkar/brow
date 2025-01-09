@XTP-73592 @XTP-73766  @tmc @Team_Sahydri
Scenario: Error Propagation Reported by TMC Low End/EndScan/Scan Commands for Defective Subarray

Given the telescope is is ON state
And the TMC subarray is in the ready observation state
When <command> is invoked on a <defective subsystem> Subarray
Then the command failure is reported by subarray with appropriate error message
Then the TMC SubarrayNode remains in <Intermediate> obsState
Examples:
            | command | defective subsystem  |Intermediate|
            | END     | CSP                  | READY |
            | END     | MCCS                 | READY |
            | END     | SDP                  | READY|
            | ENDSCAN | CSP                  | SCANNING |
            | ENDSCAN | MCCS                 | SCANNING |
            | ENDSCAN | SDP                  | SCANNING|
            | SCAN    | CSP                  | SCANNING |
            | SCAN    | MCCS                 | SCANNING |
            | SCAN    | SDP                  | SCANNING|
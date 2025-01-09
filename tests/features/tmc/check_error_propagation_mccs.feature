@XTP-39454 @tmc @Team_himalaya
Scenario: Error Propagation Reported by TMC Low Configure Command for Defective MCCS Subarray

Given the telescope is is ON state
And the TMC subarray is in the idle observation state
When Configure command is invoked on a defective MCCS Subarray
Then the command failure is reported by subarray with appropriate error message



@XTP-73592 @XTP-73766  @tmc @Team_Sahydri
Scenario: Error Propagation Reported by TMC Low End Command for Defective MCCS Subarray

Given the telescope is is ON state
And the TMC subarray is in the ready observation state
When End command is invoked on a defective <subsystem> Subarray
Then the command failure is reported by subarray with appropriate error message
Then the TMC SubarrayNode remains in READY obsState
Examples:
            | subsystem  |
            | CSP |
            | MCCS |
            | SDP |




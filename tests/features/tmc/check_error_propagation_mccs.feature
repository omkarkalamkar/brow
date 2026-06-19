Feature: Check Error Propagation Mccs

@XTP-39454 @XTP-73592 @XTP-28348
Scenario: Error Propagation Reported by TMC Low Configure Command for Defective MCCS Subarray

Given the telescope is is ON state
And the TMC subarray is in the idle observation state
When Configure command is invoked on a defective MCCS Subarray
Then the command failure is reported by subarray with appropriate error message


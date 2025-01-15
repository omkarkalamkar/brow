Feature: Default

@XTP-29336 @XTP-73797 @XTP-28348 @XTP-28347 @XTP-29227
Scenario Outline: Configure a SDP subarray for a scan using TMC
	Given the Telescope is in ON state
	And the subarray <subarray_id> obsState is IDLE
	When I configure with <scan_type> to the subarray <subarray_id>
	Then the SDP subarray <subarray_id> transitions to READY obsState
	And SDP subarray scanType reflects correctly configured <scan_type>
	And the TMC subarray <subarray_id> transitions to READY obsState
	Examples:
	| subarray_id    |    scan_type    |
	| 1              |    target:a     |
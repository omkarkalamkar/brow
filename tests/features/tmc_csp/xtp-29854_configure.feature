@L2-3414
Feature: DELETE: Observing frequency change latency
	#TMC shall implement a change in frequency band, from when the instruction is read, till when the resulting commands are output from TMC, to within 1 second.

	#This BDD test performs TMC-CSP pairwise testing to verify Configure command flow.
	@XTP-29854 @XTP-28348 @XTP-73798 @Team_HIMALAYA @Telescope_Low
	Scenario Outline: Configure a CSP subarray for a scan using TMC
		Given the Telescope is in ON state
		And the subarray <subarray_id> obsState is IDLE
		When I configure the subarray
		Then the CSP subarray transitions to READY obsState
		And the TMC subarray transitions to READY obsState
		Examples:
		| subarray_id    |
		| 1              |
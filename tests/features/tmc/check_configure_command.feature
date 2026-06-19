Feature: Check Configure Command

@XTP-28567
Scenario: Successful Configuration of Low Telescope Subarray in TMC
	Given a TMC
	And a subarray in the IDLE obsState
	And the quality monitor reports readyToScan flag to be False
	When I configure it for a scan
	Then the subarray must be in the READY obsState
	And the quality monitor reports readyToScan flag to be True

@XTP-103071
Scenario: Successful Configuration of Low Telescope Subarray in TMC with kafka addresses
	Given a TMC
	And a subarray in the IDLE obsState
	And SDP Subarray reports receive addresses attribute with kafka addresses
	When I configure it for a scan
	Then the subarray must be in the READY obsState


@XTP-28567
Scenario: Successful Configuration of Low Telescope Subarray in TMC
	Given a TMC
	Given a subarray in the IDLE obsState
	Given a quality monitor reports readyToScan flag to be False
	When I configure it for a scan
	Then the subarray must be in the READY obsState
	Then a the the quality monitor reports readyToScan flag to be True

@XTP-103071
Scenario: Successful Configuration of Low Telescope Subarray in TMC with kafka addresses
	Given a TMC
	Given a subarray in the IDLE obsState
	Given SDP Subarray reports receive addresses attribute with kafka addresses
	When I configure it for a scan
	Then the subarray must be in the READY obsState


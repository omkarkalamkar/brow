@SKB_1056
Scenario: Successful Configuration of Low Telescope Subarray in TMC
	Given a TMC
	Given a subarray in the IDLE obsState
	When I configure it for a scan
	Then the subarray must be in the READY obsState


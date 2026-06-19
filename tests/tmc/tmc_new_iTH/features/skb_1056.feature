#Tests configuration of TMC Low Telescope for voltage scan to verify SKB-1056
@XTP-91842 @XTP-28348 @TEAM_HIMALAYA @SKB_1056
Scenario: Verify SKB-1056
	Given a TMC
	Given a subarray in the IDLE obsState
	When I configure it for a voltage scan
	Then the subarray must be in the READY obsState
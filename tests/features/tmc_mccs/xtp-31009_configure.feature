	@XTP-31009 @XTP-73799 @XTP-28348 @XTP-30488
	Scenario Outline: Configure a MCCS subarray for a scan
		Given the Telescope is in the ON state
		    And obsState of subarray <subarray_id> is IDLE
		    When I configure to the subarray using TMC
		    Then the MCCS subarray obsState must transition to the READY
		    And the TMC subarray is transitioned to READY obsState
		    Examples:
		    | subarray_id    |   
		    | 1              |
@XTP-60864 @XTP-28348
Scenario: Verify SKB-477 - with TMC entrypoint
		Given a TMC
		And Subarray Node in observation state READY
		When I invoke Scan command on Subarray Node with key subarray_id
		Then TMC SubarrayNode raises exception with ResultCode.REJECTED
		And TMC SubarrayNode remains in observation state READY
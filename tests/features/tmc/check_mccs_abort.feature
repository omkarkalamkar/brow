Feature: MCCS Abort Flow via MccsController (MCCS v6.4.0+)
    @XTP-111289 @XTP-111283
    Scenario: Verify Abort in Resourcing completes without 60-second delay via MccsController
        Given a TMC
        And central node is busy assigning resources
        And mccs subarray leafnode node is in observation state ObsState.RESOURCING
        When I invoke abort on subarray node
        Then the MccsController AbortSubarray is invoked promptly
        And the Subarray node transitions to observation state ObsState.ABORTED

    @XTP-111289 @XTP-111285
    Scenario: Verify Abort propagates error when MccsController AbortSubarray is defective
        Given a TMC
        And central node is busy assigning resources
        And mccs subarray leafnode node is in observation state ObsState.RESOURCING
        And the MccsController is set as defective
        When I invoke abort on subarray node
        Then the Subarray node transitions to observation state ObsState.FAULT

    @XTP-111289 @XTP-111286 
    Scenario: Verify Abort propagates timeout when MccsController AbortSubarray is stuck
        Given a TMC
        And central node is busy assigning resources
        And mccs subarray leafnode node is in observation state ObsState.RESOURCING
        And the MccsController AbortSubarray is set to timeout
        When I invoke abort on subarray node
        Then the Subarray node transitions to observation state ObsState.FAULT
    
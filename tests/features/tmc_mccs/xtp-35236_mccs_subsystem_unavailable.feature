Feature: MCCS Controller report the error when one of the subarray beam is unavailable
    @XTP-35236 @XTP-73592 @XTP-34276 @Team_HIMALAYA
    Scenario: MCCS Controller report the error when one of the subarray beam is unavailable
        Given a Telescope consisting of TMC,MCCS,emulated SDP and emulated CSP
        And the telescope is in ON state
        And the TMC subarray is in EMPTY obsState
        When one of the MCCS subarraybeam is made unavailable
        And I assign resources with the <subarray_id> to the TMC subarray using TMC
        Then MCCS controller should throw the error and report to TMC
        And TMC should propogate the error to client 
        And the TMC SubarrayNode remains in ObsState RESOURCING
        Examples:
        | subarray_id |
        | 1           |
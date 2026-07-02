@XTP-112768 @XTP-28348
Scenario: EndScan transitions the subarray to READY when selected subsystems have already ended scan.
    Given a TMC
    And a subarray is in SCANNING obsState
    And <subsystem> have already ended scan
    When I invoke EndScan
    Then the TMC subarray and the subsystem subarray are in READY obsState
    Examples:
        | subsystem          |
        | mccs               |
        | csp                |
        | sdp                |
        | mccs, csp          |
        | mccs, sdp          |
        | sdp, csp           |
        | mccs, sdp, csp     |


@XTP- @XTP-28348
Scenario: EndScan transitions the subarray to READY when selected subsystems have already ended scan and reject the EndScan command.
    Given a TMC
    And a subarray is in SCANNING obsState
    And <subsystem> have already ended scan
    When I invoke EndScan and it is rejected by the subsystem
    Then the TMC subarray and the subsystem subarray are in READY obsState
    Examples:
        | subsystem          |
        | mccs               |
        | csp                |
        | sdp                |
        | mccs, csp          |
        | mccs, sdp          |
        | sdp, csp           |
        | mccs, sdp, csp     |
@XTP-112768 @XTP-28348
Scenario: Successful Execution of EndScan on Low Telescope Subarray when csp, sdp, mccs subsystems have Ended Scan.
    Given a TMC
    And a subarray in SCANNING obsState
    And <subsystem> have Ended Scan
    When I invoked EndScan
    Then the TMC subarray and subsystem subarray are in READY obsState
    Examples:
        | subsystem          |
        | mccs               |
        | csp                |
        | sdp                |
        | mccs, csp          |
        | mccs, sdp          |
        | sdp, csp           |
        | mccs, sdp, csp     |
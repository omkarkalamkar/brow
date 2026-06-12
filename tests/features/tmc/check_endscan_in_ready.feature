@XTP-
Scenario: Successful Execution of EndScan on Low Telescope Subarray when some subsystem have Ended Scan.
    Given a TMC
    And a subarray in SCANNING obsState
    And <subsystem> have Ended Scan
    When I invoked EndScan
    Then the TMC subarray and subsystem subarray are in READY obsState
    Examples:

            |subsystem       |
            |mccs            |
            |csp             |
            |sdp             |
            |mccs, csp       |
            |mccs, sdp       |
            |sdp, csp        |
            |mccs, sdp, csp  |


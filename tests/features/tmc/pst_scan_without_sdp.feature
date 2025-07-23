@XTP-28568
Scenario: Successful Execution of PST Scan without SDP configuration on Low Telescope Subarray in TMC
    Given a TMC
    Given a subarray in READY obsState
    When I execute PST scan for a given period
    Then the subarray must be in the SCANNING obsState until finished

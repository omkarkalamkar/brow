@XTP-106355
Scenario: Successful Execution of Abort Command on Low Telescope Subarray in TMC
    Given a TMC
    And a subarray in READY obsState
    When I command it to scan for a given period and trigger Abort
    Then the Subarray transitions to ABORTED obsState

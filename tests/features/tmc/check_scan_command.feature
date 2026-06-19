Feature: Check Scan Command

@XTP-28568
Scenario: Successful Execution of Scan Command on Low Telescope Subarray in TMC
    Given a TMC
    Given a subarray in READY obsState
    When I command it to scan for a given period
    Then the subarray must be in the SCANNING obsState until finished

@XTP-109561
Scenario: Successful Execution of early MCCS Scan scenario on Low Telescope Subarray
    Given a TMC
    And a subarray in READY obsState
    And a Scan started on MCCS subarray via leaf node
    When I command TMC Subarray to scan for a given period
    Then the subarray must be in the SCANNING obsState until a scan finished

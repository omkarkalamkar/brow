Feature: TMC closes ongoing commands on Restart after Fault

  Scenario: TMC closes ongoing commands on Restart after Fault
    Given a Subarray in IDLE obsState with resources assigned
    And the CSP Subarray is set to defective
    When I Configure the Subarray
    Then the Subarray transitions to observation state ObsState.FAULT
    When I Restart the Subarray
    Then the Restart command completes and the Configure command is aborted



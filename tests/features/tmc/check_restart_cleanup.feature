Feature: TMC closes ongoing commands on Restart after Fault

  Scenario: Restart when Subarray is in obsState FAULT with CSP defective during Configure
    Given a Subarray in IDLE obsState with resources assigned
    And the CSP Subarray is set to defective
    And I Configure the Subarray
    And the Subarray transitions to observation state ObsState.FAULT
    When I Restart the Subarray
    Then the Configure command is aborted
    And the Restart command is completed
    And the Subarray node goes to obsState EMPTY

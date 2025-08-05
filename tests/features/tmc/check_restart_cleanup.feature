Feature: TMC closes ongoing commands on Restart after Fault
  @XTP-86746 
  Scenario: Restart when Subarray is in obsState FAULT with CSP defective during Configure
    Given a Subarray in IDLE obsState with resources assigned
    And the CSP Subarray is set to defective
    And I Configure the Subarray
    And the Subarray transitions to observation state ObsState.FAULT
    When I Restart the Subarray
    Then the Configure command is aborted
    And the Restart command is completed
    And the Subarray node goes to obsState EMPTY

  @XTP-86748
  Scenario: Restart when Subarray is in obsState FAULT with CSP defective during AssignResources
    Given a Subarray in EMPTY obsState with no resources assigned
    And the CSP Subarray is set to defective
    And I Assign resources to the Subarray
    And the Subarray transitions to observation state ObsState.FAULT
    When I Restart the Subarray
    Then the AssignResources command is aborted
    And the Restart command is completed
    And the Subarray node goes to obsState EMPTY

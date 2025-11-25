Feature: Resource Monitor updates for LOW
  Verify that ResourceMonitor device attributes update when SubarrayNode and MCCS controller attributes change.
  @XTP-93546  @XTP-93550 @XTP-28348 
  Scenario: Test Resource Monitor updates when SubarrayNode and MCCS controller attributes change
    Given the LOW SubarrayNode and ResourceMonitor devices are available
    When the SubarrayNode assignedResources attribute changes after AssignResources command
    Then the ResourceMonitor attributes should reflect assigned resources
    When the SubarrayNode assignedResources attribute changes after ReleaseResources command
    Then the ResourceMonitor attributes should reflect released resources
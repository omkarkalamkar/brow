Feature: Resource Monitoring updates for LOW
  Verify that ResourceMonitoring device attributes update when SubarrayNode attributes change.
  @XTP-93546  @XTP-93550 @XTP-28348 
  @SKA_tmc_low
  Scenario: Test Resource Monitoring updates when SubarrayNode attributes change
    Given the LOW SubarrayNode and ResourceMonitoring devices are available
    When the SubarrayNode assignedResources attribute changes after AssignResources command
    Then the ResourceMonitoring stationsData attribute should reflect the change
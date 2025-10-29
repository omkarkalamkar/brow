Feature: Resource Monitoring updates for LOW
  Verify that ResourceMonitoring device attributes update when SubarrayNode attributes change.

  @SKA_tmc_low
  Scenario: Test Resource Monitoring updates when SubarrayNode attributes change
    Given the LOW SubarrayNode and ResourceMonitoring devices are available
    When a change is triggered on the SubarrayNode assigned resources
    Then the ResourceMonitoring stationsData attribute should reflect the change
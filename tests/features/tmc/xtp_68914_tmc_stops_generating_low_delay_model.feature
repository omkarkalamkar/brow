#Test case to verify TMC generates delay values
@XTP-68914 @XTP-73581 @XTP-73579 @XTP-28348 @Team_SAHYADRI
Scenario: TMC generates delay values
    Given the telescope is in ON state
    And subarray is configured and starts generating delay values
    When I end the observation
    Then CSP Subarray Leaf Node stops generating delay values

@XTP-68914 @XTP-73579 @XTP-73581
Scenario: TMC generates delay values
    Given the telescope is in ON state
    And subarray is configured and starts generating delay values
    When I end the observation
    Then CSP Subarray Leaf Node stops generating delay values

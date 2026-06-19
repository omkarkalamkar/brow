Feature: Xtp 68913 Tmc Stops Generating Delays Pst Beams

@XTP-68913 @XTP-73581 @XTP-73579
Scenario: TMC stops generating delay values for PST Beams
    Given the telescope is in ON state
    And subarray is configured and generating delay values for PST Beams
    When I end the observation
    Then CSP Subarray Leaf Node stops generating delay values for PST Beams
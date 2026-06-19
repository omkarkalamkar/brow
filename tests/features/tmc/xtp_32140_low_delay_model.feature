@XTP-32140 @XTP-73581 @XTP-73579 @XTP-28348
Scenario: TMC generates delay values
    Given the telescope is in ON state
    And subarray is in obsState IDLE
    When I configure the subarray
    Then CSP Subarray Leaf Node starts generating delay values for <attribute>
    
    Examples:
        | attribute               |
        | delayModelStationBeam01 |
        | delayModelStationBeam02 |
        | delayModelStationBeam03 |
        | delayModelStationBeam04 |
        | delayModelStationBeam05 |
        | delayModelStationBeam06 |
        | delayModelStationBeam07 |
        | delayModelStationBeam08 |
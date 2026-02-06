@XTP-101098 @XTP-98925 @XTP-28348 @TEAM_HIMALAYA
Scenario: TMC generates delay values for different station beams
    Given the telescope is in the ON state
    And subarray is in obsState IDLE
    When I configure the subarray with PSS beams using different station beams
    Then CSP Subarray Leaf Node generates delay values only for used station beams

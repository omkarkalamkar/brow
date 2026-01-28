@XTP_STN_BEAM_DELAY
Scenario: TMC generates delay values for different station beams
    Given the telescope is in the ON state
    And subarray is in obsState IDLE
    When I configure the subarray with PSS beams using different station beams
    Then CSP Subarray Leaf Node generates delay values only for used station beams
    And CSP Subarray Leaf Node does not generate delay values for unused station beams

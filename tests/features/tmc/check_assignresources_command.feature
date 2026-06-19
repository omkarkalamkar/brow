@XTP-65635
Scenario: Assign resources to Low subarray
    Given the telescope is in the ON state
    And subarray is in the EMPTY ObsState
    When I assign resources to the subarray with <assign_json>
    Then the TMC, CSP, SDP, and MCCS subarrays transition to the RESOURCING obsState
    And the TMC, CSP, SDP, and MCCS subarrays transition to the IDLE obsState
    Examples:
        | assign_json                |
        | assign_resources_low       |
        | assign_resources_low_v4_0  |

@XTP-84149 @XTP-83574 @TEAM_HIMALAYA
Scenario: Assign resources to Low subarray if one subarray in adminmode ENGINEERING
    Given the telescope is in the ON state
    And subarray is in the EMPTY ObsState
    And sdp subarray is in adminmode ENGINEERING
    When I assign resources to the subarray with <assign_json>
    Then the TMC, CSP, SDP, and MCCS subarrays transition to the RESOURCING obsState
    And the TMC, CSP, SDP, and MCCS subarrays transition to the IDLE obsState
    Examples:
        | assign_json                |
        | assign_resources_low       |
        | assign_resources_low_v4_0  |
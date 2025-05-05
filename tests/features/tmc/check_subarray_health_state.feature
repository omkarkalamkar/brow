Feature: Subarray Node Health State

  Scenario Outline: Subarray health reflects correct combined state of CSP, SDP, and MCCS
    Given CSP health is <csp_health>
    And SDP health is <sdp_health>
    And MCCS health is <mccs_health>
    When health states are applied
    Then the Subarray Node health state should be <expected_health>

    Examples:
      | csp_health | sdp_health | mccs_health | expected_health |
      | OK         | OK         | OK          | OK              |
      | OK         | OK         | FAILED      | FAILED          |
      | OK         | FAILED     | OK          | FAILED          |
      | FAILED     | OK         | OK          | FAILED          |
      | UNKNOWN    | OK         | OK          | UNKNOWN         |
      | OK         | UNKNOWN    | OK          | UNKNOWN         |
      | OK         | OK         | UNKNOWN     | UNKNOWN         |
      | DEGRADED   | OK         | OK          | DEGRADED        |
      | OK         | DEGRADED   | OK          | DEGRADED        |
      | OK         | OK         | DEGRADED    | DEGRADED        |
      | DEGRADED   | FAILED     | OK          | FAILED          |
      | UNKNOWN    | DEGRADED   | OK          | DEGRADED        |
      | DEGRADED   | UNKNOWN    | OK          | DEGRADED        |
      | OK         | UNKNOWN    | DEGRADED    | DEGRADED        |
      | FAILED     | UNKNOWN    | OK          | FAILED          |

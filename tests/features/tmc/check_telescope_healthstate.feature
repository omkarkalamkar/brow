Feature: Telescope Health State evaluation
  Verify that the CentralNode sets the correct telescopeHealthState based on the health states of its master components.

  Scenario: CentralNode reports FAILED telescopeHealthState
    Given the telescope is ON
    And CSP master health is <csp_state>
    And SDP master health is <sdp_state>
    And MCCS master health is <mccs_state>
    When health states are applied
    Then the telescopeHealthState should be FAILED

    Examples:
      | csp_state | sdp_state | mccs_state |
      | OK        | FAILED    | OK         |
      | FAILED    | OK        | OK         |
      | OK        | OK        | FAILED     |
      | OK        | FAILED    | FAILED     |
      | FAILED    | FAILED    | OK         |
      | FAILED    | OK        | FAILED     |
      | FAILED    | FAILED    | FAILED     |

  Scenario: CentralNode reports OK telescopeHealthState
    Given the telescope is ON
    And all master and subarray components have OK health
    When health states are applied
    Then the telescopeHealthState should be OK
    And the subarray healthState should be OK

  Scenario: CentralNode reports DEGRADED telescopeHealthState
    Given the telescope is ON
    And CSP master health is <csp_state>
    And SDP master health is <sdp_state>
    And MCCS master health is <mccs_state>
    When health states are applied
    Then the telescopeHealthState should be DEGRADED

    Examples:
      | csp_state | sdp_state | mccs_state |
      | OK        | DEGRADED  | OK         |
      | DEGRADED  | OK        | OK         |
      | OK        | OK        | DEGRADED   |
      | DEGRADED  | DEGRADED  | OK         |
      | OK        | DEGRADED  | DEGRADED   |

  Scenario: CentralNode reports UNKNOWN telescopeHealthState
    Given the telescope is ON
    And CSP master health is <csp_state>
    And SDP master health is <sdp_state>
    And MCCS master health is <mccs_state>
    When health states are applied
    Then the telescopeHealthState should be UNKNOWN

    Examples:
      | csp_state | sdp_state | mccs_state |
      | OK        | UNKNOWN   | OK         |
      | UNKNOWN   | OK        | OK         |
      | OK        | OK        | UNKNOWN    |
      | UNKNOWN   | UNKNOWN   | OK         |
      | UNKNOWN   | OK        | UNKNOWN    |

Feature: Subarray Node Health info

    @XTP-102560 @XTP-28348
    Scenario Outline: Subarray reflects correct healthinfo of CSP, SDP, and MCCS subarrays
        Given CSP health is <csp_health>
		And SDP health is <sdp_health>
		And MCCS health is <mccs_health>
		When health states are applied
		Then the Subarray Node health state should be <expected_health>
		And the Subarray Node healthinfo should be <expected_health_info>

        Examples:
          | csp_health | sdp_health | mccs_health | expected_health | expected_health_info                                                                 |
          | OK         | OK         | OK          | OK              | EMPTY                                                                                |
          | OK         | FAILED     | OK          | FAILED          | SDP Subarray Health State: FAILED                                                    |
          | FAILED     | OK         | OK          | FAILED          | CSP Subarray Health State: FAILED                                                    |
          | OK         | OK         | FAILED      | FAILED          | MCCS Subarray Health State: FAILED                                                   |
          | UNKNOWN    | OK         | OK          | UNKNOWN         | CSP Subarray Health State: UNKNOWN                                                   |
          | OK         | UNKNOWN    | OK          | UNKNOWN         | SDP Subarray Health State: UNKNOWN                                                   |
          | OK         | OK         | UNKNOWN     | UNKNOWN         | MCCS Subarray Health State: UNKNOWN                                                  |
          | DEGRADED   | OK         | OK          | DEGRADED        | CSP Subarray Health State: DEGRADED                                                  |
          | OK         | DEGRADED   | OK          | DEGRADED        | SDP Subarray Health State: DEGRADED                                                  |
          | OK         | OK         | DEGRADED    | DEGRADED        | MCCS Subarray Health State: DEGRADED                                                 |
          | DEGRADED   | FAILED     | OK          | FAILED          | CSP Subarray Health State: DEGRADED, SDP Subarray Health State: FAILED               |
          | UNKNOWN    | DEGRADED   | OK          | DEGRADED        | CSP Subarray Health State: UNKNOWN, SDP Subarray Health State: DEGRADED              |
          | DEGRADED   | UNKNOWN    | OK          | DEGRADED        | CSP Subarray Health State: DEGRADED, SDP Subarray Health State: UNKNOWN              |
          | OK         | UNKNOWN    | DEGRADED    | DEGRADED        | SDP Subarray Health State: UNKNOWN, MCCS Subarray Health State: DEGRADED             |
          | FAILED     | UNKNOWN    | OK          | FAILED          | CSP Subarray Health State: FAILED, SDP Subarray Health State: UNKNOWN                |
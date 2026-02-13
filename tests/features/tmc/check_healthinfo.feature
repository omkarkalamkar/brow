Feature: Subarray Node Health info

	@XTP- @XTP-
	Scenario Outline: Subarray health reflects correct healthinfo of CSP, SDP, and MCCS subarrays
		Given CSP health is <csp_health>
		And SDP health is <sdp_health>
		And MCCS health is <mccs_health>
		When health states are applied
		Then the Subarray Node health state should be <expected_health>
		And the Subarray Node healthinfo should be <expected_health_info>

		Examples:
		  | csp_health | sdp_health | mccs_health | expected_health |expected_health_info|
		  | OK         | OK         | OK          | OK              |something           |
		  | OK         | FAILED     | OK          | FAILED          |something           |
		  | FAILED     | OK         | OK          | FAILED          |something           |
		  | OK         | OK         | FAILED      | FAILED          |something           |
		  | UNKNOWN    | OK         | OK          | UNKNOWN         |something           |
		  | OK         | UNKNOWN    | OK          | UNKNOWN         |something           |
		  | OK         | OK         | UNKNOWN     | UNKNOWN         |something           |
		  | DEGRADED   | OK         | OK          | DEGRADED        |something           |
		  | OK         | DEGRADED   | OK          | DEGRADED        |something           |
		  | OK         | OK         | DEGRADED    | DEGRADED        |something           |
		  | DEGRADED   | FAILED     | OK          | FAILED          |something           |
		  | UNKNOWN    | DEGRADED   | OK          | DEGRADED        |something           |
		  | DEGRADED   | UNKNOWN    | OK          | DEGRADED        |something           |
		  | OK         | UNKNOWN    | DEGRADED    | DEGRADED        |something           |
		  | FAILED     | UNKNOWN    | OK          | FAILED          |something           |
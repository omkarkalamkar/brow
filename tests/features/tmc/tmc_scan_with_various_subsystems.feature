Feature: Tmc Scan With Various Subsystems

@XTP-87343
Scenario: Successful Execution of TMC Scan with subsystems configuration provided in input JSON
    Given a TMC
    And I assign the resources with JSON <assignjson>
    And I configure the subarray with JSON <configurejson>
    When I execute scan with <subsystems> for a given period
    Then the subarray must be in the SCANNING obsState until finished
    And the subarray is taken to the initial obsState EMPTY

    Examples:
		| subsystems           | assignjson                    | configurejson                   |
		| pst_scan_without_sdp | pst_assign_with_csp_mccs_low  | pst_configure_with_csp_mccs_low |
		| scan_without_csp     | assign_with_sdp_mccs_low      | configure_with_sdp_mccs_low     |
		| scan_with_only_sdp   | assign_with_only_sdp_low      | configure_with_only_sdp_low     |
		| scan_with_only_mccs  | assign_with_only_mccs_low     | configure_with_only_mccs_low    |

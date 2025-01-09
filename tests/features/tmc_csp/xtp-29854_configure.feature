@XTP-29855 @XTP-29682 @XTP-73798 @tmc_csp
Scenario: Configure CSP subarray using TMC
    Given the Telescope is in ON state
    And the subarray <subarray_id> obsState is IDLE
    When I configure the subarray
    Then the CSP subarray transitions to READY obsState
    And the TMC subarray transitions to READY obsState
    Examples:
        | subarray_id    |
        | 1              |
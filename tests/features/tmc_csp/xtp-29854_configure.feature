
#This BDD test performs TMC-CSP pairwise testing to verify Configure command flow.
@XTP-73798 @XTP-29854  @Team_HIMALAYA @Telescope_Low
Scenario Outline: Configure a CSP subarray for a scan using TMC
    Given the Telescope is in ON state
    And the subarray <subarray_id> obsState is IDLE
    When I configure the subarray
    Then the CSP subarray transitions to READY obsState
    And the TMC subarray transitions to READY obsState
    Examples:
    | subarray_id    |
    | 1              |

Feature: TMC performs Configuration on MCCS subsystem
@XTP-31009 @XTP-30488 @Team_HIMALAYA @tmc_mccs
Scenario: Configure a MCCS subarray for a scan
    Given the Telescope is in the ON state
    And obsState of subarray <subarray_id> is IDLE
    When I configure to the subarray using TMC
    Then the MCCS subarray obsState must transition to the READY
    And the TMC subarray is transitioned to READY obsState
    Examples:
    | subarray_id    |   
    | 1              |  
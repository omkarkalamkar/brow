@SKA_tmc_low_restart @XTP-74377
Scenario Outline: Verify SKB-646
    Given ReleaseAllResource completed on CSP, MCCS, SDP Subarray
    And TMC Subarray is in RESOURCING Observation State
    When I invoke init command on TMC Subarray
    And wait for TMC Subarray Observation State transition to EMPTY
    And Assign Resources to TMC Subarray
    Then TMC Subarray must be in IDLE Observation State
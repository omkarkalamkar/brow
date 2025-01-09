@XTP-34895 @XTP-29227 @XTP-73574 @tmc_sdp_unhappy_path @Team_himalaya
Scenario Outline: Verify TMC TelescopeHealthState transition based on SDP Controller HealthState
    Given a Telescope consisting of TMC, SDP, simulated CSP and simulated MCCS 
    When The <devices> health state changes to <health_state> 
    Then the telescope health state is <telescope_health_state>
    Examples:
    | devices                       | health_state               | telescope_health_state |
    | sdp controller                | DEGRADED                   |   DEGRADED             |
    | mccs master,sdp controller    | OK,DEGRADED                |   DEGRADED             |
    | csp master,sdp controller     | OK,DEGRADED                |   DEGRADED             |
    | mccs master,sdp controller    | DEGRADED,DEGRADED          |   DEGRADED             |
    | csp master,sdp controller     | DEGRADED,DEGRADED          |   DEGRADED             |
@XTP-60161 @XTP-28348
Scenario: Verify SKB-476
    Given a TMC
    And subarray node is in observation state IDLE
    When I invoke configure command without <key> in csp configure json
    Then subarray node transitions to observation state READY
    Examples:
    | key         |
    | timing_beams|
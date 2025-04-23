@XTP-79465 @XTP-28347 @TEAM_HIMALAYA @SKB-837
Scenario: Fallback to attribute‑read when no change event for attribute receiveAddresses
    Given subarray is in observation state IDLE
    And change event data is EMPTY for attribute receiveAddresses
    When I configure the subarray
    Then subarray node transitions to observation state READY

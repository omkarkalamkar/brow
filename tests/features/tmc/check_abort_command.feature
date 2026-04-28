@XTP-28864
Scenario: TMC validates Abort Command
    Given a Subarray in <obs_state> obsState
    When I Abort it
    Then the Subarray transitions to ABORTED obsState

    Examples:
    | obs_state   |
    | IDLE        |
    | READY       |
    | SCANNING    |

@XTP-29003
Scenario: TMC validates Abort Command in intermediate obsState
    Given a Subarray in intermediate obsState <obs_state>
    When I Abort it
    Then the Subarray transitions to ABORTED obsState

    Examples:
    | obs_state         |
    | RESOURCING        |
    | CONFIGURING       |

@XTP-28865
Scenario: TMC executes Abort Command in EMPTY obsState.
    Given a Subarray in EMPTY obsState
    When I Abort it
    Then TMC raises exception
    And the Subarray remains in obsState EMPTY
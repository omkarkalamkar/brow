@XTP-73592 @XTP-28348
@XTP-73592 @XTP-28348
Scenario Outline: TMC subarray reports errors during interactions with CSP or SDP subarray
    Given the telescope is in ON state
    And TMC subarray is in ObsState EMPTY
    When the SDP subarray is in an abnormal state    
    And I issue the AssignResources command to the TMC
    Then the Error is reported by the TMC
@SKA_low @XTP-76912 @XTP-73592 @XTP-28348
Scenario Outline: Error Propagation Reported by TMC Low AssignResources Command for Defective MCCS Controller
    Given the telescope is in ON state
    And TMC subarray is in ObsState EMPTY
    When the MCCS controller is in an abnormal state    
    And I issue the AssignResources command to the TMC
    Then the Error is reported by the TMC
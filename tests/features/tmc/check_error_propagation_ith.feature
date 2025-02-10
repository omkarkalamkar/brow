@XTP-73592 @XTP-28348
Scenario Outline: TMC subarray reports errors during interactions with CSP or SDP subarray
    Given the telescope is in ON state
    And TMC subarray is in ObsState <obs_state>
    When the <subarray> subarray is in an abnormal state    
    And I issue the <command> command to the TMC
    Then the Error is reported by the TMC


    Examples:
      | subarray       | command         	 | obs_state |
      | CSP            | AssignResources 	 | EMPTY     |
      | SDP            | AssignResources  	 | EMPTY     |
      | CSP            | ReleaseResources 	 | IDLE      |
      | SDP            | ReleaseResources	 | IDLE      |
      | CSP            | Configure         	 | IDLE      |
      | SDP        	   | Configure           | IDLE      |
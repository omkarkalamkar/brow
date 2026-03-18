@XTP-28568
Scenario: Successful Execution of Scan Command on Low Telescope Subarray in TMC
    Given a TMC
    Given a subarray in READY obsState
    When I command it to scan for a given period
    Then the subarray must be in the SCANNING obsState until finished


Scenario: Execute Scan Lifecycle with max resources
    
    Given a Low telescope in ON state
    And a subarray in READY obsState
    And the delay for the 8 station beams, PSS beams, and PST beams are updated
    When I command it to scan for a given period
    Then after the scan duration they transition back to READY observation state
    
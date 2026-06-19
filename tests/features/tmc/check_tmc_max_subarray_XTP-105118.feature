Feature: Check Tmc Max Subarray Xtp-105118

@XTP-28568 @XTP-105118
Scenario: Execute Scan Lifecycle with max resources
    
    Given a Low telescope in ON state
    And a subarray in READY obsState
    And the delay for the 8 station beams, PSS beams, and PST beams are updated
    When I command it to scan for a given period
    Then after the scan duration they transition back to READY observation state
    
Feature: Scan command with ScanStartTime


    Scenario: Successful execution of Scan command with ScanStartTime

        Given a TMC
        And a subarray in READY obsState
        When I command it to scan with a future ScanStartTime
        Then the subarray shall enter SCANNING obsState
        And the subarray shall still be in SCANNING before the expected EndScan time
        And the subarray shall automatically transition to READY
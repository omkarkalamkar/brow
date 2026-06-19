#This test verifies SKB-512.
@XTP-65055
Scenario: TMC executes EndScan on other sub-systems even if one sub-system goes to FAULT
    Given a TMC in SCANNING obsState
    When I invoke EndScan command and a sub-system goes to FAULT
    Then the command is executed successfully on other sub-systems

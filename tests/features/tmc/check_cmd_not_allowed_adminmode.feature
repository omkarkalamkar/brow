Feature: Command execution according to adminmode of subsystem devices
    Scenario: Command not allowed from CentralNode when subsystem adminmode is OFFLINE/NOT_FITTED
        Given a Low TMC
        When the adminmode of subsystem controller <subsystem> is <adminmode>
        And I invoke command <command> on centralnode
        Then the centralnode rejects the command 

        Examples:
        | subsystem           | adminmode    | command         |
        | cspcontroller       | OFFLINE      | AssignResources |
        | cspcontroller       | NOT_FITTED   | AssignResources |
        | cspcontroller       | OFFLINE      | ReleaseResources|
        | sdpcontroller       | NOT_FITTED   | ReleaseResources|
        | mccscontroller      | OFFLINE      | On              |
        | mccscontroller      | NOT_FITTED   | Off             |
        | sdpcontroller       | OFFLINE      | On              |

    Scenario: SubarrayNode command not allowed from SubarrayNode when subsystem adminmode is OFFLINE/NOT_FITTED
        Given a Low TMC
        When the adminmode of subsystem subarray <subsystem> is <adminmode>
        And I invoke command <command> on subarraynode
        Then the subarraynode rejects the command

        Examples:
        | subsystem         | adminmode    | command   |
        | cspsubarray       | OFFLINE      | Configure |
        | cspsubarray       | NOT_FITTED   | Scan      |
        | sdpsubarray       | OFFLINE      | End       |
        | sdpsubarray       | NOT_FITTED   | EndScan   |
        | mccssubarray      | OFFLINE      | Configure |
        | mccssubarray      | NOT_FITTED   | End       |
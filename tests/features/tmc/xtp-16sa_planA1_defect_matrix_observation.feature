Feature: 16-subarray observation with plan PlanA1, injected defects and recovery

    # This feature drives 16 subarrays through the observation lifecycle using a
    # single plan (PlanA1) and injects per-(subarray, command) defects.
    #
    # PlanName must reference a plan defined in:
    #   tests/features/tmc/tmc_observation_plans.feature
    #
    # DefectMatrix and RecoverMatrix are JSON lists of objects.
    #
    # DefectMatrix item schema:
    #   {"subarray_id": <int>, "command": <str>, "defect": <str>}
    #
    # RecoverMatrix item schema:
    #   {"subarray_id": <int>, "command": <str>, "recovery": <str>}
    #
    # Subarrays not present in DefectMatrix are treated as NORMAL.

    @XTP-XXXXX @SKA_tmc_low_multiple_subarrays @defect_injection
    Scenario Outline: Run 16-subarray observation with injected defects and recovery
        Given <SNCount> subarrays are in the EMPTY ObsState
        And the telescope is in the ON state

        When I run observations for all subarrays using plan <PlanName> with defects <DefectMatrix>
        Then healthy subarrays complete observation cycle

        When I try recovery as per <RecoverMatrix>
        Then recoverable subarrays transition back to <RecoveredObsState>

        Examples:
            | SNCount | PlanName | RecoveredObsState | DefectMatrix | RecoverMatrix |
            | 16 | PlanA1 | EMPTY | [{"subarray_id":4,"command":"AssignResources","defect":"ERROR_PROPAGATION_DEFECT"},{"subarray_id":7,"command":"Configure","defect":"ERROR_PROPAGATION_DEFECT"},{"subarray_id":9,"command":"Scan","defect":"ERROR_PROPAGATION_DEFECT"},{"subarray_id":5,"command":"AssignResources","defect":"FAILED_DEFECT"},{"subarray_id":8,"command":"Configure","defect":"INTERMEDIATE_CONFIGURING_OBS_STATE_DEFECT"},{"subarray_id":10,"command":"Scan","defect":"TIMEOUT_DEFECT"},{"subarray_id":11,"command":"Scan","defect":"COMMAND_NOT_ALLOWED_DEFECT"},{"subarray_id":12,"command":"Configure","defect":"INTERMEDIATE_FAULT_OBS_STATE_DEFECT"}] | [{"subarray_id":4,"command":"AssignResources","recovery":"RESTART"},{"subarray_id":7,"command":"Configure","recovery":"RESTART"},{"subarray_id":9,"command":"Scan","recovery":"ABORT_THEN_RESTART"},{"subarray_id":5,"command":"AssignResources","recovery":"RESTART"},{"subarray_id":10,"command":"Scan","recovery":"RESTART"},{"subarray_id":12,"command":"Configure","recovery":"RESTART"}] |

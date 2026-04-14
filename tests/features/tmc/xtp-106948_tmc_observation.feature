
Feature: Multi-subarray observation

    # This feature is intentionally parameterized so tests can control:
    # - how many subarrays participate (SNCount)
    # - which resource allocation plan(s) to apply (PlanMap)
    #
    # NOTE:
    # - The PlanMap value is a JSON map of subarray id -> plan name
    #   (e.g. {"1":"PlanA","2":"PlanB"}). Each plan name maps to a plan
    #   definition stored in `tmc_observation_plans.feature`.

    @XTP-106948 @XTP-28348 @TEAM_SAHYADRI
    Scenario Outline: Execute observation using <SNCount> subarrays with plan map <PlanMap>
        Given the telescope is in the ON state
        And <SNCount> subarrays are in the EMPTY ObsState
        And I assign resources using plan map <PlanMap>
        And I configure subarrays using plan map <PlanMap>
        And the Subarrays are configured successfully with correct delaymodels
        When I scan on all configured subarrays
        Then the involved subarrays transition to SCANNING and back to READY
        And I end the observations on all involved subarrays
        And I release resources from all involved subarrays

        Examples:
            | SNCount | PlanMap                                                                                                                                                                                                                                                     |
            | 16      | {"1":"PlanA1","2":"PlanA2","3":"PlanA3","4":"PlanB","5":"PlanA5","6":"PlanA6","7":"PlanA7","8":"PlanA8","9":"PlanA9","10":"PlanA10","11":"PlanA11","12":"PlanA12","13":"PlanA13","14":"PlanA14","15":"PlanA15","16":"PlanA16"} |
            | 10      | {"1":"PlanA","2":"PlanB","3":"PlanC","4":"PlanD","5":"PlanA5","6":"PlanA6","7":"PlanA7","8":"PlanA8","9":"PlanA9","10":"PlanA10"}                                                                                           |

    Scenario Outline: Execute long sequence on 16 Subarrays
        Given the telescope is in the ON state
        And <SNCount> subarrays are in the EMPTY ObsState
        And I assign resources using plan map <PlanMap>
        And I configure subarrays using plan map <PlanMap>
        And the Subarrays are configured successfully with correct delaymodels
        And I scan on all configured subarrays
        And the involved subarrays transition to SCANNING and back to READY
        And I end the observations on all involved subarrays
        And I release resources from all involved subarrays
        When I reassign all subarrays.
        And I reconfigure all subarrays.
        And I scan on all configured subarrays
        Then the involved subarrays transition to SCANNING and back to READY
        And I end the observations on all involved subarrays
        And I release resources from all involved subarrays

        Examples:
            | SNCount | PlanMap                                                                                                                                                                                                                                                     |
            | 16      | {"1":"PlanA1","2":"PlanA2","3":"PlanA3","4":"PlanB","5":"PlanA5","6":"PlanA6","7":"PlanA7","8":"PlanA8","9":"PlanA9","10":"PlanA10","11":"PlanA11","12":"PlanA12","13":"PlanA13","14":"PlanA14","15":"PlanA15","16":"PlanA16"} |


    Scenario Outline: Execute long sequence Scan on 16 Subarrays
        Given the telescope is in the ON state
        And <SNCount> subarrays are in the EMPTY ObsState
        And I assign resources using plan map <PlanMap>
        And I configure subarrays using plan map <PlanMap>
        And the Subarrays are configured successfully with correct delaymodels
        And I issue scan on all configured subarrays
        And the involved subarrays transition to SCANNING and back to READY
        When I issue scan on all subarray with new scan_id
        Then the involved subarrays transition to SCANNING and back to READY
        And I end the observations on all involved subarrays
        And I release resources from all involved subarrays

        Examples:
            | SNCount | PlanMap                                                                                                                                                                                                                                                     |
            | 16      | {"1":"PlanA1","2":"PlanA2","3":"PlanA3","4":"PlanB","5":"PlanA5","6":"PlanA6","7":"PlanA7","8":"PlanA8","9":"PlanA9","10":"PlanA10","11":"PlanA11","12":"PlanA12","13":"PlanA13","14":"PlanA14","15":"PlanA15","16":"PlanA16"} |
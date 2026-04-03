
Feature: Multi-subarray observation

    # This feature is intentionally parameterized so tests can control:
    # - how many subarrays participate (SNCount)
    # - which resource allocation plan(s) to apply (PlanMap)
    #
    # NOTE:
    # - The PlanMap value is a JSON map of subarray id -> plan name
    #   (e.g. {"1":"PlanA","2":"PlanB"}). Each plan name maps to a plan
    #   definition stored in `tmc_observation_plans.feature`.

    Scenario Outline: Execute observation using <SNCount> subarrays with plan map <PlanMap>
        Given the telescope is in the ON state
        And <SNCount> subarrays are in the EMPTY ObsState
        And I assign resources using plan map <PlanMap>
        And I configure subarrays using plan map <PlanMap>
        And the Subarrays are configured successfully

        Examples:
            | SNCount | PlanMap                                                                                                                                                                                                                                                     |
            | 16      | {"1":"PlanA1","2":"PlanA2","3":"PlanA3","4":"PlanA4","5":"PlanA5","6":"PlanA6","7":"PlanA7","8":"PlanA8","9":"PlanA9","10":"PlanA10","11":"PlanA11","12":"PlanA12","13":"PlanA13","14":"PlanA14","15":"PlanA15","16":"PlanA16"} |


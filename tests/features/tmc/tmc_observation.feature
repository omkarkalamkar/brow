
Feature: Multi-subarray observation

    # This feature is intentionally parameterized so tests can control:
    # - how many subarrays participate (SNCount)
    # - which resource allocation plan(s) to apply (PlanMap)
    #
    # NOTE:
        # - The PlanMap value is a JSON map of subarray id -> plan name
        #   (e.g. {"1":"PlanA","2":"PlanB"}). Each plan name maps to a plan
        #   definition stored in `tmc_observation_plans.feature`.
    #   stored in a separate feature file: `tmc_observation_plans.feature`.

    Scenario Outline: Execute observation using <SNCount> subarrays with plan map <PlanMap>
        Given the telescope is in the ON state
        And <SNCount> subarrays are in the EMPTY ObsState
        And I assign resources using plan map <PlanMap>
        And I configure subarrays using plan map <PlanMap>
        
        Examples:
            | SNCount | PlanMap                                                                                                                                                                           |
            | 16      | {"1":"PlanA","2":"PlanA","3":"PlanA","4":"PlanA","5":"PlanA","6":"PlanA","7":"PlanA","8":"PlanA","9":"PlanA","10":"PlanA","11":"PlanA","12":"PlanA","13":"PlanA","14":"PlanA","15":"PlanA","16":"PlanA"} |

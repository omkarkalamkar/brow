"""Test Subarray Health State"""

import pytest
from ska_tango_base.control_model import HealthState

from tests.resources.test_harness.helpers import get_device_simulators


class TestSubarrayHealthState:
    """This class implement test cases to verify HealthState
    of Subarray Node.
    This tests implement rows of following excel sheet
    https://docs.google.com/spreadsheets/d/1XbNb8We7fK-EhmOcw3S-h0V_Pu-WAfPTkEd13MSmIns/edit#gid=747888622
    """

    @pytest.mark.aki
    def test_health_state_ok(
        self, subarray_node_low, simulator_factory, event_recorder
    ):
        """Test for healthstate ok"""
        # Row 1
        (
            csp_sim,
            sdp_sim,
            mccs_sim,
        ) = get_device_simulators(simulator_factory)

        csp_sim.SetDirectHealthState(HealthState.OK)
        sdp_sim.SetDirectHealthState(HealthState.OK)
        mccs_sim.SetDirectHealthState(HealthState.OK)
        event_recorder.subscribe_event(csp_sim, "healthState")
        event_recorder.subscribe_event(sdp_sim, "healthState")
        event_recorder.subscribe_event(mccs_sim, "healthState")
        event_recorder.subscribe_event(
            subarray_node_low.subarray_node, "healthState"
        )
        assert event_recorder.has_change_event_occurred(
            csp_sim, "healthState", HealthState.OK
        )

        assert event_recorder.has_change_event_occurred(
            sdp_sim, "healthState", HealthState.OK
        )

        assert event_recorder.has_change_event_occurred(
            mccs_sim, "healthState", HealthState.OK
        )

        # Subarray node react automatically
        assert event_recorder.has_change_event_occurred(
            subarray_node_low.subarray_node,
            "healthState",
            HealthState.OK,
        ), "Expected Subarray Node HealthState to be OK"

    @pytest.mark.aki
    @pytest.mark.parametrize(
        "csp_subarray_health_state, sdp_subarray_health_state, "
        "mccs_health_state, expected_subarray_health_state",
        [
            (HealthState.OK, HealthState.OK, HealthState.OK, HealthState.OK),
            (
                HealthState.OK,
                HealthState.OK,
                HealthState.FAILED,
                HealthState.FAILED,
            ),
            (
                HealthState.OK,
                HealthState.FAILED,
                HealthState.OK,
                HealthState.FAILED,
            ),
            (
                HealthState.OK,
                HealthState.FAILED,
                HealthState.FAILED,
                HealthState.FAILED,
            ),
            (
                HealthState.FAILED,
                HealthState.OK,
                HealthState.OK,
                HealthState.FAILED,
            ),
            (
                HealthState.FAILED,
                HealthState.OK,
                HealthState.FAILED,
                HealthState.FAILED,
            ),
            (
                HealthState.FAILED,
                HealthState.FAILED,
                HealthState.OK,
                HealthState.FAILED,
            ),
            (
                HealthState.FAILED,
                HealthState.FAILED,
                HealthState.FAILED,
                HealthState.FAILED,
            ),
        ],
    )
    @pytest.mark.batch2
    @pytest.mark.SKA_mid
    def test_health_state_combinations_for_csp_sdp_mccs(
        self,
        subarray_node_low,
        simulator_factory,
        event_recorder,
        csp_subarray_health_state,
        sdp_subarray_health_state,
        mccs_health_state,
        expected_subarray_health_state,
    ):
        """Test for healthstate Failed"""
        csp_sim, sdp_sim, mccs_sim = get_device_simulators(simulator_factory)

        csp_sim.SetDirectHealthState(csp_subarray_health_state)
        sdp_sim.SetDirectHealthState(sdp_subarray_health_state)
        mccs_sim.SetDirectHealthState(mccs_health_state)

        event_recorder.subscribe_event(csp_sim, "healthState")
        event_recorder.subscribe_event(sdp_sim, "healthState")
        event_recorder.subscribe_event(mccs_sim, "healthState")
        event_recorder.subscribe_event(
            subarray_node_low.subarray_node, "healthState"
        )

        assert event_recorder.has_change_event_occurred(
            csp_sim, "healthState", csp_subarray_health_state
        )
        assert event_recorder.has_change_event_occurred(
            sdp_sim, "healthState", sdp_subarray_health_state
        )
        assert event_recorder.has_change_event_occurred(
            mccs_sim, "healthState", mccs_health_state
        )

        assert event_recorder.has_change_event_occurred(
            subarray_node_low.subarray_node,
            "healthState",
            expected_subarray_health_state,
        ), "Expected Subarray Node HealthState FAILED"

    # @pytest.mark.parametrize(
    #     "csp_subarray_health_state, sdp_subarray_health_state, \
    #     dish_master1_health_state, dish_master2_health_state, \
    #     dish_master3_health_state, dish_master4_health_state",
    #     [
    #         (
    #             HealthState.UNKNOWN,
    #             HealthState.UNKNOWN,
    #             HealthState.OK,
    #             HealthState.OK,
    #             HealthState.OK,
    #             HealthState.OK,
    #         ),
    #         (
    #             HealthState.UNKNOWN,
    #             HealthState.OK,
    #             HealthState.OK,
    #             HealthState.OK,
    #             HealthState.OK,
    #             HealthState.OK,
    #         ),
    #         (
    #             HealthState.OK,
    #             HealthState.UNKNOWN,
    #             HealthState.OK,
    #             HealthState.OK,
    #             HealthState.OK,
    #             HealthState.OK,
    #         ),
    #     ],
    # )
    # @pytest.mark.batch2
    # @pytest.mark.SKA_mid
    # def test_health_state_failed_when_csp_or_sdp_unknown(
    #     self,
    #     subarray_node,
    #     simulator_factory,
    #     event_recorder,
    #     csp_subarray_health_state,
    #     sdp_subarray_health_state,
    #     dish_master1_health_state,
    #     dish_master2_health_state,
    #     dish_master3_health_state,
    #     dish_master4_health_state,
    # ):
    #     # Row 7 to 9
    #     (
    #         csp_sim,
    #         sdp_sim,
    #         dish_master_sim_1,
    #         dish_master_sim_2,
    #         dish_master_sim_3,
    #         dish_master_sim_4,
    #     ) = get_device_simulators(simulator_factory)
    #     csp_sim.SetDirectHealthState(csp_subarray_health_state)
    #     sdp_sim.SetDirectHealthState(sdp_subarray_health_state)
    #     dish_master_sim_1.SetDirectHealthState(dish_master1_health_state)
    #     dish_master_sim_2.SetDirectHealthState(dish_master2_health_state)
    #     dish_master_sim_3.SetDirectHealthState(dish_master3_health_state)
    #     dish_master_sim_4.SetDirectHealthState(dish_master4_health_state)
    #     event_recorder.subscribe_event(csp_sim, "healthState")
    #     event_recorder.subscribe_event(sdp_sim, "healthState")
    #     event_recorder.subscribe_event(dish_master_sim_1, "healthState")
    #     event_recorder.subscribe_event(dish_master_sim_2, "healthState")
    #     event_recorder.subscribe_event(dish_master_sim_3, "healthState")
    #     event_recorder.subscribe_event(dish_master_sim_4, "healthState")
    #     event_recorder.subscribe_event(
    #         subarray_node.subarray_node, "healthState"
    #     )
    #     assert event_recorder.has_change_event_occurred(
    #         csp_sim,
    #         "healthState",
    #         csp_subarray_health_state,
    #     )

    #     assert event_recorder.has_change_event_occurred(
    #         sdp_sim,
    #         "healthState",
    #         sdp_subarray_health_state,
    #     )

    #     assert event_recorder.has_change_event_occurred(
    #         dish_master_sim_1,
    #         "healthState",
    #         dish_master1_health_state,
    #     )

    #     assert event_recorder.has_change_event_occurred(
    #         dish_master_sim_2,
    #         "healthState",
    #         dish_master2_health_state,
    #     )
    #     assert event_recorder.has_change_event_occurred(
    #         dish_master_sim_3,
    #         "healthState",
    #         dish_master3_health_state,
    #     )
    #     assert event_recorder.has_change_event_occurred(
    #         dish_master_sim_4,
    #         "healthState",
    #         dish_master4_health_state,
    #     )

    #     assert event_recorder.has_change_event_occurred(
    #         subarray_node.subarray_node,
    #         "healthState",
    #         HealthState.UNKNOWN,
    #     ), "Expected Subarray Node HealthState to be UNKNOWN"

    # @pytest.mark.parametrize(
    #     "csp_subarray_health_state, sdp_subarray_health_state, \
    #     dish_master1_health_state, dish_master2_health_state, \
    #     dish_master3_health_state, dish_master4_health_state",
    #     [
    #         (
    #             HealthState.DEGRADED,
    #             HealthState.DEGRADED,
    #             HealthState.OK,
    #             HealthState.OK,
    #             HealthState.OK,
    #             HealthState.OK,
    #         ),
    #         (
    #             HealthState.DEGRADED,
    #             HealthState.OK,
    #             HealthState.OK,
    #             HealthState.OK,
    #             HealthState.OK,
    #             HealthState.OK,
    #         ),
    #         (
    #             HealthState.OK,
    #             HealthState.DEGRADED,
    #             HealthState.OK,
    #             HealthState.OK,
    #             HealthState.OK,
    #             HealthState.OK,
    #         ),
    #     ],
    # )
    # @pytest.mark.batch2
    # @pytest.mark.SKA_mid
    # def test_health_state_degraded_when_csp_or_sdp_degraded(
    #     self,
    #     subarray_node,
    #     simulator_factory,
    #     event_recorder,
    #     csp_subarray_health_state,
    #     sdp_subarray_health_state,
    #     dish_master1_health_state,
    #     dish_master2_health_state,
    #     dish_master3_health_state,
    #     dish_master4_health_state,
    # ):
    #     # Row 12 to 14
    #     (
    #         csp_sim,
    #         sdp_sim,
    #         dish_master_sim_1,
    #         dish_master_sim_2,
    #         dish_master_sim_3,
    #         dish_master_sim_4,
    #     ) = get_device_simulators(simulator_factory)
    #     csp_sim.SetDirectHealthState(csp_subarray_health_state)
    #     sdp_sim.SetDirectHealthState(sdp_subarray_health_state)
    #     dish_master_sim_1.SetDirectHealthState(dish_master1_health_state)
    #     dish_master_sim_2.SetDirectHealthState(dish_master2_health_state)
    #     dish_master_sim_3.SetDirectHealthState(dish_master3_health_state)
    #     dish_master_sim_4.SetDirectHealthState(dish_master4_health_state)
    #     event_recorder.subscribe_event(csp_sim, "healthState")
    #     event_recorder.subscribe_event(sdp_sim, "healthState")
    #     event_recorder.subscribe_event(dish_master_sim_1, "healthState")
    #     event_recorder.subscribe_event(dish_master_sim_2, "healthState")
    #     event_recorder.subscribe_event(dish_master_sim_3, "healthState")
    #     event_recorder.subscribe_event(dish_master_sim_4, "healthState")
    #     event_recorder.subscribe_event(
    #         subarray_node.subarray_node, "healthState"
    #     )
    #     assert event_recorder.has_change_event_occurred(
    #         csp_sim,
    #         "healthState",
    #         csp_subarray_health_state,
    #     )

    #     assert event_recorder.has_change_event_occurred(
    #         sdp_sim,
    #         "healthState",
    #         sdp_subarray_health_state,
    #     )

    #     assert event_recorder.has_change_event_occurred(
    #         dish_master_sim_1,
    #         "healthState",
    #         dish_master1_health_state,
    #     )

    #     assert event_recorder.has_change_event_occurred(
    #         dish_master_sim_2,
    #         "healthState",
    #         dish_master2_health_state,
    #     )
    #     assert event_recorder.has_change_event_occurred(
    #         dish_master_sim_3,
    #         "healthState",
    #         dish_master3_health_state,
    #     )
    #     assert event_recorder.has_change_event_occurred(
    #         dish_master_sim_4,
    #         "healthState",
    #         dish_master4_health_state,
    #     )
    #     assert event_recorder.has_change_event_occurred(
    #         subarray_node.subarray_node,
    #         "healthState",
    #         HealthState.DEGRADED,
    #     ), "Expected Subarray Node HealthState to be DEGRADED"

    # @pytest.mark.parametrize(
    #     "csp_subarray_health_state, sdp_subarray_health_state, \
    #     dish_master1_health_state, dish_master2_health_state, \
    #     dish_master3_health_state, dish_master4_health_state",
    #     [
    #         (
    #             HealthState.FAILED,
    #             HealthState.OK,
    #             HealthState.OK,
    #             HealthState.OK,
    #             HealthState.OK,
    #             HealthState.OK,
    #         ),
    #         (
    #             HealthState.FAILED,
    #             HealthState.FAILED,
    #             HealthState.FAILED,
    #             HealthState.FAILED,
    #             HealthState.FAILED,
    #             HealthState.FAILED,
    #         ),
    #     ],
    # )
    # @pytest.mark.batch2
    # @pytest.mark.SKA_mid
    # def test_health_state_failed_when_all_dish_failed(
    #     self,
    #     subarray_node,
    #     central_node_mid,
    #     simulator_factory,
    #     event_recorder,
    #     command_input_factory,
    #     csp_subarray_health_state,
    #     sdp_subarray_health_state,
    #     dish_master1_health_state,
    #     dish_master2_health_state,
    #     dish_master3_health_state,
    #     dish_master4_health_state,
    # ):
    #     # Row 5 and 6
    #     (
    #         csp_sim,
    #         sdp_sim,
    #         dish_master_sim_1,
    #         dish_master_sim_2,
    #         dish_master_sim_3,
    #         dish_master_sim_4,
    #     ) = get_device_simulators(simulator_factory)

    #     csp_sim.SetDirectHealthState(csp_subarray_health_state)
    #     sdp_sim.SetDirectHealthState(sdp_subarray_health_state)
    #     dish_master_sim_1.SetDirectHealthState(dish_master1_health_state)
    #     dish_master_sim_2.SetDirectHealthState(dish_master2_health_state)
    #     dish_master_sim_3.SetDirectHealthState(dish_master3_health_state)
    #     dish_master_sim_4.SetDirectHealthState(dish_master4_health_state)
    #     event_recorder.subscribe_event(csp_sim, "healthState")
    #     event_recorder.subscribe_event(sdp_sim, "healthState")
    #     event_recorder.subscribe_event(dish_master_sim_1, "healthState")
    #     event_recorder.subscribe_event(dish_master_sim_2, "healthState")
    #     event_recorder.subscribe_event(dish_master_sim_3, "healthState")
    #     event_recorder.subscribe_event(dish_master_sim_4, "healthState")
    #     event_recorder.subscribe_event(
    #         subarray_node.subarray_node, "healthState"
    #     )
    #     assert event_recorder.has_change_event_occurred(
    #         csp_sim,
    #         "healthState",
    #         csp_subarray_health_state,
    #     )

    #     assert event_recorder.has_change_event_occurred(
    #         sdp_sim,
    #         "healthState",
    #         sdp_subarray_health_state,
    #     )

    #     assert event_recorder.has_change_event_occurred(
    #         dish_master_sim_1,
    #         "healthState",
    #         dish_master1_health_state,
    #     )

    #     assert event_recorder.has_change_event_occurred(
    #         dish_master_sim_2,
    #         "healthState",
    #         dish_master2_health_state,
    #     )

    #     assert event_recorder.has_change_event_occurred(
    #         dish_master_sim_3,
    #         "healthState",
    #         dish_master3_health_state,
    #     )
    #     assert event_recorder.has_change_event_occurred(
    #         dish_master_sim_4,
    #         "healthState",
    #         dish_master4_health_state,
    #     )
    #     assert event_recorder.has_change_event_occurred(
    #         subarray_node.subarray_node,
    #         "healthState",
    #         HealthState.FAILED,
    #     ), "Expected Subarray Node HealthState to be FAILED"

    # @pytest.mark.parametrize(
    #     "csp_subarray_health_state, sdp_subarray_health_state, \
    #     dish_master1_health_state, dish_master2_health_state, \
    #     dish_master3_health_state, dish_master4_health_state",
    #     [
    #         (
    #             HealthState.OK,
    #             HealthState.OK,
    #             HealthState.UNKNOWN,
    #             HealthState.OK,
    #             HealthState.OK,
    #             HealthState.OK,
    #         ),
    #         (
    #             HealthState.OK,
    #             HealthState.OK,
    #             HealthState.OK,
    #             HealthState.UNKNOWN,
    #             HealthState.OK,
    #             HealthState.OK,
    #         ),
    #         (
    #             HealthState.OK,
    #             HealthState.OK,
    #             HealthState.UNKNOWN,
    #             HealthState.UNKNOWN,
    #             HealthState.OK,
    #             HealthState.OK,
    #         ),
    #         (
    #             HealthState.UNKNOWN,
    #             HealthState.UNKNOWN,
    #             HealthState.UNKNOWN,
    #             HealthState.UNKNOWN,
    #             HealthState.UNKNOWN,
    #             HealthState.UNKNOWN,
    #         ),
    #     ],
    # )
    # @pytest.mark.batch2
    # @pytest.mark.SKA_mid
    # def test_health_state_failed_when_dish_unknown(
    #     self,
    #     subarray_node,
    #     central_node_mid,
    #     simulator_factory,
    #     event_recorder,
    #     command_input_factory,
    #     csp_subarray_health_state,
    #     sdp_subarray_health_state,
    #     dish_master1_health_state,
    #     dish_master2_health_state,
    #     dish_master3_health_state,
    #     dish_master4_health_state,
    # ):
    #     # Row 10 and 11
    #     (
    #         csp_sim,
    #         sdp_sim,
    #         dish_master_sim_1,
    #         dish_master_sim_2,
    #         dish_master_sim_3,
    #         dish_master_sim_4,
    #     ) = get_device_simulators(simulator_factory)

    #     csp_sim.SetDirectHealthState(csp_subarray_health_state)
    #     sdp_sim.SetDirectHealthState(sdp_subarray_health_state)
    #     dish_master_sim_1.SetDirectHealthState(dish_master1_health_state)
    #     dish_master_sim_2.SetDirectHealthState(dish_master2_health_state)
    #     dish_master_sim_3.SetDirectHealthState(dish_master3_health_state)
    #     dish_master_sim_4.SetDirectHealthState(dish_master4_health_state)
    #     event_recorder.subscribe_event(csp_sim, "healthState")
    #     event_recorder.subscribe_event(sdp_sim, "healthState")
    #     event_recorder.subscribe_event(dish_master_sim_1, "healthState")
    #     event_recorder.subscribe_event(dish_master_sim_2, "healthState")
    #     event_recorder.subscribe_event(dish_master_sim_3, "healthState")
    #     event_recorder.subscribe_event(dish_master_sim_4, "healthState")
    #     event_recorder.subscribe_event(
    #         subarray_node.subarray_node, "healthState"
    #     )
    #     assert event_recorder.has_change_event_occurred(
    #         csp_sim,
    #         "healthState",
    #         csp_subarray_health_state,
    #     )

    #     assert event_recorder.has_change_event_occurred(
    #         sdp_sim,
    #         "healthState",
    #         sdp_subarray_health_state,
    #     )

    #     assert event_recorder.has_change_event_occurred(
    #         dish_master_sim_1,
    #         "healthState",
    #         dish_master1_health_state,
    #     )

    #     assert event_recorder.has_change_event_occurred(
    #         dish_master_sim_2,
    #         "healthState",
    #         dish_master2_health_state,
    #     )
    #     assert event_recorder.has_change_event_occurred(
    #         dish_master_sim_3,
    #         "healthState",
    #         dish_master3_health_state,
    #     )
    #     assert event_recorder.has_change_event_occurred(
    #         dish_master_sim_4,
    #         "healthState",
    #         dish_master4_health_state,
    #     )
    #     assert event_recorder.has_change_event_occurred(
    #         subarray_node.subarray_node,
    #         "healthState",
    #         HealthState.UNKNOWN,
    #     ), "Expected Subarray Node HealthState to be UNKNOWN"

    # @pytest.mark.parametrize(
    #     "csp_subarray_health_state, sdp_subarray_health_state, \
    #     dish_master1_health_state, dish_master2_health_state, \
    #     dish_master3_health_state, dish_master4_health_state",
    #     [
    #         (
    #             HealthState.OK,
    #             HealthState.OK,
    #             HealthState.FAILED,
    #             HealthState.OK,
    #             HealthState.OK,
    #             HealthState.OK,
    #         ),
    #         (
    #             HealthState.OK,
    #             HealthState.OK,
    #             HealthState.OK,
    #             HealthState.FAILED,
    #             HealthState.OK,
    #             HealthState.OK,
    #         ),
    #         (
    #             HealthState.OK,
    #             HealthState.OK,
    #             HealthState.DEGRADED,
    #             HealthState.OK,
    #             HealthState.OK,
    #             HealthState.OK,
    #         ),
    #         (
    #             HealthState.OK,
    #             HealthState.OK,
    #             HealthState.OK,
    #             HealthState.DEGRADED,
    #             HealthState.OK,
    #             HealthState.OK,
    #         ),
    #         (
    #             HealthState.OK,
    #             HealthState.OK,
    #             HealthState.DEGRADED,
    #             HealthState.DEGRADED,
    #             HealthState.OK,
    #             HealthState.OK,
    #         ),
    #         (
    #             HealthState.DEGRADED,
    #             HealthState.DEGRADED,
    #             HealthState.DEGRADED,
    #             HealthState.DEGRADED,
    #             HealthState.DEGRADED,
    #             HealthState.DEGRADED,
    #         ),
    #     ],
    # )
    # @pytest.mark.batch2
    # @pytest.mark.SKA_mid
    # def test_health_state_degraded_when_one_or_more_dish_degraded_or_failed(
    #     self,
    #     subarray_node,
    #     central_node_mid,
    #     simulator_factory,
    #     event_recorder,
    #     command_input_factory,
    #     csp_subarray_health_state,
    #     sdp_subarray_health_state,
    #     dish_master1_health_state,
    #     dish_master2_health_state,
    #     dish_master3_health_state,
    #     dish_master4_health_state,
    # ):
    #     # Row 15 to 17
    #     (
    #         csp_sim,
    #         sdp_sim,
    #         dish_master_sim_1,
    #         dish_master_sim_2,
    #         dish_master_sim_3,
    #         dish_master_sim_4,
    #     ) = get_device_simulators(simulator_factory)

    #     csp_sim.SetDirectHealthState(csp_subarray_health_state)
    #     sdp_sim.SetDirectHealthState(sdp_subarray_health_state)
    #     dish_master_sim_1.SetDirectHealthState(dish_master1_health_state)
    #     dish_master_sim_2.SetDirectHealthState(dish_master2_health_state)
    #     dish_master_sim_3.SetDirectHealthState(dish_master3_health_state)
    #     dish_master_sim_4.SetDirectHealthState(dish_master4_health_state)
    #     event_recorder.subscribe_event(csp_sim, "healthState")
    #     event_recorder.subscribe_event(sdp_sim, "healthState")
    #     event_recorder.subscribe_event(dish_master_sim_1, "healthState")
    #     event_recorder.subscribe_event(dish_master_sim_2, "healthState")
    #     event_recorder.subscribe_event(dish_master_sim_3, "healthState")
    #     event_recorder.subscribe_event(dish_master_sim_4, "healthState")
    #     event_recorder.subscribe_event(
    #         subarray_node.subarray_node, "healthState"
    #     )
    #     assert event_recorder.has_change_event_occurred(
    #         csp_sim,
    #         "healthState",
    #         csp_subarray_health_state,
    #     )

    #     assert event_recorder.has_change_event_occurred(
    #         sdp_sim,
    #         "healthState",
    #         sdp_subarray_health_state,
    #     )

    #     assert event_recorder.has_change_event_occurred(
    #         dish_master_sim_1,
    #         "healthState",
    #         dish_master1_health_state,
    #     )

    #     assert event_recorder.has_change_event_occurred(
    #         dish_master_sim_2,
    #         "healthState",
    #         dish_master2_health_state,
    #     )
    #     assert event_recorder.has_change_event_occurred(
    #         dish_master_sim_3,
    #         "healthState",
    #         dish_master3_health_state,
    #     )
    #     assert event_recorder.has_change_event_occurred(
    #         dish_master_sim_4,
    #         "healthState",
    #         dish_master4_health_state,
    #     )

    #     if (
    #         dish_master1_health_state == HealthState.DEGRADED
    #         and dish_master2_health_state == HealthState.DEGRADED
    #         and dish_master3_health_state == HealthState.DEGRADED
    #         and dish_master4_health_state == HealthState.DEGRADED
    #     ):
    #         assert event_recorder.has_change_event_occurred(
    #             subarray_node.subarray_node,
    #             "healthState",
    #             HealthState.FAILED,
    #         ), "Expected Subarray Node HealthState to be DEGRADED"
    #     else:
    #         assert event_recorder.has_change_event_occurred(
    #             subarray_node.subarray_node,
    #             "healthState",
    #             HealthState.DEGRADED,
    #         ), "Expected Subarray Node HealthState to be DEGRADED"

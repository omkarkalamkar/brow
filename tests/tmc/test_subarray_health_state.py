"""Test Subarray Health State"""

import pytest
from ska_tango_base.control_model import AdminMode, HealthState

from tests.resources.test_harness.helpers import get_device_simulators


class TestSubarrayHealthState:
    """This class implement test cases to verify HealthState
    of Subarray Node.
    This tests implement rows of following excel sheet
    https://docs.google.com/spreadsheets/d/1XbNb8We7fK-EhmOcw3S-h0V_Pu-WAfPTkEd13MSmIns/edit#gid=747888622
    """

    @pytest.mark.SKA_low
    def test_health_state_ok(
        self, subarray_node_low, simulator_factory, event_recorder
    ):
        """Test for healthstate OK"""
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
    @pytest.mark.SKA_low
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
        """Test for healthstate FAILED"""
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

    @pytest.mark.parametrize(
        "csp_subarray_health_state, "
        "sdp_subarray_health_state, mccs_health_state",
        [
            (HealthState.UNKNOWN, HealthState.OK, HealthState.OK),
            (HealthState.OK, HealthState.UNKNOWN, HealthState.OK),
            (HealthState.OK, HealthState.OK, HealthState.UNKNOWN),
            (HealthState.UNKNOWN, HealthState.UNKNOWN, HealthState.OK),
            (HealthState.UNKNOWN, HealthState.OK, HealthState.UNKNOWN),
            (HealthState.OK, HealthState.UNKNOWN, HealthState.UNKNOWN),
            (HealthState.UNKNOWN, HealthState.UNKNOWN, HealthState.UNKNOWN),
        ],
    )
    @pytest.mark.SKA_low
    def test_health_state_unknown_when_any_of_csp_sdp_mccs_unknown(
        self,
        subarray_node_low,
        simulator_factory,
        event_recorder,
        csp_subarray_health_state,
        sdp_subarray_health_state,
        mccs_health_state,
    ):
        """Test for healthstate UNKNOWN"""
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
            HealthState.UNKNOWN,
        )

    @pytest.mark.parametrize(
        "csp_subarray_health_state, "
        "sdp_subarray_health_state, mccs_health_state",
        [
            (
                HealthState.DEGRADED,
                HealthState.DEGRADED,
                HealthState.OK,
            ),
            (
                HealthState.DEGRADED,
                HealthState.OK,
                HealthState.OK,
            ),
            (
                HealthState.OK,
                HealthState.DEGRADED,
                HealthState.OK,
            ),
        ],
    )
    @pytest.mark.SKA_low
    def test_health_state_degraded_when_csp_or_sdp_degraded(
        self,
        subarray_node_low,
        simulator_factory,
        event_recorder,
        csp_subarray_health_state,
        sdp_subarray_health_state,
        mccs_health_state,
    ):
        """Test for healthstate DEGRADED"""
        (
            csp_sim,
            sdp_sim,
            mccs_sim,
        ) = get_device_simulators(simulator_factory)

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
            HealthState.DEGRADED,
        ), "Expected Subarray Node HealthState to be DEGRADED"

    @pytest.mark.parametrize(
        "csp_subarray_health_state, "
        "sdp_subarray_health_state, mccs_health_state",
        [
            (
                HealthState.DEGRADED,
                HealthState.FAILED,
                HealthState.OK,
            ),
            (
                HealthState.DEGRADED,
                HealthState.OK,
                HealthState.FAILED,
            ),
            (
                HealthState.DEGRADED,
                HealthState.DEGRADED,
                HealthState.FAILED,
            ),
        ],
    )
    @pytest.mark.SKA_low
    def test_health_state_failed_when_csp_degraded_and_sdp_failed(
        self,
        subarray_node_low,
        simulator_factory,
        event_recorder,
        csp_subarray_health_state,
        sdp_subarray_health_state,
        mccs_health_state,
    ):
        """Test for healthstate FAILED and DEGRADED"""
        (
            csp_sim,
            sdp_sim,
            mccs_sim,
        ) = get_device_simulators(simulator_factory)

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
            HealthState.FAILED,
        ), "Expected Subarray Node HealthState to be FAILED"

    @pytest.mark.parametrize(
        "csp_subarray_health_state, "
        "sdp_subarray_health_state, mccs_health_state, "
        "csp_admin_mode, sdp_admin_mode, mccs_admin_mode",
        [
            (
                HealthState.OK,
                HealthState.OK,
                HealthState.OK,
                AdminMode.OFFLINE,
                AdminMode.OFFLINE,
                AdminMode.OFFLINE,
            ),
            (
                HealthState.OK,
                HealthState.OK,
                HealthState.OK,
                AdminMode.ONLINE,
                AdminMode.OFFLINE,
                AdminMode.ONLINE,
            ),
            (
                HealthState.OK,
                HealthState.OK,
                HealthState.OK,
                AdminMode.ONLINE,
                AdminMode.ONLINE,
                AdminMode.OFFLINE,
            ),
        ],
    )
    @pytest.mark.SKA_low
    def test_health_state_degraded_when_csp_or_sdp_or_mccs_offline(
        self,
        subarray_node_low,
        simulator_factory,
        event_recorder,
        csp_subarray_health_state,
        sdp_subarray_health_state,
        mccs_health_state,
        csp_admin_mode,
        sdp_admin_mode,
        mccs_admin_mode,
    ):
        """Test for healthstate DEGRADED"""
        # Get the device simulators
        csp_sim, sdp_sim, mccs_sim = get_device_simulators(simulator_factory)

        # Set the health states for CSP, SDP, and MCCS
        csp_sim.SetDirectHealthState(csp_subarray_health_state)
        sdp_sim.SetDirectHealthState(sdp_subarray_health_state)
        mccs_sim.SetDirectHealthState(mccs_health_state)

        # Set the admin mode for each device
        csp_sim.AdminMode = csp_admin_mode
        sdp_sim.AdminMode = sdp_admin_mode
        mccs_sim.AdminMode = mccs_admin_mode

        # Subscribe to health state events
        event_recorder.subscribe_event(csp_sim, "healthState")
        event_recorder.subscribe_event(sdp_sim, "healthState")
        event_recorder.subscribe_event(mccs_sim, "healthState")
        event_recorder.subscribe_event(csp_sim, "AdminMode")
        event_recorder.subscribe_event(sdp_sim, "AdminMode")
        event_recorder.subscribe_event(mccs_sim, "AdminMode")
        event_recorder.subscribe_event(
            subarray_node_low.subarray_node, "healthState"
        )

        # Assert the health state changes for CSP, SDP, and MCCS
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
            csp_sim, "AdminMode", csp_admin_mode
        )
        assert event_recorder.has_change_event_occurred(
            sdp_sim, "AdminMode", sdp_admin_mode
        )
        assert event_recorder.has_change_event_occurred(
            mccs_sim, "AdminMode", mccs_admin_mode
        )

        # Assert the health state of the subarray node based on admin mode

        assert event_recorder.has_change_event_occurred(
            subarray_node_low.subarray_node,
            "healthState",
            HealthState.DEGRADED,
        ), "Expected Subarray Node HealthState to be DEGRADED"

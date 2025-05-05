"""Test Telescope Health State"""
import pytest
from ska_tango_base.control_model import HealthState
from tango import DevState

from tests.resources.test_harness.helpers import (
    get_device_simulators,
    get_master_device_simulators,
)


class TestTelescopeHealthState:
    """Test cases to verify telescopeHealthState of CentralNode.
    This implements rows of decision table for telescopeHealthState.
    """

    @pytest.mark.parametrize(
        "csp_master_health_state, sdp_master_health_state, "
        "mccs_master_health_state",
        [
            (HealthState.OK, HealthState.FAILED, HealthState.OK),
            (HealthState.FAILED, HealthState.OK, HealthState.OK),
            (HealthState.OK, HealthState.OK, HealthState.FAILED),
            (HealthState.OK, HealthState.FAILED, HealthState.FAILED),
            (HealthState.FAILED, HealthState.FAILED, HealthState.OK),
            (HealthState.FAILED, HealthState.OK, HealthState.FAILED),
            (HealthState.FAILED, HealthState.FAILED, HealthState.FAILED),
        ],
    )
    @pytest.mark.SKA_low
    def test_telescope_health_state_failed(
        self,
        central_node_low,
        simulator_factory,
        event_recorder,
        csp_master_health_state,
        sdp_master_health_state,
        mccs_master_health_state,
    ):
        """Test for healthstate FAILED"""
        (
            csp_master_sim,
            sdp_master_sim,
            mccs_master_sim,
        ) = get_master_device_simulators(simulator_factory)
        central_node_low.move_to_on()
        event_recorder.subscribe_event(
            central_node_low.central_node, "telescopeState"
        )
        assert event_recorder.has_change_event_occurred(
            central_node_low.central_node,
            "telescopeState",
            DevState.ON,
        )

        csp_master_sim.SetDirectHealthState(csp_master_health_state)
        sdp_master_sim.SetDirectHealthState(sdp_master_health_state)
        mccs_master_sim.SetDirectHealthState(mccs_master_health_state)

        event_recorder.subscribe_event(
            central_node_low.central_node, "telescopeHealthState"
        )

        assert event_recorder.has_change_event_occurred(
            central_node_low.central_node,
            "telescopeHealthState",
            HealthState.FAILED,
        )

    @pytest.mark.SKA_low
    def test_telescope_health_state_ok(
        self,
        central_node_low,
        subarray_node_low,
        simulator_factory,
        event_recorder,
    ):
        """Test for healthstate OK"""
        (
            csp_master_sim,
            sdp_master_sim,
            mccs_master_sim,
        ) = get_master_device_simulators(simulator_factory)
        (
            csp_subarray_sim,
            sdp_subarray_sim,
            mccs_subarray_sim,
        ) = get_device_simulators(simulator_factory)
        central_node_low.move_to_on()
        event_recorder.subscribe_event(
            central_node_low.central_node, "telescopeState"
        )
        assert event_recorder.has_change_event_occurred(
            central_node_low.central_node,
            "telescopeState",
            DevState.ON,
        )
        csp_master_sim.SetDirectHealthState(HealthState.OK)
        sdp_master_sim.SetDirectHealthState(HealthState.OK)
        mccs_master_sim.SetDirectHealthState(HealthState.OK)

        # Subarray healthstate should be OK
        csp_subarray_sim.SetDirectHealthState(HealthState.OK)
        sdp_subarray_sim.SetDirectHealthState(HealthState.OK)
        mccs_subarray_sim.SetDirectHealthState(HealthState.OK)
        event_recorder.subscribe_event(
            central_node_low.central_node, "telescopeHealthState"
        )
        event_recorder.subscribe_event(
            subarray_node_low.subarray_node, "healthState"
        )

        assert event_recorder.has_change_event_occurred(
            subarray_node_low.subarray_node,
            "healthState",
            HealthState.OK,
        )
        assert event_recorder.has_change_event_occurred(
            central_node_low.central_node,
            "telescopeHealthState",
            HealthState.OK,
        )

    @pytest.mark.parametrize(
        "csp_master_health_state, sdp_master_health_state, "
        "mccs_master_health_state",
        [
            (HealthState.OK, HealthState.DEGRADED, HealthState.OK),
            (HealthState.DEGRADED, HealthState.OK, HealthState.OK),
            (HealthState.OK, HealthState.OK, HealthState.DEGRADED),
            (HealthState.DEGRADED, HealthState.DEGRADED, HealthState.OK),
            (HealthState.OK, HealthState.DEGRADED, HealthState.DEGRADED),
        ],
    )
    @pytest.mark.SKA_low
    def test_telescope_health_state_degraded(
        self,
        central_node_low,
        simulator_factory,
        event_recorder,
        csp_master_health_state,
        sdp_master_health_state,
        mccs_master_health_state,
    ):
        """Test for healthstate DEGRADED"""
        (
            csp_master_sim,
            sdp_master_sim,
            mccs_master_sim,
        ) = get_master_device_simulators(simulator_factory)
        central_node_low.move_to_on()
        event_recorder.subscribe_event(
            central_node_low.central_node, "telescopeState"
        )
        assert event_recorder.has_change_event_occurred(
            central_node_low.central_node,
            "telescopeState",
            DevState.ON,
        )
        csp_master_sim.SetDirectHealthState(csp_master_health_state)
        sdp_master_sim.SetDirectHealthState(sdp_master_health_state)
        mccs_master_sim.SetDirectHealthState(mccs_master_health_state)

        event_recorder.subscribe_event(
            central_node_low.central_node, "telescopeHealthState"
        )

        assert event_recorder.has_change_event_occurred(
            central_node_low.central_node,
            "telescopeHealthState",
            HealthState.DEGRADED,
        )

    @pytest.mark.parametrize(
        "csp_master_health_state, sdp_master_health_state, "
        "mccs_master_health_state",
        [
            (HealthState.OK, HealthState.UNKNOWN, HealthState.OK),
            (HealthState.UNKNOWN, HealthState.OK, HealthState.OK),
            (HealthState.OK, HealthState.OK, HealthState.UNKNOWN),
            (HealthState.UNKNOWN, HealthState.UNKNOWN, HealthState.OK),
            (HealthState.UNKNOWN, HealthState.OK, HealthState.UNKNOWN),
        ],
    )
    @pytest.mark.SKA_low
    def test_telescope_health_state_unknown(
        self,
        central_node_low,
        simulator_factory,
        event_recorder,
        csp_master_health_state,
        sdp_master_health_state,
        mccs_master_health_state,
    ):
        """Test for healthstate UNKNOWN"""
        (
            csp_master_sim,
            sdp_master_sim,
            mccs_master_sim,
        ) = get_master_device_simulators(simulator_factory)
        central_node_low.move_to_on()
        event_recorder.subscribe_event(
            central_node_low.central_node, "telescopeState"
        )
        assert event_recorder.has_change_event_occurred(
            central_node_low.central_node,
            "telescopeState",
            DevState.ON,
        )
        csp_master_sim.SetDirectHealthState(csp_master_health_state)
        sdp_master_sim.SetDirectHealthState(sdp_master_health_state)
        mccs_master_sim.SetDirectHealthState(mccs_master_health_state)

        event_recorder.subscribe_event(
            central_node_low.central_node, "telescopeHealthState"
        )

        assert event_recorder.has_change_event_occurred(
            central_node_low.central_node,
            "telescopeHealthState",
            HealthState.UNKNOWN,
        )

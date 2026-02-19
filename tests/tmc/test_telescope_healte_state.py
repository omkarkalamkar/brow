"""Test Telescope Health State"""
import time

import pytest
from pytest_bdd import given, parsers, scenario, then, when
from ska_tango_base.control_model import HealthState
from tango import DevState

from tests.resources.test_harness.helpers import (
    get_device_simulators,
    get_master_device_simulators,
)

state = {}


@pytest.mark.SKA_low
@scenario(
    "../features/tmc/check_telescope_healthstate.feature",
    "CentralNode reports FAILED telescopeHealthState",
)
def test_telescope_health_state_failed():
    """Test telescope healthstate"""


@pytest.mark.SKA_low
@scenario(
    "../features/tmc/check_telescope_healthstate.feature",
    "CentralNode reports OK telescopeHealthState",
)
def test_telescope_health_state_ok():
    """Test telescope healthstate"""


@pytest.mark.SKA_low
@scenario(
    "../features/tmc/check_telescope_healthstate.feature",
    "CentralNode reports DEGRADED telescopeHealthState",
)
def test_telescope_health_state_degraded():
    """Test telescope healthstate"""


@pytest.mark.SKA_low
@scenario(
    "../features/tmc/check_telescope_healthstate.feature",
    "CentralNode reports UNKNOWN telescopeHealthState",
)
def test_telescope_health_state_unknown():
    """Test telescope healthstate"""


@given("the telescope is ON")
def telescope_on(central_node_low, event_recorder):
    """Turn On the telescope"""
    central_node_low.move_to_on()
    event_recorder.subscribe_event(
        central_node_low.central_node, "telescopeState"
    )
    assert event_recorder.has_change_event_occurred(
        central_node_low.central_node, "telescopeState", DevState.ON
    )


@given("the telescope")
def telescope_exist():
    """given a telescope"""


@given(parsers.parse("CSP master health is {csp_state}"))
def set_csp_master_health(simulator_factory, csp_state):
    """Set master devices healthstate"""
    csp, _, _ = get_master_device_simulators(simulator_factory)
    state["csp"] = csp
    state["csp_state"] = csp_state


@given(parsers.parse("SDP master health is {sdp_state}"))
def set_sdp_master_health(simulator_factory, sdp_state):
    """Set master devices healthstate"""
    _, sdp, _ = get_master_device_simulators(simulator_factory)
    state["sdp"] = sdp
    state["sdp_state"] = sdp_state


@given(parsers.parse("MCCS master health is {mccs_state}"))
def set_mccs_master_health(simulator_factory, mccs_state):
    """Set master devices healthstate"""
    _, _, mccs = get_master_device_simulators(simulator_factory)
    state["mccs"] = mccs
    state["mccs_state"] = mccs_state


@given("all master and subarray components have OK health")
def set_all_ok_health(simulator_factory):
    """Set all healthstate to OK"""
    csp_m, sdp_m, mccs_m = get_master_device_simulators(simulator_factory)
    csp_s, sdp_s, mccs_s = get_device_simulators(simulator_factory)
    for device in [csp_m, sdp_m, mccs_m, csp_s, sdp_s, mccs_s]:
        device.SetDirectHealthState(HealthState.OK)
        time.sleep(0.2)
    state.update(
        {
            "csp": csp_m,
            "sdp": sdp_m,
            "mccs": mccs_m,
            "subarray_devices": (csp_s, sdp_s, mccs_s),
        }
    )


@when("health states are applied")
def apply_health_states():
    """Apply the healthstate to devices"""
    for name in ["csp", "sdp", "mccs"]:
        device = state[name]
        raw_state = state.get(f"{name}_state", "OK")
        device.SetDirectHealthState(HealthState[raw_state])
        time.sleep(0.2)


@then(parsers.parse("the telescopeHealthState should be {expected_state}"))
def check_telescope_health_state(
    event_recorder, central_node_low, expected_state
):
    """Verify the telescope healthstate"""
    event_recorder.subscribe_event(
        central_node_low.central_node, "telescopeHealthState"
    )
    assert event_recorder.has_change_event_occurred(
        central_node_low.central_node,
        "telescopeHealthState",
        HealthState[expected_state],
    )


@then("the subarray healthState should be OK")
def check_subarray_health(event_recorder, subarray_node_low):
    """Verify the subarray healthstate"""
    event_recorder.subscribe_event(
        subarray_node_low.subarray_node, "healthState"
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_node, "healthState", HealthState.OK
    )

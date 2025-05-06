"""Test Subarray Node Health State"""
import time

import pytest
from pytest_bdd import given, parsers, scenario, then, when
from ska_tango_base.control_model import HealthState

from tests.resources.test_harness.helpers import get_device_simulators

state = {}


@pytest.mark.SKA_low
@scenario(
    "../features/tmc/check_subarray_healthstate.feature",
    "Subarray health reflects correct aggregated healthstate of "
    "CSP, SDP, and MCCS subarrays",
)
def test_subarray_health_combined_states():
    """Test subarray node healthstate based on CSP, SDP, MCCS"""


@given(parsers.parse("CSP health is {csp_health}"))
def set_csp_health(simulator_factory, csp_health):
    """Set the CSP healthstate"""
    csp, _, _ = get_device_simulators(simulator_factory)
    state["csp"] = csp
    state["csp_health"] = csp_health


@given(parsers.parse("SDP health is {sdp_health}"))
def set_sdp_health(simulator_factory, sdp_health):
    """Set the SDP healthstate"""
    _, sdp, _ = get_device_simulators(simulator_factory)
    state["sdp"] = sdp
    state["sdp_health"] = sdp_health


@given(parsers.parse("MCCS health is {mccs_health}"))
def set_mccs_health(simulator_factory, mccs_health):
    """Set the MCCS healthstate"""
    _, _, mccs = get_device_simulators(simulator_factory)
    state["mccs"] = mccs
    state["mccs_health"] = mccs_health


@when("health states are applied")
def apply_subarray_health_states():
    """Apply the subarray healthstate"""
    for name in ["csp", "sdp", "mccs"]:
        device = state[name]
        raw_state = state.get(f"{name}_health", "OK")
        device.SetDirectHealthState(HealthState[raw_state])
        time.sleep(0.2)


@then(
    parsers.parse("the Subarray Node health state should be {expected_health}")
)
def check_subarray_node_health(
    event_recorder, subarray_node_low, expected_health
):
    """Check the subarray healthstate"""
    event_recorder.subscribe_event(
        subarray_node_low.subarray_node, "healthState"
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_node,
        "healthState",
        HealthState[expected_health],
    )

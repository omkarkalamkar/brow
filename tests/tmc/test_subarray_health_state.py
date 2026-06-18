"""Test Subarray Node Health State"""


import pytest
from assertpy import assert_that
from pytest_bdd import given, parsers, scenario, then, when
from ska_tango_base.control_model import HealthState

from tests.resources.test_harness.helpers import get_device_simulators
from tests.resources.test_harness.subarray_node_low import (
    SubarrayNodeWrapperLow,
)
from tests.tmc.conftest import _setup_event_subscriptions_for_healthstate

state = {}


@pytest.mark.SKA_low
@scenario(
    "features/tmc/check_subarray_healthstate.feature",
    "Subarray health reflects correct aggregated healthstate of "
    "CSP, SDP, and MCCS subarrays",
)
def test_subarray_health_combined_states():
    """Test subarray node healthstate based on CSP, SDP, MCCS"""


@given(parsers.parse("CSP health is {csp_health}"))
def set_csp_health(
    simulator_factory,
    csp_health,
    event_tracer,
    subarray_node_low: SubarrayNodeWrapperLow,
):
    """Set the CSP healthstate"""
    # Start with a clean event trace for each scenario.
    event_tracer.clear_events()
    _setup_event_subscriptions_for_healthstate(event_tracer, subarray_node_low)
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
def apply_subarray_health_states(event_tracer):
    """Apply the subarray healthstate"""
    # Subscribe before applying changes to avoid missing events.
    for name in ["csp", "sdp", "mccs"]:
        device = state[name]
        raw_state = state.get(f"{name}_health", "OK")
        expected = HealthState[raw_state]

        device.SetDirectHealthState(expected)

        assert_that(event_tracer).described_as(
            f"Expected a healthState change event for {name.upper()}"
        ).within_timeout(2).has_change_event_occurred(
            device, "healthState", expected
        )


@then(
    parsers.parse("the Subarray Node health state should be {expected_health}")
)
def check_subarray_node_health(
    event_tracer, subarray_node_low: SubarrayNodeWrapperLow, expected_health
):
    """Check the subarray healthstate"""
    expected = HealthState[expected_health]

    assert_that(event_tracer).described_as(
        "Expected a healthState change event for Subarray Node"
    ).within_timeout(2).has_change_event_occurred(
        subarray_node_low.subarray_node,
        "healthState",
        expected,
    )

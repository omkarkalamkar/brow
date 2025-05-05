"""Test the subarray healthstate"""
import pytest
from pytest_bdd import given, parsers, scenarios, then, when
from ska_tango_base.control_model import HealthState

scenarios("../features/tmc/check_subarray_health_state.feature")

HEALTH_MAP = {
    "OK": HealthState.OK,
    "FAILED": HealthState.FAILED,
    "UNKNOWN": HealthState.UNKNOWN,
    "DEGRADED": HealthState.DEGRADED,
}


@pytest.mark.SKA_low
def test_subarray_health_state():
    """Test telescope healthstate"""


@given(parsers.parse("CSP health is {csp_health}"))
def set_csp_health(simulators, csp_health):
    """Set the CSP subarray healthstate"""
    simulators[0].SetDirectHealthState(HEALTH_MAP[csp_health])


@given(parsers.parse("SDP health is {sdp_health}"))
def set_sdp_health(simulators, sdp_health):
    """Set the SDP subarray healthstate"""
    simulators[1].SetDirectHealthState(HEALTH_MAP[sdp_health])


@given(parsers.parse("MCCS health is {mccs_health}"))
def set_mccs_health(simulators, mccs_health):
    """Set the MCCS subarray healthstate"""
    simulators[2].SetDirectHealthState(HEALTH_MAP[mccs_health])


@when("health states are applied")
def subscribe_to_events(simulators, subarray_node_low, event_recorder):
    """Subscribe to events"""
    for sim in simulators:
        event_recorder.subscribe_event(sim, "healthState")
    event_recorder.subscribe_event(
        subarray_node_low.subarray_node, "healthState"
    )


@then(
    parsers.parse("the Subarray Node health state should be {expected_health}")
)
def assert_subarray_health(subarray_node_low, event_recorder, expected_health):
    """Check for subarray health state"""
    expected = HEALTH_MAP[expected_health]
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_node, "healthState", expected
    ), ("Expected Subarray Node HealthState to be %s", expected)

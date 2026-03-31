"""Test Subarray Node Healthinfo"""

import json
import time

import pytest
from assertpy import assert_that
from pytest_bdd import given, parsers, scenario, then, when
from ska_control_model import HealthState
from ska_tango_testing.mock.placeholders import Anything

from tests.resources.test_harness.helpers import LOGGER, get_device_simulators

state = {}


@pytest.mark.skip(reason="frequent failure")
@pytest.mark.SKA_low
@scenario(
    "../features/tmc/xtp_102560_check_healthinfo.feature",
    "Subarray reflects correct healthinfo of CSP, SDP, and MCCS subarrays",
)
def test_subarray_health_combined_states():
    """Test subarray node healthinfo based on CSP, SDP, MCCS healthstate"""


@given(parsers.parse("CSP health is {csp_health}"))
def set_csp_health(simulator_factory, csp_health, event_tracer):
    """Set the CSP healthstate"""
    event_tracer.clear_events()
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
    event_tracer, subarray_node_low, expected_health
):
    """Check the subarray healthstate"""
    event_tracer.subscribe_event(
        subarray_node_low.subarray_node, "healthState"
    )
    assert_that(event_tracer).has_change_event_occurred(
        subarray_node_low.subarray_node,
        "healthState",
        HealthState[expected_health],
    )


@then(
    parsers.parse(
        "the Subarray Node healthinfo should be {expected_health_info}"
    )
)
def check_subarray_node_health_info(
    event_tracer, subarray_node_low, expected_health_info
):
    """Check the subarray healthinfo"""
    event_tracer.subscribe_event(subarray_node_low.subarray_node, "healthInfo")
    assert_that(event_tracer).has_change_event_occurred(
        subarray_node_low.subarray_node,
        "healthInfo",
        Anything,
    )

    raw_health_info = subarray_node_low.subarray_node.healthInfo
    LOGGER.info("Raw healthInfo: %s", raw_health_info)

    try:
        health_info_dict = json.loads(raw_health_info)
    except json.JSONDecodeError as exc:
        LOGGER.error("Cannot parse healthInfo as JSON: %s", exc)
        pytest.fail("healthInfo is not valid JSON")

    LOGGER.info(
        "Formatted healthInfo:\n%s",
        json.dumps(health_info_dict, indent=4),
    )

    # Flatten all non-empty messages
    all_messages = [
        msg.strip()
        for leaf_node_msgs in health_info_dict.values()
        for msg in leaf_node_msgs
        if msg and msg.strip() != ""
    ]

    expected_messages = [
        msg.strip() for msg in expected_health_info.split(",") if msg.strip()
    ]

    LOGGER.info("Extracted health messages: %s", all_messages)
    LOGGER.info("Expected messages: %s", expected_messages)

    if expected_health_info != "EMPTY":
        for msg in expected_messages:
            assert msg in all_messages, (
                f"Expected message '{expected_health_info}' not"
                + " found in healthInfo"
            )

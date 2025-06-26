"""
This module defines a BDD (Behavior-Driven Development) test scenario
using pytest-bdd to verify the behavior of the Telescope Monitoring and
Control (TMC) system when the Abort command is executed in an EMPTY
observation state.
"""


import pytest
from assertpy import assert_that
from pytest_bdd import given, scenario, then, when
from ska_control_model import ObsState
from ska_tango_testing.integration import TangoEventTracer, log_events
from tango import DevFailed

from tests.resources.test_harness.subarray_node_low import (
    SubarrayNodeWrapperLow,
)
from tests.resources.test_support.constant_low import TIMEOUT


@pytest.mark.SKA_low
@scenario(
    "../features/tmc/check_abort_command.feature",
    "TMC executes Abort Command in EMPTY obsState.",
)
def test_abort_command_not_allowed_empty():
    """BDD test scenario for verifying execution of the Abort
    command in EMPTY obsState in TMC."""


@given("a Subarray in EMPTY obsState")
def given_tmc(
    subarray_node_low: SubarrayNodeWrapperLow, event_tracer: TangoEventTracer
):
    """Subarray in EMPTY obsState"""
    event_tracer.subscribe_event(subarray_node_low.subarray_node, "obsState")
    event_tracer.subscribe_event(
        subarray_node_low.subarray_node, "longRunningCommandResult"
    )
    subarray_node_low.move_to_on()
    log_events({subarray_node_low.subarray_node: ["obsState"]})
    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "GIVEN" STEP: '
        "Subarray Node device"
        f"({subarray_node_low.subarray_node.dev_name()}) "
        "is expected to be in EMPTY obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        subarray_node_low.subarray_node,
        "obsState",
        ObsState.EMPTY,
    )


@when("I Abort it")
def invoke_abort_command(subarray_node_low: SubarrayNodeWrapperLow):
    """Send a Abort command to the subarray."""
    with pytest.raises(DevFailed) as pytest.exception:
        subarray_node_low.execute_transition("Abort")


@then("TMC raises exception")
def invalid_command_rejection():
    """
    Verifies that the TMC rejects a command with ResultCode.REJECTED,
    and checks for a specific error message in the command result.
    """

    assert "Abort command not permitted in observation state EMPTY" in str(
        pytest.exception.value
    )


@then("the Subarray remains in obsState EMPTY")
def tmc_status(
    subarray_node_low: SubarrayNodeWrapperLow, event_tracer: TangoEventTracer
):
    """
    Verifies that the Subarray remains in the observation state EMPTY.
    """
    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "THEN" STEP: '
        '"the Subarray remains in obsState EMPTY"'
        "Subarray Node device"
        f"({subarray_node_low.subarray_node.dev_name()}) "
        "is expected to be in EMPTY obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        subarray_node_low.subarray_node,
        "obsState",
        ObsState.EMPTY,
    )

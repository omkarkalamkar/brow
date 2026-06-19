"""
This module defines a Pytest BDD test scenario for the successful execution of
Abort command of a Low Telescope Subarray in the Telescope Monitoring
and Control (TMC) system.
"""
import json

import pytest
from assertpy import assert_that
from pytest_bdd import given, parsers, scenario, then, when
from ska_control_model import ObsState, ResultCode
from ska_tango_testing.integration import TangoEventTracer, log_events
from tango import DevState

from tests.resources.test_harness.central_node_low import CentralNodeWrapperLow
from tests.resources.test_harness.constant import TIMEOUT
from tests.resources.test_harness.subarray_node_low import (
    SubarrayNodeWrapperLow,
)
from tests.resources.test_harness.utils.common_utils import JsonFactory
from tests.resources.test_support.common_utils.tmc_helpers import (
    prepare_json_args_for_centralnode_commands,
    prepare_json_args_for_commands,
    set_subarray_to_given_obs_state,
)


@pytest.mark.SKA_low
@scenario(
    "tmc/check_abort_command.feature",
    "TMC validates Abort Command",
)
def test_tmc_abort_command():
    """BDD test scenario for verifying successful execution of
    the Abort command in a TMC."""


@pytest.mark.SKA_low
@scenario(
    "tmc/check_abort_command.feature",
    "TMC validates Abort Command in intermediate obsState",
)
def test_tmc_abort_command_in_intermediate_obs_state():
    """BDD test scenario for verifying successful execution of
    the Abort command in a TMC for intermediate obsStates."""


@given(parsers.parse("a Subarray in {obs_state} obsState"))
def given_tmc(
    central_node_low: CentralNodeWrapperLow,
    subarray_node_low: SubarrayNodeWrapperLow,
    event_tracer: TangoEventTracer,
    command_input_factory: JsonFactory,
    obs_state: str,
):
    """Set up a TMC and ensure it is in the given ObsState."""
    event_tracer.subscribe_event(subarray_node_low.subarray_node, "obsState")
    event_tracer.subscribe_event(
        subarray_node_low.subarray_node, "longRunningCommandResult"
    )
    event_tracer.subscribe_event(
        subarray_node_low.subarray_node, "longRunningCommandInProgress"
    )
    event_tracer.subscribe_event(
        central_node_low.central_node, "telescopeState"
    )
    log_events(
        {
            central_node_low.central_node: ["telescopeState"],
            subarray_node_low.subarray_node: [
                "obsState",
                "longRunningCommandResult",
                "longRunningCommandInProgress",
            ],
        }
    )
    central_node_low.move_to_on()
    assert_that(event_tracer).described_as(
        "FAILED ASSUMPTION AFTER ON COMMAND: "
        "Central Node device"
        f"({central_node_low.central_node.dev_name()}) "
        "is expected to be in TelescopeState ON",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        central_node_low.central_node,
        "telescopeState",
        DevState.ON,
    )
    assign_input_str = prepare_json_args_for_centralnode_commands(
        "assign_resources_low", command_input_factory
    )
    configure_input_str = prepare_json_args_for_commands(
        "configure_low", command_input_factory
    )
    scan_input_str = prepare_json_args_for_commands(
        "scan_low", command_input_factory
    )
    central_node_low.store_resources(assign_input_str)

    assert_that(event_tracer).described_as(
        "FAILED ASSUMPTION AFTER ASSIGNRESOURCES COMMAND: "
        "Subarray Node device"
        f"({subarray_node_low.subarray_node.dev_name()}) "
        "is expected to be in IDLE obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        subarray_node_low.subarray_node,
        "obsState",
        ObsState.IDLE,
    )
    if obs_state == "READY":
        subarray_node_low.store_configuration_data(configure_input_str)
        assert_that(event_tracer).described_as(
            "FAILED ASSUMPTION in GIVEN Step: "
            "Subarray Node device"
            f"({subarray_node_low.subarray_node.dev_name()}) "
            f"is expected to be in {obs_state} obstate",
        ).within_timeout(TIMEOUT).has_change_event_occurred(
            subarray_node_low.subarray_node,
            "obsState",
            ObsState[obs_state],
        )
    elif obs_state == "SCANNING":
        subarray_node_low.store_configuration_data(configure_input_str)
        assert_that(event_tracer).described_as(
            "FAILED ASSUMPTION in GIVEN Step: "
            "Subarray Node device"
            f"({subarray_node_low.subarray_node.dev_name()}) "
            f"is expected to be in READY obstate",
        ).within_timeout(TIMEOUT).has_change_event_occurred(
            subarray_node_low.subarray_node,
            "obsState",
            ObsState.READY,
        )
        subarray_node_low.store_scan_data(scan_input_str)

        assert_that(event_tracer).described_as(
            "FAILED ASSUMPTION in GIVEN Step: "
            "Subarray Node device"
            f"({subarray_node_low.subarray_node.dev_name()}) "
            f"is expected to be in {obs_state} obstate",
        ).within_timeout(TIMEOUT).has_change_event_occurred(
            subarray_node_low.subarray_node,
            "obsState",
            ObsState[obs_state],
        )


@given(parsers.parse("a Subarray in intermediate obsState {obs_state}"))
def given_tmc_in_intermediate_obsstate(
    central_node_low: CentralNodeWrapperLow,
    subarray_node_low: SubarrayNodeWrapperLow,
    event_tracer: TangoEventTracer,
    obs_state: str,
    command_input_factory: JsonFactory,
):
    """Set up a TMC and ensure it is in the given ObsState."""
    event_tracer.subscribe_event(subarray_node_low.subarray_node, "obsState")
    event_tracer.subscribe_event(
        subarray_node_low.subarray_node, "longRunningCommandResult"
    )
    event_tracer.subscribe_event(subarray_node_low.subarray_node, "lrcQueue")
    event_tracer.subscribe_event(
        subarray_node_low.subarray_node, "longRunningCommandInProgress"
    )
    log_events(
        {
            subarray_node_low.subarray_node: [
                "obsState",
                "longRunningCommandResult",
                "longRunningCommandInProgress",
            ]
        }
    )
    central_node_low.move_to_on()
    set_subarray_to_given_obs_state(
        central_node_low,
        subarray_node_low,
        obs_state,
        event_tracer,
        command_input_factory,
    )
    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "GIVEN STEP: '
        f'"a Subarray in intermediate obsState {obs_state}"'
        "Subarray Node device"
        f"({subarray_node_low.subarray_node.dev_name()}) "
        f"is expected to be in {obs_state} obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        subarray_node_low.subarray_node,
        "obsState",
        ObsState[obs_state],
    )


@when("I Abort it")
def invoke_abort_command(
    subarray_node_low: SubarrayNodeWrapperLow, event_tracer: TangoEventTracer
):
    """Send a Abort command to the subarray."""
    _, unique_id = subarray_node_low.execute_transition("Abort")
    assert_that(event_tracer).described_as(
        "FAILED ASSUMPTION AFTER ABORT COMMAND: "
        "Central Node device"
        f"({subarray_node_low.subarray_node.dev_name()}) "
        "is expected have longRunningCommand as"
        '(unique_id,(ResultCode.OK,"Abort command completed"))',
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        subarray_node_low.subarray_node,
        "longRunningCommandResult",
        (
            unique_id[0],
            json.dumps((int(ResultCode.OK), "Abort command completed")),
        ),
    )
    # After abort command, the longRunningCommandInProgress and
    # lrcQueue attributes are expected to be empty
    assert_that(
        subarray_node_low.subarray_node.longRunningCommandInProgress
    ).described_as(
        'FAILED ASSUMPTION IN "THEN STEP: '
        '"the Subarray transitions to ABORTED obsState" '
        "longRunningCommandInProgress is expected to be empty"
    ).is_empty()

    assert_that(subarray_node_low.subarray_node.lrcQueue).described_as(
        'FAILED ASSUMPTION IN "THEN STEP: '
        '"the Subarray transitions to ABORTED obsState" '
        "lrcQueue is expected to be empty"
    ).is_empty()


@then("the Subarray transitions to ABORTED obsState")
def check_obs_state(
    subarray_node_low: SubarrayNodeWrapperLow,
    event_tracer: TangoEventTracer,
):
    """Verify that the subarray is in the ABORTED obsState."""
    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "THEN STEP: '
        f'"the Subarray transitions to ABORTED obsState"'
        "Subarray Node device"
        f"({subarray_node_low.subarray_node.dev_name()}) "
        f"is expected to be in ABORTING obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        subarray_node_low.subarray_node,
        "obsState",
        ObsState.ABORTING,
    )
    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "THEN STEP: '
        f'"the Subarray transitions to ABORTED obsState"'
        "Subarray Node device"
        f"({subarray_node_low.subarray_node.dev_name()}) "
        f"is expected to be in ABORTED obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        subarray_node_low.subarray_node, "obsState", ObsState.ABORTED
    )

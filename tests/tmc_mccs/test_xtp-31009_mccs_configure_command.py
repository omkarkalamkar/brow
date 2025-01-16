"""Test module for TMC-MCCS Configure functionality"""

import json

import pytest
from pytest_bdd import given, parsers, scenario, then, when
from ska_tango_base.control_model import ObsState
from tango import DevState

from tests.resources.test_harness.helpers import (
    prepare_json_args_for_centralnode_commands,
    prepare_json_args_for_commands,
    set_receive_address,
    update_eb_pb_ids,
)
from tests.resources.test_support.common_utils.result_code import ResultCode


@pytest.mark.tmc_mccs
@scenario(
    "../features/tmc_mccs/xtp-31009_configure.feature",
    "Configure a MCCS subarray for a scan",
)
def test_configure_command():
    """
    Test case to verify TMC-MCCS Configure functionality

    Glossary:
        - "central_node_low": fixture for a TMC CentralNode under test
        - "simulator_factory": fixture for SimulatorFactory class,
        which provides simulated subarray and master devices
        - "event_recorder": fixture for EventRecorder class
    """


@given("the Telescope is in the ON state")
def check_telescope_is_in_on_state(central_node_low, event_recorder) -> None:
    """Ensure telescope is in ON state."""
    central_node_low.move_to_on()
    event_recorder.subscribe_event(
        central_node_low.central_node, "telescopeState"
    )
    assert event_recorder.has_change_event_occurred(
        central_node_low.central_node,
        "telescopeState",
        DevState.ON,
        lookahead=10,
    )


@given(parsers.parse("obsState of subarray {subarray_id} is IDLE"))
def check_subarray_obs_state(
    subarray_node_low,
    central_node_low,
    event_recorder,
    command_input_factory,
    subarray_id,
):
    """Method to check subarray is in IDLE obstate"""
    event_recorder.subscribe_event(subarray_node_low.subarray_node, "obsState")
    central_node_low.set_subarray_id(subarray_id)
    event_recorder.subscribe_event(
        subarray_node_low.subarray_devices.get("mccs_subarray"), "obsState"
    )
    event_recorder.subscribe_event(
        central_node_low.central_node, "longRunningCommandResult"
    )
    assign_input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_low", command_input_factory
    )
    set_receive_address(central_node_low)
    input_json = update_eb_pb_ids(assign_input_json)
    _, unique_id = central_node_low.store_resources(input_json)
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_devices.get("mccs_subarray"),
        "obsState",
        ObsState.IDLE,
        lookahead=10,
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_node,
        "obsState",
        ObsState.IDLE,
        lookahead=10,
    )
    event_recorder.has_change_event_occurred(
        central_node_low.central_node,
        "longRunningCommandResult",
        (unique_id[0], json.dumps((int(ResultCode.OK), "Command Completed"))),
    )


@when("I configure to the subarray using TMC")
def invoke_configure(
    subarray_node_low,
    command_input_factory,
):
    """A method to invoke Configure command"""
    input_json = prepare_json_args_for_commands(
        "configure_low", command_input_factory
    )
    subarray_node_low.store_configuration_data(input_json)


@then("the MCCS subarray obsState must transition to the READY")
def check_mccs_subarray_in_ready(subarray_node_low, event_recorder):
    """A method to check MCCS subarray obsstate"""
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_devices["mccs_subarray"],
        "obsState",
        ObsState.READY,
        lookahead=10,
    )


@then("the TMC subarray is transitioned to READY obsState")
def check_tmc_subarray_obs_state(subarray_node_low, event_recorder):
    """A method to check TMC subarray obsstate"""
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_node,
        "obsState",
        ObsState.CONFIGURING,
        lookahead=15,
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_node, "obsState", ObsState.READY
    )

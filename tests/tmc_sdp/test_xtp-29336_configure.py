"""Test module for TMC-SDP Configure functionality"""
import json

import pytest
from pytest_bdd import given, parsers, scenario, then, when
from ska_tango_base.commands import ResultCode
from ska_tango_base.control_model import ObsState

from tests.resources.test_harness.helpers import (
    prepare_json_args_for_centralnode_commands,
    prepare_json_args_for_commands,
    update_eb_pb_ids,
)


@pytest.mark.tmc_sdp
@scenario(
    "../features/tmc_sdp/xtp-29336_configure.feature",
    "Configure a SDP subarray for a scan using TMC",
)
def test_tmc_sdp_configure(central_node_low):
    """
    Test case to verify TMC-SDP Configure functionality

    Glossary:
        - "central_node_low": fixture for a TMC CentralNode under test
        - "simulator_factory": fixture for SimulatorFactory class,
        which provides simulated subarray and master devices
        - "event_recorder": fixture for EventRecorder class
    """
    assert central_node_low.central_node.ping() > 0
    assert central_node_low.subarray_devices["sdp_subarray"].ping() > 0
    assert central_node_low.are_sdp_components_online()


# @given -> ../conftest.py


@given(parsers.parse("the subarray {subarray_id} obsState is IDLE"))
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
        central_node_low.central_node, "longRunningCommandResult"
    )
    event_recorder.subscribe_event(
        subarray_node_low.subarray_devices.get("sdp_subarray"), "obsState"
    )
    assign_input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_low", command_input_factory
    )
    input_json = update_eb_pb_ids(assign_input_json)

    _, unique_id = central_node_low.store_resources(input_json)

    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_devices.get("sdp_subarray"),
        "obsState",
        ObsState.IDLE,
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_node,
        "obsState",
        ObsState.IDLE,
    )
    assert event_recorder.has_change_event_occurred(
        central_node_low.central_node,
        "longRunningCommandResult",
        (
            unique_id[0],
            json.dumps((int(ResultCode.OK), "Command Completed")),
        ),
    )


@when(
    parsers.parse("I configure with {scan_type} to the subarray {subarray_id}")
)
def invoke_configure(
    subarray_node_low,
    event_recorder,
    scan_type,
    command_input_factory,
):
    """A method to invoke Configure command"""
    event_recorder.subscribe_event(
        subarray_node_low.subarray_node, "longRunningCommandResult"
    )
    input_json = prepare_json_args_for_commands(
        "configure_low", command_input_factory
    )
    input_json = json.loads(input_json)
    input_json["sdp"]["scan_type"] = scan_type
    _, unique_id = subarray_node_low.store_configuration_data(
        input_json=json.dumps(input_json)
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_node,
        "longRunningCommandResult",
        (
            unique_id[0],
            json.dumps((int(ResultCode.OK), "Command Completed")),
        ),
    )


# pylint: disable=unused-argument
@then(
    parsers.parse(
        "the SDP subarray {subarray_id} transitions to READY obsState"
    )
)
def check_sdp_subarray_in_ready(
    subarray_node_low, event_recorder, subarray_id
):
    """A method to check SDP subarray obsstate"""
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_devices["sdp_subarray"],
        "obsState",
        ObsState.READY,
    )


@then(
    parsers.parse(
        "SDP subarray scanType reflects correctly configured {scan_type}"
    )
)
def check_sdp_subarray_scan_type(subarray_node_low, event_recorder, scan_type):
    """A method to check SDP subarray obsstates"""
    event_recorder.subscribe_event(
        subarray_node_low.subarray_devices["sdp_subarray"], "scanType"
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_devices["sdp_subarray"],
        "scanType",
        scan_type,
    )


@then(
    parsers.parse(
        "the TMC subarray {subarray_id} transitions to READY obsState"
    )
)
def check_tmc_subarray_obs_state(subarray_node_low, event_recorder):
    """A method to check TMC subarray obsstate"""
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_node,
        "obsState",
        ObsState.READY,
    )

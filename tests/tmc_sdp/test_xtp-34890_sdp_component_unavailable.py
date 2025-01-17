"""Test TMC-SDP Negative Scenarios Unavailable subsystem"""
import json
import os

import pytest
from pytest_bdd import given, parsers, scenario, then, when
from ska_control_model import ObsState
from ska_tango_testing.mock.placeholders import Anything
from tango import DevState

from tests.resources.test_harness.helpers import update_eb_pb_ids
from tests.resources.test_support.common_utils.tmc_helpers import (
    prepare_json_args_for_centralnode_commands,
)


@pytest.mark.tmc_sdp_unhappy_path
@scenario(
    "../features/tmc_sdp/xtp-34890_sdp_component_unavailable.feature",
    "SDP Subarray report the error when one of the SDP's component is"
    + " unavailable",
)
def test_tmc_sdp_component_unavailable(central_node_low):
    """
    Test case to verify if TMC-SDP component is unavailable
    """
    assert central_node_low.subarray_devices["sdp_subarray"].ping() > 0


@given("a Telescope consisting of TMC,SDP,simulated CSP and simulated MCCS")
def given_tmc_with_simulated_csp_mccs():
    """A method to check if tmc subsystems are simulated."""

    assert os.environ.get("MCCS_SIMULATION_ENABLED") == "true"
    assert os.environ.get("SDP_SIMULATION_ENABLED") == "false"
    assert os.environ.get("CSP_SIMULATION_ENABLED") == "true"


@given("the telescope is in ON state")
def subarray_is_in_on_state(
    central_node_low,
    event_recorder,
):
    """A method to check if telescope in is ON telescopeState."""
    central_node_low.move_to_on()
    event_recorder.subscribe_event(
        central_node_low.central_node, "telescopeState"
    )
    assert event_recorder.has_change_event_occurred(
        central_node_low.central_node,
        "telescopeState",
        DevState.ON,
    )


@given("the subarray is in EMPTY obsState")
def subarray_is_in_empty_obsstate(
    subarray_node_low,
    event_recorder,
):
    """A method to check if telescope in is EMPTY obsSstate."""
    event_recorder.subscribe_event(subarray_node_low.subarray_node, "obsState")
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_node,
        "obsState",
        ObsState.EMPTY,
    )


@when("one of the SDP's component subsystem is made unavailable")
def sdp_proc_controller_unavailable():
    """
    Proc control is made unavailable in gitlab script
    """


@when(parsers.parse("I assign resources to the subarray {subarray_id}"))
def tmc_assign_resources_invoke(
    central_node_low, subarray_id, command_input_factory
):
    """
    Method to invoke AssignResources command.
    """
    central_node_low.set_subarray_id(subarray_id)
    input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_low", command_input_factory
    )

    input_json = update_eb_pb_ids(input_json)
    pytest.result, pytest.unique_id = central_node_low.perform_action(
        "AssignResources", input_json
    )


@then("SDP subarray report the unavailability of SDP Component")
def sdp_subarray_reports_unavailability(event_recorder, central_node_low):
    """
    Method to verify SDP subarray reports unavailability to TMC.
    """
    event_recorder.subscribe_event(
        central_node_low.central_node,
        "longRunningCommandResult",
    )
    exception_message = (
        " The processing controller, helm deployer, or both are OFFLINE:"
        + " cannot start processing blocks.\n"
    )
    pytest.assertion_data = event_recorder.has_change_event_occurred(
        central_node_low.central_node,
        attribute_name="longRunningCommandResult",
        attribute_value=(pytest.unique_id[0], Anything),
    )
    assert "AssignResources" in pytest.assertion_data["attribute_value"][0]
    assert (
        exception_message
        in json.loads(pytest.assertion_data["attribute_value"][1])[1]
    )


@then("TMC should report the error to client")
def tmc_reports_unavailability_to_client():
    """
    Method to verify TMC subarray reports unavailability to client.
    """
    exception_message = (
        " ska_low/tm_subarray_node/1: Exception occurred on the"
        + " following devices: ska_low/tm_leaf_node/sdp_subarray01:"
        + " The processing controller, helm deployer, or both are OFFLINE:"
        + " cannot start processing blocks.\n"
    )

    assert "AssignResources" in pytest.assertion_data["attribute_value"][0]
    assert (
        exception_message
        in json.loads(pytest.assertion_data["attribute_value"][1])[1]
    )


@then(parsers.parse("the TMC SubarrayNode {subarray_id} stuck in RESOURCING"))
def tmc_stuck_in_resourcing(subarray_node_low, event_recorder):
    """
    Method to verify the subarray stuck in RESOURCING obsstate
    """
    event_recorder.subscribe_event(subarray_node_low.subarray_node, "obsState")
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_node,
        "obsState",
        ObsState.RESOURCING,
    )

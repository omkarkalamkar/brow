"""Test TMC-SDP Abort functionality in RESOURCING obsState"""
import time

import pytest
from pytest_bdd import given, scenario, then
from ska_control_model import ObsState
from tango import DevState

from tests.resources.test_harness.helpers import (
    get_device_simulators,
    prepare_json_args_for_centralnode_commands,
    update_eb_pb_ids,
)
from tests.resources.test_harness.utils.enums import SimulatorDeviceType


@pytest.mark.tmc_sdp
@scenario(
    "../features/tmc_sdp/xtp-29582_abort_resourcing_tmc_sdp.feature",
    "Abort invocation using TMC",
)
def test_tmc_sdp_abort_in_resourcing(subarray_node_low):
    """
    Test case to verify TMC-SDP Abort functionality in RESOURCING obsState
    """
    assert subarray_node_low.central_node.ping() > 0
    assert subarray_node_low.subarray_devices["sdp_subarray"].ping() > 0


@given("TMC and SDP subarray are busy assigning resources")
def telescope_is_in_resourcing_obsstate(
    subarray_node_low,
    event_recorder,
    command_input_factory,
    central_node_low,
    simulator_factory,
):
    """A method to check if telescope in is resourcing obsSstate."""
    central_node_low.move_to_on()
    event_recorder.subscribe_event(
        subarray_node_low.central_node, "telescopeState"
    )
    assert event_recorder.has_change_event_occurred(
        central_node_low.central_node,
        "telescopeState",
        DevState.ON,
    )
    delay_command_params_str = '{"%s": %s}' % (
        "AssignResources",
        4,
    )
    mccs_subarray_sim = simulator_factory.get_or_create_simulator_device(
        SimulatorDeviceType.MCCS_SUBARRAY_DEVICE
    )
    csp_sim, _, _ = get_device_simulators(simulator_factory)
    csp_sim.SetDelayInfo(delay_command_params_str)
    mccs_subarray_sim.SetDelayInfo(delay_command_params_str)

    assign_input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_low", command_input_factory
    )
    input_json = update_eb_pb_ids(assign_input_json)
    central_node_low.perform_action("AssignResources", input_json)

    event_recorder.subscribe_event(
        subarray_node_low.subarray_devices.get("sdp_subarray"), "obsState"
    )
    event_recorder.subscribe_event(subarray_node_low.subarray_node, "obsState")
    event_recorder.subscribe_event(
        subarray_node_low.sdp_subarray_leaf_node, "sdpSubarrayObsState"
    )
    event_recorder.subscribe_event(
        subarray_node_low.csp_subarray_leaf_node, "cspSubarrayObsState"
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_devices.get("sdp_subarray"),
        "obsState",
        ObsState.RESOURCING,
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_node,
        "obsState",
        ObsState.RESOURCING,
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.sdp_subarray_leaf_node,
        "sdpSubarrayObsState",
        ObsState.RESOURCING,
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.csp_subarray_leaf_node,
        "cspSubarrayObsState",
        ObsState.RESOURCING,
    )
    csp_sim.ResetDelayInfo()
    mccs_subarray_sim.ResetDelayInfo()
    # The sleep is required here because subarraynode takes
    # some time to process obsstate resourcing, resulting
    # in invocation of abort command in empty obsstate
    time.sleep(1.8)


# @when -> ../conftest.py


@then("the SDP subarray should go into an aborted obsstate")
def sdp_subarray_is_in_aborted_obsstate(subarray_node_low, event_recorder):
    """
    Method to check SDP subarray is in ABORTED obsstate
    """
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_devices.get("sdp_subarray"),
        "obsState",
        ObsState.ABORTED,
    )


@then("the TMC subarray obsState transitions to ABORTED")
def tmc_subarray_is_in_aborted_obsstate(subarray_node_low, event_recorder):
    """
    Method to check if TMC subarray is in ABORTED obsstate
    """
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_node,
        "obsState",
        ObsState.ABORTED,
    )

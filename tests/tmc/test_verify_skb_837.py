"""
This module defines a BDD (Behavior-Driven Development) test scenario
using pytest-bdd to verify the behavior of the Telescope Monitoring and
Control (TMC) system resolution of SKB-476.
"""

import json

import pytest
from assertpy import assert_that
from pytest_bdd import given, scenario, then, when
from ska_control_model import ObsState
from ska_tango_base.commands import ResultCode
from ska_tango_testing.integration import TangoEventTracer
from tango import DevState

from tests.resources.test_harness.central_node_low import CentralNodeWrapperLow
from tests.resources.test_harness.subarray_node_low import (
    SubarrayNodeWrapperLow,
)
from tests.resources.test_harness.utils.common_utils import JsonFactory
from tests.resources.test_support.common_utils.tmc_helpers import (
    prepare_json_args_for_centralnode_commands,
    prepare_json_args_for_commands,
)
from tests.resources.test_support.constant_low import (
    EVENT_DEFECT,
    RECEIVE_ADDRESSES,
    RESET_DEFECT,
    TIMEOUT,
)


@pytest.mark.test
@pytest.mark.SKA_low
@scenario(
    "../features/tmc/check_configure_command_missing_event.feature",
    "Fallback to attribute‑read when no change event for attribute"
    " receiveAddresses",
)
def test_verify_skb_837():
    """BDD test scenario for verifying SKB-476"""


@given("subarray is in observation state IDLE")
def subarray_obsstate_in_idle(
    central_node_low: CentralNodeWrapperLow,
    command_input_factory: JsonFactory,
    event_tracer: TangoEventTracer,
):
    """
    This method invokes AssignResources command on central node.

    Args:
        central_node (CentralNodeWrapperLow): Object of Central node wrapper
        command_input_factory (JsonFactory): Object of json factory
        event_tracer(TangoEventTracer): object of TangoEventTracer used for
        managing the device events
    """
    event_tracer.subscribe_event(
        central_node_low.central_node, "telescopeState"
    )
    event_tracer.subscribe_event(
        central_node_low.central_node, "longRunningCommandResult"
    )
    event_tracer.subscribe_event(
        central_node_low.subarray_node, "longRunningCommandResult"
    )
    event_tracer.subscribe_event(
        central_node_low.sdp_subarray1, "receiveAddresses"
    )
    event_tracer.subscribe_event(central_node_low.subarray_node, "obsState")
    central_node_low.move_to_on()
    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "GIVEN STEP: '
        '"a TMC'
        "Central Node device"
        f"({central_node_low.central_node.dev_name()}) "
        "is expected to be in TelescopeState ON",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        central_node_low.central_node,
        "telescopeState",
        DevState.ON,
    )
    assign_input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_low", command_input_factory
    )
    result, pytest.unique_id = central_node_low.perform_action(
        "AssignResources", assign_input_json
    )
    assert pytest.unique_id[0].endswith("AssignResources")
    assert result[0] == ResultCode.QUEUED

    assert_that(event_tracer).described_as(
        "FAILED UNEXPECTED OBSSTATE: "
        "Subarray Node device"
        f"({central_node_low.subarray_node.dev_name()}) "
        "is expected to be in IDLE obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        central_node_low.subarray_node,
        "obsState",
        ObsState.IDLE,
    )


@given("change event data is EMPTY for attribute receiveAddresses")
def central_node_assign_resources(
    subarray_node_low: SubarrayNodeWrapperLow,
    event_tracer: TangoEventTracer,
):

    """
    This method invokes simulates empty event in sdpsubarray device

    Args:
        central_node (CentralNodeWrapperLow): Object of Central node wrapper
        event_tracer(TangoEventTracer): object of TangoEventTracer used for
        managing the device events
    """
    subarray_node_low.sdp_subarray1.SetDirectreceiveAddresses("{}")
    subarray_node_low.sdp_subarray1.SetDefective(EVENT_DEFECT)
    subarray_node_low.sdp_subarray1.SetDirectreceiveAddresses(
        RECEIVE_ADDRESSES
    )
    subarray_node_low.sdp_subarray1.SetDefective(json.dumps(RESET_DEFECT))
    assert_that(event_tracer).described_as(
        "SDP subarry "
        f"({subarray_node_low.sdp_subarray1.dev_name}) "
        "is expected to report the"
        "receiveAddresses as EMPTY"
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        subarray_node_low.sdp_subarray1,
        "receiveAddresses",
        "{}",
    )


@when("I configure the subarray")
def invoke_configure_command(
    command_input_factory: JsonFactory,
    subarray_node_low: SubarrayNodeWrapperLow,
    event_tracer: TangoEventTracer,
):
    """
    Method to verify the input json and invocation of configure command
    on subarray node.

    Args:
        command_input_factory (JsonFactory): Object of json factory.
        subarray_node_low (SubarrayNodeWrapperLow): Object of subarray
        node wrapper.

    """

    # Prepare initial JSON input for the configure command
    configure_input_json = prepare_json_args_for_commands(
        "configure_low", command_input_factory
    )

    # Invoke the command on the subarray node with the modified JSON
    subarray_node_low.store_configuration_data(configure_input_json)
    assert_that(event_tracer).described_as(
        "FAILED UNEXPECTED OBSSTATE: "
        "Subarray Node device"
        f"({subarray_node_low.subarray_node.dev_name()}) "
        "is expected to be in READY obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        subarray_node_low.subarray_node,
        "obsState",
        ObsState.CONFIGURING,
    )


@then("subarray node transitions to observation state READY")
def check_obs_state_ready(
    event_tracer: TangoEventTracer, subarray_node_low: SubarrayNodeWrapperLow
):
    """Method to check observation state of subarray node
    after configure command.

    Args:
        event_tracer(TangoEventTracer): object of TangoEventTracer used for
        managing the device events
        subarray_node_low (SubarrayNodeWrapperLow): Object of subarray
        node wrapper
    """
    assert_that(event_tracer).described_as(
        "FAILED UNEXPECTED OBSSTATE: "
        "Subarray Node device"
        f"({subarray_node_low.subarray_node.dev_name()}) "
        "is expected to be in READY obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        subarray_node_low.subarray_node,
        "obsState",
        ObsState.READY,
    )

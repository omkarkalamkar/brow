"""
This module defines a BDD (Behavior-Driven Development) test scenario
using pytest-bdd to verify the behavior of the Telescope Monitoring and
Control (TMC) system to verify the SKB-646.
"""


import json
import time

import pytest
from assertpy import assert_that
from pytest_bdd import given, scenario, then, when
from ska_control_model import ObsState
from ska_tango_base.commands import ResultCode
from ska_tango_testing.integration import TangoEventTracer, log_events
from tango import DevState

from tests.resources.test_harness.central_node_low import CentralNodeWrapperLow
from tests.resources.test_harness.helpers import (
    prepare_json_args_for_centralnode_commands,
    set_receive_address,
    wait_and_validate_device_attribute_value,
)
from tests.resources.test_harness.subarray_node_low import (
    SubarrayNodeWrapperLow,
)
from tests.resources.test_support.constant_low import (
    TIMEOUT,
    tmc_csp_subarray_leaf_node,
)


@pytest.mark.SKA_low
@scenario(
    "../features/tmc/SKB_646.feature",
    "Verify SKB-646",
)
def test_verify_skb_646():
    """BDD test scenario for verifying SKB-646"""


@given("ReleaseAllResource completed on CSP, MCCS, SDP Subarray")
def given_a_tmc(
    central_node_low: CentralNodeWrapperLow,
    subarray_node_low: SubarrayNodeWrapperLow,
    event_tracer: TangoEventTracer,
    command_input_factory,
):
    """
    This method invokes On command from central node and verifies
    the state of telescope after the invocation.
    Args:
        central_node (CentralNodeWrapperLow): Object of Central node wrapper
        event_tracer(TangoEventTracer): object of TangoEventTracer used for
        managing the device events
    """
    event_tracer.subscribe_event(
        central_node_low.central_node, "telescopeState"
    )
    event_tracer.subscribe_event(
        central_node_low.central_node, "longRunningCommandResult"
    )
    event_tracer.subscribe_event(subarray_node_low.subarray_node, "obsState")
    event_tracer.subscribe_event(
        subarray_node_low.subarray_node, "longRunningCommandResult"
    )
    event_tracer.subscribe_event(subarray_node_low.mccs_subarray1, "obsState")
    event_tracer.subscribe_event(subarray_node_low.csp_subarray1, "obsState")
    event_tracer.subscribe_event(subarray_node_low.sdp_subarray1, "obsState")

    event_tracer.subscribe_event(
        subarray_node_low.mccs_subarray_leaf_node, "obsState"
    )
    event_tracer.subscribe_event(
        subarray_node_low.csp_subarray_leaf_node, "cspSubarrayobsState"
    )
    event_tracer.subscribe_event(
        subarray_node_low.sdp_subarray_leaf_node, "sdpSubarrayobsState"
    )
    log_events(
        {
            central_node_low.central_node: [
                "telescopeState",
                "longRunningCommandResult",
            ],
            subarray_node_low.subarray_node: [
                "obsState",
                "longRunningCommandResult",
            ],
            subarray_node_low.mccs_subarray1: ["obsState"],
            subarray_node_low.csp_subarray1: ["obsState"],
            subarray_node_low.sdp_subarray1: ["obsState"],
            subarray_node_low.mccs_subarray_leaf_node: ["obsState"],
            subarray_node_low.csp_subarray_leaf_node: ["cspSubarrayobsState"],
            subarray_node_low.sdp_subarray_leaf_node: ["sdpSubarrayobsState"],
        }
    )

    central_node_low.move_to_on()
    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "GIVEN" STEP: '
        "'the telescope is is ON state'"
        "Central Node device"
        f"({central_node_low.central_node.dev_name()}) "
        "is expected to be in TelescopeState ON",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        central_node_low.central_node,
        "telescopeState",
        DevState.ON,
    )
    assert_that(event_tracer).described_as(
        "FAILED UNEXPECTED INITIAL OBSSTATE: "
        "Subarray Node device"
        f"({central_node_low.subarray_node.dev_name()}) "
        "is expected to be in EMPTY obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        central_node_low.subarray_node,
        "obsState",
        ObsState.EMPTY,
    )
    event_tracer.clear_events()

    set_receive_address(central_node_low)
    assign_input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_low", command_input_factory
    )
    _, unique_id = central_node_low.store_resources(assign_input_json)
    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "GIVEN" STEP: '
        "'the subarray is in IDLE obsState'"
        "Subarray Node device"
        f"({subarray_node_low.subarray_node.dev_name()}) "
        "is expected to be in IDLE obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        subarray_node_low.subarray_node,
        "obsState",
        ObsState.IDLE,
    )
    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "GIVEN" STEP: '
        "'the subarray is in IDLE obsState'"
        "Subarray Node device"
        f"({central_node_low.central_node.dev_name()}) "
        "is expected have longRunningCommand as"
        '(unique_id,(ResultCode.OK,"Command Completed"))',
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        central_node_low.central_node,
        "longRunningCommandResult",
        (unique_id[0], json.dumps((int(ResultCode.OK), "Command Completed"))),
    )

    event_tracer.clear_events()
    # Invoke release all  resource on csp, sdp, mccs
    subarray_node_low.mccs_subarray1.ReleaseAllResources()
    subarray_node_low.csp_subarray1.ReleaseAllResources()
    subarray_node_low.sdp_subarray1.ReleaseAllResources()

    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "GIVEN" STEP: '
        "'a mccs subarray in IDLE obsState'"
        "mccs subarray device"
        f"({subarray_node_low.mccs_subarray1.dev_name()}) "
        "is expected to be in EMPTY obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        subarray_node_low.mccs_subarray1,
        "obsState",
        ObsState.EMPTY,
    )
    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "GIVEN" STEP: '
        "'a csp subarray in IDLE obsState'"
        "CSP Subarray device"
        f"({subarray_node_low.csp_subarray1.dev_name()}) "
        "is expected to be in EMPTY obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        subarray_node_low.csp_subarray1,
        "obsState",
        ObsState.EMPTY,
    )
    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "GIVEN" STEP: '
        "'a subarray in IDLE obsState'"
        "SDP Subarray device"
        f"({subarray_node_low.sdp_subarray1.dev_name()}) "
        "is expected to be in EMPTY obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        subarray_node_low.sdp_subarray1,
        "obsState",
        ObsState.EMPTY,
    )

    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "GIVEN" STEP: '
        "'a mccs subarray leaf node in IDLE obsState'"
        "mccs subarray device"
        f"({subarray_node_low.mccs_subarray_leaf_node.dev_name()}) "
        "is expected to be in EMPTY obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        subarray_node_low.mccs_subarray_leaf_node,
        "obsState",
        ObsState.EMPTY,
    )
    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "GIVEN" STEP: '
        "'a csp subarray leaf node in IDLE obsState'"
        "CSP Subarray device"
        f"({subarray_node_low.csp_subarray_leaf_node.dev_name()}) "
        "is expected to be in EMPTY obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        subarray_node_low.csp_subarray_leaf_node,
        "cspSubarrayobsState",
        ObsState.EMPTY,
    )
    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "GIVEN" STEP: '
        "'a sdp subarray leaf in IDLE obsState'"
        "SDP Subarray device"
        f"({subarray_node_low.sdp_subarray_leaf_node.dev_name()}) "
        "is expected to be in EMPTY obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        subarray_node_low.sdp_subarray_leaf_node,
        "sdpSubarrayobsState",
        ObsState.EMPTY,
    )
    # This sleep is required because after empty event
    # received in subarray it take some time to process
    time.sleep(1)


@given("TMC Subarray is in RESOURCING Observation State")
def tmc_subarray_is_in_resourcing(
    subarray_node_low: SubarrayNodeWrapperLow, event_tracer: TangoEventTracer
):
    """
    Invoke Release All resource and check tmc subarray is in resourcing state
    """
    result, unique_id = subarray_node_low.execute_transition(
        "ReleaseAllResources"
    )
    assert result[0] == ResultCode.QUEUED
    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "GIVEN" STEP: '
        "'a subarray in IDLE obsState'"
        "Subarray Node device"
        f"({subarray_node_low.subarray_node.dev_name()}) "
        "is expected to be in Resourcing obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        subarray_node_low.subarray_node,
        "obsState",
        ObsState.RESOURCING,
    )
    exception_message = [
        "Exception occurred on the following devices:",
        f"{tmc_csp_subarray_leaf_node}:",
        "Command is not allowed",
    ]
    assert_that(event_tracer).described_as(
        "FAILED ASSUMPTION ATER ASSIGN RESOURCES: "
        "Central Node device"
        f"({subarray_node_low.subarray_node.dev_name()}) "
        "is expected have longRunningCommandResult"
        "(ResultCode.FAILED,exception)",
    ).within_timeout(TIMEOUT).has_desired_result_code_message_in_lrcr_event(
        subarray_node_low.subarray_node,
        exception_message,
        unique_id[0],
        ResultCode.FAILED,
    )


@when("I invoke init command on TMC Subarray")
def invoke_init_on_subarray(subarray_node_low: SubarrayNodeWrapperLow):
    """Invoke Init command on subarray"""
    subarray_node_low.subarray_node.init()
    wait_and_validate_device_attribute_value(
        subarray_node_low.subarray_node, "State", DevState.ON
    )
    # Wait for all events to receive
    time.sleep(1)


@when("wait for TMC Subarray Observation State transition to EMPTY")
def subarray_is_empty(subarray_node_low: SubarrayNodeWrapperLow, event_tracer):
    """Check subarray is in empty"""
    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "GIVEN" STEP: '
        "'a subarray in RESOURCING obsState'"
        "Subarray Node device"
        f"({subarray_node_low.subarray_node.dev_name()}) "
        "is expected to be in EMPTY obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        subarray_node_low.subarray_node,
        "obsState",
        ObsState.EMPTY,
    )
    event_tracer.clear_events()


@when("Assign Resources to TMC Subarray")
def assign_resources_to_subarray(
    central_node_low: CentralNodeWrapperLow,
    event_tracer: TangoEventTracer,
    command_input_factory,
):
    """Validate after init command assign resource is successful"""
    set_receive_address(central_node_low)
    assign_input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_low", command_input_factory
    )
    _, unique_id = central_node_low.perform_action(
        "AssignResources", assign_input_json
    )
    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "GIVEN" STEP: '
        "'the subarray is in IDLE obsState'"
        "Subarray Node device"
        f"({central_node_low.central_node.dev_name()}) "
        "is expected have longRunningCommand as"
        '(unique_id,(ResultCode.OK,"Command Completed"))',
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        central_node_low.central_node,
        "longRunningCommandResult",
        (unique_id[0], json.dumps((int(ResultCode.OK), "Command Completed"))),
    )


@then("TMC Subarray must be in IDLE Observation State")
def tmc_subarray_is_in_idle(
    subarray_node_low: SubarrayNodeWrapperLow, event_tracer: TangoEventTracer
):
    """Check Subarray is in IDLE obs state"""
    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "GIVEN" STEP: '
        "'a mccs subarray leaf node in EMPTY obsState'"
        "mccs subarray device"
        f"({subarray_node_low.mccs_subarray_leaf_node.dev_name()}) "
        "is expected to be in IDLE obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        subarray_node_low.mccs_subarray_leaf_node,
        "obsState",
        ObsState.IDLE,
    )
    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "GIVEN" STEP: '
        "'a csp subarray leaf node in EMPTY obsState'"
        "CSP Subarray device"
        f"({subarray_node_low.csp_subarray_leaf_node.dev_name()}) "
        "is expected to be in IDLE obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        subarray_node_low.csp_subarray_leaf_node,
        "cspSubarrayobsState",
        ObsState.IDLE,
    )
    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "GIVEN" STEP: '
        "'a sdp subarray leaf in EMPTY obsState'"
        "SDP Subarray device"
        f"({subarray_node_low.sdp_subarray_leaf_node.dev_name()}) "
        "is expected to be in IDLE obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        subarray_node_low.sdp_subarray_leaf_node,
        "sdpSubarrayobsState",
        ObsState.IDLE,
    )

    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "GIVEN" STEP: '
        "'the subarray is in EMPTY obsState'"
        "Subarray Node device"
        f"({subarray_node_low.subarray_node.dev_name()}) "
        "is expected to be in IDLE obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        subarray_node_low.subarray_node,
        "obsState",
        ObsState.IDLE,
    )

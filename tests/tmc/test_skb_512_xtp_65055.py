"""
This module defines a BDD (Behavior-Driven Development) test scenario
using pytest-bdd to verify the behavior of the Telescope Monitoring and
Control (TMC) system resolution of SKB-512.
"""


import json

import pytest
from assertpy import assert_that
from pytest_bdd import given, scenario, then, when
from ska_control_model import ObsState
from ska_tango_base.commands import ResultCode
from ska_tango_testing.integration import TangoEventTracer, log_events
from ska_tango_testing.mock.placeholders import Anything
from tango import DevState

from tests.resources.test_harness.central_node_low import CentralNodeWrapperLow
from tests.resources.test_harness.helpers import get_device_simulators
from tests.resources.test_harness.simulator_factory import SimulatorFactory
from tests.resources.test_harness.subarray_node_low import (
    SubarrayNodeWrapperLow,
)
from tests.resources.test_harness.utils.common_utils import JsonFactory
from tests.resources.test_support.common_utils.tmc_helpers import (
    prepare_json_args_for_centralnode_commands,
    prepare_json_args_for_commands,
)
from tests.resources.test_support.constant_low import (
    INTERMEDIATE_FAULT_OBS_STATE_DEFECT,
    RESET_DEFECT,
    TIMEOUT,
)


@pytest.mark.SKA_low
@scenario(
    "../features/tmc/SKB_512.feature",
    "TMC executes EndScan on other sub-systems even if one sub-system goes "
    + "to FAULT",
)
def test_verify_skb_512():
    """Test to verify TMC SubarrayNode invokes EndScan on all the Leaf Nodes
    even if one goes to FAULT
    """


@given("a TMC in SCANNING obsState")
def given_a_tmc_in_scanning_obs_state(
    central_node_low: CentralNodeWrapperLow,
    subarray_node_low: SubarrayNodeWrapperLow,
    command_input_factory: JsonFactory,
    event_tracer: TangoEventTracer,
):
    """
    This method brings TMC to Scanning ObsState
    Args:
        central_node (CentralNodeWrapperLow): Object of Central node wrapper
        subarray_node_low (SubarrayNodeWrapperLow): Object of subarray
        node wrapper
        command_input_factory (JsonFactory): object of TangoEventTracer
        used for
        event_tracer(TangoEventTracer): object of TangoEventTracer used for
        managing the device events
    """
    # Event Subscriptions
    event_tracer.subscribe_event(
        central_node_low.central_node, "telescopeState"
    )
    event_tracer.subscribe_event(
        central_node_low.central_node, "longRunningCommandResult"
    )
    event_tracer.subscribe_event(
        subarray_node_low.subarray_node, "longRunningCommandResult"
    )
    event_tracer.subscribe_event(central_node_low.subarray_node, "obsState")

    # Logging events
    log_events(
        {
            central_node_low.central_node: [
                "telescopeState",
                "longRunningCommandResult",
            ],
            central_node_low.subarray_node: [
                "longRunningCommandResult",
                "obsState",
            ],
        }
    )

    # Invoking commands on TMC
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

    assign_input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_low", command_input_factory
    )
    _, unique_id = central_node_low.store_resources(assign_input_json)
    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "GIVEN" STEP: '
        "'a TMC in SCANNING obsState'"
        "Subarray Node device"
        f"({central_node_low.subarray_node.dev_name()}) "
        "is expected to be in IDLE obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        central_node_low.subarray_node,
        "obsState",
        ObsState.IDLE,
    )
    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "GIVEN" STEP: '
        "'a TMC in SCANNING obsState'"
        "Subarray Node device"
        f"({central_node_low.central_node.dev_name()}) "
        "is expected have longRunningCommand as"
        '(unique_id,(ResultCode.OK,"Command Completed"))',
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        central_node_low.central_node,
        "longRunningCommandResult",
        (unique_id[0], json.dumps((int(ResultCode.OK), "Command Completed"))),
    )

    configure_input_json = prepare_json_args_for_commands(
        "configure_low", command_input_factory
    )
    _, unique_id = subarray_node_low.store_configuration_data(
        configure_input_json
    )
    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "GIVEN" STEP: '
        "'a TMC in SCANNING obsState'"
        "Subarray Node device"
        f"({central_node_low.subarray_node.dev_name()}) "
        "is expected to be in READY obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        central_node_low.subarray_node,
        "obsState",
        ObsState.READY,
    )
    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "GIVEN" STEP: '
        "'a TMC in SCANNING obsState'"
        "Subarray Node device"
        f"({central_node_low.subarray_node.dev_name()}) "
        "is expected have longRunningCommand as"
        '(unique_id,(ResultCode.OK,"Command Completed"))',
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        central_node_low.subarray_node,
        "longRunningCommandResult",
        (unique_id[0], json.dumps((int(ResultCode.OK), "Command Completed"))),
    )

    scan_input_json = prepare_json_args_for_commands(
        "scan_low", command_input_factory
    )
    _, unique_id = subarray_node_low.store_scan_data(scan_input_json)
    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "GIVEN" STEP: '
        "'a TMC in SCANNING obsState'"
        "Subarray Node device"
        f"({central_node_low.subarray_node.dev_name()}) "
        "is expected to be in SCANNING obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        central_node_low.subarray_node,
        "obsState",
        ObsState.SCANNING,
    )
    event_tracer.clear_events()


@when("I invoke EndScan command and a sub-system goes to FAULT")
def invoke_endscan_with_a_device_going_to_fault(
    subarray_node_low: SubarrayNodeWrapperLow,
    simulator_factory: SimulatorFactory,
    event_tracer: TangoEventTracer,
):
    """Method to call EndScan command with a device going to FAULT obsState

    Args:
        subarray_node_low (SubarrayNodeWrapperLow): Object of subarray
        node wrapper
    """
    # Event Subscription
    event_tracer.subscribe_event(
        subarray_node_low.csp_subarray_leaf_node, "cspSubarrayObsState"
    )

    csp_sim, _ = get_device_simulators(simulator_factory)
    csp_sim.SetDefective(json.dumps(INTERMEDIATE_FAULT_OBS_STATE_DEFECT))

    _, unique_id = subarray_node_low.execute_transition("EndScan")
    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "WHEN" STEP: '
        "'I invoke EndScan command and a sub-system goes to FAULT'"
        "CSP Subarray Leaf Node device"
        f"({subarray_node_low.csp_subarray_leaf_node.dev_name()}) "
        "is expected to be in FAULT obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        subarray_node_low.csp_subarray_leaf_node,
        "cspSubarrayObsState",
        ObsState.FAULT,
    )

    # Resetting defect for teardown.
    csp_sim.SetDefective(json.dumps(RESET_DEFECT))
    event_tracer.clear_events()


@then("the command is executed successfully on other sub-systems")
def check_obs_state_ready_for_leaf_nodes(
    event_tracer: TangoEventTracer,
    subarray_node_low: SubarrayNodeWrapperLow,
):
    """Method to check observation state of subarray leaf nodes
    after EndScan command.

    Args:
        event_tracer(TangoEventTracer): object of TangoEventTracer
        used for managing the device events
        subarray_node_low (SubarrayNodeWrapperLow): Object of subarray
        node wrapper
    """
    # Subscribing to events
    event_tracer.subscribe_event(
        subarray_node_low.sdp_subarray_leaf_node, "sdpSubarrayObsState"
    )
    event_tracer.subscribe_event(
        subarray_node_low.mccs_subarray_leaf_node, "obsState"
    )

    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "THEN" STEP: '
        "'the command is executed successfully on other sub-systems'"
        "SDP Subarray Leaf Node device"
        f"({subarray_node_low.sdp_subarray_leaf_node.dev_name()}) "
        "is expected to be in READY obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        subarray_node_low.sdp_subarray_leaf_node,
        "sdpSubarrayObsState",
        ObsState.READY,
    )
    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "THEN" STEP: '
        "'the command is executed successfully on other sub-systems'"
        "MCCS Subarray Leaf Node device"
        f"({subarray_node_low.mccs_subarray_leaf_node.dev_name()}) "
        "is expected to be in READY obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        subarray_node_low.mccs_subarray_leaf_node,
        "obsState",
        ObsState.READY,
    )

    exception_message = "Timeout has occurred, command failed"

    assert_that(event_tracer).described_as(
        "FAILED ASSUMPTION AFTER ENDSCAN COMMAND: "
        "Subarray Node device"
        f"({subarray_node_low.subarray_node.dev_name()}) "
        "is expected have longRunningCommandResult"
        "(ResultCode.FAILED,exception)",
    ).within_timeout(TIMEOUT).has_desired_result_code_message_in_lrcr_event(
        subarray_node_low.subarray_node,
        [exception_message],
        Anything,
        ResultCode.FAILED,
    )

    event_tracer.clear_events()

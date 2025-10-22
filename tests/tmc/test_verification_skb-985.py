"""
SKB-985 – Restart must abort an in-flight Configure when the Subarray is in
obsState FAULT (caused by a CSP defect), then complete successfully and leave
the Subarray in a clean EMPTY state.

Sequence exercised:
  1. Subarray  →  ON
  2. CentralNode → AssignResources  (Subarray moves to IDLE)
  3. Inject CSP Leaf-Node defect
  4. Subarray → Configure   ⟹   transitions to FAULT
  5. Clear defect, Subarray → Restart
     • Restart must abort Configure         (ResultCode.ABORTED)
     • Restart must complete successfully   (ResultCode.OK)
     • Subarray must return to obsState EMPTY
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
from tests.resources.test_harness.subarray_node_low import (
    SubarrayNodeWrapperLow,
)
from tests.resources.test_harness.utils.common_utils import JsonFactory
from tests.resources.test_support.common_utils.tmc_helpers import (
    prepare_json_args_for_centralnode_commands,
    prepare_json_args_for_commands,
)
from tests.resources.test_support.constant_low import (
    FAULT_DEFECT,
    RESET_DEFECT,
)

TIMEOUT = 100  # seconds


@pytest.mark.post_deployment
@pytest.mark.SKA_low
@scenario(
    "../features/tmc/check_restart_cleanup.feature",
    "Restart when Subarray is in obsState FAULT with"
    " CSP defective during Configure",
)
def test_restart_cleanup_skb_985():
    """Root test function created by pytest-bdd (does nothing by itself)."""


@given("a Subarray in IDLE obsState with resources assigned")
def given_subarray_ready(
    central_node_low: CentralNodeWrapperLow,
    subarray_node_low: SubarrayNodeWrapperLow,
    command_input_factory: JsonFactory,
    event_tracer: TangoEventTracer,
):
    """
    Bring the system to a usable IDLE state:

    • Set admin modes ONLINE,
    • Turn the Subarray ON,
    • Assign resources (CentralNode → AssignResources),
    • Verify the Subarray reaches ObsState.IDLE.
    """
    # Subscribe to events needed later
    event_tracer.subscribe_event(subarray_node_low.subarray_node, "obsState")

    event_tracer.subscribe_event(
        subarray_node_low.subarray_node, "longRunningCommandResult"
    )
    event_tracer.subscribe_event(
        central_node_low.central_node, "longRunningCommandResult"
    )
    event_tracer.subscribe_event(
        central_node_low.central_node, "telescopeState"
    )
    log_events(
        {
            subarray_node_low.subarray_node: [
                "obsState",
                "longRunningCommandResult",
            ],
            central_node_low.central_node: [
                "longRunningCommandResult",
                "telescopeState",
            ],
        }
    )

    # 1) Telescope → ON
    central_node_low.move_to_on()
    assert_that(event_tracer).within_timeout(
        TIMEOUT
    ).has_change_event_occurred(
        central_node_low.central_node, "telescopeState", DevState.ON
    )

    # Subarray starts EMPTY
    assert_that(event_tracer).within_timeout(
        TIMEOUT
    ).has_change_event_occurred(
        central_node_low.subarray_node, "obsState", ObsState.EMPTY
    )

    # 2) Assign resources → Subarray should become IDLE
    assign_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_low", command_input_factory
    )
    central_node_low.perform_action("AssignResources", assign_json)
    assert_that(event_tracer).within_timeout(
        TIMEOUT
    ).has_change_event_occurred(
        subarray_node_low.subarray_node, "obsState", ObsState.IDLE
    )


@given("the CSP Subarray is set to defective")
def inject_csp_defect(subarray_node_low: SubarrayNodeWrapperLow):
    """
    Introduce a fault in the CSP Subarray Leaf-Node to force a later FAULT
    transition during Configure.
    """
    subarray_node_low.subarray_devices["csp_subarray"].SetDefective(
        FAULT_DEFECT
    )


@given("I Configure the Subarray")
def configure_subarray(
    subarray_node_low: SubarrayNodeWrapperLow,
    command_input_factory: JsonFactory,
):
    """
    Invoke the Configure transition and stash its command-ID in pytest
    so we can check its final result later.
    """
    configure_json = prepare_json_args_for_commands(
        "configure_low", command_input_factory
    )
    pytest.configure_id = subarray_node_low.execute_transition(
        "Configure", configure_json
    )


@given("the Subarray transitions to observation state ObsState.FAULT")
def wait_for_fault(
    event_tracer: TangoEventTracer, central_node_low: CentralNodeWrapperLow
):
    """Block until the Subarray reports ObsState.FAULT."""
    assert_that(event_tracer).within_timeout(
        TIMEOUT
    ).has_change_event_occurred(
        central_node_low.subarray_node, "obsState", ObsState.FAULT
    )


@given(
    "the Subarray transitions to observation state ObsState.FAULT"
    " from RESOURCING"
)
def wait_for_fault_resourcing(
    event_tracer: TangoEventTracer, central_node_low: CentralNodeWrapperLow
):
    """Block until the Subarray reports ObsState.FAULT."""
    assert_that(event_tracer).within_timeout(
        TIMEOUT
    ).has_change_event_occurred(
        central_node_low.sdp_subarray_leaf_node,
        "sdpSubarrayObsState",
        ObsState.RESOURCING,
    )
    assert_that(event_tracer).within_timeout(
        TIMEOUT
    ).has_change_event_occurred(
        central_node_low.mccs_subarray_leaf_node,
        "obsState",
        ObsState.RESOURCING,
    )
    assert_that(event_tracer).within_timeout(
        TIMEOUT
    ).has_change_event_occurred(
        central_node_low.csp_subarray_leaf_node,
        "cspSubarrayObsState",
        ObsState.FAULT,
    )
    assert_that(event_tracer).within_timeout(
        TIMEOUT
    ).has_change_event_occurred(
        central_node_low.subarray_node, "obsState", ObsState.FAULT
    )


@when("I Restart the Subarray")
def restart_subarray(subarray_node_low: SubarrayNodeWrapperLow):
    """
    Clear the CSP defect and issue the Restart command, storing its command-ID
    for later verification.
    """
    csp_device = subarray_node_low.subarray_devices["csp_subarray"]
    csp_device.SetDefective(json.dumps(RESET_DEFECT))
    pytest.restart_id = subarray_node_low.execute_transition("Restart")


@then("the Configure command is aborted")
def verify_configure_aborted(
    subarray_node_low: SubarrayNodeWrapperLow, event_tracer: TangoEventTracer
):
    """Ensure the original Configure command
    finished with ResultCode.ABORTED."""
    assert_that(event_tracer).within_timeout(
        TIMEOUT
    ).has_change_event_occurred(
        subarray_node_low.subarray_node,
        "longRunningCommandResult",
        (
            pytest.configure_id[1][0],
            json.dumps([ResultCode.ABORTED, "Command has been aborted"]),
        ),
    )


@then("the Restart command is completed")
def verify_restart_completed(
    subarray_node_low: SubarrayNodeWrapperLow, event_tracer: TangoEventTracer
):
    """Ensure Restart itself completed with ResultCode.OK."""
    assert_that(event_tracer).within_timeout(
        TIMEOUT
    ).has_change_event_occurred(
        subarray_node_low.subarray_node,
        "longRunningCommandResult",
        (
            pytest.restart_id[1][0],
            json.dumps([int(ResultCode.OK), "Command Completed"]),
        ),
    )


@then("the Subarray node goes to obsState EMPTY")
def verify_subarray_empty(
    subarray_node_low: SubarrayNodeWrapperLow, event_tracer: TangoEventTracer
):
    """Ensure the Subarray returns to a clean EMPTY state."""
    assert_that(event_tracer).within_timeout(
        TIMEOUT
    ).has_change_event_occurred(
        subarray_node_low.subarray_node, "obsState", ObsState.EMPTY
    )


# test case with assignResources command


@pytest.mark.post_deployment
@pytest.mark.SKA_low
@pytest.mark.test
@scenario(
    "../features/tmc/check_restart_cleanup.feature",
    "Restart when Subarray is in obsState FAULT with"
    " CSP defective during AssignResources",
)
def test_restart_cleanup_csp_defective_before_assign():
    """Root test function created by pytest-bdd (does nothing by itself)."""


@given("a Subarray in EMPTY obsState with no resources assigned")
def given_subarray_empty(
    central_node_low: CentralNodeWrapperLow,
    subarray_node_low: SubarrayNodeWrapperLow,
    event_tracer: TangoEventTracer,
):
    """
    Bring the system to an EMPTY state(Subarray ON with no resources assigned):
    - Set admin modes ONLINE (handled internally by move_to_on),
    - Turn the Subarray ON (via CentralNode),
    - Verify the Subarray reaches ObsState.EMPTY.
    """
    # Subscribe to events needed for the test
    event_tracer.subscribe_event(subarray_node_low.subarray_node, "obsState")
    event_tracer.subscribe_event(
        subarray_node_low.subarray_node, "longRunningCommandResult"
    )
    event_tracer.subscribe_event(
        subarray_node_low.sdp_subarray_leaf_node, "sdpSubarrayObsState"
    )
    event_tracer.subscribe_event(
        subarray_node_low.csp_subarray_leaf_node, "cspSubarrayObsState"
    )
    event_tracer.subscribe_event(
        subarray_node_low.mccs_subarray_leaf_node, "obsState"
    )
    event_tracer.subscribe_event(
        central_node_low.central_node, "longRunningCommandResult"
    )
    event_tracer.subscribe_event(
        central_node_low.central_node, "telescopeState"
    )
    log_events(
        {
            subarray_node_low.subarray_node: [
                "obsState",
                "longRunningCommandResult",
            ],
            central_node_low.central_node: [
                "longRunningCommandResult",
                "telescopeState",
            ],
            subarray_node_low.sdp_subarray_leaf_node: ["sdpSubarrayObsState"],
            subarray_node_low.csp_subarray_leaf_node: ["cspSubarrayObsState"],
            subarray_node_low.mccs_subarray_leaf_node: ["obsState"],
        }
    )

    # 1) Turn the telescope (CentralNode) ON
    central_node_low.move_to_on()
    # Ensure the CentralNode reports state ON
    assert_that(event_tracer).within_timeout(
        TIMEOUT
    ).has_change_event_occurred(
        central_node_low.central_node, "telescopeState", DevState.ON
    )
    # The Subarray should start in EMPTY obsState (no resources assigned yet)
    assert_that(event_tracer).within_timeout(
        TIMEOUT
    ).has_change_event_occurred(
        subarray_node_low.subarray_node, "obsState", ObsState.EMPTY
    )


@given("I Assign resources to the Subarray")
def assign_resources_to_subarray(
    central_node_low: CentralNodeWrapperLow,
    command_input_factory: JsonFactory,
):
    """
    Invoke the AssignResources command on the CentralNode.
    """
    assign_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_low", command_input_factory
    )
    pytest.assign_id = central_node_low.perform_action(
        "AssignResources", assign_json
    )


@then("the AssignResources command is aborted")
def verify_assign_aborted(
    subarray_node_low, central_node_low, event_tracer: TangoEventTracer
):
    """Ensure the AssignResources command finished with ResultCode.ABORTED."""
    # testing with Anything placeholder as
    # we don't have commandid of assign resources command on subarray node
    assert_that(event_tracer).within_timeout(
        TIMEOUT
    ).has_change_event_occurred(
        subarray_node_low.subarray_node,
        "longRunningCommandResult",
        (
            Anything,
            json.dumps([ResultCode.ABORTED, "Command has been aborted"]),
        ),
    )
    assert_that(event_tracer).within_timeout(
        TIMEOUT
    ).has_change_event_occurred(
        central_node_low.central_node,
        "longRunningCommandResult",
        (
            pytest.assign_id[1][0],
            Anything,
        ),
    )

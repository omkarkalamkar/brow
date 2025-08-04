"""
This module defines a BDD (Behaviour-Driven Development) test scenario,
verifying SKB-985: the TMC SubarrayNode's Restart command must abort any
ongoing work (threads/commands) and complete successfully, after which the
system is left in a clean state.

The scenario exercises the path:
  1. Subarray ⇢ On
  2. CentralNode ⇢ AssignResources  (resources move Subarray to IDLE)
  3. Inject CSP Leaf-Node defect
  4. Subarray ⇢ Configure  → transitions to FAULT
  5. Clear defects, Subarray ⇢ Restart
     • Restart must abort Configure (ResultCode.ABORTED)
     • Restart must complete (ResultCode.OK)
"""

import json

import pytest
from assertpy import assert_that
from pytest_bdd import given, scenario, then, when
from ska_control_model import ObsState
from ska_tango_base.commands import ResultCode
from ska_tango_testing.integration import TangoEventTracer, log_events
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

TIMEOUT = 90  # seconds


@pytest.mark.test1
@pytest.mark.post_deployment
@pytest.mark.SKA_low
@scenario(
    "../features/tmc/check_restart_cleanup.feature",
    "TMC closes ongoing commands on Restart after Fault",
)
def test_restart_cleanup_skb_985():
    """BDD shell for SKB-985 Restart-cleanup scenario."""


# ─────────────────────────── GIVEN ────────────────────────────
@given("a Subarray in IDLE obsState with resources assigned")
def given_subarray_ready(
    central_node_low: CentralNodeWrapperLow,
    subarray_node_low: SubarrayNodeWrapperLow,
    command_input_factory: JsonFactory,
    event_tracer: TangoEventTracer,
):
    """
    • Sets admin modes ONLINE,
    • Turns Subarray ON,
    • Assigns resources from the CentralNode (moving Subarray to IDLE).
    """

    # Subscribe for state & LRCR events used later
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
                "telescopeState",
            ],
            central_node_low.central_node: ["longRunningCommandResult"],
        }
    )

    # 1) Subarray -> ON
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

    # 2) CentralNode -> AssignResources
    assign_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_low", command_input_factory
    )
    central_node_low.perform_action("AssignResources", assign_json)

    # Helper: MCCS Subarray LN reports IDLE once resources are assigned

    # Wait for Subarray to land in IDLE
    assert_that(event_tracer).described_as(
        "Subarray should enter IDLE after AssignResources"
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        subarray_node_low.subarray_node, "obsState", ObsState.IDLE
    )


# ─────────────────────────── WHEN ─────────────────────────────
@when("the CSP Subarray is set to defective")
def inject_csp_defect(subarray_node_low: SubarrayNodeWrapperLow):
    """Introduce a fault on the CSP Subarray LN to force FAULT."""
    # Set the CSP Subarray LN to defective
    # csp_device = subarray_node_low.subarray_devices["csp_subarray"]
    # csp_device.SetDefective(FAULT_DEFECT)
    csp_device = subarray_node_low.subarray_devices["csp_subarray"]
    csp_device.SetDefective(FAULT_DEFECT)


@when("I Configure the Subarray")
def configure_subarray(
    subarray_node_low: SubarrayNodeWrapperLow, command_input_factory
):
    """Issue Configure; store command-id for later assertions."""
    configure_json = prepare_json_args_for_commands(
        "configure_low", command_input_factory
    )
    pytest.configure_id = subarray_node_low.execute_transition(
        "Configure", configure_json
    )


# ─────────────────────────── THEN ─────────────────────────────
@then("the Subarray transitions to observation state ObsState.FAULT")
def verify_fault_state(
    event_tracer: TangoEventTracer,
    central_node_low: CentralNodeWrapperLow,
):
    """Wait for FAULT transition caused by defective CSP LN."""
    assert_that(event_tracer).described_as(
        "FAILED UNEXPECTED INITIAL OBSSTATE: "
        "Subarray Node device"
        f"({central_node_low.subarray_node.dev_name()}) "
        "is expected to be in FAULT obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        central_node_low.subarray_node,
        "obsState",
        ObsState.FAULT,
    )


# ─────────────────────────── WHEN ─────────────────────────────
@when("I Restart the Subarray")
def restart_subarray(subarray_node_low):
    """
    • Clears CSP defects,
    • Invokes Restart,
    • Stores restart-command id for later checks.
    """
    csp_device = subarray_node_low.subarray_devices["csp_subarray"]
    csp_device.SetDefective(json.dumps(RESET_DEFECT))
    pytest.restart_id = subarray_node_low.invoke_command("Restart")


# ─────────────────────────── THEN ─────────────────────────────
@then("the Restart command completes and the Configure command is aborted")
def verify_restart_cleanup(subarray_node_low, event_tracer: TangoEventTracer):
    """
    Validate:
      • Configure ended ABORTED,
      • Restart completed OK,
      • Subarray left FAULT and re-entered IDLE (implicit in completion).
    """

    assert (
        assert_that(event_tracer)
        .described_as(
            "FAILED UNEXPECTED INITIAL OBSSTATE: "
            "Subarray Node device"
            f"({subarray_node_low.subarray_node.dev_name()}) "
            "is expected to be in EMPTY obstate",
        )
        .within_timeout(TIMEOUT)
        .has_change_event_occurred(
            subarray_node_low.subarray_node,
            "longRunningCommandResult",
            (
                pytest.configure_id,
                json.dumps(
                    (int(ResultCode.ABORTED), "Command has been aborted")
                ),
            ),
        )
    )
    assert (
        assert_that(event_tracer)
        .described_as(
            "FAILED UNEXPECTED INITIAL OBSSTATE: "
            "Subarray Node device"
            f"({subarray_node_low.subarray_node.dev_name()}) "
            "is expected to be in EMPTY obstate",
        )
        .within_timeout(TIMEOUT)
        .has_change_event_occurred(
            subarray_node_low.subarray_node,
            "longRunningCommandResult",
            (
                pytest.restart_id,
                json.dumps((int(ResultCode.OK), "Command Completed")),
            ),
        )
    )

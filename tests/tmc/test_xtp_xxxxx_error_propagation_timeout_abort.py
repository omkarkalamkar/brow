"""Test case to verify error propagation functionality for
the Abort command"""
import json

import pytest
from assertpy import assert_that
from pytest_bdd import given, parsers, scenario, then, when
from ska_control_model import ObsState
from ska_integration_test_harness.facades.csp_facade import CSPFacade
from ska_integration_test_harness.facades.sdp_facade import SDPFacade
from ska_integration_test_harness.facades.tmc_facade import TMCFacade
from ska_integration_test_harness.inputs.test_harness_inputs import (
    TestHarnessInputs,
)
from ska_tango_testing.integration import TangoEventTracer

from tests.conftest import SubarrayTestContextData, _setup_event_subscriptions
from tests.resources.test_harness.constant import ERROR_PROPAGATION_DEFECT

TIMEOUT = 60


@pytest.mark.test
@pytest.mark.SKA_low
@scenario(
    "../features/tmc/error_propagation_timeout_abort.feature",
    "Error Propagation Reported by TMC Low Abort Command for "
    "Defective Subarray",
)
def test_tmc_command_error_propagation():
    """
    Test case to verify TMC Error Propagation functionality.
    """


exception_message = (
    '[3, "Exception occurred on the following devices: '
    'low-tmc/subarray-leaf-node-csp/01: Exception occurred, command failed."]'
)


# @given ---> conftest


@given("TMC subarray is in ObsState IDLE")
def subarray_in_ready_state(
    context_fixt: SubarrayTestContextData,
    tmc: TMCFacade,
    sdp: SDPFacade,
    csp: CSPFacade,
    event_tracers: TangoEventTracer,
    default_commands_inputs: TestHarnessInputs,
):
    """Ensure the subarray is in the initial obsstate state."""
    _setup_event_subscriptions(tmc, csp, sdp, event_tracers)
    context_fixt.starting_state = ObsState.IDLE

    tmc.force_change_of_obs_state(
        ObsState.IDLE,
        default_commands_inputs,
        wait_termination=True,
    )


@when(
    parsers.parse(
        "Abort is invoked on a defective subsystem {defectiveSubsystem}"
    )
)
def execute_command_abort(
    tmc: TMCFacade, context_fixt: SubarrayTestContextData, csp: CSPFacade
):
    """
    Executes the Abort command on the TMC Subarray Node.
    """
    csp.csp_subarray.SetDefective(ERROR_PROPAGATION_DEFECT)
    context_fixt.when_action_name = "Abort"
    _, pytest.unique_id = tmc.subarray_node.Abort()


@then("TMC SubarrayNode obsstate changes to FAULT obsState")
def verify_fault_obsstate(
    tmc: TMCFacade,
    event_tracers: TangoEventTracer,
):
    """
    Verify the subarray's transition to the FAULT observation state.
    """
    assert_that(event_tracers).described_as(
        'FAILED ASSUMPTION IN "THEN" STEP: '
        "'the tmc subarray must be in the ABORTING obsState' "
        "TMC Subarray device"
        f"({tmc.subarray_node.dev_name()}) "
        "is expected to be in ABORTING obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        tmc.subarray_node,
        "obsState",
        ObsState.ABORTING,
    )

    assert_that(event_tracers).described_as(
        'FAILED ASSUMPTION IN "THEN" STEP: '
        "'the tmc subarray must be in the FAULT obsState' "
        "TMC Subarray device"
        f"({tmc.subarray_node.dev_name()}) "
        "is expected to be in FAULT obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        tmc.subarray_node,
        "obsState",
        ObsState.FAULT,
    )


@then("the command failure is reported by TMC SubarrayNode with error message")
def error_reporting(
    tmc: TMCFacade,
    csp: CSPFacade,
    event_tracers: TangoEventTracer,
):
    """Validates that an error is correctly reported by the TMC.

    This function checks if an error message is generated and logged
    by the TMC when the AssignResources command fails due to a defective
    MCCS Controller.
    It verifies the error reporting mechanism by asserting the expected
    failure message in the longRunningCommandResult event."""

    assert_that(event_tracers).described_as(
        'FAILED ASSUMPTION IN "THEN" STEP: '
        '"the command failure is reported by subarray_node with appropriate"'
        '"error message"'
        "SubarrayNode device"
        f"({tmc.subarray_node.dev_name()}) "
        "is expected have longRunningCommandResult"
        "(ResultCode.FAILED,exception)",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        tmc.subarray_node,
        "longRunningCommandResult",
        (pytest.unique_id[0], exception_message),
    )
    csp.csp_subarray.SetDefective(json.dumps({"enabled": False}))

    csp.csp_subarray.Abort()

    assert_that(event_tracers).within_timeout(5).has_change_event_occurred(
        csp.csp_subarray,
        "obsState",
        ObsState.ABORTED,
    )

    tmc.subarray_node.Restart()
    assert_that(event_tracers).within_timeout(5).has_change_event_occurred(
        tmc.subarray_node, "obsState", ObsState.EMPTY
    )

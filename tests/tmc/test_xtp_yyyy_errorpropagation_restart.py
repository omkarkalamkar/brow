"""Test case to verify error propagation functionality for
the Restart command"""
import json

import pytest
from assertpy import assert_that
from pytest_bdd import given, parsers, scenario, then, when
from ska_control_model import ObsState
from ska_integration_test_harness.facades.csp_facade import CSPFacade
from ska_integration_test_harness.facades.mccs_facade import MCCSFacade
from ska_integration_test_harness.facades.sdp_facade import SDPFacade
from ska_integration_test_harness.facades.tmc_facade import TMCFacade
from ska_integration_test_harness.inputs.test_harness_inputs import (
    TestHarnessInputs,
)
from ska_tango_testing.integration import TangoEventTracer

from tests.conftest import SubarrayTestContextData, _setup_event_subscriptions
from tests.resources.test_harness.constant import (
    ERROR_PROPAGATION_DEFECT,
    FAILED_RESULT_DEFECT,
)

TIMEOUT = 60


@pytest.mark.SKA_low
@scenario(
    "../features/tmc/error_propagation_timeout_abort.feature",
    "Error Propagation Reported by TMC Low Restart Command for "
    "Defective Subarray",
)
def test_tmc_command_error_propagation():
    """
    Test case to verify TMC Error Propagation functionality.
    """


exception_messages = {
    "CSP": (
        '[3, "Exception occurred on the following devices: '
        "low-tmc/subarray-leaf-node-csp/01: Exception occurred, "
        'command failed."]'
    ),
    "SDP": (
        '[3, "Exception occurred on the following devices: '
        "low-tmc/subarray-leaf-node-sdp/01: Exception occurred, "
        'command failed"]'
    ),
    "MCCS": (
        '[3, "Exception occurred on the following devices: '
        "low-tmc/subarray-leaf-node-mccs/01: Exception occurred, "
        'command failed."]'
    ),
}


# @given ---> conftest


@given(parsers.parse("TMC subarray is in ABORTED ObsState"))
def subarray_in_aborted_state(
    context_fixt: SubarrayTestContextData,
    tmc: TMCFacade,
    sdp: SDPFacade,
    csp: CSPFacade,
    mccs: MCCSFacade,
    event_tracers: TangoEventTracer,
    default_commands_inputs: TestHarnessInputs,
):
    """Ensure the subarray is in the initial obsstate state."""
    _setup_event_subscriptions(tmc, csp, sdp, mccs, event_tracers)
    context_fixt.starting_state = ObsState.ABORTED
    tmc.force_change_of_obs_state(
        ObsState.ABORTED,
        default_commands_inputs,
        wait_termination=True,
    )


@when(
    parsers.parse(
        "Restart is invoked on a defective subsystem {defectiveSubsystem}"
    )
)
def execute_command_restart(
    tmc: TMCFacade,
    context_fixt: SubarrayTestContextData,
    csp: CSPFacade,
    sdp: SDPFacade,
    mccs: MCCSFacade,
    defectiveSubsystem: str,
):
    """
    Executes the Restart command on the TMC Subarray Node.
    """
    if defectiveSubsystem == "CSP":
        csp.csp_subarray.SetDefective(ERROR_PROPAGATION_DEFECT)
    elif defectiveSubsystem == "SDP":
        sdp.sdp_subarray.SetDefective(FAILED_RESULT_DEFECT)
    elif defectiveSubsystem == "MCCS":
        mccs.mccs_subarray.SetDefective(ERROR_PROPAGATION_DEFECT)
    context_fixt.when_action_name = "Restart"
    _, pytest.unique_id = tmc.subarray_node.Restart()


@then(
    parsers.parse(
        "the command failure is reported by subarray with error message "
        "with {defectiveSubsystem}"
    )
)
def error_reporting(
    tmc: TMCFacade,
    csp: CSPFacade,
    sdp: SDPFacade,
    mccs: MCCSFacade,
    event_tracers: TangoEventTracer,
    defectiveSubsystem: str,
):
    """Validates that an error is correctly reported by the TMC.

    This function checks if an error message is generated and logged
    by the TMC when the AssignResources command fails due to a defective
    MCCS Controller.
    It verifies the error reporting mechanism by asserting the expected
    failure message in the longRunningCommandResult event."""
    expected_msg = exception_messages[defectiveSubsystem]

    assert_that(event_tracers).within_timeout(
        TIMEOUT
    ).has_change_event_occurred(
        tmc.subarray_node,
        "longRunningCommandResult",
        (pytest.unique_id[0], expected_msg),
    )

    # Reset subsystem and bring it to ABORTED so TMC can be restarted
    if defectiveSubsystem == "CSP":
        csp.csp_subarray.SetDefective(json.dumps({"enabled": False}))
        csp.csp_subarray.Restart()
        assert_that(event_tracers).within_timeout(5).has_change_event_occurred(
            csp.csp_subarray, "obsState", ObsState.EMPTY
        )
    elif defectiveSubsystem == "SDP":
        sdp.sdp_subarray.SetDefective(json.dumps({"enabled": False}))
        sdp.sdp_subarray.Restart()
        assert_that(event_tracers).within_timeout(5).has_change_event_occurred(
            sdp.sdp_subarray, "obsState", ObsState.EMPTY
        )
    elif defectiveSubsystem == "MCCS":
        mccs.mccs_subarray.SetDefective(json.dumps({"enabled": False}))
        mccs.mccs_subarray.Restart()
        assert_that(event_tracers).within_timeout(5).has_change_event_occurred(
            mccs.mccs_subarray, "obsState", ObsState.EMPTY
        )

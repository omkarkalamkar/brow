"""
Test case to verify error propagation functionality for
the Abort command

This test case verifies that one of  the MCCS/CSP/SDP Subarray
is identified as defective,
 and the required command is executed on the TMC Low,
 then Subarry node
   reports an error.
"""
import pytest
from assertpy import assert_that
from pytest_bdd import given, parsers, scenario, then, when
from ska_control_model import ObsState, ResultCode
from ska_integration_test_harness.facades.csp_facade import CSPFacade
from ska_integration_test_harness.facades.mccs_facade import MCCSFacade
from ska_integration_test_harness.facades.sdp_facade import SDPFacade
from ska_integration_test_harness.facades.tmc_facade import TMCFacade
from ska_integration_test_harness.inputs.test_harness_inputs import (
    TestHarnessInputs,
)
from ska_tango_testing.integration import TangoEventTracer, log_events

from tests.conftest import SubarrayTestContextData
from tests.resources.test_harness.constant import (
    ERROR_PROPAGATION_DEFECT,
    low_csp_subarray_leaf_node,
    low_sdp_subarray_leaf_node,
    mccs_subarray_leaf_node,
)

# from tests.resources.test_harness.utils.my_file_json_input import (
#     MyFileJSONInput,
# )

TIMEOUT = 80


@pytest.mark.SKA_low
@scenario(
    "../features/tmc/error_propagation_timeout_abort.feature",
    "Error Propagation Reported by TMC Low Abort Commands for Defective "
    "Subarray",
)
def test_tmc_command_error_propagation():
    """
    Test case to verify TMC Error Propagation functionality.
    """


@pytest.mark.SKA_low
@scenario(
    "../features/tmc/xtp_xxxxx_error_propagation_timeout_abort.feature",
    "TimeOut Reported by TMC Low Abort Command for Defective Subarray",
)
def test_tmc_command_timeout_error_propagation():
    """
    Test case to verify TMC TimeOut Error Propagation functionality.
    """


@given("the telescope is in the ON state")
def given_the_telescope_is_in_on_state(
    tmc: TMCFacade,
    event_tracers: TangoEventTracer,
):
    """Ensure the telescope is in ON state."""
    tmc.move_to_on(wait_termination=True)
    event_tracers.subscribe_event(tmc.central_node, "telescopeState")
    event_tracers.subscribe_event(tmc.central_node, "longRunningCommandResult")
    event_tracers.subscribe_event(tmc.subarray_node, "obsState")
    event_tracers.subscribe_event(
        tmc.subarray_node, "longRunningCommandResult"
    )

    # Logging setup
    log_events(
        {
            tmc.central_node: [
                "telescopeState",
                "longRunningCommandResult",
            ],
            tmc.subarray_node: [
                "obsState",
                "longRunningCommandResult",
            ],
        }
    )
    # Assertions
    event_tracers.clear_events()


@given(
    parsers.parse(
        "the TMC subarray is in the {initialObsState} observation state"
    )
)
def set_subarray_obs_state(
    initialObsState: str,
    tmc: TMCFacade,
    context_fixt: SubarrayTestContextData,
):
    """Sets the TMC subarray to the specified observation state.

    This step is used in BDD tests to ensure the subarray is in a known
    ObsState before triggering further actions such as Abort or Restart."""
    target_obs_state = getattr(ObsState, initialObsState.upper())
    context_fixt.starting_state = target_obs_state
    tmc.force_change_of_obs_state(
        target_obs_state,
        TestHarnessInputs(),
        wait_termination=True,
    )


@when(
    parsers.parse(
        "{command} is invoked on a defective subsystem {defectiveSubsystem}"
    )
)
def defect_subsystem_and_invoke_command(
    command: str,
    defectiveSubsystem: str,
    tmc: TMCFacade,
    csp: CSPFacade,
    mccs: MCCSFacade,
    sdp: SDPFacade,
    event_tracers: TangoEventTracer,
):
    """This step simulates a failure in one of the subsystems
    (CSP, SDP, or MCCS) by setting it to a defective state,
    then triggers the given command (e.g., Abort, Restart)
    on the TMC SubarrayNode to verify proper error propagation."""
    facade_map = {
        "CSP": csp.csp_subarray,
        "SDP": sdp.sdp_subarray,
        "MCCS": mccs.mccs_subarray,
    }

    subarray_device = facade_map[defectiveSubsystem]
    subarray_device.SetDefective(ERROR_PROPAGATION_DEFECT)

    event_tracers.clear_events()

    cmd_method = getattr(
        tmc.subarray_node, command.capitalize()
    )  # Abort/Restart
    _, pytest.unique_id = cmd_method()


@then(
    "the command failure is reported by subarray with "
    "an appropriate error message"
)
def verify_abort_failure(
    defectiveSubsystem: str,
    event_tracers: TangoEventTracer,
    tmc: TMCFacade,
):
    """This function checks that when an Abort or Restart command is
    issued after a subsystem is set to defective, the expected error
    message is present in the longRunningCommandResult
    event of the SubarrayNode, and that the result code is FAILED."""
    device_map = {
        "CSP": low_csp_subarray_leaf_node,
        "SDP": low_sdp_subarray_leaf_node,
        "MCCS": mccs_subarray_leaf_node,
    }

    error_keywords = [
        f"{device_map[defectiveSubsystem]}:",
        "Exception occurred on device:",
    ]

    assert_that(event_tracers).described_as(
        f"Expected longRunningCommandResult failure from "
        f"SubarrayNode for {defectiveSubsystem}"
    ).within_timeout(TIMEOUT).has_desired_result_code_message_in_lrcr_event(
        tmc.subarray_node,
        error_keywords,
        pytest.unique_id[0],
        ResultCode.FAILED,
    )

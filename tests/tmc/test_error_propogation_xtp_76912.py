"""Test case to verify error propagation functionality for
the AssignResourcs command"""
import json

import pytest
from assertpy import assert_that
from pytest_bdd import given, parsers, scenario, then, when
from ska_control_model import ObsState, ResultCode
from ska_integration_test_harness.facades.mccs_facade import MCCSFacade
from ska_integration_test_harness.facades.tmc_facade import TMCFacade
from ska_integration_test_harness.inputs.test_harness_inputs import (
    TestHarnessInputs,
)
from ska_tango_testing.integration import TangoEventTracer, log_events

from tests.conftest import SubarrayTestContextData
from tests.resources.test_harness.constant import ERROR_PROPAGATION_DEFECT
from tests.resources.test_harness.utils.my_file_json_input import (
    MyFileJSONInput,
)

TIMEOUT = 80


@pytest.mark.SKA_low
@scenario(
    "../features/tmc/check_error_propagation_ith.feature",
    "Error Propagation Reported by TMC Low AssignResources Command for "
    "Defective MCCS Controller",
)
def test_tmc_command_error_propagation():
    """
    Test case to verify TMC Error Propagation functionality.
    """


@given("the telescope is in ON state")
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


@given("TMC subarray is in ObsState EMPTY")
def subarray_in_empty_obsstate(
    tmc: TMCFacade, context_fixt: SubarrayTestContextData
):
    """Verify the subarray's transition to the EMPTY state."""
    context_fixt.starting_state = ObsState.EMPTY
    tmc.force_change_of_obs_state(
        ObsState.EMPTY,
        TestHarnessInputs(),
        wait_termination=True,
    )


@when("the MCCS controller is in an abnormal state")
def execute_command_on_abnormal_mccs_subarray(
    mccs: MCCSFacade,
):
    "the mccs controller is in an abnormal state"
    mccs.mccs_controller.SetDefective(ERROR_PROPAGATION_DEFECT)


@when(parsers.parse("I issue the AssignResources command to the TMC"))
def execute_command_assign_resources(
    tmc: TMCFacade,
):
    """
    Executes the AssignResources command on the TMC Central Node.
    """
    assign_input = MyFileJSONInput("centralnode", "assign_resources_low")
    _, pytest.unique_id = tmc.central_node.AssignResources(
        assign_input.as_str()
    )


@then("the command failure is reported by TMC CentralNode with error message")
def error_reporting(
    tmc: TMCFacade,
    mccs: MCCSFacade,
    event_tracers: TangoEventTracer,
):
    """Validates that an error is correctly reported by the TMC.

    This function checks if an error message is generated and logged
    by the TMC when the AssignResources command fails due to a defective
    MCCS Controller.
    It verifies the error reporting mechanism by asserting the expected
    failure message in the longRunningCommandResult event."""
    exception_message = [
        "ska_low/tm_leaf_node/mccs_master: ",
        "Exception occurred on device:",
    ]

    assert_that(event_tracers).described_as(
        'FAILED ASSUMPTION IN "THEN" STEP: '
        '"the command failure is reported by central_node with appropriate"'
        '"error message"'
        "CentralNode device"
        f"({tmc.central_node.dev_name()}) "
        "is expected have longRunningCommandResult"
        "(ResultCode.FAILED,exception)",
    ).within_timeout(TIMEOUT).has_desired_result_code_message_in_lrcr_event(
        tmc.central_node,
        exception_message,
        pytest.unique_id[0],
        ResultCode.FAILED,
    )
    mccs.mccs_controller.SetDefective(json.dumps({"enabled": False}))
    tmc.subarray_node.Abort()
    assert_that(event_tracers).within_timeout(5).has_change_event_occurred(
        tmc.subarray_node, "obsState", ObsState.ABORTED
    )

    tmc.subarray_node.Restart()
    assert_that(event_tracers).within_timeout(5).has_change_event_occurred(
        tmc.subarray_node, "obsState", ObsState.EMPTY
    )

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
from ska_integration_test_harness.facades.sdp_facade import SDPFacade
from ska_integration_test_harness.facades.tmc_facade import TMCFacade
from ska_integration_test_harness.inputs.test_harness_inputs import (
    TestHarnessInputs,
)
from ska_tango_testing.integration import TangoEventTracer, log_events

from tests.conftest import SubarrayTestContextData, _setup_event_subscriptions
from tests.resources.test_harness.constant import (
    ERROR_PROPAGATION_DEFECT,
    low_csp_subarray_leaf_node,
)
from tests.resources.test_harness.utils.my_file_json_input import (
    MyFileJSONInput,
)

TIMEOUT = 80


@pytest.mark.test
@pytest.mark.SKA_low
@scenario(
    "../features/tmc/error_propagation_timeout_abort.feature",
    "Error Propagation Reported by TMC Low Abort Command "
    "for Defective Subarray",
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


@given(parsers.parse("the TMC subarray is in the IDLE observation state"))
def perform_idle_transition(
    tmc: TMCFacade,
    sdp: SDPFacade,
    csp: CSPFacade,
    event_tracer: TangoEventTracer,
    context_fixt: SubarrayTestContextData,
):
    """
    Execute Assign and verify
    """
    _setup_event_subscriptions(tmc, csp, sdp, event_tracer)
    context_fixt.starting_state = ObsState.EMPTY
    tmc.force_change_of_obs_state(
        ObsState.EMPTY,
        TestHarnessInputs(),
        wait_termination=True,
    )
    assign_input = MyFileJSONInput("centralnode", "assign_resources_low")
    _, pytest.unique_id = tmc.central_node.AssignResources(
        assign_input.as_str()
    )
    assert_that(event_tracer).described_as(
        "FAILED ASSUMPTION AFTER ASSIGNRESOURCES COMMAND: "
        "Subarray Node device"
        f"({tmc.subarray_node.dev_name()}) "
        "is expected to be in IDLE obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        tmc.subarray_node,
        "obsState",
        ObsState.IDLE,
    )


@when(parsers.parse("Abort is invoked on a defective subsystem"))
def defect_subsystem_and_invoke_command(
    csp: CSPFacade,
    tmc: TMCFacade,
):
    """This step simulates a failure in one of the subsystems
    (CSP, SDP, or MCCS) by setting it to a defective state,
    then triggers the given command (e.g., Abort, Restart)
    on the TMC SubarrayNode to verify proper error propagation."""
    csp.csp_subarray.SetDefective(ERROR_PROPAGATION_DEFECT)
    _, pytest.unique_id = tmc.subarray_node.Abort()


@then(
    "the command failure is reported by subarray with "
    "an appropriate error message"
)
def verify_abort_failure(
    event_tracers: TangoEventTracer,
    tmc: TMCFacade,
):
    """This function checks that when an Abort or Restart command is
    issued after a subsystem is set to defective, the expected error
    message is present in the longRunningCommandResult
    event of the SubarrayNode, and that the result code is FAILED."""
    exception_message = [
        f" {low_csp_subarray_leaf_node}: ",
        "Exception occurred on device:",
    ]

    assert_that(event_tracers).described_as(
        'FAILED ASSUMPTION IN "THEN" STEP: '
        '"the command failure is reported by subarray_node with appropriate"'
        '"error message"'
        "CentralNode device"
        f"({tmc.subarray_node.dev_name()}) "
        "is expected have longRunningCommandResult"
        "(ResultCode.FAILED,exception)",
    ).within_timeout(TIMEOUT).has_desired_result_code_message_in_lrcr_event(
        tmc.subarray_node,
        exception_message,
        pytest.unique_id[0],
        ResultCode.FAILED,
    )

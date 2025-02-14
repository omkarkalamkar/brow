"""Test case to verify error propagation functionality for
the AssignResourcs command"""

import json

import pytest
from assertpy import assert_that
from pytest_bdd import given, parsers, scenario, then, when
from ska_control_model import ResultCode
from ska_integration_test_harness.facades.mccs_facade import MCCSFacade
from ska_integration_test_harness.facades.tmc_facade import TMCFacade
from ska_tango_testing.integration import log_events

from tests.resources.test_harness.constant import (  # mccs_master_leaf_node,
    ERROR_PROPAGATION_DEFECT,
)
from tests.resources.test_harness.utils.my_file_json_input import (
    MyFileJSONInput,
)

# import time


# from ska_integration_test_harness.inputs.test_harness_inputs import (
# TestHarnessInputs,
# from tango import DevState


TIMEOUT = 80


@pytest.mark.test
@pytest.mark.SKA_low
@scenario(
    "../features/tmc/check_error_propagation_ith.feature",
    "TMC subarray reports errors during interactions with CSP or SDP subarray",
)
def test_tmc_command_error_propagation():
    """
    Test case to verify TMC Error Propagation functionality.
    """


@given("the telescope is in ON state")
def given_the_telescope_is_in_on_state(
    tmc: TMCFacade,
    event_tracer,
):
    """Ensure the telescope is in ON state."""
    tmc.move_to_on(wait_termination=True)
    event_tracer.subscribe_event(tmc.central_node, "telescopeState")
    event_tracer.subscribe_event(tmc.central_node, "longRunningCommandResult")
    event_tracer.subscribe_event(tmc.subarray_node, "obsState")
    event_tracer.subscribe_event(tmc.subarray_node, "longRunningCommandResult")

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
    # TelescopeOn
    tmc.move_to_on()

    # Assertions
    event_tracer.clear_events()


@given("TMC subarray is in ObsState EMPTY")
def subarray_in_empty_obsstate():
    "TMC subarray is in ObsState EMPTY"


@when("the MCCS controller is in an abnormal state")
def execute_command_on_abnormal_mccs_subarray(
    mccs: MCCSFacade,
):
    "the mccs subarray is in an abnormal state"
    mccs.mccs_controller.SetDefective(json.dumps(ERROR_PROPAGATION_DEFECT))


@when(parsers.parse("I issue the AssignResources command to the TMC"))
def execute_command_assign_resources(
    tmc,
):
    """executes commands"""
    assign_input = MyFileJSONInput("centralnode", "assign_resources_low")
    pytest.unique_id = tmc.central_node.AssignResources(assign_input.as_str())


@then("the Error is reported by the TMC")
def error_reporting(
    tmc,
    event_tracers,
):
    """executes commands"""
    # exception_message = (
    #     "Exception occurred on the following devices:"
    #     + "ska_low/tm_leaf_node/mccs_master:"
    #     + "Exception occurred, command failed."
    # )
    exception_message = "command failed"
    log_events({tmc.central_node: ["longRunningCommandResult"]})
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
        [exception_message],
        pytest.unique_id[0],
        ResultCode.FAILED,
    )

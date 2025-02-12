# import time

import pytest
from assertpy import assert_that
from pytest_bdd import given, parsers, scenario, then, when
from ska_control_model import ObsState, ResultCode
from ska_integration_test_harness.facades.csp_facade import CSPFacade
from ska_integration_test_harness.facades.sdp_facade import SDPFacade
from ska_integration_test_harness.facades.tmc_facade import TMCFacade

# )
from ska_tango_testing.integration import log_events

from tests.resources.test_harness.constant import INTERMEDIATE_STATE_DEFECT
from tests.resources.test_harness.utils.my_file_json_input import (
    MyFileJSONInput,
)

# from ska_integration_test_harness.inputs.test_harness_inputs import (
# TestHarnessInputs,
# from tango import DevState


TIMEOUT = 100


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

@when("the SDP subarray is in an abnormal state")
def execute_command_on_abnormal_sdp_subarray(
    sdp: SDPFacade,
):
    sdp.sdp_subarray.SetDefective(INTERMEDIATE_STATE_DEFECT)


@when("the CSP subarray is in an abnormal state")
def execute_command_on_abnormal_csp_subarray(
    csp: CSPFacade,
):
    csp.csp_subarray.SetDefective(INTERMEDIATE_STATE_DEFECT)


@when(parsers.parse("I issue the AssignResources command to the TMC"))
def execute_command_assign_resources(
    command: str,
    tmc,
    event_tracer,
):
    """executes commands"""
    assign_input = MyFileJSONInput("centralnode", "assign_resources_low")
    pytest.unique_id = tmc.assign_resources(assign_input)
    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "GIVEN STEP: '
        f'"a Subarray in intermediate obsState {"Resourcing"}"'
        "SDP Subarray device"
        f"({tmc.central_node.subarray_node.dev_name()}) "
        f"is expected to be in IDLE obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        tmc.central_node.subarray_node,
        "obsState",
        ObsState.RESOURCING,
    )


@when("I issue the ReleaseResources command to the TMC")
def execute_commands_release_resources(
    command: str,
    tmc,
    event_tracer,
):
    """executes commands"""
    release_input = MyFileJSONInput("centralnode", "release_resources_low")
    pytest.unique_id = tmc.release_resources(release_input)
    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "GIVEN STEP: '
        f'"a Subarray in intermediate obsState {"Resourcing"}"'
        "SDP Subarray device"
        f"({tmc.central_node.subarray_node.dev_name()}) "
        f"is expected to be in RESOURCING obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        tmc.central_node.subarray_node,
        "obsState",
        ObsState.RESOURCING,
    )


@then("the Error is reported by the TMC")
def error_reporting(
    command,
    tmc,
    event_tracer,
):
    """executes commands"""
    exception_message = "Device stuck in intermediate state"

    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "THEN" STEP: '
        '"the command failure is reported by subarray with appropriate"'
        '"error message"'
        "Subarray Node device"
        f"({tmc.subarray_node.dev_name()}) "
        "is expected have longRunningCommandResult"
        "(ResultCode.FAILED,exception)",
    ).within_timeout(TIMEOUT).has_desired_result_code_message_in_lrcr_event(
        tmc.subarray_node,
        [exception_message],
        pytest.unique_id[0],
        ResultCode.FAILED,
    )

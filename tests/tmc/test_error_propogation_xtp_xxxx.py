"""
This module contains a BDD test case to verify the error propagation
mechanism in the Telescope Monitoring and Control (TMC) system when
interacting with CSP or SDP subarrays.
"""

import pytest
from assertpy import assert_that
from pytest_bdd import given, parsers, scenario, then, when
from ska_control_model import ObsState, ResultCode
from ska_integration_test_harness.facades.csp_facade import CSPFacade
from ska_integration_test_harness.facades.sdp_facade import SDPFacade
from ska_integration_test_harness.facades.tmc_facade import TMCFacade
from ska_tango_testing.integration import TangoEventTracer, log_events
from tango import DevState

from tests.resources.test_harness.constant import INTERMEDIATE_STATE_DEFECT
from tests.resources.test_harness.utils.my_file_json_input import (
    MyFileJSONInput,
)

TIMEOUT = 100


@pytest.mark.test1
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
    event_tracer: TangoEventTracer,
):
    """Ensure the telescope is in ON state."""
    tmc.move_to_on(wait_termination=True)
    event_tracer.subscribe_event(
        tmc.central_node.central_node, "telescopeState"
    )
    event_tracer.subscribe_event(
        tmc.central_node.central_node, "longRunningCommandResult"
    )
    event_tracer.subscribe_event(
        tmc.subarray_node.tmc.subarray_node, "obsState"
    )
    event_tracer.subscribe_event(
        tmc.subarray_node.tmc.subarray_node, "longRunningCommandResult"
    )

    # Logging setup
    log_events(
        {
            tmc.central_node.central_node: [
                "telescopeState",
                "longRunningCommandResult",
            ],
            tmc.subarray_node.tmc.subarray_node: [
                "obsState",
                "longRunningCommandResult",
            ],
        }
    )
    # TelescopeOn
    tmc.move_to_on()

    # Assertions
    assert_that(event_tracer).described_as(
        "FAILED ASSUMPTION AFTER ON COMMAND: "
        "Central Node device"
        f"({tmc.central_node.central_node.dev_name()}) "
        "is expected to be in TelescopeState ON",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        tmc.central_node.central_node,
        "telescopeState",
        DevState.ON,
    )
    assert_that(event_tracer).described_as(
        "FAILED UNEXPECTED INITIAL OBSSTATE: "
        "Subarray Node device"
        f"({tmc.central_node.tmc.subarray_node.dev_name()}) "
        "is expected to be in EMPTY obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        tmc.central_node.tmc.subarray_node,
        "obsState",
        ObsState.EMPTY,
    )
    event_tracer.clear_events()


@given(parsers.parse("TMC subarray is in ObsState {obs_state}"))
def subarray_in_idle_state(
    context_fixt,
    tmc: TMCFacade,
    event_tracer,
    obs_state,
):
    """Ensure the subarray is in the EMPTY state."""
    context_fixt.starting_state = ObsState.EMPTY
    if obs_state == "IDLE":
        assign_input = MyFileJSONInput("centralnode", "assign_resources_low")
        tmc.assign_resources(assign_input)
        assert_that(event_tracer).described_as(
            'FAILED ASSUMPTION IN "GIVEN STEP: '
            f'"a Subarray in intermediate obsState {obs_state}"'
            "SDP Subarray device"
            f"({tmc.central_node.subarray_node.dev_name()}) "
            f"is expected to be in IDLE obstate",
        ).within_timeout(TIMEOUT).has_change_event_occurred(
            tmc.central_node.subarray_node,
            "obsState",
            ObsState.IDLE,
        )


@when(parsers.parse("the {subarray} subarray is in an abnormal state"))
def execute_command_on_abnormal_subarray(
    subarray,
    csp: CSPFacade,
    sdp: SDPFacade,
):
    """executes commands"""
    if subarray == "SDP":
        sdp.sdp_subarray.SetDefective(INTERMEDIATE_STATE_DEFECT)
    elif subarray == "CSP":
        csp.csp_subarray.SetDefective(INTERMEDIATE_STATE_DEFECT)


@when(parsers.parse("And I issue the {command} command to the TMC"))
def execute_commands(
    command: str,
    tmc,
    event_tracer,
):
    """executes commands"""
    if command == "AssignResource":
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
    elif command == "ReleaseResource":
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

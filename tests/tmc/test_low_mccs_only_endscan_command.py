"""
Module: test_low_mccs_only_endscan_command

This module defines a Pytest BDD test scenario for the successful execution
of the EndScan Command on a Low Telescope Subarray in the Telescope Monitoring
and Control (TMC) system with an MCCS-only subsystem.
The scenario includes steps to set up the TMC, prepare a subarray in the IDLE
observation state, configure only the MCCS subsystem, invoke the Scan command
to transition to SCANNING, and then invoke the EndScan command. The successful
execution is verified by checking that the subarray transitions to the READY
observation state after the EndScan command.
"""
import json

import pytest
from assertpy import assert_that
from pytest_bdd import given, scenario, then, when
from ska_control_model import ObsState
from ska_integration_test_harness.facades.tmc_facade import TMCFacade
from ska_tango_testing.integration import TangoEventTracer, log_events

from tests.resources.test_harness.constant import TIMEOUT
from tests.resources.test_harness.utils.my_file_json_input import (
    MyFileJSONInput,
)
from tests.resources.test_support.common_utils.result_code import ResultCode


@pytest.mark.SKA_fault
@pytest.mark.SKA_low
@scenario(
    "../features/tmc/check_mccs_only_endscan.feature",
    "Successful Execution of the EndScan Command on a Low"
    + " Telescope Subarray with an MCCS-Only subsystem",
)
def test_tmc_mccs_only_endscan_command():
    """BDD test scenario for verifying successful execution of
    the Low End command in a TMC with MCCS only subsystem."""


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


@given("the TMC subarray is in the IDLE obsState")
def perform_idle_transition(
    tmc: TMCFacade,
    event_tracers: TangoEventTracer,
):
    """
    Execute Assign and verify
    """
    assign_input = MyFileJSONInput("centralnode", "assign_resources_low")

    _, pytest.unique_id = tmc.central_node.AssignResources(
        assign_input.as_str()
    )

    assert_that(event_tracers).described_as(
        "FAILED ASSUMPTION AFTER ASSIGNRESOURCES COMMAND: "
        "Subarray Node device"
        f"({tmc.subarray_node.dev_name()}) "
        "is expected to be in IDLE obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        tmc.subarray_node,
        "obsState",
        ObsState.IDLE,
    )

    assert_that(event_tracers).described_as(
        'FAILED ASSUMPTION IN "GIVEN" STEP: '
        "Central Node device"
        f"({tmc.central_node.dev_name()}) "
        "is expected have longRunningCommand as"
        '(unique_id,(ResultCode.OK,"Command Completed"))',
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        tmc.central_node,
        "longRunningCommandResult",
        (
            pytest.unique_id[0],
            json.dumps((int(ResultCode.OK), "Command Completed")),
        ),
    )
    event_tracers.clear_events()


@given("I configure the TMC subarray with an MCCS-only configuration")
def mccs_only_configure(tmc: TMCFacade):
    """Send a Configure command to the subarray with only mccs key."""
    configure_input = MyFileJSONInput("subarray", "configure_low")

    configure_input_json = json.loads(configure_input.as_str())

    for subsystem in ["sdp", "csp"]:
        del configure_input_json[subsystem]

    configure_input_json[
        "interface"
    ] = "https://schema.skao.int/ska-low-tmc-configure/4.2"

    configure_input_json = json.dumps(configure_input_json)

    _, pytest.unique_id = tmc.subarray_node.Configure(configure_input_json)
    # In an effort to reduce number of data files we are modifying the
    # existing configure_low.


@given("the TMC subarray is in the READY obsState")
def check_subarray_obs_state_ready(
    tmc: TMCFacade,
    event_tracers: TangoEventTracer,
):
    """Verify that the subarray is in the READY obsState."""
    assert_that(event_tracers).described_as(
        'FAILED ASSUMPTION IN "THEN" STEP: '
        "'And the subarray is in the READY obsState'"
        "Subarray Node device"
        f"({tmc.subarray_node.dev_name()}) "
        "is expected to be in READY obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        tmc.subarray_node,
        "obsState",
        ObsState.READY,
    )
    assert_that(event_tracers).described_as(
        "FAILED ASSUMPTION : "
        "Subarray Node device"
        f"({tmc.subarray_node.dev_name()}) "
        "is expected have longRunningCommand as"
        '(unique_id,(ResultCode.OK,"Command Completed"))',
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        tmc.subarray_node,
        "longRunningCommandResult",
        (
            pytest.unique_id[0],
            json.dumps((int(ResultCode.OK), "Command Completed")),
        ),
    )


@given("I invoke the Scan command on the TMC subarray")
def mccs_only_scan(
    tmc: TMCFacade,
):
    """Inovke Scan command"""

    scan_input = MyFileJSONInput("subarray", "scan_low")

    _, pytest.unique_id = tmc.subarray_node.Scan(scan_input.as_str())


@given("the TMC subarray is in the SCANNING obsState")
def check_subarray_obs_state_idle_scanning(
    tmc: TMCFacade,
    event_tracers: TangoEventTracer,
):
    """Verify that the subarray is in the SCANNING obsState."""
    assert_that(event_tracers).described_as(
        'FAILED ASSUMPTION IN "THEN" STEP: '
        "'the subarray must be in the SCANNING obsState until finished'"
        "Subarray Node device"
        f"({tmc.subarray_node.dev_name()}) "
        "is expected to be in SCANNING obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        tmc.subarray_node,
        "obsState",
        ObsState.SCANNING,
    )
    assert_that(event_tracers).described_as(
        'FAILED ASSUMPTION IN "GIVEN" STEP: '
        "Subarray Node device"
        f"({tmc.subarray_node.dev_name()}) "
        "is expected have longRunningCommand as"
        '(unique_id,(ResultCode.OK,"Command Completed"))',
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        tmc.subarray_node,
        "longRunningCommandResult",
        (
            pytest.unique_id[0],
            json.dumps((int(ResultCode.OK), "Command Completed")),
        ),
    )


@when("I invoke the EndScan command on the TMC subarray")
def mccs_only_end(
    tmc: TMCFacade,
):
    """Inovke EndScan command"""

    _, pytest.unique_id = tmc.subarray_node.EndScan()


@then("the TMC subarray transitions to the READY obsState")
def check_subarray_obs_state_is_ready(
    tmc: TMCFacade,
    event_tracers: TangoEventTracer,
):
    """Verify that the subarray is in the READY obsState."""

    assert_that(event_tracers).described_as(
        'FAILED ASSUMPTION IN "THEN" STEP: '
        "'And the subarray is in the READY obsState'"
        "Subarray Node device"
        f"({tmc.subarray_node.dev_name()}) "
        "is expected to be in READY obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        tmc.subarray_node,
        "obsState",
        ObsState.READY,
    )

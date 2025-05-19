"""Test module to validate timeout behavior in the Abort command
when a defective subsystem (CSP, SDP, or MCCS) causes the command to fail.
"""
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
from tests.resources.test_harness.constant import TIMEOUT_DEFECT

TIMEOUT = 60


@pytest.mark.SKA_low
@scenario(
    "../features/tmc/error_propagation_timeout_abort.feature",
    "Timeout Reported by TMC Low Abort Command for Defective Subarray",
)
def test_tmc_command_timeout():
    """
    Test case to verify TMC Timeout functionality.
    """


exception_messages = {
    "CSP": ('[3, "Timeout has occurred, command failed"]'),
    "SDP": ('[3, "Timeout has occurred, command failed"]'),
    "MCCS": ('[3, "Timeout has occurred, command failed"]'),
}


# @given ---> conftest


@given(
    parsers.parse(
        "TMC subarray is in initial ObsState for {defectiveSubsystem}"
    )
)
def subarray_in_initial_state(
    context_fixt: SubarrayTestContextData,
    tmc: TMCFacade,
    sdp: SDPFacade,
    csp: CSPFacade,
    mccs: MCCSFacade,
    event_tracers: TangoEventTracer,
    default_commands_inputs: TestHarnessInputs,
    defectiveSubsystem: str,
):
    """Ensure the subarray is in the initial obsstate state.
    Args:
        context_fixt: Subarray test context for maintaining state.
        tmc: TMCFacade instance for controlling the TMC Subarray.
        sdp: SDPFacade instance for controlling the SDP Subarray.
        csp: CSPFacade instance for controlling the CSP Subarray.
        mccs: MCCSFacade instance for controlling the MCCS Subarray.
        event_tracers: For monitoring Tango events.
        default_commands_inputs: Default command input data.
        defectiveSubsystem: The subsystem name expected to simulate a timeout
    """
    _setup_event_subscriptions(tmc, csp, sdp, mccs, event_tracers)
    target_state = (
        ObsState.READY if defectiveSubsystem == "MCCS" else ObsState.IDLE
    )
    context_fixt.starting_state = target_state

    tmc.force_change_of_obs_state(
        target_state,
        default_commands_inputs,
        wait_termination=True,
    )


@when(
    parsers.parse(
        "Abort is invoked on a defective subsystem {defectiveSubsystem}"
    )
)
def execute_command_abort(
    tmc: TMCFacade,
    context_fixt: SubarrayTestContextData,
    csp: CSPFacade,
    sdp: SDPFacade,
    mccs: MCCSFacade,
    defectiveSubsystem: str,
):
    """
    Simulates a timeout by setting the specified subsystem as defective
    or delayed, then triggers Abort.
    Args:
        tmc: TMCFacade instance to execute the Abort command.
        context_fixt: Context object to record action being tested.
        csp: CSPFacade instance.
        sdp: SDPFacade instance.
        mccs: MCCSFacade instance.
        defectiveSubsystem: The name of the defective subsystem.
    """
    if defectiveSubsystem == "CSP":
        csp.csp_subarray.SetDefective(TIMEOUT_DEFECT)
    elif defectiveSubsystem == "SDP":
        sdp.sdp_subarray.SetDelayInfo(json.dumps({"Abort": 135}))
    elif defectiveSubsystem == "MCCS":
        mccs.mccs_subarray.SetDefective(TIMEOUT_DEFECT)
    context_fixt.when_action_name = "Abort"
    _, pytest.unique_id = tmc.subarray_node.Abort()


@then("TMC SubarrayNode obsstate changes to FAULT obsState")
def verify_fault_obsstate(
    tmc: TMCFacade,
    event_tracers: TangoEventTracer,
):
    """
    Verify the subarray's transition to the FAULT observation state.
    Args:
        tmc: TMC facade for the SubarrayNode.
        event_tracers: Event tracer to verify state changes.
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


@then(
    parsers.parse(
        "the Timeout is reported by subarray with error message "
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
    """Validates that TMC's SubarrayNode correctly reports the timeout via
    longRunningCommandResult.
        Args:
        tmc: TMCFacade instance.
        csp: CSPFacade instance.
        sdp: SDPFacade instance.
        mccs: MCCSFacade instance.
        event_tracers: Used to monitor Tango events for error reporting.
        defectiveSubsystem: The subsystem name that triggered the timeout.
    """
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
        csp.csp_subarray.Abort()
        assert_that(event_tracers).within_timeout(
            TIMEOUT
        ).has_change_event_occurred(
            csp.csp_subarray, "obsState", ObsState.ABORTED
        )
    elif defectiveSubsystem == "SDP":
        sdp.sdp_subarray.ResetDelayInfo()
        sdp.sdp_subarray.Abort()
        assert_that(event_tracers).within_timeout(
            135
        ).has_change_event_occurred(
            sdp.sdp_subarray, "obsState", ObsState.ABORTED
        )
    elif defectiveSubsystem == "MCCS":
        mccs.mccs_subarray.SetDefective(json.dumps({"enabled": False}))
        mccs.mccs_subarray.Abort()
        assert_that(event_tracers).within_timeout(
            TIMEOUT
        ).has_change_event_occurred(
            mccs.mccs_subarray, "obsState", ObsState.ABORTED
        )

    tmc.restart()
    assert_that(event_tracers).within_timeout(
        TIMEOUT
    ).has_change_event_occurred(tmc.subarray_node, "obsState", ObsState.EMPTY)
    event_tracers.clear_events()

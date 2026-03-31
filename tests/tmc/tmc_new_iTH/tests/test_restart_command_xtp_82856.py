import time

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
from ska_tango_base.commands import ResultCode
from ska_tango_testing.integration import TangoEventTracer, log_events
from ska_tango_testing.mock.placeholders import Anything

from tests.tmc.tmc_new_iTH.conftest import TestContextData
from tests.tmc.tmc_new_iTH.utils import (
    TIMEOUT,
    invoke_command_with_defect,
    reset_defects,
)


def _setup_event_subscriptions(
    tmc: TMCFacade,
    csp: CSPFacade,
    sdp: SDPFacade,
    mccs: MCCSFacade,
    event_tracer: TangoEventTracer,
):
    """Subscribe TMC, CSP and SDP devices to track and log obsState events.

    :param tmc: the TMC facade.
    :param csp: the CSP facade.
    :param sdp: the SDP facade.
    :param event_tracer: the event tracer.
    """
    event_tracer.subscribe_event(tmc.subarray_node, "obsState")
    event_tracer.subscribe_event(csp.csp_subarray, "obsState")
    event_tracer.subscribe_event(sdp.sdp_subarray, "obsState")
    event_tracer.subscribe_event(mccs.mccs_subarray, "obsState")
    event_tracer.subscribe_event(tmc.central_node, "longRunningCommandResult")
    event_tracer.subscribe_event(tmc.subarray_node, "longRunningCommandResult")

    log_events(
        {
            tmc.subarray_node: [
                "obsState",
                "longRunningCommandResult",
            ],
            csp.csp_subarray: ["obsState"],
            sdp.sdp_subarray: ["obsState"],
            mccs.mccs_subarray: ["obsState"],
            tmc.central_node: ["longRunningCommandResult"],
        },
        event_enum_mapping={"obsState": ObsState},
    )


def _check_abort_flow(
    csp: CSPFacade,
    sdp: SDPFacade,
    mccs: MCCSFacade,
    context_data: TestContextData,
    event_tracer: TangoEventTracer,
):
    """This function checks obstates for abort and
    tracks abort flow if it will be aborted.
    """
    abort_not_allowed_obs_states = [
        ObsState.ABORTED,
        ObsState.FAULT,
        ObsState.EMPTY,
    ]
    if context_data.csp_obsstate not in abort_not_allowed_obs_states:
        assert_that(event_tracer).described_as(
            f"CSP Subarray device ({csp.csp_subarray}) "
            "ObsState attribute values should move "
            f"to ABORTED."
        ).within_timeout(TIMEOUT).has_change_event_occurred(
            csp.csp_subarray,
            "obsState",
            ObsState.ABORTED,
            previous_value=ObsState.ABORTING,
        )

    if context_data.sdp_obsstate not in abort_not_allowed_obs_states:
        assert_that(event_tracer).described_as(
            f"SDP Subarray device ({sdp.sdp_subarray}) "
            "ObsState attribute values should move "
            f"to ABORTED."
        ).within_timeout(TIMEOUT).has_change_event_occurred(
            sdp.sdp_subarray,
            "obsState",
            ObsState.ABORTED,
            previous_value=ObsState.ABORTING,
        )
    if context_data.mccs_obsstate not in abort_not_allowed_obs_states:
        assert_that(event_tracer).described_as(
            f"MCCS Subarray device ({mccs.mccs_subarray}) "
            "ObsState attribute values should move "
            f"to ABORTED."
        ).within_timeout(TIMEOUT).has_change_event_occurred(
            mccs.mccs_subarray,
            "obsState",
            ObsState.ABORTED,
            previous_value=ObsState.ABORTING,
        )


@pytest.mark.SKA_tmc_low_negative_tests
@scenario(
    "../tmc/tmc_new_iTH/features/xtp_82856.feature",
    "Test Restart Command when TMC subarray transitions to "
    "FAULT observation state",
)
def test_restart_command_in_observation_state_fault():
    """BDD test scenario for verifying execution of the Restart
    command in FAULT obsState in TMC."""


@given(
    parsers.parse(
        "CSP,SDP and MCCS in observation states {csp_obsstate},{sdp_obsstate} "
        "and {mccs_obsstate} after {command}"
    )
)
def verify_subsystem_after_command(
    admin_mode,
    csp_obsstate: str,
    sdp_obsstate: str,
    mccs_obsstate: str,
    command: str,
    tmc: TMCFacade,
    csp: CSPFacade,
    sdp: SDPFacade,
    mccs: MCCSFacade,
    default_commands_inputs: TestHarnessInputs,
    event_tracer: TangoEventTracer,
    context_data: TestContextData,
):
    """Verifies the the subsystem obsStates after command is invoked"""
    _setup_event_subscriptions(tmc, csp, sdp, mccs, event_tracer)
    invoke_command_with_defect(
        tmc,
        default_commands_inputs,
        csp,
        sdp,
        mccs,
        csp_obsstate,
        sdp_obsstate,
        mccs_obsstate,
        command,
    )
    assert_that(event_tracer).described_as(
        f"CSP Subarray device ({csp.csp_subarray})"
        "ObsState attribute value should move "
        f"to {csp_obsstate}."
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        csp.csp_subarray, "obsState", ObsState[csp_obsstate]
    )

    assert_that(event_tracer).described_as(
        f"SDP Subarray device ({sdp.sdp_subarray})"
        "ObsState attribute value should move "
        f" to {sdp_obsstate}."
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        sdp.sdp_subarray, "obsState", ObsState[sdp_obsstate]
    )
    assert_that(event_tracer).described_as(
        f"MCCS Subarray device ({mccs.mccs_subarray})"
        "ObsState attribute value should move "
        f" to {mccs_obsstate}."
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        mccs.mccs_subarray,
        "obsState",
        ObsState[mccs_obsstate],
    )
    context_data.csp_obsstate = ObsState[csp_obsstate]
    context_data.sdp_obsstate = ObsState[sdp_obsstate]
    context_data.mccs_obsstate = ObsState[mccs_obsstate]


@given("TMC Subarray in observation state FAULT")
def verify_tmc_subarray_observation_state_fault(
    event_tracer: TangoEventTracer,
    tmc: TMCFacade,
    csp: CSPFacade,
    sdp: SDPFacade,
    mccs: MCCSFacade,
):
    """Verifies the TMC subarray observation state FAULT"""
    assert_that(event_tracer).described_as(
        f"TMC Subarray Node device ({tmc.subarray_node})"
        "ObsState attribute value should move "
        f" to FAULT."
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        tmc.subarray_node,
        "obsState",
        ObsState.FAULT,
    )

    log_events({tmc.subarray_node: ["longRunningCommandResult"]})

    assert_that(event_tracer).described_as(
        f"FAILED ASSUMPTION: "
        "Subarray Node device"
        f"({tmc.subarray_node}) "
        "is expected to have longRunningCommandResult"
        "(ResultCode.FAILED,Timeout has occurred, command failed)",
    ).within_timeout(TIMEOUT).has_desired_result_code_message_in_lrcr_event(
        tmc.subarray_node,
        ["occurred"],
        Anything,
        ResultCode.FAILED,
    )

    reset_defects(csp, sdp, mccs)


@when("I invoke restart command on the TMC Subarray")
def invoke_restart_command(tmc: TMCFacade):
    """Invokes restart command on the TMC Subarray."""
    # Add explicit wait before invoking to ensure consistent timing
    time.sleep(0.1)
    tmc.restart()


@then("SDP,CSP and MCCS transitions to observation state EMPTY")
def verify_sdp_csp_mccs_in_empty_observation_state(
    event_tracer: TangoEventTracer,
    csp: CSPFacade,
    sdp: SDPFacade,
    mccs: MCCSFacade,
    context_data: TestContextData,
):
    """Verifies the observation states of SDP,CSP and MCCS
    after command Restart.
    """
    _check_abort_flow(csp, sdp, mccs, context_data, event_tracer)
    assert_that(event_tracer).described_as(
        f"MCCS Subarray device ({mccs.mccs_subarray})"
        f", CSP Subarray device ({csp.csp_subarray}) "
        f"and SDP Subarray device ({sdp.sdp_subarray}) "
        "ObsState attribute values should move "
        f"to RESTARTING."
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        mccs.mccs_subarray, "obsState", ObsState.RESTARTING
    ).has_change_event_occurred(
        csp.csp_subarray, "obsState", ObsState.RESTARTING
    ).has_change_event_occurred(
        sdp.sdp_subarray, "obsState", ObsState.RESTARTING
    )

    assert_that(event_tracer).described_as(
        f"MCCS Subarray device ({mccs.mccs_subarray})"
        f", CSP Subarray device ({csp.csp_subarray}) "
        f"and SDP Subarray device ({sdp.sdp_subarray}) "
        "ObsState attribute values should move "
        f"to EMPTY."
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        mccs.mccs_subarray, "obsState", ObsState.EMPTY
    ).has_change_event_occurred(
        csp.csp_subarray, "obsState", ObsState.EMPTY
    ).has_change_event_occurred(
        sdp.sdp_subarray, "obsState", ObsState.EMPTY
    )


@then("TMC subarray transitions to observation state EMPTY")
def verify_tmc_subarray_in_empty_observation_state(
    event_tracer: TangoEventTracer, tmc: TMCFacade
):
    """Verifies the observation state of TMC Subarray."""
    assert_that(event_tracer).described_as(
        f"TMC Subarray Node device ({tmc.subarray_node})"
        "ObsState attribute value should move "
        f"from {ObsState.FAULT} to EMPTY."
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        tmc.subarray_node, "obsState", ObsState.EMPTY
    )

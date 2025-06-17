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
from ska_tango_testing.integration import TangoEventTracer, log_events

from tests.tmc.tmc_new_iTH.utils import (
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


@pytest.mark.SKA_low
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
        "CSP,SDP and MCCS in observation states {CSP_obsState},{SDP_obsState} "
        "and {MCCS_obsState} after {command}"
    )
)
def verify_subsystem_after_command(
    CSP_obsState: str,
    SDP_obsState: str,
    MCCS_obsState: str,
    command: str,
    tmc: TMCFacade,
    csp: CSPFacade,
    sdp: SDPFacade,
    mccs: MCCSFacade,
    default_commands_inputs: TestHarnessInputs,
    event_tracer: TangoEventTracer,
):
    _setup_event_subscriptions()
    invoke_command_with_defect(
        tmc,
        default_commands_inputs,
        csp,
        sdp,
        mccs,
        CSP_obsState,
        SDP_obsState,
        MCCS_obsState,
        command,
    )
    assert_that(event_tracer).described_as(
        f"CSP Subarray device ({csp.csp_subarray})"
        "ObsState attribute value should move "
        f"to {CSP_obsState}."
    ).within_timeout(100).has_change_event_occurred(
        csp.csp_subarray, "obsState", ObsState[CSP_obsState]
    )

    assert_that(event_tracer).described_as(
        f"SDP Subarray device ({sdp.sdp_subarray})"
        "ObsState attribute value should move "
        f" to {SDP_obsState}."
    ).within_timeout(100).has_change_event_occurred(
        sdp.sdp_subarray, "obsState", ObsState[SDP_obsState]
    )
    assert_that(event_tracer).described_as(
        f"MCCS Subarray device ({mccs.mccs_subarray})"
        "ObsState attribute value should move "
        f" to {MCCS_obsState}."
    ).within_timeout(100).has_change_event_occurred(
        mccs.mccs_subarray,
        "obsState",
        ObsState[MCCS_obsState],
    )


@given("TMC subarray in observation state FAULT")
def verify_tmc_subarray_observation_state_fault(
    event_tracer: TangoEventTracer,
    tmc: TMCFacade,
    csp: CSPFacade,
    sdp: SDPFacade,
    mccs: MCCSFacade,
):
    assert_that(event_tracer).described_as(
        f"TMC Subarray Node device ({tmc.subarray_node})"
        "ObsState attribute value should move "
        f" to EMPTY."
    ).within_timeout(100).has_change_event_occurred(
        tmc.subarray_node,
        "obsState",
        ObsState.FAULT,
    )
    reset_defects(csp, sdp, mccs)


@when("I invoke Restart Command on the TMC Subarray")
def invoke_restart_command(tmc: TMCFacade):
    tmc.restart()


@then("SDP,CSP and MCCS transitions to observation state EMPTY")
def verify_sdp_csp_mccs_in_empty_observation_state(
    event_tracer: TangoEventTracer,
    csp: CSPFacade,
    sdp: SDPFacade,
    mccs: MCCSFacade,
):
    assert_that(event_tracer).described_as(
        f"MCCS Subarray device ({mccs.mccs_subarray})"
        f", CSP Subarray device ({csp.csp_subarray}) "
        f"and SDP Subarray device ({sdp.sdp_subarray}) "
        "ObsState attribute values should move "
        f"to EMPTY."
    ).within_timeout(100).has_change_event_occurred(
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
    assert_that(event_tracer).described_as(
        f"TMC Subarray Node device ({tmc.subarray_node})"
        "ObsState attribute value should move "
        f"from {ObsState.FAULT} to EMPTY."
    ).within_timeout(100).has_change_event_occurred(
        tmc.subarray_node, "obsState", ObsState.EMPTY
    )

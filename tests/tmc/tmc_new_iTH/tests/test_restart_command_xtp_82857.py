import pytest
from assertpy import assert_that
from pytest_bdd import given, scenario, then, when
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
    MCCS_RELEASE_INPUT,
    TIMEOUT,
    reset_defects,
    set_subsystem_defects,
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


@pytest.mark.SKA_tmc_low_restart
@scenario(
    "../tmc/tmc_new_iTH/features/xtp_82857.feature",
    "Test Restart Command flow when TMC Subarray observation state is FAULT"
    " and subsystems are EMPTY",
)
def test_restart_command_from_observation_state_resourcing_fault():
    """BDD test scenario for verifying execution of the Restart
    command in FAULT obsState in TMC."""


@given(
    "a TMC Subarray transitioned from RESOURCING to FAULT observation state"
    " after command failure"
)
def verify_tmc_subarray_resourcing_fault(
    tmc: TMCFacade,
    csp: CSPFacade,
    sdp: SDPFacade,
    mccs: MCCSFacade,
    default_commands_inputs: TestHarnessInputs,
    event_tracer: TangoEventTracer,
):
    """Verifies TMC Subarray Observation state into FAULT after
    AssignResources failure.
    """
    _setup_event_subscriptions(tmc, csp, sdp, mccs, event_tracer)
    set_subsystem_defects(
        csp, sdp, mccs, "EMPTY", "EMPTY", "IDLE", "AssignResources"
    )
    tmc.assign_resources(
        default_commands_inputs.assign_input, wait_termination=True
    )
    assert_that(event_tracer).described_as(
        f"TMC Subarray Node device ({tmc.subarray_node})"
        "ObsState attribute value should move "
        f"to {ObsState.FAULT}."
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        tmc.subarray_node, "obsState", ObsState.FAULT
    )


@given("CSP,SDP and MCCS in observation state EMPTY,EMPTY and IDLE")
def verify_csp_mccs_sdp_obs_state_empty(
    csp: CSPFacade, sdp: SDPFacade, mccs: MCCSFacade
):
    """Verifies observation states of the subsystems."""
    assert csp.csp_subarray.obsState == ObsState.RESOURCING
    assert sdp.sdp_subarray.obsState == ObsState.EMPTY
    assert mccs.mccs_subarray.obsState == ObsState.EMPTY
    reset_defects(csp, sdp, mccs)


@given("MCCS resources are released directly using MCCS Controller")
def invoke_release_on_mccs_controller(
    mccs: MCCSFacade, event_tracer: TangoEventTracer
):
    """Invokes release command on mccs controller"""
    mccs.mccs_controller.Release(MCCS_RELEASE_INPUT)
    assert_that(event_tracer).described_as(
        f"MCCS Subarray device ({mccs.mccs_subarray})"
        "ObsState attribute value should move "
        f"from {ObsState.EMPTY}."
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        mccs.mccs_subarray, "obsState", ObsState.EMPTY
    )


@when("I invoke Restart Command on the TMC Subarray")
def invoke_restart_command(tmc: TMCFacade):
    """Invokes restart command on TMC Subarray."""
    tmc.restart()


@then("TMC subarray transitions to observation state EMPTY")
def verify_tmc_subarray_transitions_to_obs_state_empty(
    event_tracer: TangoEventTracer, tmc: TMCFacade
):
    """Verifies TMC subarray observation state EMPTY after restart
    command."""
    assert_that(event_tracer).described_as(
        f"TMC Subarray Node device ({tmc.subarray_node})"
        "ObsState attribute value should move "
        f"from {ObsState.FAULT} to EMPTY."
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        tmc.subarray_node, "obsState", ObsState.EMPTY
    )

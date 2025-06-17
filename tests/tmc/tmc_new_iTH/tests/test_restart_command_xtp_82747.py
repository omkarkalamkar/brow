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

from tests.tmc.tmc_new_iTH.utils import reset_defects, set_subsystem_defects


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
    "../tmc/tmc_new_iTH/features/xtp_82747.feature",
    "Test Restart Command when TMC subarray transitions to "
    "FAULT observation state",
)
def test_restart_command_from_observation_state_resourcing_fault():
    """BDD test scenario for verifying execution of the Restart
    command in FAULT obsState in TMC."""


@given(
    "a TMC Subarray transitioned from RESOURCING to FAULT observation state"
)
def subarray_tmc_subarray_resourcing_fault(
    tmc: TMCFacade,
    csp: CSPFacade,
    sdp: SDPFacade,
    mccs: MCCSFacade,
    default_commands_inputs: TestHarnessInputs,
    event_tracer: TangoEventTracer,
):
    _setup_event_subscriptions(tmc, csp, sdp, mccs, event_tracer)
    set_subsystem_defects(
        csp, sdp, mccs, "EMPTY", "EMPTY", "EMPTY", "AssignResources"
    )
    tmc.assign_resources(
        default_commands_inputs.assign_input, wait_termination=False
    )
    assert_that(event_tracer).described_as(
        f"TMC Subarray Node device ({tmc.subarray_node})"
        "ObsState attribute value should move "
        f"from {ObsState.FAULT}."
    ).within_timeout(100).has_change_event_occurred(
        tmc.subarray_node, "obsState", ObsState.FAULT
    )


@given("CSP,SDP and MCCS in observation state EMPTY")
def verify_csp_mccs_sdp_obs_state_empty(
    csp: CSPFacade, sdp: SDPFacade, mccs: MCCSFacade
):
    assert csp.csp_subarray.obsState == ObsState.EMPTY
    assert sdp.sdp_subarray.obsState == ObsState.EMPTY
    assert mccs.mccs_subarray.obsState == ObsState.EMPTY
    reset_defects(csp, sdp, mccs)


@when("I invoke Restart Command on the TMC Subarray")
def invoke_restart_command(tmc: TMCFacade):
    tmc.restart()


@then("TMC subarray transitions to observation state EMPTY")
def verify_tmc_subarray_transitions_to_obs_state_empty(
    event_tracer: TangoEventTracer, tmc: TMCFacade
):
    assert_that(event_tracer).described_as(
        f"TMC Subarray Node device ({tmc.subarray_node})"
        "ObsState attribute value should move "
        f"from {ObsState.FAULT} to EMPTY."
    ).within_timeout(100).has_change_event_occurred(
        tmc.subarray_node, "obsState", ObsState.EMPTY
    )

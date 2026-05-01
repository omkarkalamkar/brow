import pytest
from assertpy import assert_that
from pytest_bdd import given, scenario, then, when
from ska_control_model import ObsState, ResultCode
from ska_integration_test_harness.facades.csp_facade import CSPFacade
from ska_integration_test_harness.facades.mccs_facade import MCCSFacade
from ska_integration_test_harness.facades.sdp_facade import SDPFacade
from ska_integration_test_harness.facades.tmc_facade import TMCFacade
from ska_integration_test_harness.inputs.test_harness_inputs import (
    TestHarnessInputs,
)
from ska_tango_testing.integration import TangoEventTracer, log_events

from tests.tmc.tmc_new_iTH.utils import TIMEOUT


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
    event_tracer.subscribe_event(
        tmc.sdp_subarray_leaf_node, "SdpSubarrayObsState"
    )
    event_tracer.subscribe_event(
        tmc.csp_subarray_leaf_node, "CspSubarrayObsState"
    )

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
            tmc.sdp_subarray_leaf_node: ["SdpSubarrayObsState"],
            tmc.csp_subarray_leaf_node: ["CspSubarrayObsState"],
        },
        event_enum_mapping={"obsState": ObsState},
    )


@pytest.mark.new
@scenario(
    "../tmc/tmc_new_iTH/features/xtp_109108.feature",
    "Verify SKB-1396",
)
def test_configure_command_with_itf_jsons_to_verify_skb_1396():
    """BDD test scenario for verifying SKB-1396."""


def setup_tmc(
    tmc: TMCFacade,
    csp: CSPFacade,
    sdp: SDPFacade,
    mccs: MCCSFacade,
    event_tracer: TangoEventTracer,
):
    """Verifies TMC initial state."""
    _setup_event_subscriptions(tmc, csp, sdp, mccs, event_tracer)
    tmc.move_to_on(wait_termination=True)
    assert_that(event_tracer).described_as(
        f"Both TMC Subarray Node device ({tmc.subarray_node})"
        f", CSP Subarray device ({csp.csp_subarray}) "
        f", MCCS Subarray device ({mccs.mccs_subarray}) "
        f"and SDP Subarray device ({sdp.sdp_subarray}) "
        "ObsState attribute values should be EMPTY."
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        tmc.subarray_node,
        "obsState",
        ObsState.EMPTY,
    ).has_change_event_occurred(
        csp.csp_subarray,
        "obsState",
        ObsState.EMPTY,
    ).has_change_event_occurred(
        sdp.sdp_subarray,
        "obsState",
        ObsState.EMPTY,
    ).has_change_event_occurred(
        mccs.mccs_subarray,
        "obsState",
        ObsState.EMPTY,
    )


@given("TMC Subarray in observation state RESTARTING")
def verify_tmc_subarray_observation_state_restarting(
    event_tracer: TangoEventTracer,
    tmc: TMCFacade,
    csp: CSPFacade,
    sdp: SDPFacade,
    mccs: MCCSFacade,
):
    """Verifies the TMC subarray observation state IDLE"""
    setup_tmc(tmc, csp, sdp, mccs, event_tracer)
    tmc.force_change_of_obs_state(ObsState.ABORTED)

    assert_that(event_tracer).described_as(
        f"Both TMC Subarray Node device ({tmc.subarray_node})"
        f", CSP Subarray device ({csp.csp_subarray}) "
        f", MCCS Subarray device ({mccs.mccs_subarray}) "
        f"and SDP Subarray device ({sdp.sdp_subarray}) "
        "ObsState attribute values should be ABORTED."
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        tmc.subarray_node,
        "obsState",
        ObsState.ABORTED,
    ).has_change_event_occurred(
        csp.csp_subarray,
        "obsState",
        ObsState.ABORTED,
    ).has_change_event_occurred(
        sdp.sdp_subarray,
        "obsState",
        ObsState.ABORTED,
    ).has_change_event_occurred(
        mccs.mccs_subarray,
        "obsState",
        ObsState.ABORTED,
    )
    pytest.unique_id = tmc.restart(wait_termination=False)
    assert_that(event_tracer).described_as(
        f"TMC Subarray Node device ({tmc.subarray_node})"
        "ObsState attribute values should be RESTARTING."
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        tmc.subarray_node,
        "obsState",
        ObsState.RESTARTING,
    )


@given("SDP Subarray leaf node in Observation state EMPTY")
def verify_sdp_empty(tmc: TMCFacade, event_tracer: TangoEventTracer):
    """Verify SDP leaf node in observation state EMPTY"""

    assert_that(event_tracer).described_as(
        f"TMC Subarray Node device ({tmc.sdp_subarray_leaf_node})"
        "ObsState attribute values should be RESTARTING."
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        tmc.subarray_node,
        "SdpSubarrayObsState",
        ObsState.EMPTY,
    )


@when(
    "CSP subarray leaf node raises error and transitions"
    " to observation state EMPTY"
)
def verify_csp_ln_error():
    pass


@then("the TMC subarray aggregates to observation state EMPTY")
def verify_sdp_csp_mccs_in_empty_observation_state(
    event_tracer: TangoEventTracer,
    csp: CSPFacade,
    sdp: SDPFacade,
    mccs: MCCSFacade,
    tmc: TMCFacade,
    default_commands_inputs: TestHarnessInputs,
):
    """Verifies the observation states of SDP,CSP and MCCS
    after command Configure.
    """
    assert_that(event_tracer).described_as(
        f"Both TMC Subarray Node device ({tmc.subarray_node})"
        f", CSP Subarray device ({csp.csp_subarray}) "
        f", MCCS Subarray device ({mccs.mccs_subarray}) "
        f"and SDP Subarray device ({sdp.sdp_subarray}) "
        "ObsState attribute values should be READY."
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        tmc.subarray_node,
        "obsState",
        ObsState.EMPTY,
    ).has_change_event_occurred(
        csp.csp_subarray,
        "obsState",
        ObsState.EMPTY,
    ).has_change_event_occurred(
        sdp.sdp_subarray,
        "obsState",
        ObsState.EMPTY,
    ).has_change_event_occurred(
        mccs.mccs_subarray,
        "obsState",
        ObsState.EMPTY,
    )


@then("the TMC subarray reports failure on LongRunningCommandResult attribute")
def verify_subarray_lrcr_failure(
    tmc: TMCFacade, event_tracer: TangoEventTracer
):
    """Verify subarray failure"""

    exception_message = [
        "Exception occurred on the following devices:",
        f"{tmc.csp_subarray_leaf_node.dev_name()}:",
        "Command is not allowed",
    ]
    assert_that(event_tracer).described_as(
        "FAILED ASSUMPTION AFTER ASSIGN RESOURCES: "
        "Central Node device"
        f"({tmc.subarray_node.dev_name()}) "
        "is expected have longRunningCommandResult"
        "(ResultCode.FAILED,exception)",
    ).within_timeout(TIMEOUT).has_desired_result_code_message_in_lrcr_event(
        tmc.subarray_node,
        exception_message,
        pytest.unique_id[0],
        ResultCode.FAILED,
    )

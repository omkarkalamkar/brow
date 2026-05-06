import pytest
from assertpy import assert_that
from pytest_bdd import given, parsers, scenario, then, when
from ska_control_model import ObsState, ResultCode
from ska_integration_test_harness.facades.csp_facade import CSPFacade
from ska_integration_test_harness.facades.mccs_facade import MCCSFacade
from ska_integration_test_harness.facades.sdp_facade import SDPFacade
from ska_integration_test_harness.facades.tmc_facade import TMCFacade
from ska_integration_test_harness.inputs.test_harness_inputs import (
    TestHarnessInputs,
)
from ska_tango_testing.integration import TangoEventTracer, log_events
from ska_tango_testing.mock.placeholders import Anything
from tango import DeviceProxy

from tests.resources.test_harness.constant import (
    ERROR_PROPAGATION_DEFECT,
    RESET_DEFECT,
)
from tests.tmc.tmc_new_iTH.utils import TIMEOUT


def _get_proxy_by_subsystem(
    subsystem: str, csp: CSPFacade, sdp: SDPFacade, mccs: MCCSFacade
) -> DeviceProxy:
    """Returns subsystem proxy."""
    match subsystem:
        case "CSP":
            return csp.csp_subarray
        case "SDP":
            return sdp.sdp_subarray
        case "MCCS":
            return mccs.mccs_subarray


def _get_leaf_node_proxy_by_subsystem(
    subsystem: str, tmc: TMCFacade
) -> DeviceProxy:
    """Returns subsystem leaf node proxy."""
    match subsystem:
        case "CSP":
            return tmc.csp_subarray_leaf_node
        case "SDP":
            return tmc.sdp_subarray_leaf_node
        case "MCCS":
            return tmc.mccs_subarray_leaf_node


def _get_leaf_node_obs_state(subsystem: str) -> str:
    """Returns observation state."""
    match subsystem:
        case "CSP":
            return "CspSubarrayObsState"
        case "SDP":
            return "SdpSubarrayObsState"
        case "MCCS":
            return "ObsState"


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
        tmc.csp_subarray_leaf_node, "longRunningCommandResult"
    )
    event_tracer.subscribe_event(
        tmc.sdp_subarray_leaf_node, "longRunningCommandResult"
    )
    event_tracer.subscribe_event(
        tmc.mccs_subarray_leaf_node, "longRunningCommandResult"
    )
    event_tracer.subscribe_event(
        tmc.sdp_subarray_leaf_node, "SdpSubarrayObsState"
    )
    event_tracer.subscribe_event(
        tmc.csp_subarray_leaf_node, "CspSubarrayObsState"
    )
    event_tracer.subscribe_event(tmc.mccs_subarray_leaf_node, "ObsState")
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
            tmc.sdp_subarray_leaf_node: [
                "SdpSubarrayObsState",
                "longRunningCommandResult",
            ],
            tmc.csp_subarray_leaf_node: [
                "CspSubarrayObsState",
                "longRunningCommandResult",
            ],
            tmc.mccs_subarray_leaf_node: [
                "ObsState",
                "longRunningCommandResult",
            ],
        },
        event_enum_mapping={
            "obsState": ObsState,
            "SdpSubarrayObsState": ObsState,
            "CspSubarrayObsState": ObsState,
        },
    )


@pytest.mark.new
@scenario(
    "../tmc/tmc_new_iTH/features/xtp_109108.feature",
    "Verify SKB-1326",
)
def test_verify_skb_1326():
    """BDD test scenario for verifying SKB-1326."""


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


@given(parsers.parse("{subsystem3} subarray as defective device"))
def set_device_defective(subsystem3: str):
    """Set device as defective."""
    pytest.defective_subsystem = subsystem3


@given("TMC Subarray in observation state RESTARTING")
def verify_tmc_subarray_observation_state_restarting(
    event_tracer: TangoEventTracer,
    tmc: TMCFacade,
    csp: CSPFacade,
    sdp: SDPFacade,
    mccs: MCCSFacade,
    default_commands_inputs: TestHarnessInputs,
):
    """Verifies the TMC subarray observation state IDLE"""
    setup_tmc(tmc, csp, sdp, mccs, event_tracer)
    tmc.force_change_of_obs_state(ObsState.ABORTED, default_commands_inputs)

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
    subarray = _get_proxy_by_subsystem(
        pytest.defective_subsystem, csp, sdp, mccs
    )
    subarray.SetDefective(ERROR_PROPAGATION_DEFECT)
    pytest.unique_id = tmc.restart(wait_termination=False)
    assert_that(event_tracer).described_as(
        f"TMC Subarray Node device ({tmc.subarray_node})"
        "ObsState attribute values should be RESTARTING."
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        tmc.subarray_node,
        "obsState",
        ObsState.RESTARTING,
    )
    assert_that(event_tracer).described_as(
        f"TMC Subarray Node device ({tmc.sdp_subarray_leaf_node})"
        "ObsState attribute values should be RESTARTING."
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        tmc.sdp_subarray_leaf_node,
        "SdpSubarrayObsState",
        ObsState.RESTARTING,
    )


@given(
    parsers.parse("{subsystem1} subarray leaf node in Observation state EMPTY")
)
def verify_subsystem1_ln_empty(
    tmc: TMCFacade, event_tracer: TangoEventTracer, subsystem1: str
):
    """Verify SDP leaf node in observation state EMPTY"""
    subarray_ln = _get_leaf_node_proxy_by_subsystem(subsystem1)
    assert_that(event_tracer).described_as(
        f"TMC Subarray Node device ({subarray_ln.dev_name()})"
        "ObsState attribute values should be EMPTY."
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        subarray_ln,
        _get_leaf_node_obs_state(subsystem1),
        ObsState.EMPTY,
    )


@given(
    parsers.parse("{subsystem2} subarray leaf node in Observation state EMPTY")
)
def verify_subsystem2_ln_empty(
    tmc: TMCFacade, event_tracer: TangoEventTracer, subsystem2: str
):
    """Verify SDP leaf node in observation state EMPTY"""
    subarray_ln = _get_leaf_node_proxy_by_subsystem(subsystem2, tmc)
    assert_that(event_tracer).described_as(
        f"TMC Subarray Node device ({subarray_ln.dev_name()})"
        "ObsState attribute values should be EMPTY."
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        subarray_ln,
        _get_leaf_node_obs_state(subsystem2),
        ObsState.EMPTY,
    )


@when(
    parsers.parse(
        "{subsystem3} subarray leaf node raises error"
        " and transitions to observation state EMPTY"
    )
)
def verify_csp_ln_error(
    csp: CSPFacade,
    sdp: SDPFacade,
    mccs: MCCSFacade,
    tmc: TMCFacade,
    event_tracer: TangoEventTracer,
    subsystem3: str,
):
    exception_message = [
        "Exception occurred, command failed.",
    ]
    subarray = _get_proxy_by_subsystem(subsystem3, csp, sdp, mccs)
    subarray.SetDirectObsState(ObsState.EMPTY)
    subarray_ln = _get_leaf_node_proxy_by_subsystem(subsystem3, tmc)
    assert_that(event_tracer).described_as(
        "FAILED ASSUMPTION AFTER ASSIGN RESOURCES: "
        "Central Node device"
        f"({subarray_ln.dev_name()}) "
        "is expected have longRunningCommandResult"
        "(ResultCode.FAILED,exception)",
    ).within_timeout(TIMEOUT).has_desired_result_code_message_in_lrcr_event(
        subarray_ln,
        exception_message,
        Anything,
        ResultCode.FAILED,
    )

    assert_that(event_tracer).described_as(
        f"TMC Subarray Node device ({subarray_ln.dev_name()})"
        "ObsState attribute values should be EMPTY."
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        subarray_ln,
        "CspSubarrayObsState",
        ObsState.EMPTY,
    )


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
    tmc: TMCFacade,
    csp: CSPFacade,
    sdp: SDPFacade,
    mccs: MCCSFacade,
    event_tracer: TangoEventTracer,
):
    """Verify subarray failure"""
    subarray_ln = _get_leaf_node_proxy_by_subsystem(
        pytest.defective_subsystem, tmc
    )
    exception_message = [
        "Exception occurred on the following devices:",
        f"{subarray_ln}:",
        "Exception occurred, command failed.",
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
        pytest.unique_id[1][0],
        ResultCode.FAILED,
    )
    subarray = _get_proxy_by_subsystem(
        pytest.defective_subsystem, csp, sdp, mccs
    )
    subarray.SetDefective(RESET_DEFECT)

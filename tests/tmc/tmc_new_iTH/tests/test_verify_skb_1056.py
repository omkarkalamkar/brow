import pytest
import tango
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

from tests.resources.test_harness.utils.my_file_json_input import (
    MyFileJSONInput,
)
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


def _update_tel_model_for_csp(tmc: TMCFacade, telmodel_src: str):
    """Updates Tel model source.

    :param csp: _description_
    :type csp: CSPFacade
    """
    itf_telmodel = telmodel_src
    ()
    db = tango.Database()
    db.put_device_property(
        tmc.csp_subarray_leaf_node.dev_name,
        {"TelmodelSource": itf_telmodel},
    )
    cspsal_node = tango.DeviceProxy(tmc.csp_subarray_leaf_node.dev_name)
    cspsal_node.init()


@pytest.mark.SKB_1056
@scenario(
    "../tmc/tmc_new_iTH/features/skb_1056.feature",
    "Verify SKB-1056",
)
def test_configure_command_with_itf_jsons_to_verify_skb_1056():
    """BDD test scenario for verifying SKB-1056."""


@given("a TMC")
def tmc(
    tmc: TMCFacade,
    csp: CSPFacade,
    sdp: SDPFacade,
    mccs: MCCSFacade,
    event_tracer: TangoEventTracer,
):
    """Verifies TMC initial state."""
    _update_tel_model_for_csp(
        tmc, "gitlab://gitlab.com/ska-telescope/aiv/ska-low-itf?main#tmdata"
    )
    _setup_event_subscriptions(tmc, csp, sdp, mccs, event_tracer)
    tmc.move_to_on()
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


@given("a subarray in the IDLE obsState")
def verify_tmc_subarray_observation_state_idle(
    event_tracer: TangoEventTracer,
    tmc: TMCFacade,
    csp: CSPFacade,
    sdp: SDPFacade,
    mccs: MCCSFacade,
):
    """Verifies the TMC subarray observation state IDLE"""
    json_input = MyFileJSONInput("centralnode", "assign_low_itf")

    tmc.assign_resources(json_input)
    assert_that(event_tracer).described_as(
        f"Both TMC Subarray Node device ({tmc.subarray_node})"
        f", CSP Subarray device ({csp.csp_subarray}) "
        f", MCCS Subarray device ({mccs.mccs_subarray}) "
        f"and SDP Subarray device ({sdp.sdp_subarray}) "
        "ObsState attribute values should be IDLE."
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        tmc.subarray_node,
        "obsState",
        ObsState.IDLE,
    ).has_change_event_occurred(
        csp.csp_subarray,
        "obsState",
        ObsState.IDLE,
    ).has_change_event_occurred(
        sdp.sdp_subarray,
        "obsState",
        ObsState.IDLE,
    ).has_change_event_occurred(
        mccs.mccs_subarray,
        "obsState",
        ObsState.IDLE,
    )


@when("I configure it for a scan")
def invoke_configure_command(tmc: TMCFacade):
    """Invokes Configure command on the TMC Subarray."""
    json_input = MyFileJSONInput("subarray", "configure_low_itf")
    tmc.configure(
        json_input,
        wait_termination=True,
    )


@then("the subarray must be in the READY obsState")
def verify_sdp_csp_mccs_in_ready_observation_state(
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
        ObsState.READY,
    ).has_change_event_occurred(
        csp.csp_subarray,
        "obsState",
        ObsState.READY,
    ).has_change_event_occurred(
        sdp.sdp_subarray,
        "obsState",
        ObsState.READY,
    ).has_change_event_occurred(
        mccs.mccs_subarray,
        "obsState",
        ObsState.READY,
    )

    tmc.force_change_of_obs_state(ObsState.EMPTY, default_commands_inputs)
    _update_tel_model_for_csp(
        tmc, "gitlab://gitlab.com/ska-telescope/ska-telmodel-data?main#tmdata"
    )

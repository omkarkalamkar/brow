import json
import logging
import time

import pytest
from assertpy import assert_that
from pytest_bdd import given, parsers, scenario, then, when
from ska_control_model import ObsState, ResultCode
from ska_integration_test_harness.facades.csp_facade import CSPFacade
from ska_integration_test_harness.facades.mccs_facade import MCCSFacade
from ska_integration_test_harness.facades.sdp_facade import SDPFacade
from ska_integration_test_harness.facades.tmc_facade import TMCFacade
from ska_tango_testing.integration import TangoEventTracer
from ska_telmodel.schema import validate as telmodel_validate

from tests.resources.test_harness.constant import (
    INITIAL_LOW_DELAY_JSON,
    LOW_DELAYMODEL_VERSION,
    TIMEOUT,
)
from tests.resources.test_harness.utils.my_file_json_input import (
    MyFileJSONInput,
)
from tests.tmc.tmc_new_iTH.conftest import TestContextData
from tests.tmc.tmc_new_iTH.utils import (
    PSS_BEAMS_CONFIG,
    setup_event_subscriptions,
)


@pytest.mark.SKA_low
@scenario(
    "../tmc/tmc_new_iTH/features/pss_beams_two_subarray.feature",
    "Execute two observations simultaneously where two subarrays are "
    "allocated PSS beams without sharing in TMC Low",
)
def test_pss_beams_two_subarray():
    """BDD test scenario for verifying pss beams with two subarrays."""


@given("subarray 1 and 2 are in the EMPTY ObsState")
def verify_tmc_subarray_observation_state_empty(
    event_tracer: TangoEventTracer,
    tmc: TMCFacade,
    csp: CSPFacade,
    sdp: SDPFacade,
    mccs: MCCSFacade,
    context_data: TestContextData,
):
    setup_event_subscriptions(tmc, csp, sdp, mccs, event_tracer)
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


@when(
    parsers.parse(
        "I Assign subarray 1 with pss beams {pss_beams_subarray1} and "
        "subarray 2 with pss beams {pss_beams_subarray2}"
    )
)
def invoke_assign_resources(
    event_tracer: TangoEventTracer,
    tmc: TMCFacade,
    csp: CSPFacade,
    sdp: SDPFacade,
    mccs: MCCSFacade,
    pss_beams_subarray1: str,
    pss_beams_subarray2: str,
):
    """Assigns and verifies subarrays in IDLE ObsState."""
    json_input = MyFileJSONInput("centralnode", "assign_resources_low")
    json_input_data = json.loads(json_input.as_str())
    pss_beams_start, pss_beams_end = list(
        map(int, pss_beams_subarray1.split("-"))
    )
    json_input_data["csp"]["pss"]["pss_beam_ids"] = list(
        range(pss_beams_start, pss_beams_end + 1)
    )

    _, pytest.unique_id = tmc.central_node.AssignResources(
        json.dumps(json_input_data)
    )
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

    json_input_data = json.loads(json_input.as_str())
    json_input_data["subarray_id"] = 2
    pss_beams_start, pss_beams_end = list(
        map(int, pss_beams_subarray2.split("-"))
    )
    json_input_data["csp"]["pss"]["pss_beam_ids"] = list(
        range(pss_beams_start, pss_beams_end + 1)
    )
    _, pytest.unique_id = tmc.central_node.AssignResources(
        json.dumps(json_input_data)
    )
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


@then("invoking Configure command on both subarrays TMC moves to CONFIGURING")
def delay_calculation_on_cspsln_starts(
    tmc: TMCFacade,
    event_tracer: TangoEventTracer,
):
    """Invokes configure command on the TMC Subarrays
    and verifies delay generation."""

    # Load the base JSON from file
    json_input = MyFileJSONInput("subarray", "configure_low")

    # Parse its data into a dict
    json_input_data = json.loads(json_input.as_str())

    # Configuring subarray 1
    tmc.set_subarray_id(1)
    search_beams_key = PSS_BEAMS_CONFIG["beams"]
    pss_beam_key = PSS_BEAMS_CONFIG["beam"]
    json_input_data["csp"]["search_beams"]["beams"] = search_beams_key[:15]
    json_input_data["csp"]["pss"]["beam"] = pss_beam_key[:15]

    event_tracer.subscribe_event(tmc.subarray_node, "longRunningCommandResult")

    _, pytest.unique_id1 = tmc.subarray_node.Configure(
        json.dumps(json_input_data)
    )

    assert_that(event_tracer).described_as(
        "TMC Subarray Node ObsState should move to CONFIGURING"
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        tmc.subarray_node,
        "obsState",
        ObsState.CONFIGURING,
    )

    # Configuring subarray 2
    tmc.set_subarray_id(2)

    json_input_data = json.loads(json_input.as_str())
    json_input_data["csp"]["search_beams"]["beams"] = search_beams_key[16:]
    json_input_data["csp"]["pss"]["beam"] = pss_beam_key[16:]

    event_tracer.subscribe_event(tmc.subarray_node, "longRunningCommandResult")

    _, pytest.unique_id2 = tmc.subarray_node.Configure(
        json.dumps(json_input_data)
    )

    assert_that(event_tracer).described_as(
        "TMC Subarray Node ObsState should move to CONFIGURING"
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        tmc.subarray_node,
        "obsState",
        ObsState.CONFIGURING,
    )


@then("the Subarray is configured successfully")
def verify_sdp_csp_mccs_in_ready_observation_state(
    event_tracer: TangoEventTracer,
    csp: CSPFacade,
    sdp: SDPFacade,
    mccs: MCCSFacade,
    tmc: TMCFacade,
):
    """Verifies the observation states of SDP,CSP and MCCS
    after command Configure.
    """
    expected_lrcr = (
        pytest.unique_id2[0],
        json.dumps((int(ResultCode.OK), "Command Completed")),
    )

    assert_that(event_tracer).described_as(
        "TMC Subarray Node longRunningCommandResult should indicate "
        "successful completion of Configure command"
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        tmc.subarray_node,
        "longRunningCommandResult",
        expected_lrcr,
    )
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


@then("CSPSLN generates updated delay model for pss beams")
def verify_cspsln_delay_model_updated(
    tmc: TMCFacade,
):
    """
    Verifies that CSPSLN has generated / updated delay models
    on some configured pss beam attributes after successful Configure.
    """
    wait_time = time.time() + 5
    attributes = [f"delayModelPSSBeam{str(i).zfill(2)}" for i in range(1, 30)]
    generated_delay_model_json = INITIAL_LOW_DELAY_JSON
    for attribute in attributes:
        while time.time() < wait_time:
            generated_delay_model = tmc.csp_subarray_leaf_node.read_attribute(
                attribute
            ).value
            generated_delay_model_json = json.loads(generated_delay_model)
            logging.info(
                "Generated %s Delay Model json: %s",
                attribute,
                generated_delay_model_json,
            )
            if generated_delay_model_json != INITIAL_LOW_DELAY_JSON:
                break
            time.sleep(1)

        assert (
            generated_delay_model_json != INITIAL_LOW_DELAY_JSON
        ), f"{attribute} has not been updated from initial values"

        telmodel_validate(
            version=LOW_DELAYMODEL_VERSION,
            config=generated_delay_model_json,
            strictness=2,
        )

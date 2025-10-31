import copy
import json
import logging

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
from ska_tango_testing.mock.placeholders import Anything
from tests.resources.test_harness.utils.my_file_json_input import (
    MyFileJSONInput,
)
from tests.resources.test_support.constant_low import (
    FAILED_RESULT_DEFECT,
    SDP_BACK_TO_INITIAL_STATE,
)
from tests.tmc.tmc_new_iTH.conftest import TestContextData
from tests.tmc.tmc_new_iTH.utils import (
    TIMEOUT,
    reset_defects,
    setup_event_subscriptions,
)


@pytest.mark.SKB_1056
@scenario(
    "../tmc/tmc_new_iTH/features/non_sidereal_tracking.feature",
    "Non sidereal tracking in TMC Low",
)
def test_non_sidereal_tracking():
    """BDD test scenario for verifying non sidereal tracking."""
    
@given("a Subarray with resources assigned")
def verify_tmc_subarray_observation_state_idle(
    event_tracer: TangoEventTracer,
    tmc: TMCFacade,
    csp: CSPFacade,
    sdp: SDPFacade,
    mccs: MCCSFacade,
    default_commands_inputs: TestHarnessInputs,
    context_data: TestContextData,
):
    setup_event_subscriptions(tmc, csp, sdp, mccs, event_tracer)
    tmc.move_to_on(wait_termination=True)
    tmc.force_change_of_obs_state(
        ObsState.IDLE, default_commands_inputs, wait_termination=True
    )
    context_data.csp_obsstate = ObsState.IDLE
    context_data.sdp_obsstate = ObsState.IDLE
    context_data.mccs_obsstate = ObsState.IDLE
    pytest.is_successive_configure = False



@when(
    parsers.parse("I Configure it for tracking a non-sidereal object "
    "from {non_sidereal_objects}")
)
def invoke_configure_command(
    tmc: TMCFacade,
    sdp: SDPFacade,
    csp: CSPFacade,
    non_sidereal_objects: str,
    event_tracer: TangoEventTracer,
    failed_devices: str,
):
    """Invokes configure command on the TMC Subarray."""
    logging.info(
        f"Invoking Configure command on TMC Subarray "
        f"for non-sidereal object: {non_sidereal_objects}"
    )
    json_input = MyFileJSONInput("subarray", "non_sidereal_tracking")
    tmc.configure(
        json_input,
        wait_termination=False,
    )
    assert_that(event_tracer).described_as(
        "TMC Subarray Leaf Node"
        "ObsState attribute value should move "
        " to CONFIGURING."
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
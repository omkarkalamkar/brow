import json
import logging
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
from ska_tango_testing.integration import TangoEventTracer
from ska_telmodel.schema import validate as telmodel_validate

from tests.resources.test_harness.constant import (
    INITIAL_LOW_DELAY_JSON,
    LOW_DELAYMODEL_VERSION,
)
from tests.resources.test_harness.utils.my_file_json_input import (
    MyFileJSONInput,
)
from tests.tmc.tmc_new_iTH.conftest import TestContextData
from tests.tmc.tmc_new_iTH.utils import (
    FIELD_CONFIGS,
    TIMEOUT,
    setup_event_subscriptions,
)


@pytest.mark.SKA_low
@scenario(
    "non_sidereal_tracking_adr63.feature",
    "Configure using ADR-63 field key with different "
    "reference frames in TMC Low",
    features_base_dir="tests/tmc/tmc_new_iTH/features",
)
def test_non_sidereal_tracking():
    """BDD test scenario for verifying ADR-63 field key support in TMC Low."""


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
    parsers.parse(
        "I Configure the subarray using the MCCS field "
        "key with reference_frame {reference_frame} "
        "and target {target_name}"
    )
)
def invoke_configure_command(
    tmc: TMCFacade,
    reference_frame: str,
    target_name: str,
    event_tracer: TangoEventTracer,
):
    """Invokes configure command on the TMC Subarray using ADR-63 field key."""
    logging.info(
        f"Invoking Configure command on TMC Subarray "
        f"with MCCS field reference_frame={reference_frame}, "
        f"target={target_name}"
    )

    # Load the base JSON from file
    json_input = MyFileJSONInput("subarray", "non_sidereal_tracking_adr63")

    # Parse its data into a dict
    json_input_data = json.loads(json_input.as_str())

    if (
        "mccs" in json_input_data
        and "subarray_beams" in json_input_data["mccs"]
    ):
        for beam in json_input_data["mccs"]["subarray_beams"]:
            if "field" in beam and isinstance(beam["field"], dict):
                field_config = FIELD_CONFIGS[target_name]
                beam["field"] = field_config

    updated_json_input = json.dumps(json_input_data)

    event_tracer.subscribe_event(tmc.subarray_node, "longRunningCommandResult")

    _, pytest.unique_id = tmc.subarray_node.Configure(updated_json_input)

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
        pytest.unique_id[0],
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


@then("CSPSLN generates updated delay model for station beams")
def verify_cspsln_delay_model_updated(
    tmc: TMCFacade,
):
    """
    Verifies that CSPSLN has generated / updated delay models on at least
    some station beam attributes after successful Configure with ADR-63 target.
    """
    wait_time = time.time() + 5
    attributes = [
        f"delayModelStationBeam{str(i).zfill(2)}" for i in range(1, 9)
    ]
    generated_delay_model_json = INITIAL_LOW_DELAY_JSON
    for attribute in attributes:
        while time.time() < wait_time:
            generated_delay_model = tmc.csp_subarray_leaf_node.read_attribute(
                attribute
            ).value
            generated_delay_model_json = json.loads(generated_delay_model)
            logging.info(
                "Generated %s (poll): %s",
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


@then(
    parsers.parse(
        "the MCCS Subarray commandCallInfo contains the correct "
        "field configuration "
        "for target {target_name}"
    )
)
def verify_mccs_command_call_info(
    tmc: TMCFacade,
    mccs: MCCSFacade,
    target_name: str,
    event_tracer: TangoEventTracer,
):
    """Verifies that the MCCS commandCallInfo contains
    the exact expected field configuration."""
    event_tracer.subscribe_event(mccs.mccs_subarray, "CommandCallInfo")
    logging.info(
        f"MCCS Command Call Info: {mccs.mccs_subarray.commandCallInfo}"
    )
    command_call_info = mccs.mccs_subarray.commandCallInfo

    if (
        isinstance(command_call_info, (tuple, list))
        and len(command_call_info) > 0
    ):
        command_entry = command_call_info[0]
        assert isinstance(
            command_entry, (tuple, list)
        ), "Invalid command entry format."
        command_name, command_json_str = command_entry
    else:
        raise AssertionError(
            f"Unexpected commandCallInfo format: {command_call_info}"
        )

    assert (
        command_name == "Configure"
    ), f"Unexpected command name: {command_name}"

    command_data = json.loads(command_json_str)
    assert (
        "subarray_beams" in command_data
    ), "Missing 'subarray_beams' in commandCallInfo JSON."

    received_field = command_data["subarray_beams"][0]["field"]
    expected_field = FIELD_CONFIGS[target_name]

    assert received_field == expected_field, (
        f"Incorrect field configuration in MCCS commandCallInfo.\n"
        f"Expected: {expected_field}\n"
        f"Received: {received_field}"
    )

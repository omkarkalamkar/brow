"""
This module defines a Pytest BDD test scenario for checking the rejection of
invalid JSON inputs during the Configure command execution on a
Telescope Monitoring and Control (TMC) system
The scenario includes steps to set up the TMC, configure the subarray,
and validate the rejection
of various invalid JSON inputs.
"""
import json

import pytest
from assertpy import assert_that
from pytest_bdd import given, parsers, scenario, then, when
from ska_control_model import ObsState
from ska_tango_testing.integration import TangoEventTracer, log_events
from tango import DevState

from tests.conftest import LOGGER
from tests.resources.test_harness.central_node_low import CentralNodeWrapperLow
from tests.resources.test_harness.constant import TIMEOUT
from tests.resources.test_harness.helpers import set_receive_address
from tests.resources.test_harness.subarray_node_low import (
    SubarrayNodeWrapperLow,
)
from tests.resources.test_harness.utils.common_utils import JsonFactory
from tests.resources.test_support.common_utils.result_code import ResultCode
from tests.resources.test_support.common_utils.tmc_helpers import (
    prepare_json_args_for_centralnode_commands,
    prepare_json_args_for_commands,
)


@pytest.mark.SKA_low
@scenario(
    "../features/tmc/check_invalid_json_not_allowed.feature",
    "Invalid json rejected by TMC Low for Configure command",
)
def test_invalid_json_in_configure_obsState():
    """
    Test SubarrayNode Low Configure command with invalid json data.
    """


@given("the TMC is On")
def given_tmc(
    central_node_low: CentralNodeWrapperLow, event_tracer: TangoEventTracer
):
    """Ensure the TMC is in the 'On' state."""
    event_tracer.subscribe_event(
        central_node_low.central_node, "telescopeState"
    )
    event_tracer.subscribe_event(
        central_node_low.central_node, "longRunningCommandResult"
    )
    event_tracer.subscribe_event(
        central_node_low.subarray_node, "longRunningCommandResult"
    )
    central_node_low.move_to_on()
    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "GIVEN" STEP: '
        "'the TMC is On'"
        "Central Node device"
        f"({central_node_low.central_node.dev_name()}) "
        "is expected to be in TelescopeState ON",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        central_node_low.central_node,
        "telescopeState",
        DevState.ON,
    )


@given("the subarray is in IDLE obsState")
def tmc_check_status(
    central_node_low: CentralNodeWrapperLow,
    event_tracer: TangoEventTracer,
    command_input_factory: JsonFactory,
):
    """Set the subarray to 'IDLE' observation state."""
    event_tracer.subscribe_event(central_node_low.subarray_node, "obsState")
    set_receive_address(central_node_low)
    assign_input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_low", command_input_factory
    )
    _, unique_id = central_node_low.store_resources(assign_input_json)
    print(unique_id)
    log_events(
        {
            central_node_low.subarray_node: [
                "obsState",
                "longRunningCommandResult",
            ],
            central_node_low.central_node: ["longRunningCommandResult"],
        }
    )
    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "GIVEN" STEP: '
        "'the subarray is in IDLE obsState'"
        "Subarray Node device"
        f"({central_node_low.subarray_node.dev_name()}) "
        "is expected to be in IDLE obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        central_node_low.subarray_node,
        "obsState",
        ObsState.IDLE,
    )
    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "GIVEN" STEP: '
        "'the subarray is in IDLE obsState'"
        "Central Node device"
        f"({central_node_low.central_node.dev_name()}) "
        "is expected have longRunningCommand as"
        '(unique_id,(ResultCode.OK,"Command Completed"))',
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        central_node_low.central_node,
        "longRunningCommandResult",
        (unique_id[0], json.dumps((int(ResultCode.OK), "Command Completed"))),
    )


@when(
    parsers.parse("the command Configure is invoked with {invalid_json} input")
)
def send(subarray_node_low, invalid_json, command_input_factory):
    """Invoke the Configure command with different invalid JSON inputs."""

    configure_json = prepare_json_args_for_commands(
        "configure_low_4.1", command_input_factory
    )
    if invalid_json == "csp_key_missing":
        invalid_configure_json = json.loads(configure_json)
        del invalid_configure_json["csp"]
        pytest.command_result = subarray_node_low.execute_transition(
            "Configure", json.dumps(invalid_configure_json)
        )
    elif invalid_json == "sdp_key_missing":
        invalid_configure_json = json.loads(configure_json)
        del invalid_configure_json["sdp"]
        pytest.command_result = subarray_node_low.execute_transition(
            "Configure", json.dumps(invalid_configure_json)
        )
    elif invalid_json == "mccs_key_missing":
        invalid_configure_json = json.loads(configure_json)
        del invalid_configure_json["mccs"]
        pytest.command_result = subarray_node_low.execute_transition(
            "Configure", json.dumps(invalid_configure_json)
        )
    # elif invalid_json == "tmc_key_missing":
    #     invalid_configure_json = json.loads(configure_json)
    #     del invalid_configure_json["tmc"]
    #     pytest.command_result = subarray_node_low.execute_transition(
    #         "Configure", json.dumps(invalid_configure_json)
    #     )
    elif invalid_json == "scan_duration_key_missing":
        invalid_configure_json = json.loads(configure_json)
        del invalid_configure_json["tmc"]["scan_duration"]
        pytest.command_result = subarray_node_low.execute_transition(
            "Configure", json.dumps(invalid_configure_json)
        )
    elif invalid_json == "empty_string":
        invalid_configure_json = {}
        pytest.command_result = subarray_node_low.execute_transition(
            "Configure", json.dumps(invalid_configure_json)
        )


@then(
    parsers.parse(
        "the TMC should reject the {invalid_json} with ResultCode.Rejected"
    )
)
def invalid_command_rejection(invalid_json):
    """Verify that the TMC rejects the invalid JSON with the expected
    ResultCode  and validation messages."""
    # asserting validation resultcode
    assert pytest.command_result[0][0] == ResultCode.REJECTED
    # asserting validations message as per invalid json
    if invalid_json == "csp_key_missing":
        assert (
            "Validation 'Low TMC configure 4.1' Missing key: 'csp'"
            in pytest.command_result[1][0]
        )
    elif invalid_json == "sdp_key_missing":
        assert (
            "Validation 'Low TMC configure 4.1' Missing key: 'sdp'"
            in pytest.command_result[1][0]
        )
    elif invalid_json == "mccs_key_missing":
        assert (
            "Validation 'Low TMC configure 4.1' Missing key: 'mccs'"
            in pytest.command_result[1][0]
        )
    # TODO: Enable this once CDM validations are accomodated
    # Tel Model validations doesn't raise error for missing
    # "tmc" key since its optional in schema generation
    # elif invalid_json == "tmc_key_missing":
    #     assert (
    #         "Malformed input string. Missing key: 'tmc'"
    #         in pytest.command_result[1][0]
    #     )
    elif invalid_json == "scan_duration_key_missing":
        assert (
            "Validation 'Low TMC configure 4.1' Key 'tmc' "
            + "error:\nMissing key: 'scan_duration'"
            in pytest.command_result[1][0]
        )
    elif invalid_json == "empty_string":
        # TODO: Enable this once CDM available with latest telmodel
        # assert "Invalid 'interface' value: None"
        # in pytest.command_result[1][0]
        assert (
            "JSON Error: Missing 'interface' "
            "key in the Configure json" in pytest.command_result[1][0]
        )


@then("TMC subarray remains in IDLE obsState")
def tmc_status(subarray_node_low: SubarrayNodeWrapperLow):
    """Ensure that the TMC subarray remains in the 'IDLE' observation state
    after rejection."""
    assert subarray_node_low.subarray_node.obsState == ObsState.IDLE


@then(
    "TMC successfully executes the Configure \
command for the subarray with a valid json"
)
def tmc_accepts_next_commands(
    subarray_node_low: SubarrayNodeWrapperLow,
    event_tracer: TangoEventTracer,
    command_input_factory: JsonFactory,
):
    """Execute the Configure command with a valid JSON and verify successful
    execution."""
    configure_json = prepare_json_args_for_commands(
        "configure_low", command_input_factory
    )
    LOGGER.info("Input argin for Configure:%s", configure_json)

    # Invoke Configure() Command on TMC
    LOGGER.info("Invoking Configure command on TMC SubarrayNode")

    subarray_node_low.store_configuration_data(configure_json)

    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "THEN" STEP: '
        "'TMC successfully executes the Configure'"
        "'command for the subarray with a valid json'"
        "Subarray Node device"
        f"({subarray_node_low.subarray_node.dev_name()}) "
        "is expected to be in READY obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        subarray_node_low.subarray_node,
        "obsState",
        ObsState.READY,
    )

"""
This module defines a Pytest BDD test scenario for checking the
delay value generation during the Configure command execution on a
Telescope Monitoring and Control (TMC) system
The scenario includes steps to set up the TMC, configure the subarray,
and checks whether CspSubarrayLeafNode starts generating delay value.
"""
import json

import pytest
from assertpy import assert_that
from pytest_bdd import given, scenario, then, when
from ska_control_model import ObsState
from ska_tango_base.commands import ResultCode
from ska_tango_testing.integration import TangoEventTracer, log_events
from ska_telmodel.schema import validate as telmodel_validate
from tango import DevState

from tests.resources.test_harness.central_node_low import CentralNodeWrapperLow
from tests.resources.test_harness.constant import (
    INITIAL_LOW_DELAY_JSON,
    LOW_DELAYMODEL_VERSION,
    TIMEOUT,
)
from tests.resources.test_harness.helpers import (
    prepare_json_args_for_centralnode_commands,
    prepare_json_args_for_commands,
    set_receive_address,
    wait_and_validate_device_attribute_value,
)
from tests.resources.test_harness.subarray_node_low import (
    SubarrayNodeWrapperLow,
)
from tests.resources.test_harness.utils.common_utils import JsonFactory


@pytest.mark.SKA_low
@scenario(
    "../features/tmc/xtp_68914_tmc_stops_generating_low_delay_model.feature",
    "TMC generates delay values",
)
def test_test_tmc_stops_generating_delay_model():
    """
    Test whether tmc stops generating delay values on CSP Subarray Leaf Node.
    """


@given("the telescope is in ON state")
def given_telescope_is_in_on_state(
    central_node_low: CentralNodeWrapperLow, event_tracer: TangoEventTracer
):
    """Method to check if telescope is in ON State"""
    event_tracer.subscribe_event(
        central_node_low.central_node, "telescopeState"
    )
    event_tracer.subscribe_event(
        central_node_low.central_node, "longRunningCommandResult"
    )
    log_events(
        {
            central_node_low.central_node: [
                "telescopeState",
                "longRunningCommandResult",
            ],
        }
    )
    central_node_low.move_to_on()
    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "GIVEN" STEP: '
        "'the telescope is is ON state'"
        "Central Node device"
        f"({central_node_low.central_node.dev_name()}) "
        "is expected to be in TelescopeState ON",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        central_node_low.central_node,
        "telescopeState",
        DevState.ON,
    )
    event_tracer.clear_events()


@given("subarray is configured and starts generating delay values")
def subarray_start_generating_delay_values(
    central_node_low: CentralNodeWrapperLow,
    subarray_node_low: SubarrayNodeWrapperLow,
    event_tracer: TangoEventTracer,
    command_input_factory: JsonFactory,
) -> None:
    """Checks subarray is configured and delay values are getting generated."""
    event_tracer.subscribe_event(subarray_node_low.subarray_node, "obsState")
    event_tracer.subscribe_event(
        subarray_node_low.subarray_node, "longRunningCommandResult"
    )
    log_events(
        {
            subarray_node_low.subarray_node: [
                "obsState",
                "longRunningCommandResult",
            ]
        }
    )
    set_receive_address(central_node_low)
    assign_input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_low", command_input_factory
    )
    configure_input_json = prepare_json_args_for_commands(
        "configure_low", command_input_factory
    )
    _, unique_id = central_node_low.store_resources(assign_input_json)
    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "GIVEN" STEP: '
        '"subarray is in obsState IDLE"'
        "Subarray Node device"
        f"({subarray_node_low.subarray_node.dev_name()}) "
        "is expected to be in IDLE obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        subarray_node_low.subarray_node,
        "obsState",
        ObsState.IDLE,
    )
    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "GIVEN" STEP: '
        '"subarray is in obsState IDLE"'
        "Central Node device"
        f"({subarray_node_low.subarray_node.dev_name()}) "
        "is expected have longRunningCommand as"
        '(unique_id,(ResultCode.OK,"Command Completed"))',
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        central_node_low.central_node,
        "longRunningCommandResult",
        (
            unique_id[0],
            json.dumps((int(ResultCode.OK), "Command Completed")),
        ),
    )

    _, unique_id = subarray_node_low.store_configuration_data(
        configure_input_json
    )
    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "WHEN" STEP: '
        '"I configure the subarray"'
        "Subarray Node device"
        f"({subarray_node_low.subarray_node.dev_name()}) "
        "is expected to be in READY obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        subarray_node_low.subarray_node,
        "obsState",
        ObsState.READY,
    )
    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "WHEN" STEP: '
        '"I configure the subarray"'
        "Subarray Node device"
        f"({subarray_node_low.subarray_node.dev_name()}) "
        "is expected have longRunningCommand as"
        '(unique_id,(ResultCode.OK,"Command Completed"))',
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        subarray_node_low.subarray_node,
        "longRunningCommandResult",
        (
            unique_id[0],
            json.dumps((int(ResultCode.OK), "Command Completed")),
        ),
    )
    generated_delay_model = (
        subarray_node_low.csp_subarray_leaf_node.read_attribute(
            "delayModel"
        ).value
    )
    generated_delay_model_json = json.loads(generated_delay_model)
    assert generated_delay_model_json != json.dumps(INITIAL_LOW_DELAY_JSON)
    telmodel_validate(
        version=LOW_DELAYMODEL_VERSION,
        config=generated_delay_model_json,
        strictness=2,
    )
    event_tracer.clear_events()


@when("I end the observation")
def invoke_end_command(
    subarray_node_low: SubarrayNodeWrapperLow, event_tracer: TangoEventTracer
) -> None:
    """Invoke End command."""
    _, unique_id = subarray_node_low.end_observation()

    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "WHEN" STEP: '
        '"I end the observation"'
        "Subarray Node device"
        f"({subarray_node_low.subarray_node.dev_name()}) "
        "is expected to be in IDLE obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        subarray_node_low.subarray_node,
        "obsState",
        ObsState.IDLE,
    )
    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "WHEN" STEP: '
        '"I end the observation"'
        "Subarray Node device"
        f"({subarray_node_low.subarray_node.dev_name()}) "
        "is expected have longRunningCommand as"
        '(unique_id,(ResultCode.OK,"Command Completed"))',
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        subarray_node_low.subarray_node,
        "longRunningCommandResult",
        (
            unique_id[0],
            json.dumps((int(ResultCode.OK), "Command Completed")),
        ),
    )
    event_tracer.clear_events()


@then("CSP Subarray Leaf Node stops generating delay values")
def check_if_delay_values_are_not_generating(subarray_node_low) -> None:
    """Check if delay values are stopped generating."""
    assert wait_and_validate_device_attribute_value(
        subarray_node_low.csp_subarray_leaf_node,
        "delayModel",
        json.dumps(INITIAL_LOW_DELAY_JSON),
        is_json=True,
    )

"""
This module defines a BDD (Behavior-Driven Development) test scenario
using pytest-bdd to verify the behavior of the Telescope Monitoring and
Control (TMC) system resolution of SKB-476.
"""


import json

import pytest
from assertpy import assert_that
from pytest_bdd import given, parsers, scenario, then, when
from ska_control_model import ObsState
from ska_tango_base.commands import ResultCode
from ska_tango_testing.integration import TangoEventTracer, log_events
from tango import DevState

from tests.resources.test_harness.central_node_low import CentralNodeWrapperLow
from tests.resources.test_harness.helpers import remove_timing_beams
from tests.resources.test_harness.subarray_node_low import (
    SubarrayNodeWrapperLow,
)
from tests.resources.test_harness.utils.common_utils import JsonFactory
from tests.resources.test_support.common_utils.tmc_helpers import (
    prepare_json_args_for_centralnode_commands,
    prepare_json_args_for_commands,
)
from tests.resources.test_support.constant_low import TIMEOUT


@pytest.mark.SKA_low
@scenario(
    "../features/tmc/SKB_476.feature",
    "Verify SKB-476",
)
def test_verify_skb_476():
    """BDD test scenario for verifying SKB-476"""


@given("a TMC")
def given_a_tmc(
    central_node_low: CentralNodeWrapperLow, event_tracer: TangoEventTracer
):
    """
    This method invokes On command from central node and verifies
    the state of telescope after the invocation.
    Args:
        central_node (CentralNodeWrapperLow): Object of Central node wrapper
        event_tracer(TangoEventTracer): object of TangoEventTracer used for
        managing the device events
    """
    event_tracer.subscribe_event(
        central_node_low.central_node, "telescopeState"
    )
    event_tracer.subscribe_event(
        central_node_low.central_node, "longRunningCommandResult"
    )
    event_tracer.subscribe_event(central_node_low.subarray_node, "obsState")
    log_events(
        {
            central_node_low.central_node: [
                "telescopeState",
                "longRunningCommandResult",
            ],
            central_node_low.subarray_node: ["obsState"],
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
    assert_that(event_tracer).described_as(
        "FAILED UNEXPECTED INITIAL OBSSTATE: "
        "Subarray Node device"
        f"({central_node_low.subarray_node.dev_name()}) "
        "is expected to be in EMPTY obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        central_node_low.subarray_node,
        "obsState",
        ObsState.EMPTY,
    )


@given("subarray node is in observation state IDLE")
def central_node_assign_resources(
    central_node_low: CentralNodeWrapperLow,
    command_input_factory: JsonFactory,
    event_tracer: TangoEventTracer,
):
    """
    This method invokes AssignResources command on central node.

    Args:
        central_node (CentralNodeWrapperLow): Object of Central node wrapper
        command_input_factory (JsonFactory): Object of json factory
        event_tracer(TangoEventTracer): object of TangoEventTracer used for
        managing the device events
    """
    assign_input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_low", command_input_factory
    )
    result, pytest.unique_id = central_node_low.perform_action(
        "AssignResources", assign_input_json
    )
    assert pytest.unique_id[0].endswith("AssignResources")
    assert result[0] == ResultCode.QUEUED

    assert_that(event_tracer).described_as(
        "FAILED UNEXPECTED OBSSTATE: "
        "Subarray Node device"
        f"({central_node_low.subarray_node.dev_name()}) "
        "is expected to be in IDLE obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        central_node_low.subarray_node,
        "obsState",
        ObsState.IDLE,
    )


@when(
    parsers.parse(
        "I invoke configure command without {key} in csp configure json"
    )
)
def check_configure_json_and_invoke_command(
    command_input_factory: JsonFactory,
    subarray_node_low: SubarrayNodeWrapperLow,
    key: str,
):
    """
    Method to verify the input json and invocation of configure command
    on subarray node.

    Args:
        command_input_factory (JsonFactory): Object of json factory.
        subarray_node_low (SubarrayNodeWrapperLow): Object of subarray
        node wrapper.
        key (str): Key that should be absent in configure json after
        removing 'timing_beams'.
    """

    # Prepare initial JSON input for the configure command
    configure_input_json = prepare_json_args_for_commands(
        "configure_low", command_input_factory
    )

    # Remove the 'timing_beams' from the configure input JSON
    config_json = remove_timing_beams(configure_input_json)

    # Check if the 'key' is not present in the modified configure JSON
    assert key not in json.loads(config_json)["csp"]["lowcbf"].keys()

    # Invoke the command on the subarray node with the modified JSON
    subarray_node_low.store_configuration_data(config_json)


@then("subarray node transitions to observation state READY")
def check_obs_state_ready(
    event_tracer: TangoEventTracer, subarray_node_low: SubarrayNodeWrapperLow
):
    """Method to check observation state of subarray node
    after configure command.

    Args:
        event_tracer(TangoEventTracer): object of TangoEventTracer used for
        managing the device events
        subarray_node_low (SubarrayNodeWrapperLow): Object of subarray
        node wrapper
    """
    assert_that(event_tracer).described_as(
        "FAILED UNEXPECTED OBSSTATE: "
        "Subarray Node device"
        f"({subarray_node_low.subarray_node.dev_name()}) "
        "is expected to be in READY obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        subarray_node_low.subarray_node,
        "obsState",
        ObsState.READY,
    )

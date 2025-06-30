"""
This module defines a BDD (Behavior-Driven Development) test scenario
using pytest-bdd to verify the behavior of the Telescope Monitoring and
Control (TMC) system to verify the SKB-643.
"""


import json
from copy import deepcopy

import pytest
from assertpy import assert_that
from pytest_bdd import given, parsers, scenario, then, when
from ska_control_model import ObsState
from ska_tango_base.commands import ResultCode
from ska_tango_testing.integration import TangoEventTracer, log_events
from tango import DevState

from tests.resources.test_harness.central_node_low import CentralNodeWrapperLow
from tests.resources.test_harness.subarray_node_low import (
    SubarrayNodeWrapperLow,
)
from tests.resources.test_harness.utils.common_utils import JsonFactory
from tests.resources.test_support.common_utils.tmc_helpers import (
    prepare_json_args_for_centralnode_commands,
)
from tests.resources.test_support.constant_low import TIMEOUT

RESOURCE_CONFIG = {
    "pst": {
        "beams_id_key": "pst_beam_ids",
        "beams_id_values": [1],
    },  # Use 'beams_id' as expected after processing
    "pss": {
        "beams_id_key": "pss_beam_ids",
        "beams_id_values": [1, 2, 3],
    },  # Same for 'pss'
}


@pytest.mark.SKA_low
@scenario(
    "../features/tmc/SKB_643.feature",
    "Verify SKB-643",
)
def test_verify_skb_643():
    """BDD test scenario for verifying SKB-643"""


@given("TMC Subarray is in observation state EMPTY")
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


@when(
    parsers.parse(
        "I invoke the assign command on TMC Subarray with only "
        + "{resource_type} resource"
    )
)
def invoke_assign_resources(
    central_node_low: CentralNodeWrapperLow,
    command_input_factory: JsonFactory,
    event_tracer: TangoEventTracer,
    resource_type,
):
    """Invoke assign resources."""
    config = RESOURCE_CONFIG[resource_type]

    assign_input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_low", command_input_factory
    )
    assign_data = deepcopy(
        json.loads(assign_input_json)
        if isinstance(assign_input_json, str)
        else assign_input_json
    )

    if "csp" not in assign_data:
        assign_data["csp"] = {}

    assign_data["csp"][resource_type] = {
        config["beams_id_key"]: config["beams_id_values"]
    }
    # Convert assign_data to JSON string if needed
    assign_data_json = json.dumps(assign_data)

    _, unique_id = central_node_low.store_resources(assign_data_json)
    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "WHEN" STEP: '
        "'I invoke the assign'"
        "command on TMC Subarray"
        f"({central_node_low.subarray_node.dev_name()}) "
        "is expected to be in IDLE obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        central_node_low.subarray_node,
        "obsState",
        ObsState.IDLE,
    )
    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "GIVEN" STEP: '
        "'I invoke the assign'"
        "command on TMC Subarray"
        f"({central_node_low.central_node.dev_name()}) "
        "is expected have longRunningCommand as"
        '(unique_id,(ResultCode.OK,"Command Completed"))',
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        central_node_low.central_node,
        "longRunningCommandResult",
        (unique_id[0], json.dumps((int(ResultCode.OK), "Command Completed"))),
    )


@then("TMC Subarray invokes assign on csp with json containing beams_id")
def check_beam_ids_in_json(subarray_node_low: SubarrayNodeWrapperLow):
    """Check beam id for csp assign json"""
    # Retrieve the JSON input from the last command call to CSP
    input_json = subarray_node_low.subarray_devices[
        "csp_subarray"
    ].commandCallInfo[-1][-1]

    # If input_json is a string, parse it into a dictionary
    if isinstance(input_json, str):
        try:
            input_json = json.loads(input_json)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to decode JSON: {e}") from e

    # Navigate to the 'csp' section of the JSON
    argin_csp = input_json.get("csp", {})

    # Check for "pss" and verify the presence of "beams_id"
    if "pss" in argin_csp:
        pss = argin_csp["pss"]
        # After assign is invoked, simply check for the presence of "beams_id"
        assert (
            "beams_id" in pss
        ), "'beams_id' not found in pss after assignment"

    # Check for "pst" and verify the presence of "beams_id"
    if "pst" in argin_csp:
        pst = argin_csp["pst"]
        # After assign is invoked, simply check for the presence of "beams_id"
        assert (
            "beams_id" in pst
        ), "'beams_id' not found in pst after assignment"


@then("TMC Subarray transitions to observation state IDLE")
def check_subarray_is_in_idle(
    event_tracer: TangoEventTracer,
    subarray_node_low: SubarrayNodeWrapperLow,
):
    """Check Subarray is in IDLE Observation state"""
    assert_that(event_tracer).described_as(
        "FAILED ASSUMPTION AFTER ASSIGN RESOURCES: "
        "Subarray Node device"
        f"({subarray_node_low.subarray_node.dev_name()}) "
        "is expected to be in IDLE obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        subarray_node_low.subarray_node,
        "obsState",
        ObsState.IDLE,
    )

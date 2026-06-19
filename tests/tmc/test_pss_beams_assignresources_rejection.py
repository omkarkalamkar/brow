"""
This module defines a BDD test scenario using pytest-bdd to verify:
PSS beam sharing rejection during AssignResources .
"""
import json

import pytest
from assertpy import assert_that
from pytest_bdd import given, scenario, then, when
from ska_control_model import ObsState
from ska_tango_base.commands import ResultCode
from ska_tango_testing.integration import TangoEventTracer, log_events
from tango import DevState

from tests.resources.test_harness.central_node_low import CentralNodeWrapperLow
from tests.resources.test_harness.utils.common_utils import JsonFactory
from tests.resources.test_support.common_utils.tmc_helpers import (
    prepare_json_args_for_centralnode_commands,
)
from tests.resources.test_support.constant_low import TIMEOUT


@pytest.fixture(scope="function")
def pss_beams_from_json(command_input_factory: JsonFactory) -> list[int]:
    """
    Fixture that extracts the actual PSS beam IDs from the standard
    assign_resources_low.json file so the test stays in sync with the data.
    """
    assign_input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_low", command_input_factory
    )
    assign_data = json.loads(assign_input_json)
    beams = assign_data.get("csp", {}).get("pss", {}).get("pss_beam_ids", [])
    if not beams:
        pytest.fail(
            "No PSS beams found in assign_resources_low.json - "
            "cannot test conflict logic"
        )
    return beams


@pytest.mark.SKA_low
@scenario(
    "features/tmc/check_pss_assign_resource_rejection.feature",
    "Verify for PSS scan integration with shared beam rejection",
)
def test_verify_assign_resource_rejection():
    """BDD test scenario for verifying assign resource rejection."""


@given("the telescope is in the ON state")
def given_a_telescope_is_in_on(
    central_node_low: CentralNodeWrapperLow,
    event_tracer: TangoEventTracer,
):
    """
    This method invokes On command from central node and verifies
    the state of telescope after the invocation.
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

    central_node_low.set_subarray_id(2)
    event_tracer.subscribe_event(central_node_low.subarray_node, "obsState")
    log_events(
        {
            central_node_low.subarray_node: ["obsState"],
        }
    )
    central_node_low.set_subarray_id(1)

    central_node_low.move_to_on()

    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "GIVEN" STEP: '
        "'the telescope is in ON state' "
        f"Central Node device ({central_node_low.central_node.dev_name()}) "
        "is expected to be in TelescopeState ON",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        central_node_low.central_node,
        "telescopeState",
        DevState.ON,
    )


@given("subarray 1 and 2 are in the EMPTY ObsState")
def verify_subarrays_in_empty(
    central_node_low: CentralNodeWrapperLow,
    event_tracer: TangoEventTracer,
):
    """Verifies subarrays in EMPTY ObsState."""
    central_node_low.set_subarray_id(1)
    assert_that(event_tracer).described_as(
        f"TMC subarray device ({central_node_low.subarray_node.dev_name()}) "
        "is expected to be in EMPTY obsState",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        central_node_low.subarray_node,
        "obsState",
        ObsState.EMPTY,
    )

    central_node_low.set_subarray_id(2)
    assert_that(event_tracer).described_as(
        f"TMC subarray device ({central_node_low.subarray_node.dev_name()}) "
        "is expected to be in EMPTY obsState",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        central_node_low.subarray_node,
        "obsState",
        ObsState.EMPTY,
    )


@when(
    "I assign resources with shared PSS beams to both subarrays simultaneously"
)
def central_node_assign_resources_shared_beams(
    central_node_low: CentralNodeWrapperLow,
    command_input_factory: JsonFactory,
):
    """Invokes assign resources on two subarrays with shared PSS beams."""
    assign_input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_low", command_input_factory
    )

    _, pytest.unique_id1 = central_node_low.perform_action(
        "AssignResources", assign_input_json
    )

    central_node_low.set_subarray_id(2)
    assign_data = json.loads(assign_input_json)
    assign_data["subarray_id"] = 2
    pytest.result2, pytest.unique_id2 = central_node_low.perform_action(
        "AssignResources", json.dumps(assign_data)
    )


@then("the first assignment succeeds with OK result")
def verify_first_assignment_ok(
    central_node_low: CentralNodeWrapperLow,
    event_tracer: TangoEventTracer,
):
    """Verifies first assignment result is OK."""
    central_node_low.set_subarray_id(1)
    assert_that(event_tracer).described_as(
        f"Central Node device ({central_node_low.central_node.dev_name()}) "
        "is expected to have longRunningCommandResult as "
        '(unique_id,(ResultCode.OK,"Command Completed"))',
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        central_node_low.central_node,
        "longRunningCommandResult",
        (
            pytest.unique_id1[0],
            json.dumps((int(ResultCode.OK), "Command Completed")),
        ),
    )


@then("the second assignment fails with PSS beam conflict error")
def verify_second_assignment_failed(  # pylint: disable=redefined-outer-name
    pss_beams_from_json: list[int],
):
    """
    Verifies second assignment rejects due to PSS beam conflict.
    Uses beams extracted automatically from the JSON fixture.
    """
    expected_message = (
        f"PSS beams: {pss_beams_from_json} already assigned to "
        "another subarray"
    )
    assert pytest.unique_id2[0] == expected_message
    assert pytest.result2[0] == ResultCode.REJECTED

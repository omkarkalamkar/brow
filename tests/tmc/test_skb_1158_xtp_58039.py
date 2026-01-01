"""
This module defines a BDD (Behavior-Driven Development) test scenario
using pytest-bdd to verify the behavior of the Telescope Monitoring and
Control (TMC) system to verify the SKB-1158.
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
from tests.resources.test_harness.subarray_node_low import (
    SubarrayNodeWrapperLow,
)
from tests.resources.test_harness.utils.common_utils import JsonFactory
from tests.resources.test_support.common_utils.tmc_helpers import (
    prepare_json_args_for_centralnode_commands,
)
from tests.resources.test_support.constant_low import TIMEOUT


@pytest.mark.SKA_low
@scenario(
    "../features/tmc/SKB_1158.feature",
    "Verify SKB-1158",
)
def test_verify_skb_1158():
    """BDD test scenario for verifying SKB-1158"""


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


@given("central node is busy assigning resources")
def central_node_assign_resources(
    central_node_low: CentralNodeWrapperLow, command_input_factory: JsonFactory
):
    """
    This method invokes AssignResources command on central node.

    Args:
        central_node (CentralNodeWrapperLow): Object of Central node wrapper
        command_input_factory (JsonFactory): Object of json factory
    """
    assign_input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_low", command_input_factory
    )
    _, pytest.unique_id_assign = central_node_low.central_node.AssignResources(
        assign_input_json
    )


@given("subarray node is in observation state RESOURCING")
def subarray_node_obs_state_resourcing(
    central_node_low: CentralNodeWrapperLow,
    event_tracer: TangoEventTracer,
):
    """
    This method checks the subarray node observation state RESOURCING after
    AssignResources is invoked on central node.
    Args:
        central_node (CentralNodeWrapperLow): Object of Central node wrapper
        event_tracer(TangoEventTracer): Object of TangoEventTracer used for
        managing the device events
        command_input_factory (JsonFactory): Object of json factory
    """
    assert_that(event_tracer).described_as(
        "FAILED UNEXPECTED OBSSTATE: "
        "Subarray Node device"
        f"({central_node_low.subarray_node.dev_name()}) "
        "is expected to be in RESOURCING obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        central_node_low.subarray_node,
        "obsState",
        ObsState.RESOURCING,
    )


@when("I invoke abort on subarray node")
def subarray_node_invoke_abort(subarray_node_low: SubarrayNodeWrapperLow):
    """This method invokes abort on subarray node

    Args:
        central_node (CentralNodeWrapperLow): Object of Central node wrapper
    """
    _, pytest.unique_id_abort = subarray_node_low.execute_transition("Abort")


@then("the subarray Node is transitioned to observation state ABORTED")
def tmc_status(
    subarray_node_low: SubarrayNodeWrapperLow, event_tracer: TangoEventTracer
):
    """
    Verifies that the Subarray transition to ObsState.ABORTED.
    """
    assert_that(event_tracer).described_as(
        '"the Subarray transitions to ABORTED"'
        "Subarray Node device"
        f"({subarray_node_low.subarray_node.dev_name()}) "
        "is expected to be in EMPTY obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        subarray_node_low.subarray_node,
        "obsState",
        ObsState.ABORTED,
    )
    assert_that(event_tracer).described_as(
        "FAILED ASSUMPTION AFTER ABORT COMMAND: "
        "Central Node device"
        f"({subarray_node_low.subarray_node.dev_name()}) "
        "is expected have longRunningCommand as"
        '(unique_id,(ResultCode.OK,"Abort command completed"))',
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        subarray_node_low.subarray_node,
        "longRunningCommandResult",
        (
            pytest.unique_id_abort[0],
            json.dumps((int(ResultCode.OK), "Abort command completed")),
        ),
    )


@then(
    "central node receives AssignResources longrunningcommandresult with "
    + "message `Command has been aborted`"
)
def check_central_node_lrcr(
    central_node_low: CentralNodeWrapperLow, event_tracer: TangoEventTracer
):
    """
    This method checks for central node long running command result
    attribute's desired event.

    Args:
        central_node (CentralNodeWrapperLow): Object of Central node wrapper
        event_tracer(TangoEventTracer): Object of TangoEventTracer used for
        managing the device events
    """
    exception_message = "Command has been aborted"
    assert_that(event_tracer).described_as(
        "FAILED ASSUMPTION AFTER ABORT: "
        "Central Node device"
        f"({central_node_low.central_node.dev_name()}) "
        "is expected have longRunningCommandResult"
        "(ResultCode.FAILED,exception)",
    ).within_timeout(TIMEOUT).has_desired_result_code_message_in_lrcr_event(
        central_node_low.central_node,
        [exception_message],
        pytest.unique_id_assign[0],
        ResultCode.FAILED,
    )

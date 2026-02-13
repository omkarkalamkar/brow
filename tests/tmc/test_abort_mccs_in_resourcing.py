"""
This module defines a BDD (Behavior-Driven Development) test scenario
using pytest-bdd to verify the behavior of the Telescope Monitoring and
Control (TMC) system to verify the SKB-438.
"""


import json

import pytest
from assertpy import assert_that
from pytest_bdd import given, scenario, then, when
from ska_control_model import ObsState
from ska_tango_base.commands import ResultCode
from ska_tango_testing.integration import TangoEventTracer, log_events
from ska_tango_testing.mock.placeholders import Anything
from tango import DevState

from tests.resources.test_harness.central_node_low import CentralNodeWrapperLow
from tests.resources.test_harness.simulator_factory import SimulatorFactory
from tests.resources.test_harness.subarray_node_low import (
    SubarrayNodeWrapperLow,
)
from tests.resources.test_harness.utils.common_utils import JsonFactory
from tests.resources.test_harness.utils.enums import SimulatorDeviceType
from tests.resources.test_support.common_utils.tmc_helpers import (
    prepare_json_args_for_centralnode_commands,
)
from tests.resources.test_support.constant_low import TIMEOUT


@pytest.mark.SKA_low
@scenario(
    "../features/tmc/check_mccs_abort.feature",
    "Verify Abort in Resourcing",
)
def test_verify_abort_mccs():
    """BDD test scenario for verifying abort in resourcing"""


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
    event_tracer.clear_events()
    event_tracer.subscribe_event(
        central_node_low.central_node, "telescopeState"
    )
    event_tracer.subscribe_event(
        central_node_low.central_node, "longRunningCommandResult"
    )
    event_tracer.subscribe_event(
        central_node_low.mccs_master_leaf_node, "longRunningCommandResult"
    )
    event_tracer.subscribe_event(central_node_low.subarray_node, "obsState")
    event_tracer.subscribe_event(
        central_node_low.csp_subarray_leaf_node, "cspSubarrayobsState"
    )
    event_tracer.subscribe_event(
        central_node_low.sdp_subarray_leaf_node, "sdpSubarrayobsState"
    )

    log_events(
        {
            central_node_low.central_node: [
                "telescopeState",
                "longRunningCommandResult",
            ],
            central_node_low.subarray_node: ["obsState"],
            central_node_low.csp_subarray_leaf_node: ["cspSubarrayObsState"],
            central_node_low.sdp_subarray_leaf_node: ["sdpSubarrayObsState"],
        }
    )
    central_node_low.move_to_on()
    # assert_that(event_tracer).described_as(
    #     'FAILED ASSUMPTION IN "GIVEN" STEP: '
    #     "'the telescope is is ON state'"
    #     "Central Node device"
    #     f"({central_node_low.central_node.dev_name()}) "
    #     "is expected to be in TelescopeState ON",
    # ).within_timeout(TIMEOUT).has_change_event_occurred(
    #     central_node_low.central_node,
    #     "telescopeState",
    #     DevState.ON,
    # )
    assert central_node_low.central_node.telescopeState == DevState.ON
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
    result, pytest.unique_id = central_node_low.perform_action(
        "AssignResources", assign_input_json
    )
    assert pytest.unique_id[0].endswith("AssignResources")
    assert result[0] == ResultCode.QUEUED


@given(
    "mccs subarray leafnode node is in observation state ObsState.RESOURCING"
)
def subarray_node_obs_state_resourcing(
    central_node_low: CentralNodeWrapperLow,
    event_tracer: TangoEventTracer,
    simulator_factory: SimulatorFactory,
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

    mccs_sim = simulator_factory.get_or_create_simulator_device(
        SimulatorDeviceType.MCCS_SUBARRAY_DEVICE
    )
    event_tracer.subscribe_event(mccs_sim, "obsState")

    mccs_sim.setDelayInfo(json.dumps({"AssignResources": 50}))

    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "THEN" STEP: '
        "'the subarray must be in the RESOURCING obsState'"
        "CSP Subarray Leaf Node device"
        f"({central_node_low.csp_subarray_leaf_node.dev_name()}) "
        "is expected to be in RESOURCING obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        central_node_low.csp_subarray_leaf_node,
        "cspSubarrayObsState",
        ObsState.RESOURCING,
    )
    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "THEN" STEP: '
        "'the subarray must be in the RESOURCING obsState'"
        "SDP Subarray Leaf Node device"
        f"({central_node_low.sdp_subarray_leaf_node.dev_name()}) "
        "is expected to be in RESOURCING obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        central_node_low.sdp_subarray_leaf_node,
        "sdpSubarrayObsState",
        ObsState.RESOURCING,
    )

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

    assert_that(event_tracer).described_as(
        "FAILED UNEXPECTED OBSSTATE: "
        "mccs subarray device"
        f"({central_node_low.mccs_subarray1.dev_name()}) "
        "is expected to be in RESOURCING obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        mccs_sim,
        "obsState",
        ObsState.RESOURCING,
    )
    mccs_sim.ResetDelayInfo()


@when("I invoke abort on subarray node")
def mccs_subarray_node_invoke_abort(subarray_node_low: SubarrayNodeWrapperLow):
    """This method invokes abort on subarray node

    Args:
        central_node (CentralNodeWrapperLow): Object of Central node wrapper
    """
    subarray_node_low.abort_subarray()


@then("mccs master leafnode result to aborted")
def check_central_node_lrcr(
    central_node_low: CentralNodeWrapperLow,
    event_tracer: TangoEventTracer,
):
    """
    This method checks for mccs master leafnode command result
    attribute's desired event.

    Args:
        central_node (CentralNodeWrapperLow): Object of Central node wrapper
        event_tracer(TangoEventTracer): Object of TangoEventTracer used for
        managing the device events
    """

    assert_that(event_tracer).described_as(
        "FAILED ASSUMPTION ATER ASSIGN RESOURCES: "
        "Central Node device"
        f"({central_node_low.central_node.dev_name()}) "
        "is expected have longRunningCommandResult"
        "(ResultCode.ABORTED, command is aborted)",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        central_node_low.mccs_master_leaf_node,
        attribute_name="longRunningCommandResult",
        attribute_value=(
            Anything,
            json.dumps([ResultCode.ABORTED, "Command has been aborted"]),
        ),
    )
    assert_that(event_tracer).described_as(
        "FAILED ASSUMPTION ATER ASSIGN RESOURCES: "
        "Central Node device"
        f"({central_node_low.central_node.dev_name()}) "
        "is expected have longRunningCommandResult"
        "(ResultCode.ABORTED, command is aborted)",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        central_node_low.central_node,
        attribute_name="longRunningCommandResult",
        attribute_value=(
            pytest.unique_id[0],
            Anything,
        ),
    )


@then("the Subarray node transitions to observation state ObsState.ABORTED")
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

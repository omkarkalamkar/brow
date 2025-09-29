"""
This module defines a BDD (Behavior-Driven Development) test scenario
using pytest-bdd to verify the behavior of the Telescope Monitoring and
Control (TMC) system to verify the SKB-1051.
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
from tests.resources.test_harness.simulator_factory import SimulatorFactory
from tests.resources.test_harness.utils.common_utils import JsonFactory
from tests.resources.test_harness.utils.enums import SimulatorDeviceType
from tests.resources.test_support.common_utils.tmc_helpers import (
    prepare_json_args_for_centralnode_commands,
)
from tests.resources.test_support.constant_low import TIMEOUT


@pytest.mark.SKA_low
@scenario(
    "../features/tmc/skb_1051.feature",
    "Verify SKB-1051",
)
def test_verify_skb_1051():
    """BDD test scenario for verifying SKB-1051"""


@given("the telescope is in the ON state")
def given_a_telescope_is_in_on(
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


@given("subarray 1 and 2 are in the IDLE ObsState")
def central_node_assign_resources(
    central_node_low: CentralNodeWrapperLow,
    command_input_factory: JsonFactory,
    event_tracer: TangoEventTracer,
):
    """Invokes assign resources on two subarrays."""
    assign_input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_low", command_input_factory
    )
    central_node_low.store_resources(assign_input_json)
    assert_that(event_tracer).described_as(
        "FAILED UNEXPECTED OBSSTATE: "
        "TMC subarray device"
        f"({central_node_low.subarray_node.dev_name()}) "
        "is expected to be in RESOURCING obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        central_node_low.subarray_node,
        "obsState",
        ObsState.IDLE,
    )
    central_node_low.set_subarray_id(2)
    assign_data = json.loads(assign_input_json)
    assign_data["subarray_id"] = 2
    central_node_low.perform_action("AssignResources", json.dumps(assign_data))
    assert_that(event_tracer).described_as(
        "TMC subarray device"
        f"({central_node_low.subarray_node.dev_name()}) "
        "is expected to be in RESOURCING obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        central_node_low.subarray_node,
        "obsState",
        ObsState.IDLE,
    )


@when("I release resources from the both the subarrays")
def release_resources_from_both_subarrays(
    central_node_low: CentralNodeWrapperLow,
    command_input_factory: JsonFactory,
    event_tracer: TangoEventTracer,
):
    """Invokes release resources on two subarrays."""
    central_node_low.set_subarray_id(1)
    release_input_json = prepare_json_args_for_centralnode_commands(
        "release_resources_low", command_input_factory
    )
    _, unique_id = central_node_low.invoke_release_resources(
        release_input_json
    )
    assert_that(event_tracer).described_as(
        "Central Node device"
        f"({central_node_low.central_node.dev_name()}) "
        "is expected have longRunningCommand as"
        '(unique_id,(ResultCode.OK,"Command Completed"))',
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        central_node_low.central_node,
        "longRunningCommandResult",
        (unique_id[0], json.dumps((int(ResultCode.OK), "Command Completed"))),
    )
    release_data = json.loads(release_input_json)
    release_data["subarray_id"] = 2
    _, unique_id = central_node_low.perform_action(
        "ReleaseResources", json.dumps(release_data)
    )
    assert_that(event_tracer).described_as(
        "Central Node device"
        f"({central_node_low.central_node.dev_name()}) "
        "is expected have longRunningCommand as"
        '(unique_id,(ResultCode.OK,"Command Completed"))',
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        central_node_low.central_node,
        "longRunningCommandResult",
        (unique_id[0], json.dumps((int(ResultCode.OK), "Command Completed"))),
    )


@then(
    "the TMC, CSP, SDP, and MCCS subarray 1 transition to the EMPTY obsState"
)
def verify_subarrays_in_empty(
    central_node_low: CentralNodeWrapperLow,
    event_tracer: TangoEventTracer,
    simulator_factory: SimulatorFactory,
):
    """Method checks the subarray node observation state EMPTY after
    ReleaseResources is invoked on central node."""
    central_node_low.set_subarray_id(1)
    sdp_sim = simulator_factory.get_or_create_simulator_device(
        SimulatorDeviceType.LOW_SDP_DEVICE
    )
    csp_sim = simulator_factory.get_or_create_simulator_device(
        SimulatorDeviceType.LOW_CSP_DEVICE
    )
    mccs_sim = simulator_factory.get_or_create_simulator_device(
        SimulatorDeviceType.MCCS_SUBARRAY_DEVICE
    )
    event_tracer.subscribe_event(csp_sim, "obsState")
    event_tracer.subscribe_event(sdp_sim, "obsState")
    event_tracer.subscribe_event(mccs_sim, "obsState")

    event_tracer.subscribe_event(
        central_node_low.csp_subarray_leaf_node, "cspSubarrayObsState"
    )
    event_tracer.subscribe_event(
        central_node_low.sdp_subarray_leaf_node, "sdpSubarrayObsState"
    )
    event_tracer.subscribe_event(
        central_node_low.mccs_subarray_leaf_node, "obsState"
    )
    log_events(
        {
            csp_sim: ["obsState"],
            sdp_sim: ["obsState"],
            central_node_low.csp_subarray_leaf_node: ["cspSubarrayObsState"],
            central_node_low.sdp_subarray_leaf_node: ["sdpSubarrayObsState"],
            central_node_low.mccs_subarray_leaf_node: ["obsState"],
        }
    )
    assert_that(event_tracer).described_as(
        "Subarray Node device"
        f"({central_node_low.subarray_node.dev_name()}) "
        "is expected to be in EMPTY obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        central_node_low.subarray_node,
        "obsState",
        ObsState.EMPTY,
    )
    assert_that(event_tracer).described_as(
        "SDP subarray device"
        f"({sdp_sim.dev_name()}) "
        "is expected to be in EMPTY obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        sdp_sim,
        "obsState",
        ObsState.EMPTY,
    )
    assert_that(event_tracer).described_as(
        "SDP subarray leaf device"
        f"({central_node_low.sdp_subarray_leaf_node.dev_name()}) "
        "is expected to be in EMPTY obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        central_node_low.sdp_subarray_leaf_node,
        "sdpSubarrayObsState",
        ObsState.EMPTY,
    )
    assert_that(event_tracer).described_as(
        "CSP subarray leaf device"
        f"({central_node_low.csp_subarray_leaf_node.dev_name()}) "
        "is expected to be in EMPTY obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        central_node_low.csp_subarray_leaf_node,
        "cspSubarrayObsState",
        ObsState.EMPTY,
    )
    assert_that(event_tracer).described_as(
        "CSP subarray device"
        f"({csp_sim.dev_name()}) "
        "is expected to be in EMPTY obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        csp_sim,
        "obsState",
        ObsState.EMPTY,
    )
    assert_that(event_tracer).described_as(
        "MCCS subarray leaf device"
        f"({central_node_low.mccs_subarray_leaf_node.dev_name()}) "
        "is expected to be in EMPTY obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        central_node_low.mccs_subarray_leaf_node,
        "obsState",
        ObsState.EMPTY,
    )
    assert_that(event_tracer).described_as(
        "MCCS subarray device"
        f"({mccs_sim.dev_name()}) "
        "is expected to be in EMPTY obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        mccs_sim,
        "obsState",
        ObsState.EMPTY,
    )


@then(
    "the TMC, CSP, SDP, and MCCS subarray 2 transition to the EMPTY obsState"
)
def verify_subarrays2_in_empty(
    central_node_low: CentralNodeWrapperLow,
    event_tracer: TangoEventTracer,
    simulator_factory: SimulatorFactory,
):
    """Method checks the subarray node 2 observation state EMPTY after
    ReleaseResources is invoked on central node.
    """
    central_node_low.set_subarray_id(2)
    sdp_sim2 = simulator_factory.get_or_create_simulator_device(
        SimulatorDeviceType.LOW_SDP_DEVICE2
    )
    csp_sim2 = simulator_factory.get_or_create_simulator_device(
        SimulatorDeviceType.LOW_CSP_DEVICE2
    )
    mccs_sim2 = simulator_factory.get_or_create_simulator_device(
        SimulatorDeviceType.MCCS_SUBARRAY_DEVICE2
    )
    event_tracer.subscribe_event(csp_sim2, "obsState")
    event_tracer.subscribe_event(sdp_sim2, "obsState")
    event_tracer.subscribe_event(mccs_sim2, "obsState")

    event_tracer.subscribe_event(
        central_node_low.csp_subarray_leaf_node, "cspSubarrayObsState"
    )
    event_tracer.subscribe_event(
        central_node_low.sdp_subarray_leaf_node, "sdpSubarrayObsState"
    )
    event_tracer.subscribe_event(
        central_node_low.mccs_subarray_leaf_node, "obsState"
    )
    log_events(
        {
            csp_sim2: ["obsState"],
            sdp_sim2: ["obsState"],
            mccs_sim2: ["obsState"],
            central_node_low.csp_subarray_leaf_node: ["cspSubarrayObsState"],
            central_node_low.sdp_subarray_leaf_node: ["sdpSubarrayObsState"],
            central_node_low.mccs_subarray_leaf_node: ["obsState"],
        }
    )
    assert_that(event_tracer).described_as(
        "Subarray Node device"
        f"({central_node_low.subarray_node.dev_name()}) "
        "is expected to be in EMPTY obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        central_node_low.subarray_node,
        "obsState",
        ObsState.EMPTY,
    )
    assert_that(event_tracer).described_as(
        "SDP subarray device"
        f"({sdp_sim2.dev_name()}) "
        "is expected to be in EMPTY obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        sdp_sim2,
        "obsState",
        ObsState.EMPTY,
    )
    assert_that(event_tracer).described_as(
        "SDP subarray leaf device"
        f"({central_node_low.sdp_subarray_leaf_node.dev_name()}) "
        "is expected to be in EMPTY obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        central_node_low.sdp_subarray_leaf_node,
        "sdpSubarrayObsState",
        ObsState.EMPTY,
    )
    assert_that(event_tracer).described_as(
        "MCCS subarray leaf device"
        f"({central_node_low.mccs_subarray_leaf_node.dev_name()}) "
        "is expected to be in EMPTY obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        central_node_low.mccs_subarray_leaf_node,
        "obsState",
        ObsState.EMPTY,
    )
    assert_that(event_tracer).described_as(
        "MCCS subarray device"
        f"({mccs_sim2.dev_name()}) "
        "is expected to be in EMPTY obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        mccs_sim2,
        "obsState",
        ObsState.EMPTY,
    )

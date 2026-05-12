"""
This module defines BDD test scenarios to verify the
updated Abort command flow for TMC Low with MCCS 6.4.0+
"""
import json
import time

import pytest
from assertpy import assert_that
from pytest_bdd import given, scenario, then, when
from ska_control_model import ObsState
from ska_tango_base.commands import ResultCode
from ska_tango_testing.integration import TangoEventTracer, log_events
from ska_tango_testing.mock.placeholders import Anything
from tango import DevState

from tests.resources.test_harness.central_node_low import CentralNodeWrapperLow
from tests.resources.test_harness.constant import (
    ERROR_PROPAGATION_DEFECT,
    RESET_DEFECT,
    TIMEOUT,
    TIMEOUT_DEFECT,
)
from tests.resources.test_harness.simulator_factory import SimulatorFactory
from tests.resources.test_harness.subarray_node_low import (
    SubarrayNodeWrapperLow,
)
from tests.resources.test_harness.utils.common_utils import JsonFactory
from tests.resources.test_harness.utils.enums import SimulatorDeviceType
from tests.resources.test_support.common_utils.tmc_helpers import (
    prepare_json_args_for_centralnode_commands,
)

ABORT_COMPLETION_TIMEOUT = 30


@pytest.mark.test1
@scenario(
    "../features/tmc/check_mccs_abort.feature",
    (
        "Verify Abort in Resourcing completes without 60-second delay "
        "via MccsController"
    ),
)
def test_verify_abort_mccs_via_controller():
    """BDD scenario for MCCS 6.4.0+ AbortSubarray flow in RESOURCING."""


@pytest.mark.test1
@scenario(
    "../features/tmc/check_mccs_abort.feature",
    (
        "Verify Abort propagates error when MccsController "
        "AbortSubarray is defective"
    ),
)
def test_verify_abort_mccs_controller_defective():
    """BDD scenario for error propagation from defective MccsController."""


@pytest.mark.test1
@scenario(
    "../features/tmc/check_mccs_abort.feature",
    (
        "Verify Abort propagates timeout when MccsController "
        "AbortSubarray is stuck"
    ),
)
def test_verify_abort_mccs_controller_timeout():
    """BDD scenario for timeout propagation from MccsController."""


@given("a TMC")
def given_a_tmc(
    central_node_low: CentralNodeWrapperLow,
    event_tracer: TangoEventTracer,
):
    """Brings telescope to ON state and subscribes to events."""
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
    event_tracer.subscribe_event(
        central_node_low.csp_subarray_leaf_node, "longRunningCommandResult"
    )
    event_tracer.subscribe_event(
        central_node_low.sdp_subarray_leaf_node, "longRunningCommandResult"
    )
    event_tracer.subscribe_event(
        central_node_low.subarray_node, "longRunningCommandResult"
    )
    event_tracer.subscribe_event(central_node_low.subarray_node, "obsState")
    event_tracer.subscribe_event(
        central_node_low.csp_subarray_leaf_node, "cspSubarrayObsState"
    )
    event_tracer.subscribe_event(
        central_node_low.sdp_subarray_leaf_node, "sdpSubarrayObsState"
    )

    log_events(
        {
            central_node_low.central_node: [
                "telescopeState",
                "longRunningCommandResult",
            ],
            central_node_low.subarray_node: [
                "obsState",
                "longRunningCommandResult",
            ],
            central_node_low.csp_subarray_leaf_node: [
                "cspSubarrayObsState",
                "longRunningCommandResult",
            ],
            central_node_low.sdp_subarray_leaf_node: [
                "sdpSubarrayObsState",
                "longRunningCommandResult",
            ],
            central_node_low.mccs_master_leaf_node: [
                "longRunningCommandResult"
            ],
        }
    )

    central_node_low.move_to_on()

    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "GIVEN" STEP: '
        "'the telescope is in ON state' "
        "Central Node device "
        f"({central_node_low.central_node.dev_name()}) "
        "is expected to be in TelescopeState ON"
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        central_node_low.central_node, "telescopeState", DevState.ON
    )

    assert_that(event_tracer).described_as(
        "FAILED UNEXPECTED INITIAL OBSSTATE: "
        "Subarray Node device "
        f"({central_node_low.subarray_node.dev_name()}) "
        "is expected to be in EMPTY obstate"
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        central_node_low.subarray_node, "obsState", ObsState.EMPTY
    )


@given("central node is busy assigning resources")
def central_node_assign_resources(
    central_node_low: CentralNodeWrapperLow,
    command_input_factory: JsonFactory,
):
    """Invokes AssignResources on Central Node."""
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
    """Forces MCCS subarray into RESOURCING with delayed AssignResources."""
    mccs_sim = simulator_factory.get_or_create_simulator_device(
        SimulatorDeviceType.MCCS_SUBARRAY_DEVICE
    )
    event_tracer.subscribe_event(mccs_sim, "obsState")
    mccs_sim.delay = 50

    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "GIVEN" STEP: '
        "'the subarray must be in the RESOURCING obsState' "
        "CSP Subarray Leaf Node device "
        f"({central_node_low.csp_subarray_leaf_node.dev_name()}) "
        "is expected to be in RESOURCING obstate"
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        central_node_low.csp_subarray_leaf_node,
        "cspSubarrayObsState",
        ObsState.RESOURCING,
    )

    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "GIVEN" STEP: '
        "'the subarray must be in the RESOURCING obsState' "
        "SDP Subarray Leaf Node device "
        f"({central_node_low.sdp_subarray_leaf_node.dev_name()}) "
        "is expected to be in RESOURCING obstate"
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        central_node_low.sdp_subarray_leaf_node,
        "sdpSubarrayObsState",
        ObsState.RESOURCING,
    )

    assert_that(event_tracer).described_as(
        "FAILED UNEXPECTED OBSSTATE: "
        "Subarray Node device "
        f"({central_node_low.subarray_node.dev_name()}) "
        "is expected to be in RESOURCING obstate"
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        central_node_low.subarray_node, "obsState", ObsState.RESOURCING
    )

    assert_that(event_tracer).described_as(
        "FAILED UNEXPECTED OBSSTATE: "
        "mccs subarray device "
        f"({mccs_sim.dev_name()}) "
        "is expected to be in RESOURCING obstate"
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        mccs_sim, "obsState", ObsState.RESOURCING
    )
    mccs_sim.delay = 2


@given("the MccsController is set as defective")
def mccs_controller_set_defective(simulator_factory: SimulatorFactory):
    """Sets MccsController simulator as defective."""
    mccs_controller_sim = simulator_factory.get_or_create_simulator_device(
        SimulatorDeviceType.MCCS_MASTER_DEVICE
    )
    mccs_controller_sim.SetDefective(ERROR_PROPAGATION_DEFECT)


@given("the MccsController AbortSubarray is set to timeout")
def mccs_controller_abort_set_to_timeout(simulator_factory: SimulatorFactory):
    """Sets timeout defect on MccsController.AbortSubarray."""
    mccs_controller_sim = simulator_factory.get_or_create_simulator_device(
        SimulatorDeviceType.MCCS_MASTER_DEVICE
    )
    mccs_controller_sim.SetDefective(TIMEOUT_DEFECT)


@when("I invoke abort on subarray node")
def mccs_subarray_node_invoke_abort(subarray_node_low: SubarrayNodeWrapperLow):
    """Invokes Abort on SubarrayNode."""
    pytest.abort_start_time = time.monotonic()
    subarray_node_low.subarray_node.Abort()


@then("the MccsController AbortSubarray is invoked promptly")
def mccs_controller_abort_subarray_invoked_promptly(
    central_node_low: CentralNodeWrapperLow,
    event_tracer: TangoEventTracer,
):
    """Verifies MccsController.AbortSubarray completes promptly."""
    assert_that(event_tracer).described_as(
        "FAILED ASSUMPTION AFTER ABORT COMMAND: "
        "MCCS Master Leaf Node device "
        f"({central_node_low.mccs_master_leaf_node.dev_name()}) "
        "is expected have longRunningCommandResult "
        '[0, "Command Completed"]'
    ).within_timeout(ABORT_COMPLETION_TIMEOUT).has_change_event_occurred(
        central_node_low.mccs_master_leaf_node,
        attribute_name="longRunningCommandResult",
        attribute_value=(
            Anything,
            json.dumps([ResultCode.OK, "Command Completed"]),
        ),
    )

    elapsed = time.monotonic() - pytest.abort_start_time
    assert elapsed < ABORT_COMPLETION_TIMEOUT, (
        f"Abort completed in {elapsed:.1f}s which exceeds "
        f"{ABORT_COMPLETION_TIMEOUT}s threshold"
    )


@then("the Subarray node transitions to observation state ObsState.ABORTED")
def subarray_node_transitions_to_aborted(
    central_node_low: CentralNodeWrapperLow,
    event_tracer: TangoEventTracer,
):
    """Verifies SubarrayNode transitions to ObsState.ABORTED."""
    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "THEN" STEP: '
        "'the Subarray transitions to ABORTED' "
        "Subarray Node device "
        f"({central_node_low.subarray_node.dev_name()}) "
        "is expected to be in ABORTED obstate"
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        central_node_low.subarray_node, "obsState", ObsState.ABORTED
    )


@then("the Subarray node transitions to observation state ObsState.FAULT")
def subarray_node_transitions_to_fault(
    central_node_low: CentralNodeWrapperLow,
    event_tracer: TangoEventTracer,
    simulator_factory: SimulatorFactory,
):
    """Verifies SubarrayNode transitions to FAULT and cleans MCCS subarray."""
    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "THEN" STEP: '
        "'the tmc subarray must be in the ABORTING obsState' "
        "Subarray Node device "
        f"({central_node_low.subarray_node.dev_name()}) "
        "is expected to be in ABORTING obstate"
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        central_node_low.subarray_node, "obsState", ObsState.ABORTING
    )

    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "THEN" STEP: '
        "'the tmc subarray must be in the FAULT obsState' "
        "Subarray Node device "
        f"({central_node_low.subarray_node.dev_name()}) "
        "is expected to be in FAULT obstate"
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        central_node_low.subarray_node, "obsState", ObsState.FAULT
    )

    mccs_controller_sim = simulator_factory.get_or_create_simulator_device(
        SimulatorDeviceType.MCCS_MASTER_DEVICE
    )
    mccs_controller_sim.SetDefective(RESET_DEFECT)

    mccs_sub_sim = simulator_factory.get_or_create_simulator_device(
        SimulatorDeviceType.MCCS_SUBARRAY_DEVICE
    )
    event_tracer.subscribe_event(mccs_sub_sim, "obsState")
    mccs_sub_sim.Abort()

    assert_that(event_tracer).described_as(
        "FAILED ASSUMPTION AFTER ABORT COMMAND: "
        "mccs subarray device "
        f"({mccs_sub_sim.dev_name()}) "
        "is expected to be in ABORTED obstate"
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        mccs_sub_sim, "obsState", ObsState.ABORTED
    )

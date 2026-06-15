"""
This module defines a Pytest BDD test scenario for the successful execution of
EndScan Command of a Low Telescope Subarray in the Telescope Monitoring and
Control (TMC) system when some subsystem subarrays have already ended scan and
are in READY obsState.
"""
import json

import pytest
from assertpy import assert_that
from pytest_bdd import given, parsers, scenario, then, when
from ska_control_model import ObsState
from ska_tango_testing.integration import TangoEventTracer, log_events
from ska_tango_testing.mock.placeholders import Anything
from tango import DevState

from tests.resources.test_harness.central_node_low import CentralNodeWrapperLow
from tests.resources.test_harness.constant import TIMEOUT
from tests.resources.test_harness.subarray_node_low import (
    LOGGER,
    SubarrayNodeWrapperLow,
)
from tests.resources.test_harness.utils.common_utils import JsonFactory
from tests.resources.test_support.common_utils.result_code import ResultCode
from tests.resources.test_support.common_utils.tmc_helpers import (
    prepare_json_args_for_centralnode_commands,
    prepare_json_args_for_commands,
)


@pytest.mark.sah1946
@pytest.mark.SKA_low
@scenario(
    "../features/tmc/check_endscan_in_ready.feature",
    "Successful Execution of EndScan on Low Telescope Subarray when"
    " some subsystem have Ended Scan.",
)
def test_tmc_endscan_command():
    """BDD test scenario for verifying successful execution of
    the Low EndScan command in a TMC when some subsystem subarrays
    have already ended scan and are in READY obsState."""


@given("a TMC")
def given_tmc(
    central_node_low: CentralNodeWrapperLow,
    subarray_node_low: SubarrayNodeWrapperLow,
    event_tracer: TangoEventTracer,
):
    """Set up a TMC and ensure it is in the ON state."""
    # ---------Event Subscriptions and Logging----------
    event_tracer.subscribe_event(
        central_node_low.central_node, "telescopeState"
    )
    event_tracer.subscribe_event(
        central_node_low.central_node, "longRunningCommandResult"
    )
    event_tracer.subscribe_event(
        subarray_node_low.subarray_node, "longRunningCommandResult"
    )
    event_tracer.subscribe_event(subarray_node_low.subarray_node, "obsState")
    event_tracer.subscribe_event(
        subarray_node_low.mccs_subarray_leaf_node,
        "obsState",
    )
    event_tracer.subscribe_event(
        subarray_node_low.csp_subarray_leaf_node,
        "cspSubarrayObsState",
    )
    event_tracer.subscribe_event(
        subarray_node_low.sdp_subarray_leaf_node,
        "sdpSubarrayObsState",
    )
    event_tracer.subscribe_event(
        subarray_node_low.mccs_subarray_leaf_node, "longRunningCommandResult"
    )
    event_tracer.subscribe_event(
        subarray_node_low.csp_subarray_leaf_node, "longRunningCommandResult"
    )
    event_tracer.subscribe_event(
        subarray_node_low.sdp_subarray_leaf_node, "longRunningCommandResult"
    )
    log_events(
        {
            central_node_low.central_node: [
                "telescopeState",
                "longRunningCommandResult",
            ],
            subarray_node_low.subarray_node: [
                "longRunningCommandResult",
                "obsState",
            ],
            subarray_node_low.mccs_subarray_leaf_node: [
                "obsState",
                "longRunningCommandResult",
            ],
            subarray_node_low.csp_subarray_leaf_node: [
                "cspSubarrayObsState",
                "longRunningCommandResult",
            ],
            subarray_node_low.sdp_subarray_leaf_node: [
                "sdpSubarrayObsState",
                "longRunningCommandResult",
            ],
        }
    )
    LOGGER.info("Subscribed to events and set up logging for TMC devices.")
    # ----------Move TMC to ON State and Verify----------
    central_node_low.move_to_on()
    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "GIVEN STEP: '
        '"a TMC'
        "Central Node device"
        f"({central_node_low.central_node.dev_name()}) "
        "is expected to be in TelescopeState ON",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        central_node_low.central_node,
        "telescopeState",
        DevState.ON,
    )
    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "GIVEN STEP: '
        '"a TMC'
        "Subarray Node device"
        f"({central_node_low.subarray_node.dev_name()}) "
        f"is expected to be in EMPTY obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        central_node_low.subarray_node,
        "obsState",
        ObsState.EMPTY,
    )


@given("a subarray in SCANNING obsState")
def given_subarray_in_scanning(
    command_input_factory: JsonFactory,
    central_node_low: CentralNodeWrapperLow,
    event_tracer: TangoEventTracer,
    subarray_node_low: SubarrayNodeWrapperLow,
):
    """Set up a subarray in the SCANNING obsState."""
    # -----------------Assign Resources to Subarray-----------------
    assign_input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_low", command_input_factory
    )
    _, unique_id = central_node_low.store_resources(assign_input_json)
    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "GIVEN" STEP: '
        "'a subarray in READY obsState'"
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
        "'a subarray in READY obsState'"
        "Subarray Node device"
        f"({central_node_low.central_node.dev_name()}) "
        "is expected have longRunningCommand as"
        '(unique_id,(ResultCode.OK,"Command Completed"))',
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        central_node_low.central_node,
        "longRunningCommandResult",
        (unique_id[0], json.dumps((int(ResultCode.OK), "Command Completed"))),
    )
    LOGGER.info(
        "Assigned resources to subarray and verified it is in IDLE obsState."
    )

    # -----------------Configure Subarray-----------------
    configure_input_json = prepare_json_args_for_commands(
        "configure_low", command_input_factory
    )
    _, unique_id = subarray_node_low.store_configuration_data(
        configure_input_json
    )
    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "GIVEN" STEP: '
        "'a subarray in READY obsState'"
        "Subarray Node device"
        f"({central_node_low.subarray_node.dev_name()}) "
        "is expected to be in READY obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        central_node_low.subarray_node,
        "obsState",
        ObsState.READY,
    )
    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "GIVEN" STEP: '
        "'a subarray in READY obsState'"
        "Subarray Node device"
        f"({central_node_low.subarray_node.dev_name()}) "
        "is expected have longRunningCommand as"
        '(unique_id,(ResultCode.OK,"Command Completed"))',
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        central_node_low.subarray_node,
        "longRunningCommandResult",
        (unique_id[0], json.dumps((int(ResultCode.OK), "Command Completed"))),
    )
    LOGGER.info("Configured subarray and verified it is in READY obsState.")

    # -----------------Execute Scan Command-----------------
    scan_input_json = prepare_json_args_for_commands(
        "scan_low", command_input_factory
    )
    _, unique_id = subarray_node_low.execute_transition(
        "Scan", scan_input_json
    )
    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "WHEN" STEP: '
        "'the subarray must be in the SCANNING obsState'"
        f"({subarray_node_low.subarray_node.dev_name()}) "
        "is expected to be in SCANNING obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        subarray_node_low.subarray_node,
        "obsState",
        ObsState.SCANNING,
    )
    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "GIVEN" STEP: '
        "'a subarray in SCANNING obsState'"
        "Subarray Node device"
        f"({central_node_low.subarray_node.dev_name()}) "
        "is expected have longRunningCommand as"
        '(unique_id,(ResultCode.OK,"Command Completed"))',
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        central_node_low.subarray_node,
        "longRunningCommandResult",
        (unique_id[0], json.dumps((int(ResultCode.OK), "Command Completed"))),
    )
    LOGGER.info(
        "Executed Scan command and verified subarray is in SCANNING obsState."
    )


@given(parsers.parse("{subsystem} have Ended Scan"))
def given_subarray_ended_scan(
    subsystem: str,
    subarray_node_low: SubarrayNodeWrapperLow,
    event_tracer: TangoEventTracer,
):
    """EndScan on the specified subsystem."""

    subsystems_to_endscan = subsystem.split(",")

    # Invoke EndScan on the specified subsystem(s) and verify that the
    # obsState changes to READY
    if "mccs" in subsystems_to_endscan:

        subarray_node_low.mccs_subarray_leaf_node.EndScan()
        LOGGER.info(
            "Invoked EndScan on MCCS Subarray Leaf Node: %s",
            subarray_node_low.mccs_subarray_leaf_node.dev_name(),
        )

        assert_that(event_tracer).described_as(
            'FAILED ASSUMPTION IN "GIVEN" STEP: '
            "'a mccs subarray in READY obsState'"
            f"({subarray_node_low.mccs_subarray_leaf_node.dev_name()}) "
            "is expected to be in READY obstate",
        ).within_timeout(TIMEOUT).has_change_event_occurred(
            subarray_node_low.mccs_subarray_leaf_node,
            "obsState",
            ObsState.READY,
        )
        assert_that(event_tracer).described_as(
            'FAILED ASSUMPTION IN "GIVEN" STEP: '
            "'a mccs subarray in READY obsState'"
            f"({subarray_node_low.mccs_subarray_leaf_node.dev_name()}) "
            "is expected have longRunningCommand as"
            '(unique_id,(ResultCode.OK,"Command Completed"))',
        ).within_timeout(TIMEOUT).has_change_event_occurred(
            subarray_node_low.mccs_subarray_leaf_node,
            "longRunningCommandResult",
            (
                Anything,
                json.dumps((int(ResultCode.OK), "Command Completed")),
            ),
        )

    if "sdp" in subsystems_to_endscan:

        subarray_node_low.sdp_subarray_leaf_node.EndScan()
        LOGGER.info(
            "Invoked EndScan on SDP Subarray Leaf Node: %s",
            subarray_node_low.sdp_subarray_leaf_node.dev_name(),
        )
        assert_that(event_tracer).described_as(
            'FAILED ASSUMPTION IN "GIVEN" STEP: '
            "'a sdp subarray in READY obsState'"
            f"({subarray_node_low.sdp_subarray_leaf_node.dev_name()}) "
            "is expected to be in READY obstate",
        ).within_timeout(TIMEOUT).has_change_event_occurred(
            subarray_node_low.sdp_subarray_leaf_node,
            "sdpSubarrayObsState",
            ObsState.READY,
        )
        assert_that(event_tracer).described_as(
            'FAILED ASSUMPTION IN "GIVEN" STEP: '
            "'a sdp subarray in READY obsState'"
            f"({subarray_node_low.sdp_subarray_leaf_node.dev_name()}) "
            "is expected have longRunningCommand as"
            '(unique_id,(ResultCode.OK,"Command Completed"))',
        ).within_timeout(TIMEOUT).has_change_event_occurred(
            subarray_node_low.sdp_subarray_leaf_node,
            "longRunningCommandResult",
            (
                Anything,
                json.dumps((int(ResultCode.OK), "Command Completed")),
            ),
        )

    if "csp" in subsystems_to_endscan:

        subarray_node_low.csp_subarray_leaf_node.EndScan()
        LOGGER.info(
            "Invoked EndScan on CSP Subarray Leaf Node: %s",
            subarray_node_low.csp_subarray_leaf_node.dev_name(),
        )
        assert_that(event_tracer).described_as(
            'FAILED ASSUMPTION IN "GIVEN" STEP: '
            "'a csp subarray in READY obsState'"
            f"({subarray_node_low.csp_subarray_leaf_node.dev_name()}) "
            "is expected to be in READY obstate",
        ).within_timeout(TIMEOUT).has_change_event_occurred(
            subarray_node_low.csp_subarray_leaf_node,
            "cspSubarrayObsState",
            ObsState.READY,
        )
        assert_that(event_tracer).described_as(
            'FAILED ASSUMPTION IN "GIVEN" STEP: '
            "'a csp subarray in READY obsState'"
            f"({subarray_node_low.csp_subarray_leaf_node.dev_name()}) "
            "is expected have longRunningCommand as"
            '(unique_id,(ResultCode.OK,"Command Completed"))',
        ).within_timeout(TIMEOUT).has_change_event_occurred(
            subarray_node_low.csp_subarray_leaf_node,
            "longRunningCommandResult",
            (
                Anything,
                json.dumps((int(ResultCode.OK), "Command Completed")),
            ),
        )


@when("I invoked EndScan")
def when_endscan_invoked(
    subarray_node_low: SubarrayNodeWrapperLow,
    event_tracer: TangoEventTracer,
):
    """Invoke EndScan on the subarray."""

    _, unique_id = subarray_node_low.execute_transition("EndScan")
    LOGGER.info(
        "Invoked EndScan on Subarray Node: %s",
        subarray_node_low.subarray_node.dev_name(),
    )

    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "WHEN" STEP: '
        "'the subarray must be in the READY obsState'"
        f"({subarray_node_low.subarray_node.dev_name()}) "
        "is expected to be in READY obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        subarray_node_low.subarray_node,
        "obsState",
        ObsState.READY,
    )

    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "WHEN" STEP: '
        "'a subarray in READY obsState'"
        "Subarray Node device"
        f"({subarray_node_low.subarray_node.dev_name()}) "
        "is expected have longRunningCommand as"
        '(unique_id,(ResultCode.OK,"Command Completed"))',
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        subarray_node_low.subarray_node,
        "longRunningCommandResult",
        (unique_id[0], json.dumps((int(ResultCode.OK), "Command Completed"))),
    )


@then("the TMC subarray and subsystem subarray are in READY obsState")
def then_subarrays_in_ready_obsstate(
    subarray_node_low: SubarrayNodeWrapperLow,
    event_tracer: TangoEventTracer,
):
    """Check that the TMC subarray and subsystem subarray are in
    READY obsState."""

    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "THEN" STEP: '
        "'the csp subarray must be in the READY obsState'"
        f"({subarray_node_low.csp_subarray_leaf_node.dev_name()}) "
        "is expected to be in READY obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        subarray_node_low.csp_subarray_leaf_node,
        "cspSubarrayObsState",
        ObsState.READY,
    )

    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "THEN" STEP: '
        "'the mccs subarray must be in the READY obsState'"
        f"({subarray_node_low.mccs_subarray_leaf_node.dev_name()}) "
        "is expected to be in READY obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        subarray_node_low.mccs_subarray_leaf_node,
        "obsState",
        ObsState.READY,
    )

    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "THEN" STEP: '
        "'the sdp subarray must be in the READY obsState'"
        f"({subarray_node_low.sdp_subarray_leaf_node.dev_name()}) "
        "is expected to be in READY obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        subarray_node_low.sdp_subarray_leaf_node,
        "sdpSubarrayObsState",
        ObsState.READY,
    )

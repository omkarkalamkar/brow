"""
Module: test_tmc_configure_command

This module defines a Pytest BDD test scenario for the successful configuration
of a Low Telescope Subarray in the Telescope Monitoring and Control (TMC)
system.
The scenario includes steps to set up the TMC, prepare a subarray in the IDLE
observation state, and configure it for a scan. The completion of the
configuration is verified by checking that the subarray transitions to
the READY observation state.
"""
import json
import logging

import pytest
from assertpy import assert_that
from pytest_bdd import given, scenario, then, when
from ska_control_model import ObsState
from ska_tango_testing.integration import TangoEventTracer, log_events
from tango import DevState

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

logger = logging.getLogger(__name__)


@pytest.mark.sah_1947
@pytest.mark.SKA_low
@scenario(
    "../features/tmc/check_configure_command.feature",
    "Successful Configuration of Low Telescope Subarray in TMC",
)
def test_tmc_configure_command():
    """BDD test scenario for verifying successful execution of
    the Low Configure command in a TMC."""


@given("a TMC")
def given_tmc(
    central_node_low: CentralNodeWrapperLow, event_tracer: TangoEventTracer
):
    """Set up a TMC and ensure it is in the ON state."""
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


@given("a subarray in the IDLE obsState")
def given_subarray_in_idle(
    command_input_factory: JsonFactory,
    central_node_low: CentralNodeWrapperLow,
    event_tracer: TangoEventTracer,
):
    """Set up a subarray in the IDLE obsState."""
    set_receive_address(central_node_low)
    assign_input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_low", command_input_factory
    )
    _, unique_id = central_node_low.store_resources(assign_input_json)
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
        "Subarray Node device"
        f"({central_node_low.central_node.dev_name()}) "
        "is expected have longRunningCommand as"
        '(unique_id,(ResultCode.OK,"Command Completed"))',
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        central_node_low.central_node,
        "longRunningCommandResult",
        (unique_id[0], json.dumps((int(ResultCode.OK), "Command Completed"))),
    )


@given("the quality monitor reports readyToScan flag to be False")
def given_quality_monitor_not_ready_for_scan(
    subarray_node_low: SubarrayNodeWrapperLow,
):
    """Verify quality monitor readyToScan attrbute"""
    assert subarray_node_low.quality_monitor.readyToScan is False
    csp_qa_metrics = (
        subarray_node_low.quality_monitor.qualityMetricsCspSubarray
    )
    logger.info("qualityMetricsCspSubarray: %s", csp_qa_metrics)


@when("I configure it for a scan")
def send_configure(
    command_input_factory: JsonFactory,
    subarray_node_low: SubarrayNodeWrapperLow,
):
    """Send a Configure command to the subarray."""
    configure_input_json = prepare_json_args_for_commands(
        "configure_low", command_input_factory
    )
    subarray_node_low.store_configuration_data(configure_input_json)


@then("the subarray must be in the READY obsState")
def check_configure_completion(
    central_node_low: CentralNodeWrapperLow,
    subarray_node_low: SubarrayNodeWrapperLow,
    event_tracer: TangoEventTracer,
):
    """Verify that the subarray is in the READY obsState."""
    event_tracer.subscribe_event(
        subarray_node_low.subarray_devices.get("sdp_subarray"), "obsState"
    )
    event_tracer.subscribe_event(
        subarray_node_low.subarray_devices.get("csp_subarray"), "obsState"
    )
    event_tracer.subscribe_event(
        subarray_node_low.csp_subarray_leaf_node, "cspSubarrayObsState"
    )
    event_tracer.subscribe_event(
        subarray_node_low.sdp_subarray_leaf_node, "sdpSubarrayObsState"
    )
    log_events(
        {
            subarray_node_low.subarray_devices.get("sdp_subarray"): [
                "obsState"
            ],
            subarray_node_low.subarray_devices.get("csp_subarray"): [
                "obsState"
            ],
            subarray_node_low.csp_subarray_leaf_node: ["cspSubarrayObsState"],
            subarray_node_low.sdp_subarray_leaf_node: ["sdpSubarrayObsState"],
        }
    )
    csp = subarray_node_low.subarray_devices.get("csp_subarray")
    sdp = subarray_node_low.subarray_devices.get("sdp_subarray")
    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "THEN" STEP: '
        "'the subarray must be in the READY obsState'"
        "CSP Subarray Leaf Node device"
        f"({subarray_node_low.csp_subarray_leaf_node.dev_name()}) "
        "is expected to be in READY obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        subarray_node_low.csp_subarray_leaf_node,
        "cspSubarrayObsState",
        ObsState.READY,
    )
    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "THEN" STEP: '
        "'the subarray must be in the READY obsState'"
        "SDP Subarray Leaf Node device"
        f"({subarray_node_low.sdp_subarray_leaf_node.dev_name()}) "
        "is expected to be in READY obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        subarray_node_low.sdp_subarray_leaf_node,
        "sdpSubarrayObsState",
        ObsState.READY,
    )
    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "THEN" STEP: '
        "'the subarray must be in the READY obsState'"
        "CSP Subarray device"
        f"({csp.dev_name()}) "
        "is expected to be in READY obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        csp,
        "obsState",
        ObsState.READY,
    )
    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "THEN" STEP: '
        "'the subarray must be in the READY obsState'"
        "SDP Subarray device"
        f"({sdp.dev_name()}) "
        "is expected to be in READY obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        sdp,
        "obsState",
        ObsState.READY,
    )
    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "THEN" STEP: '
        "'the subarray must be in the READY obsState'"
        "Subarray Node device"
        f"({central_node_low.subarray_node.dev_name()}) "
        "is expected to be in READY obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        central_node_low.subarray_node,
        "obsState",
        ObsState.READY,
    )


@then("the quality monitor reports readyToScan flag to be True")
def check_if_quality_monitor_ready_for_scan(
    subarray_node_low: SubarrayNodeWrapperLow,
    event_tracer: TangoEventTracer,
):
    """Verify that the subarray is in the READY obsState."""

    event_tracer.subscribe_event(
        subarray_node_low.quality_monitor, "readyToScan"
    )
    log_events(
        {
            subarray_node_low.quality_monitor: [
                "readyToScan",
            ],
        }
    )
    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "THEN" STEP: '
        "'the quality monitor readyToScan must be True'"
        f"({subarray_node_low.quality_monitor.dev_name()}) "
        "readyToScan flag is expected to be True",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        subarray_node_low.quality_monitor,
        "readyToScan",
        True,
    )
    csp_qa_metrics = (
        subarray_node_low.quality_monitor.qualityMetricsCspSubarray
    )
    logger.info("qualityMetricsCspSubarray: %s", csp_qa_metrics)

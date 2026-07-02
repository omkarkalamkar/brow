"""
This module defines a Pytest BDD test scenario for the successful execution of
EndScan Command of a Low Telescope Subarray in the Telescope Monitoring and
Control (TMC) system when some subsystem subarrays have already ended scan and
rejected the EndScan command.
"""
import json

import pytest
from assertpy import assert_that
from pytest_bdd import given, parsers, scenario, then, when
from ska_control_model import ObsState
from ska_tango_testing.integration import TangoEventTracer
from ska_tango_testing.mock.placeholders import Anything

from tests.resources.test_harness.central_node_low import CentralNodeWrapperLow
from tests.resources.test_harness.constant import (
    COMMAND_REJECTED_DEFECT,
    SDP_COMMAND_REJECTED_DEFECT,
    TIMEOUT,
)
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


@pytest.mark.SKA_low
@scenario(
    "../features/tmc/check_endscan_in_ready.feature",
    "EndScan transitions the subarray to READY when selected subsystems have"
    " already ended scan and reject the EndScan command.",
)
def test_tmc_endscan_command_in_ready():
    """BDD test scenario for verifying successful execution of
    the Low EndScan command in a TMC when some subsystem subarrays
    have already ended scan and are in READY obsState and reject the
    EndScan command.

    This scenario validates the TMC behavior when a subarray and its
    subsystem leaf nodes are already in READY before the EndScan
    command is invoked and the subsystems reject the EndScan command.
    """


def _normalize_subsystems(subsystem: str) -> list[str]:
    """Return a cleaned list of subsystem names from the feature examples."""
    return [name.strip() for name in subsystem.split(",") if name.strip()]


def _assert_subsystem_ready_state(
    event_tracer: TangoEventTracer,
    leaf_node,
    state_attribute: str,
    subsystem_name: str,
) -> None:
    """Assert that a subsystem leaf node reaches the READY state."""
    assert_that(event_tracer).described_as(
        f'FAILED ASSUMPTION IN "GIVEN" STEP: "{subsystem_name}" '
        f"subsystem is expected to be in READY obstate"
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        leaf_node,
        state_attribute,
        ObsState.READY,
    )


def _assert_subsystem_command_result(
    event_tracer: TangoEventTracer,
    leaf_node,
    expected_result: tuple,
    subsystem_name: str,
) -> None:
    """Assert that a subsystem leaf node reports expected command result."""
    assert_that(event_tracer).described_as(
        f'FAILED ASSUMPTION IN "GIVEN" STEP: "{subsystem_name}" '
        "subsystem is expected to report the expected command result"
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        leaf_node,
        "longRunningCommandResult",
        expected_result,
    )


@given("a subarray is in SCANNING obsState")
def given_subarray_in_scanning(
    command_input_factory: JsonFactory,
    central_node_low: CentralNodeWrapperLow,
    event_tracer: TangoEventTracer,
    subarray_node_low: SubarrayNodeWrapperLow,
):
    """Set up a subarray in the SCANNING obsState.

    This fixture assigns resources to the subarray, configures it, and
    then issues the Scan transition to move it into SCANNING.

    Args:
        command_input_factory: JSON factory for building command inputs.
        central_node_low: Wrapper for the central node device.
        event_tracer: Tango event tracer used to verify state transitions.
        subarray_node_low: Wrapper for the low subarray node and its
            subsystem leaf nodes.
    """
    # -----------------Assign Resources to Subarray-----------------
    assign_input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_low", command_input_factory
    )
    _, unique_id = central_node_low.store_resources(assign_input_json)
    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "GIVEN" STEP: '
        "'a subarray in SCANNING obsState'"
        " Subarray Node device"
        f"({central_node_low.subarray_node.dev_name()}) "
        "is expected to be in IDLE obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        central_node_low.subarray_node,
        "obsState",
        ObsState.IDLE,
    )
    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "GIVEN" STEP: '
        "'a subarray in SCANNING obsState'"
        " Central Node device"
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
        "'a subarray in SCANNING obsState'"
        " Subarray Node device"
        f"({central_node_low.subarray_node.dev_name()}) "
        "is expected to be in READY obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        central_node_low.subarray_node,
        "obsState",
        ObsState.READY,
    )
    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "GIVEN" STEP: '
        "'a subarray in SCANNING obsState'"
        " Subarray Node device"
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
        'FAILED ASSUMPTION IN "GIVEN" STEP: '
        "'a subarray in SCANNING obsState'"
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
        " Subarray Node device"
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


@given(parsers.parse("{subsystem} have already ended scan"))
def given_subarray_ended_scan(
    subsystem: str,
    subarray_node_low: SubarrayNodeWrapperLow,
    event_tracer: TangoEventTracer,
):
    """Invoke EndScan on the specified subsystem(s) already in READY.

    Args:
        subsystem: Comma-separated list of subsystem names to end scan for.
        subarray_node_low: Wrapper for the low subarray node and its
            subsystem leaf nodes.
        event_tracer: Tango event tracer used to verify subsystem state
            transitions and command completion.
    """

    pytest.subsystems_to_endscan = _normalize_subsystems(subsystem)

    command_result = (
        Anything,
        json.dumps((int(ResultCode.OK), "Command Completed")),
    )

    if "mccs" in pytest.subsystems_to_endscan:
        subarray_node_low.mccs_subarray_leaf_node.EndScan()
        LOGGER.info(
            "Invoked EndScan on MCCS Subarray Leaf Node: %s",
            subarray_node_low.mccs_subarray_leaf_node.dev_name(),
        )
        _assert_subsystem_ready_state(
            event_tracer,
            subarray_node_low.mccs_subarray_leaf_node,
            "obsState",
            "mccs",
        )
        _assert_subsystem_command_result(
            event_tracer,
            subarray_node_low.mccs_subarray_leaf_node,
            command_result,
            "mccs",
        )
        subarray_node_low.mccs_subarray1.SetDefective(
            SDP_COMMAND_REJECTED_DEFECT
        )
    elif "sdp" in pytest.subsystems_to_endscan:
        subarray_node_low.sdp_subarray_leaf_node.EndScan()
        LOGGER.info(
            "Invoked EndScan on SDP Subarray Leaf Node: %s",
            subarray_node_low.sdp_subarray_leaf_node.dev_name(),
        )
        _assert_subsystem_ready_state(
            event_tracer,
            subarray_node_low.sdp_subarray_leaf_node,
            "sdpSubarrayObsState",
            "sdp",
        )
        _assert_subsystem_command_result(
            event_tracer,
            subarray_node_low.sdp_subarray_leaf_node,
            command_result,
            "sdp",
        )
    elif "csp" in pytest.subsystems_to_endscan:
        subarray_node_low.csp_subarray_leaf_node.EndScan()
        LOGGER.info(
            "Invoked EndScan on CSP Subarray Leaf Node: %s",
            subarray_node_low.csp_subarray_leaf_node.dev_name(),
        )
        _assert_subsystem_ready_state(
            event_tracer,
            subarray_node_low.csp_subarray_leaf_node,
            "cspSubarrayObsState",
            "csp",
        )
        _assert_subsystem_command_result(
            event_tracer,
            subarray_node_low.csp_subarray_leaf_node,
            command_result,
            "csp",
        )
        subarray_node_low.csp_subarray1.SetDefective(COMMAND_REJECTED_DEFECT)


@when("I invoke EndScan and it is rejected by the subsystem")
def when_endscan_invoked(
    subarray_node_low: SubarrayNodeWrapperLow,
    event_tracer: TangoEventTracer,
):
    """Invoke EndScan on the subarray and verify the ready condition.

    Args:
        subarray_node_low: Wrapper for the low subarray node used to execute
            the EndScan transition.
        event_tracer: Tango event tracer used to verify that the subarray is
            in READY and receives a successful command result.
    """

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
        " Subarray Node device"
        f"({subarray_node_low.subarray_node.dev_name()}) "
        "is expected have longRunningCommand as"
        '(unique_id,(ResultCode.OK,"Command Completed"))',
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        subarray_node_low.subarray_node,
        "longRunningCommandResult",
        (unique_id[0], json.dumps((int(ResultCode.OK), "Command Completed"))),
    )

    if "mccs" in pytest.subsystems_to_endscan:
        subarray_node_low.mccs_subarray1.SetDefective(
            json.dumps({"enabled": False})
        )
    elif "sdp" in pytest.subsystems_to_endscan:
        subarray_node_low.sdp_subarray1.SetDefective(
            json.dumps({"enabled": False})
        )
    elif "csp" in pytest.subsystems_to_endscan:
        subarray_node_low.csp_subarray1.SetDefective(
            json.dumps({"enabled": False})
        )


@then("the TMC subarray and the subsystem subarray are in READY obsState")
def then_subarrays_in_ready_obsstate(
    subarray_node_low: SubarrayNodeWrapperLow,
    event_tracer: TangoEventTracer,
):
    """Check that the TMC subarray and subsystem subarray are in READY.

    Args:
        subarray_node_low: Wrapper for the low subarray node and its
            subsystem leaf nodes.
        event_tracer: Tango event tracer used to assert final ready state
            transitions and long-running command results.
    """

    MESSAGE = (
        f"EndScan command returned: {ResultCode.REJECTED.name}; "
        "sub-system is already in READY ObsState, "
        "treating this as scan completed.",
    )

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

    for subsystem_name in pytest.subsystems_to_endscan:
        if subsystem_name == "mccs":
            _assert_subsystem_command_result(
                event_tracer,
                subarray_node_low.mccs_subarray_leaf_node,
                (
                    Anything,
                    json.dumps(
                        (
                            int(ResultCode.OK),
                            MESSAGE,
                        )
                    ),
                ),
                "mccs",
            )
        elif subsystem_name == "sdp":
            _assert_subsystem_command_result(
                event_tracer,
                subarray_node_low.sdp_subarray_leaf_node,
                (
                    Anything,
                    json.dumps(
                        (
                            int(ResultCode.OK),
                            MESSAGE,
                        )
                    ),
                ),
                "sdp",
            )
        elif subsystem_name == "csp":
            _assert_subsystem_command_result(
                event_tracer,
                subarray_node_low.csp_subarray_leaf_node,
                (
                    Anything,
                    json.dumps(
                        (
                            int(ResultCode.OK),
                            MESSAGE,
                        )
                    ),
                ),
                "csp",
            )

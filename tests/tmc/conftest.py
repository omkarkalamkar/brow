"""
Common modules for reuse
"""


import json

# import pytest
from assertpy import assert_that
from pytest_bdd import given, parsers, then, when
from ska_control_model import ObsState, ResultCode
from ska_tango_testing.integration import TangoEventTracer, log_events
from tango import DevState

from tests.conftest import LOGGER
from tests.resources.test_harness.central_node_low import CentralNodeWrapperLow
from tests.resources.test_harness.constant import (
    ERROR_PROPAGATION_DEFECT,
    TIMEOUT,
    low_csp_subarray_leaf_node,
    low_sdp_subarray_leaf_node,
    mccs_subarray_leaf_node,
)
from tests.resources.test_harness.simulator_factory import SimulatorFactory
from tests.resources.test_harness.subarray_node_low import (
    SubarrayNodeWrapperLow,
)
from tests.resources.test_harness.utils.common_utils import JsonFactory
from tests.resources.test_harness.utils.enums import SimulatorDeviceType
from tests.resources.test_support.common_utils.tmc_helpers import (
    prepare_json_args_for_centralnode_commands,
    prepare_json_args_for_commands,
)


@given("the telescope is is ON state")
def check_telescope_is_in_on_state(
    central_node_low: CentralNodeWrapperLow,
    subarray_node_low: SubarrayNodeWrapperLow,
    event_tracer: TangoEventTracer,
) -> None:
    """
    Ensure telescope is in ON state.
    """
    # Event Subscriptions
    event_tracer.subscribe_event(
        central_node_low.central_node, "telescopeState"
    )
    event_tracer.subscribe_event(
        subarray_node_low.subarray_node, "longRunningCommandResult"
    )
    log_events(
        {
            central_node_low.central_node: ["telescopeState"],
            subarray_node_low.subarray_node: [
                "obsState",
                "longRunningCommandResult",
            ],
        }
    )
    central_node_low.move_to_on()
    assert_that(event_tracer).described_as(
        "FAILED ASSUMPTION AFTER ON COMMAND: "
        "Central Node device"
        f"({central_node_low.central_node.dev_name()}) "
        "is expected to be in TelescopeState ON",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        central_node_low.central_node,
        "telescopeState",
        DevState.ON,
    )


def perform_idle_transition(
    central_node_low: CentralNodeWrapperLow,
    subarray_node_low: SubarrayNodeWrapperLow,
    event_tracer: TangoEventTracer,
    command_input_factory: JsonFactory,
):
    """
    Execute Assign and verify
    """

    event_tracer.subscribe_event(subarray_node_low.subarray_node, "obsState")
    event_tracer.subscribe_event(
        central_node_low.central_node, "longRunningCommandResult"
    )

    log_events(
        {
            central_node_low.central_node: [
                "longRunningCommandResult",
            ]
        }
    )

    assign_input_str = prepare_json_args_for_centralnode_commands(
        "assign_resources_low", command_input_factory
    )
    _, unique_id = central_node_low.store_resources(assign_input_str)

    assert_that(event_tracer).described_as(
        "FAILED ASSUMPTION AFTER ASSIGNRESOURCES COMMAND: "
        "Subarray Node device"
        f"({subarray_node_low.subarray_node.dev_name()}) "
        "is expected to be in IDLE obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        subarray_node_low.subarray_node,
        "obsState",
        ObsState.IDLE,
    )

    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "GIVEN" STEP: '
        "Central Node device"
        f"({central_node_low.central_node.dev_name()}) "
        "is expected have longRunningCommand as"
        '(unique_id,(ResultCode.OK,"Command Completed"))',
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        central_node_low.central_node,
        "longRunningCommandResult",
        (unique_id[0], json.dumps((int(ResultCode.OK), "Command Completed"))),
    )
    event_tracer.clear_events()


def perform_ready_transition_with_end(
    subarray_node_low: SubarrayNodeWrapperLow,
    event_tracer: TangoEventTracer,
    defective_device,
):
    """
    Execute End and verify error propogation
    """

    _, unique_id = subarray_node_low.end_observation()

    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "WHEN" STEP: '
        '"I end the observation"'
        "Subarray Node device"
        f"({subarray_node_low.subarray_node.dev_name()}) "
        "is expected to be in IDLE obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        subarray_node_low.subarray_node,
        "obsState",
        ObsState.CONFIGURING,
    )

    exception_message = (
        "Exception occurred on the following devices:"
        + f" {defective_device}:"
        + " Exception occurred, command failed."
    )

    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "THEN" STEP: '
        '"the command failure is reported by subarray with appropriate"'
        '"error message"'
        "Subarray Node device"
        f"({subarray_node_low.subarray_node.dev_name()}) "
        "is expected have longRunningCommandResult"
        "(ResultCode.FAILED,exception)",
    ).within_timeout(TIMEOUT).has_desired_result_code_message_in_lrcr_event(
        subarray_node_low.subarray_node,
        [exception_message],
        unique_id[0],
        ResultCode.FAILED,
    )

    defective_device.SetDefective(json.dumps({"enabled": False}))

    event_tracer.clear_events()


def perform_scanning_transition(
    # central_node_low: CentralNodeWrapperLow,
    subarray_node_low: SubarrayNodeWrapperLow,
    event_tracer: TangoEventTracer,
    command_input_factory: JsonFactory,
):
    """
    Execute Scan and verify
    """

    scan_input_json = prepare_json_args_for_commands(
        "scan_low", command_input_factory
    )
    subarray_node_low.execute_transition("Scan", scan_input_json)

    # """Verify that the subarray is in the SCANNING obsState."""
    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "THEN" STEP: '
        "'the subarray must be in the SCANNING obsState until finished'"
        "Subarray Node device"
        f"({subarray_node_low.subarray_node.dev_name()}) "
        "is expected to be in SCANNING obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        subarray_node_low.subarray_node,
        "obsState",
        ObsState.SCANNING,
    )
    # assert_that(event_tracer).described_as(
    #     'FAILED ASSUMPTION IN "THEN" STEP: '
    #     "'the subarray must be in the SCANNING obsState until finished'"
    #     "Subarray Node device"
    #     f"({subarray_node_low.subarray_node.dev_name()}) "
    #     "is expected to be in READY obstate",
    # ).within_timeout(TIMEOUT).has_change_event_occurred(
    #     subarray_node_low.subarray_node,
    #     "obsState",
    #     ObsState.READY,
    # )


def perform_ready_transition(
    central_node_low: CentralNodeWrapperLow,
    subarray_node_low: SubarrayNodeWrapperLow,
    event_tracer: TangoEventTracer,
    command_input_factory: JsonFactory,
):
    """
    Execute Configure and verify
    """

    # """Send a Configure command to the subarray."""
    configure_input_json = prepare_json_args_for_commands(
        "configure_low", command_input_factory
    )
    _, unique_id = subarray_node_low.store_configuration_data(
        configure_input_json
    )

    # """Verify that the subarray is in the READY obsState."""
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

    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "GIVEN" STEP: '
        "Subarray Node device"
        f"({central_node_low.subarray_node.dev_name()}) "
        "is expected have longRunningCommand as"
        '(unique_id,(ResultCode.OK,"Command Completed"))',
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        central_node_low.subarray_node,
        "longRunningCommandResult",
        (unique_id[0], json.dumps((int(ResultCode.OK), "Command Completed"))),
    )


@given(
    parsers.parse(
        "the TMC subarray is in the {initialObsState} observation state"
    )
)
def move_tmc_to_intial_state(
    central_node_low: CentralNodeWrapperLow,
    subarray_node_low: SubarrayNodeWrapperLow,
    event_tracer: TangoEventTracer,
    command_input_factory: JsonFactory,
    initialObsState,
):

    """
    Method to move and verify tmc  subarray  in required initial
    observation state.
    """

    match initialObsState:
        case "READY":
            LOGGER.info("Working on Ready State")
            perform_idle_transition(
                central_node_low,
                subarray_node_low,
                event_tracer,
                command_input_factory,
            )

            LOGGER.info("Sending End Command")
            perform_ready_transition(
                central_node_low,
                subarray_node_low,
                event_tracer,
                command_input_factory,
            )
        case "SCANNING":
            LOGGER.info("Working on SCANNING")
            LOGGER.info("Working on Ready State")
            perform_idle_transition(
                central_node_low,
                subarray_node_low,
                event_tracer,
                command_input_factory,
            )

            perform_ready_transition(
                central_node_low,
                subarray_node_low,
                event_tracer,
                command_input_factory,
            )

            perform_scanning_transition(
                # central_node_low,
                subarray_node_low,
                event_tracer,
                command_input_factory,
            )

    # case
    # 2:
    # return "Two"
    # case
    # _:
    # return "Other"


@when(parsers.parse("{command} is invoked on a {defectiveSubsystem} Subarray"))
def execute_command_on_tmc_with_defectivesetup(
    subarray_node_low: SubarrayNodeWrapperLow,
    event_tracer: TangoEventTracer,
    simulator_factory: SimulatorFactory,
    command,
    defectiveSubsystem,
):
    """
    Send next command on TMC
    """

    LOGGER.info("Inside %s  is invoked for %s", command, defectiveSubsystem)

    defective_subarray = None
    match defectiveSubsystem:
        case "CSP":
            defective_subarray = (
                simulator_factory.get_or_create_simulator_device(
                    SimulatorDeviceType.LOW_CSP_DEVICE
                )
            )
            defective_device = low_csp_subarray_leaf_node
        case "SDP":
            defective_subarray = (
                simulator_factory.get_or_create_simulator_device(
                    SimulatorDeviceType.LOW_SDP_DEVICE
                )
            )
            defective_device = low_sdp_subarray_leaf_node

        case "MCCS":
            defective_subarray = (
                simulator_factory.get_or_create_simulator_device(
                    SimulatorDeviceType.MCCS_SUBARRAY_DEVICE
                )
            )

            defective_device = mccs_subarray_leaf_node

        # Inducing Fault
    #
    defective_subarray.SetDefective(ERROR_PROPAGATION_DEFECT)

    match command:
        case "END":
            LOGGER.info("Working on Ready State")
            perform_ready_transition_with_end(
                subarray_node_low,
                event_tracer,
                defective_device,
            )


@then(
    parsers.parse(
        "the command failure is reported by subarray with appropriate"
        " error message"
    )
)
def validate_error_message_reporting(
    # central_node_low: CentralNodeWrapperLow,
    # subarray_node_low: SubarrayNodeWrapperLow,
    # event_tracer: TangoEventTracer,
    # command_input_factory: JsonFactory,
):
    """
    Send next command on TMC
    """

    LOGGER.info("validate_error_message_reporting")


@then(parsers.parse("the TMC SubarrayNode remains in {Intermediate} obsState"))
def validate_subarry_obsState(
    # central_node_low: CentralNodeWrapperLow,
    # subarray_node_low: SubarrayNodeWrapperLow,
    # event_tracer: TangoEventTracer,
    # command_input_factory: JsonFactory,
    Intermediate,
):
    """
    Send next command on TMC
    """

    LOGGER.info("validate_error_message_reporting for %s ", Intermediate)

"""
Common modules for reuse
"""

import json

import pytest
from assertpy import assert_that
from pytest_bdd import given, parsers, then, when
from ska_control_model import ObsState, ResultCode
from ska_integration_test_harness.facades.csp_facade import CSPFacade
from ska_integration_test_harness.facades.mccs_facade import MCCSFacade
from ska_integration_test_harness.facades.sdp_facade import SDPFacade
from ska_integration_test_harness.facades.tmc_facade import TMCFacade
from ska_tango_testing.integration import TangoEventTracer, log_events
from tango import DevState

from tests.resources.test_harness.central_node_low import CentralNodeWrapperLow
from tests.resources.test_harness.constant import (
    ERROR_PROPAGATION_DEFECT,
    FAILED_DEFECT,
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
from tests.resources.test_harness.utils.my_file_json_input import (
    MyFileJSONInput,
)
from tests.resources.test_support.common_utils.tmc_helpers import (
    prepare_json_args_for_centralnode_commands,
    prepare_json_args_for_commands,
)


@given("the telescope is in the ON state")
def given_the_telescope_is_in_on_state(
    tmc: TMCFacade,
    csp: CSPFacade,
    sdp: SDPFacade,
    mccs: MCCSFacade,
    event_tracer: TangoEventTracer,
):
    """Set up event subscriptions for the test.
    and Ensure the telescope is in ON state
    """
    tmc.move_to_on(wait_termination=True)
    event_tracer.subscribe_event(tmc.subarray_node, "obsState")
    event_tracer.subscribe_event(csp.csp_subarray, "obsState")
    event_tracer.subscribe_event(sdp.sdp_subarray, "obsState")
    event_tracer.subscribe_event(mccs.mccs_subarray, "obsState")
    event_tracer.subscribe_event(tmc.subarray_node, "assignedResources")
    event_tracer.subscribe_event(tmc.central_node, "longRunningCommandResult")
    event_tracer.subscribe_event(tmc.subarray_node, "longRunningCommandResult")

    log_events(
        {
            tmc.subarray_node: [
                "obsState",
                "longRunningCommandResult",
                "assignedResources",
            ],
            csp.csp_subarray: ["obsState"],
            sdp.sdp_subarray: ["obsState"],
            mccs.mccs_subarray: ["obsState"],
            tmc.central_node: ["longRunningCommandResult"],
        },
        event_enum_mapping={"obsState": ObsState},
    )


@given("a Low telescope")
def given_the_sut(
    event_tracer: TangoEventTracer,
    tmc: TMCFacade,
    csp: CSPFacade,
    sdp: SDPFacade,
    mccs: MCCSFacade,
):
    """
    Set up event subscriptions for the test for a Low Telescope consisting of
    csp , sdp and mccs devices
    """
    event_tracer.subscribe_event(tmc.central_node, "telescopeState")
    event_tracer.subscribe_event(csp.csp_master, "State")
    event_tracer.subscribe_event(csp.csp_subarray, "State")
    event_tracer.subscribe_event(sdp.sdp_master, "State")
    event_tracer.subscribe_event(sdp.sdp_subarray, "State")
    event_tracer.subscribe_event(mccs.mccs_controller, "State")
    event_tracer.subscribe_event(mccs.mccs_subarray, "State")

    log_events(
        {
            tmc.central_node: ["telescopeState"],
            csp.csp_master: ["State"],
            sdp.sdp_master: ["State"],
            mccs.mccs_controller: ["State"],
            mccs.mccs_subarray: ["State"],
            sdp.sdp_subarray: ["State"],
            csp.csp_subarray: ["State"],
        }
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


def verify_scanning_transition_with_endscan(
    subarray_node_low: SubarrayNodeWrapperLow,
):
    """
    Execute EndScan
    """

    _, pytest.unique_id = subarray_node_low.execute_transition("EndScan")


def perform_ready_transition_with_end(
    subarray_node_low: SubarrayNodeWrapperLow,
    event_tracer: TangoEventTracer,
):
    """
    Execute End and verify error propagation
    """

    _, pytest.unique_id = subarray_node_low.subarray_node.End()

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


def perform_scan(
    subarray_node_low: SubarrayNodeWrapperLow,
    command_input_factory: JsonFactory,
):
    """
    Perform Scan
    """
    scan_input_json = prepare_json_args_for_commands(
        "scan_low", command_input_factory
    )
    _, pytest.unique_id = subarray_node_low.execute_transition(
        "Scan", scan_input_json
    )


def perform_scanning_transition(
    subarray_node_low: SubarrayNodeWrapperLow,
    event_tracer: TangoEventTracer,
    command_input_factory: JsonFactory,
):
    """
    Send a Scan command to the subarray.
    """
    event_tracer.subscribe_event(
        subarray_node_low.subarray_node, "longRunningCommandResult"
    )
    scan_input_json = prepare_json_args_for_commands(
        "scan_low", command_input_factory
    )
    _, unique_id = subarray_node_low.execute_transition(
        "Scan", scan_input_json
    )

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

    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "GIVEN" STEP: '
        "Central Node device"
        f"({subarray_node_low.subarray_node.dev_name()}) "
        "is expected have longRunningCommand as"
        '(unique_id,(ResultCode.OK,"Command Completed"))',
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        subarray_node_low.subarray_node,
        "longRunningCommandResult",
        (unique_id[0], json.dumps((int(ResultCode.OK), "Command Completed"))),
    )
    event_tracer.clear_events()


def perform_ready_transition(
    central_node_low: CentralNodeWrapperLow,
    subarray_node_low: SubarrayNodeWrapperLow,
    event_tracer: TangoEventTracer,
    command_input_factory: JsonFactory,
):
    """
    Send a Configure command to the subarray.
    """

    configure_input_json = prepare_json_args_for_commands(
        "configure_low", command_input_factory
    )
    _, unique_id = subarray_node_low.store_configuration_data(
        configure_input_json
    )

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
        case "SCANNING":

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
                subarray_node_low,
                event_tracer,
                command_input_factory,
            )


@when(
    parsers.parse(
        "{command} is invoked on a defectiveSubsystem {defectiveSubsystem}"
    )
)
def execute_command_on_tmc_with_defectivesetup(
    subarray_node_low: SubarrayNodeWrapperLow,
    event_tracer: TangoEventTracer,
    simulator_factory: SimulatorFactory,
    command_input_factory: JsonFactory,
    command,
    defectiveSubsystem,
):
    """
    Execute command on TMC subarray node with defective subsystem.
    """

    pytest.defective_subarray = None
    match defectiveSubsystem:
        case "CSP":
            pytest.defective_subarray = (
                simulator_factory.get_or_create_simulator_device(
                    SimulatorDeviceType.LOW_CSP_DEVICE
                )
            )
            pytest.defective_device = low_csp_subarray_leaf_node
            pytest.defective_subarray.SetDefective(ERROR_PROPAGATION_DEFECT)
        case "SDP":
            pytest.defective_subarray = (
                simulator_factory.get_or_create_simulator_device(
                    SimulatorDeviceType.LOW_SDP_DEVICE
                )
            )
            pytest.defective_device = low_sdp_subarray_leaf_node
            pytest.defective_subarray.SetDefective(FAILED_DEFECT)

        case "MCCS":
            pytest.defective_subarray = (
                simulator_factory.get_or_create_simulator_device(
                    SimulatorDeviceType.MCCS_SUBARRAY_DEVICE
                )
            )

            pytest.defective_device = mccs_subarray_leaf_node

            pytest.defective_subarray.SetDefective(ERROR_PROPAGATION_DEFECT)

    match command:
        case "END":

            perform_ready_transition_with_end(
                subarray_node_low,
                event_tracer,
            )

        case "ENDSCAN":

            verify_scanning_transition_with_endscan(
                subarray_node_low,
            )
        case "SCAN":

            perform_scan(
                subarray_node_low,
                command_input_factory,
            )


@then(
    parsers.parse(
        "the command failure is reported by subarray with error message"
    )
)
def validate_error_message_reporting(
    subarray_node_low: SubarrayNodeWrapperLow,
    event_tracer: TangoEventTracer,
):
    """
    Check if subarray node populates error message correctly.
    """

    exception_message = (
        "Exception occurred on the following devices:"
        + f" {pytest.defective_device}:"
    )

    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "THEN" STEP: '
        '"the command failure is reported by subarray with appropriate"'
        '"error message"'
        "Subarray Node device"
        f"({subarray_node_low.subarray_node.dev_name()}) "
        "is expected have longRunningCommandResult"
        "(ResultCode.FAILED,exception)",
    ).within_timeout(120).has_desired_result_code_message_in_lrcr_event(
        subarray_node_low.subarray_node,
        [exception_message],
        pytest.unique_id[0],
        ResultCode.FAILED,
    )

    pytest.defective_subarray.SetDefective(json.dumps({"enabled": False}))


@then(parsers.parse("the TMC SubarrayNode transitions to FAULT obsState"))
def validate_subarry_obsState(
    subarray_node_low: SubarrayNodeWrapperLow,
    event_tracer: TangoEventTracer,
):
    """
    Check if TMC subarray remains in stuck Obs-State.
    """
    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "THEN" STEP: '
        '"the TMC SubarrayNode transitions to FAULT obsState"'
        f"({subarray_node_low.subarray_node.dev_name()}) "
        "is expected to be in FAULT obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        subarray_node_low.subarray_node,
        "obsState",
        ObsState.FAULT,
    )


def move_to_idle(tmc: TMCFacade, event_tracer: TangoEventTracer):
    """Move subarray to idle state"""
    assign_input = MyFileJSONInput("centralnode", "assign_resources_low")

    _, unique_id = tmc.central_node.AssignResources(assign_input.as_str())
    assert_that(event_tracer).described_as(
        "FAILED ASSUMPTION AFTER ASSIGNRESOURCES COMMAND: "
        "Subarray Node device"
        f"({tmc.subarray_node.dev_name()}) "
        "is expected to be in IDLE obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        tmc.subarray_node,
        "obsState",
        ObsState.IDLE,
    )

    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "GIVEN" STEP: '
        "Central Node device"
        f"({tmc.central_node.dev_name()}) "
        "is expected have longRunningCommand as"
        '(unique_id,(ResultCode.OK,"Command Completed"))',
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        tmc.central_node,
        "longRunningCommandResult",
        (
            unique_id[0],
            json.dumps((int(ResultCode.OK), "Command Completed")),
        ),
    )


def move_to_ready(
    tmc: TMCFacade, event_tracer: TangoEventTracer, is_single_subsystem=False
):
    """Send a Configure command to the subarray"""
    configure_input = MyFileJSONInput("subarray", "configure_low")

    configure_input_json = json.loads(configure_input.as_str())
    configure_input_json[
        "interface"
    ] = "https://schema.skao.int/ska-low-tmc-configure/4.2"

    if is_single_subsystem:
        for subsystem in ["sdp", "csp"]:
            del configure_input_json[subsystem]

    configure_input_json = json.dumps(configure_input_json)

    _, unique_id = tmc.subarray_node.Configure(configure_input_json)

    assert_that(event_tracer).described_as(
        "FAILED ASSUMPTION : "
        "Subarray Node device"
        f"({tmc.subarray_node.dev_name()}) "
        "is expected have longRunningCommand as"
        '(unique_id,(ResultCode.OK,"Command Completed"))',
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        tmc.subarray_node,
        "longRunningCommandResult",
        (
            unique_id[0],
            json.dumps((int(ResultCode.OK), "Command Completed")),
        ),
    )
    assert_that(event_tracer).described_as(
        "FAILED ASSUMPTION : "
        "'the subarray is in the READY obsState'"
        "Subarray Node device"
        f"({tmc.subarray_node.dev_name()}) "
        "is expected to be in READY obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        tmc.subarray_node,
        "obsState",
        ObsState.READY,
    )


def move_to_scanning(tmc: TMCFacade, event_tracer: TangoEventTracer):
    """invoke scan command"""
    scan_input = MyFileJSONInput("subarray", "scan_low")

    _, unique_id = tmc.subarray_node.Scan(scan_input.as_str())

    assert_that(event_tracer).described_as(
        "FAILED ASSUMPTION : "
        "'the subarray must be in the SCANNING obsState'"
        "Subarray Node device"
        f"({tmc.subarray_node.dev_name()}) "
        "is expected to be in SCANNING obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        tmc.subarray_node,
        "obsState",
        ObsState.SCANNING,
    )
    assert_that(event_tracer).described_as(
        "SubarrayNode device"
        f"({tmc.subarray_node.dev_name()}) "
        "is expected have longRunningCommand as"
        '(unique_id,(ResultCode.OK,"Command Completed"))',
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        tmc.subarray_node,
        "longRunningCommandResult",
        (
            unique_id[0],
            json.dumps((int(ResultCode.OK), "Command Completed")),
        ),
    )


def invoke_endscan(tmc: TMCFacade, event_tracer: TangoEventTracer):
    """Invoke endscan command"""
    tmc.subarray_node.EndScan()
    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "THEN" STEP: '
        "'And the subarray is in the READY obsState'"
        "Subarray Node device"
        f"({tmc.subarray_node.dev_name()}) "
        "is expected to be in READY obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        tmc.subarray_node,
        "obsState",
        ObsState.READY,
    )

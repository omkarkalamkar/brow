"""
Test case to verify error propagation functionality for
the Scan /EndScan command

This test case verifies that the MCCS Subarray
is identified as defective,
 and the required command is executed on the TMC Low,
 then Subarry node
   reports an error.
"""
import json

import pytest
from assertpy import assert_that
from pytest_bdd import given, parsers, scenario, then, when
from ska_control_model import ObsState, ResultCode
from ska_tango_testing.integration import TangoEventTracer

from tests.resources.test_harness.central_node_low import CentralNodeWrapperLow
from tests.resources.test_harness.constant import (
    ERROR_PROPAGATION_DEFECT,
    TIMEOUT,
    mccs_subarray_leaf_node,
)
from tests.resources.test_harness.simulator_factory import SimulatorFactory
from tests.resources.test_harness.subarray_node_low import (
    SubarrayNodeWrapperLow,
)
from tests.resources.test_harness.utils.common_utils import JsonFactory
from tests.resources.test_harness.utils.enums import SimulatorDeviceType
from tests.resources.test_support.common_utils.tmc_helpers import (
    prepare_json_args_for_commands,
)
from tests.tmc.conftest import perform_idle_transition


@pytest.mark.SKA_fault
@pytest.mark.SKA_low
@scenario(
    "../features/tmc/check_error_propagation_mccs_only.feature",
    "Error Propagation Reported by TMC Low EndScan/Scan "
    "Commands for Defective MCCS Subarray",
)
def test_tmc_command_error_propagation_fault():
    """
    Test case to verify TMC Error Propagation functionality.
    """


def execute_command(
    command,
    subarray_node_low: SubarrayNodeWrapperLow,
    command_input_factory: JsonFactory,
):
    """
    Execute command
    """

    pytest.defective_subarray.SetDefective(ERROR_PROPAGATION_DEFECT)
    match command:

        case "ENDSCAN":
            subarray_node_low.subarray_node.EndScan()
        case "SCAN":
            scan_input_json = prepare_json_args_for_commands(
                "scan_low", command_input_factory
            )
            _, pytest.unique_id = subarray_node_low.subarray_node.Scan(
                scan_input_json
            )


@given(
    parsers.parse(
        "the TMC subarraynode is in the {obsState} observation state"
    )
)
def move_to_obsstate(
    central_node_low: CentralNodeWrapperLow,
    subarray_node_low: SubarrayNodeWrapperLow,
    event_tracer: TangoEventTracer,
    obsState,
    command_input_factory,
):
    """Move Tmc to the given obsstate"""

    match obsState:
        case "READY":
            perform_idle_transition(
                central_node_low,
                subarray_node_low,
                event_tracer,
                command_input_factory,
            )
            configure_input_json = prepare_json_args_for_commands(
                "configure_low", command_input_factory
            )

            configure_input_json = json.loads(configure_input_json)
            configure_input_json[
                "interface"
            ] = "https://schema.skao.int/ska-low-tmc-configure/4.2"
            for subsystem in ["sdp", "csp"]:
                del configure_input_json[subsystem]

            configure_input_json = json.dumps(configure_input_json)
            _, unique_id = subarray_node_low.subarray_node.Configure(
                configure_input_json
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
                (
                    unique_id[0],
                    json.dumps((int(ResultCode.OK), "Command Completed")),
                ),
            )
        case "SCANNING":
            perform_idle_transition(
                central_node_low,
                subarray_node_low,
                event_tracer,
                command_input_factory,
            )
            configure_input_json = prepare_json_args_for_commands(
                "configure_low", command_input_factory
            )

            configure_input_json = json.loads(configure_input_json)
            configure_input_json[
                "interface"
            ] = "https://schema.skao.int/ska-low-tmc-configure/4.2"
            for subsystem in ["sdp", "csp"]:
                del configure_input_json[subsystem]

            configure_input_json = json.dumps(configure_input_json)
            _, unique_id = subarray_node_low.store_configuration_data(
                configure_input_json
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
                (
                    unique_id[0],
                    json.dumps((int(ResultCode.OK), "Command Completed")),
                ),
            )
            scan_input_json = prepare_json_args_for_commands(
                "scan_low", command_input_factory
            )
            _, pytest.unique_id = subarray_node_low.subarray_node.Scan(
                scan_input_json
            )


@when(parsers.parse("{command} is invoked on a defective MCCS Subarray"))
def execute_command_on_tmc_with_defectivesetup(
    subarray_node_low: SubarrayNodeWrapperLow,
    simulator_factory: SimulatorFactory,
    command,
    command_input_factory: JsonFactory,
):
    """
    Send next command on TMC
    """

    pytest.defective_subarray = (
        simulator_factory.get_or_create_simulator_device(
            SimulatorDeviceType.MCCS_SUBARRAY_DEVICE
        )
    )

    pytest.defective_device = mccs_subarray_leaf_node

    execute_command(command, subarray_node_low, command_input_factory)


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

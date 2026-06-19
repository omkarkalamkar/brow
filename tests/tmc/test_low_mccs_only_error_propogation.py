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
from ska_integration_test_harness.facades.tmc_facade import TMCFacade
from ska_tango_testing.integration import TangoEventTracer

from tests.resources.test_harness.constant import (
    ERROR_PROPAGATION_DEFECT,
    TIMEOUT,
    mccs_subarray_leaf_node,
)
from tests.resources.test_harness.simulator_factory import SimulatorFactory
from tests.resources.test_harness.utils.enums import SimulatorDeviceType
from tests.resources.test_harness.utils.my_file_json_input import (
    MyFileJSONInput,
)
from tests.tmc.conftest import move_to_idle, move_to_ready, move_to_scanning


@pytest.mark.SKA_tmc_low_negative_tests
@scenario(
    "tmc/check_error_propagation_mccs_only.feature",
    "Error Propagation Reported by TMC Low Configure/End/EndScan/Scan "
    "Commands for Defective MCCS Subarray",
)
def test_tmc_command_error_propagation_fault():
    """
    Test case to verify TMC Error Propagation functionality.
    """


def execute_command(
    command,
    tmc: TMCFacade,
):
    """
    Execute command
    """

    pytest.defective_subarray.SetDefective(ERROR_PROPAGATION_DEFECT)
    match command:
        case "ENDSCAN":
            _, pytest.unique_id = tmc.subarray_node.EndScan()
        case "SCAN":
            scan_input = MyFileJSONInput("subarray", "scan_low")
            _, pytest.unique_id = tmc.subarray_node.Scan(scan_input.as_str())
        case "CONFIGURE":
            configure_input = MyFileJSONInput("subarray", "configure_low")

            configure_input_json = json.loads(configure_input.as_str())
            configure_input_json[
                "interface"
            ] = "https://schema.skao.int/ska-low-tmc-configure/4.2"

            for subsystem in ["sdp", "csp"]:
                del configure_input_json[subsystem]

            configure_input_json = json.dumps(configure_input_json)

            _, pytest.unique_id = tmc.subarray_node.Configure(
                configure_input_json
            )
        case "END":
            _, pytest.unique_id = tmc.subarray_node.End()


@given(
    parsers.parse(
        "the TMC subarraynode is in the {obsState} observation state"
    )
)
def move_to_obsstate(
    tmc: TMCFacade,
    event_tracer: TangoEventTracer,
    obsState,
):
    """Move Tmc to the given obsstate"""

    match obsState:
        case "READY":
            move_to_idle(tmc, event_tracer)
            move_to_ready(tmc, event_tracer, is_single_subsystem=True)
        case "SCANNING":
            move_to_idle(tmc, event_tracer)
            move_to_ready(tmc, event_tracer, is_single_subsystem=True)
            move_to_scanning(tmc, event_tracer)
        case "IDLE":
            move_to_idle(tmc, event_tracer)


@when(parsers.parse("{command} is invoked on a defective MCCS Subarray"))
def execute_command_on_tmc_with_defectivesetup(
    tmc: TMCFacade,
    simulator_factory: SimulatorFactory,
    command,
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

    execute_command(command, tmc)


@then(
    parsers.parse(
        "the command failure is reported by subarray with error message"
    )
)
def validate_error_message_reporting(
    tmc: TMCFacade,
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
        f"({tmc.subarray_node.dev_name()}) "
        "is expected have longRunningCommandResult"
        "(ResultCode.FAILED,exception)",
    ).within_timeout(120).has_desired_result_code_message_in_lrcr_event(
        tmc.subarray_node,
        [exception_message],
        pytest.unique_id[0],
        ResultCode.FAILED,
    )

    pytest.defective_subarray.SetDefective(json.dumps({"enabled": False}))


@then("the TMC SubarrayNode transitions to FAULT obsState")
def validate_subarry_obsState(
    tmc: TMCFacade,
    event_tracer: TangoEventTracer,
):
    """
    Check if TMC subarray remains in stuck Obs-State.
    """
    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "THEN" STEP: '
        '"the TMC SubarrayNode transitions to FAULT obsState"'
        f"({tmc.subarray_node.dev_name()}) "
        "is expected to be in FAULT obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        tmc.subarray_node,
        "obsState",
        ObsState.FAULT,
    )

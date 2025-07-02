"""
Test case to verify error propagation functionality for
the End / Scan /EndScan command

This test case verifies that one of  the MCCS/CSP/SDP Subarray
is identified as defective,
 and the required command is executed on the TMC Low,
 then Subarry node
   reports an error.
"""
import json

import pytest
from assertpy import assert_that
from pytest_bdd import parsers, scenario, then, when
from ska_control_model import ObsState, ResultCode
from ska_tango_testing.integration import TangoEventTracer

from tests.resources.test_harness.constant import (
    INTERMEDIATE_CONFIGURING_STATE_DEFECT,
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
from tests.tmc.conftest import (
    perform_configure,
    perform_ready_transition_with_end,
    perform_scan,
    verify_scanning_transition_with_endscan,
)


@pytest.mark.SKA_low
@scenario(
    "../features/tmc/check_error_propagation.feature",
    "Error Propagation Reported by TMC Low Configure/End/EndScan/Scan "
    "Commands for Defective Subarray",
)
def test_tmc_command_error_propagation():
    """
    Test case to verify TMC Error Propagation functionality.
    """


@pytest.mark.SKA_low
@scenario(
    "../features/tmc/check_error_propagation.feature",
    "TimeOut Reported by TMC Low Configure/End/EndScan/Scan "
    "Commands for Defective Subarray",
)
def test_tmc_command_timeout_error_propagation():
    """
    Test case to verify TMC TimeOut Error Propagation functionality.
    """


def execute_command(
    device,
    command,
    subarray_node_low: SubarrayNodeWrapperLow,
    event_tracer: TangoEventTracer,
    command_input_factory: JsonFactory,
):
    """
    Execute command
    """
    if device in ["CSP", "MCCS"]:
        match command:
            case "END":
                pytest.defective_subarray.SetDefective(
                    INTERMEDIATE_CONFIGURING_STATE_DEFECT
                )

                perform_ready_transition_with_end(
                    subarray_node_low,
                    event_tracer,
                )

            case "ENDSCAN":

                pytest.defective_subarray.SetDefective(
                    INTERMEDIATE_CONFIGURING_STATE_DEFECT
                )

                verify_scanning_transition_with_endscan(
                    subarray_node_low,
                )
            case "SCAN":

                pytest.defective_subarray.SetDefective(
                    INTERMEDIATE_CONFIGURING_STATE_DEFECT
                )

                perform_scan(
                    subarray_node_low,
                    command_input_factory,
                )
            case "CONFIGURE":
                pytest.defective_subarray.SetDefective(
                    INTERMEDIATE_CONFIGURING_STATE_DEFECT
                )
                perform_configure(
                    subarray_node_low,
                    command_input_factory,
                )
    elif device == "SDP":

        match command:
            case "END":

                pytest.defective_subarray.SetDelayInfo(json.dumps({"End": 55}))

                perform_ready_transition_with_end(
                    subarray_node_low,
                    event_tracer,
                )

            case "ENDSCAN":

                pytest.defective_subarray.SetDelayInfo(
                    json.dumps({"EndScan": 55})
                )

                verify_scanning_transition_with_endscan(
                    subarray_node_low,
                    # event_tracer,
                )
            case "SCAN":

                pytest.defective_subarray.SetDelayInfo(
                    json.dumps({"Scan": 55})
                )

                perform_scan(
                    subarray_node_low,
                    command_input_factory,
                )
            case "CONFIGURE":
                pytest.defective_subarray.SetDelayInfo(
                    json.dumps({"Configure": 55})
                )
                perform_configure(
                    subarray_node_low,
                    command_input_factory,
                )


@when(parsers.parse("{command} is invoked on a {defectiveSubsystem} Subarray"))
def execute_command_on_tmc_with_defectivesetup(
    subarray_node_low: SubarrayNodeWrapperLow,
    event_tracer: TangoEventTracer,
    simulator_factory: SimulatorFactory,
    command_input_factory: JsonFactory,
    command,
    defectiveSubsystem,
):
    """
    Send next command on TMC
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
            execute_command(
                "CSP",
                command,
                subarray_node_low,
                event_tracer,
                command_input_factory,
            )

        case "SDP":
            pytest.defective_subarray = (
                simulator_factory.get_or_create_simulator_device(
                    SimulatorDeviceType.LOW_SDP_DEVICE
                )
            )
            pytest.defective_device = low_sdp_subarray_leaf_node
            execute_command(
                "SDP",
                command,
                subarray_node_low,
                event_tracer,
                command_input_factory,
            )

        case "MCCS":
            pytest.defective_subarray = (
                simulator_factory.get_or_create_simulator_device(
                    SimulatorDeviceType.MCCS_SUBARRAY_DEVICE
                )
            )

            pytest.defective_device = mccs_subarray_leaf_node
            execute_command(
                "MCCS",
                command,
                subarray_node_low,
                event_tracer,
                command_input_factory,
            )


@then(
    parsers.parse(
        "the command failure is reported by subarray with appropriate"
        " error message"
    )
)
def validate_error_message_reporting(
    subarray_node_low: SubarrayNodeWrapperLow,
    event_tracer: TangoEventTracer,
):
    """
    Send next command on TMC
    """

    exception_message = "Timeout has occurred, command failed"

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
    pytest.defective_subarray.ResetDelayInfo()


@then("the TMC SubarrayNode transitions to FAULT obsState")
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

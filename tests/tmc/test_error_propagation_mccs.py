"""
Test case to verify error propagation functionality for the Configure command
 of Mccsleafnodes.
This test case verifies that when the MCCS Subarray is identified as defective,
 and the Configure command is executed on the TMC Low, the Configure command
   reports an error.
"""


import pytest
from assertpy import assert_that
from pytest_bdd import given, scenario, then, when
from ska_control_model import ObsState, ResultCode
from ska_tango_testing.integration import TangoEventTracer, log_events
from tango import DevState

from tests.resources.test_harness.central_node_low import CentralNodeWrapperLow
from tests.resources.test_harness.constant import (
    ERROR_PROPAGATION_DEFECT,
    TIMEOUT,
    mccs_subarray1,
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


@pytest.mark.SKA_low
@scenario(
    "../features/tmc/check_error_propagation_mccs.feature",
    "Error Propagation Reported by TMC Low Configure Command for"
    + " Defective MCCS Subarray",
)
def test_mccs_configure_command_error_propagation():
    """
    Test case to verify TMC-MCCS Error Propagation functionality.
    """


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


@given("the TMC subarray is in the idle observation state")
def check_subarray_obs_state(
    central_node_low: CentralNodeWrapperLow,
    subarray_node_low: SubarrayNodeWrapperLow,
    event_tracer: TangoEventTracer,
    command_input_factory: JsonFactory,
):
    """
    Method to check subarray is in IDLE observation state.
    """
    event_tracer.subscribe_event(subarray_node_low.subarray_node, "obsState")
    assign_input_str = prepare_json_args_for_centralnode_commands(
        "assign_resources_low", command_input_factory
    )
    central_node_low.store_resources(assign_input_str)

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


@when("Configure command is invoked on a defective MCCS Subarray")
def invoke_configure_command_with_mccs_defective(
    subarray_node_low: SubarrayNodeWrapperLow,
    event_tracer: TangoEventTracer,
    simulator_factory: SimulatorFactory,
    command_input_factory: JsonFactory,
):
    """
    Invoke the Configure command with the MCCS Subarray identified as defective

    This method prepares the input files, induces a fault in the MCCS Subarray
      simulator,
    and executes the Configure command on the TMC Low. It asserts that the
      subarray is in the CONFIGURING observation state after the
        command execution.
    """
    mccs_subarray_sim = simulator_factory.get_or_create_simulator_device(
        SimulatorDeviceType.MCCS_SUBARRAY_DEVICE
    )
    # Preparing input files
    configure_input_str = prepare_json_args_for_commands(
        "configure_low", command_input_factory
    )
    # Inducing Fault
    #
    mccs_subarray_sim.SetDefective(ERROR_PROPAGATION_DEFECT)

    _, pytest.unique_id = subarray_node_low.execute_transition(
        "Configure", configure_input_str
    )
    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "WHEN" STEP: '
        '"Configure command is invoked on a defective MCCS Subarray"'
        "Subarray Node device"
        f"({subarray_node_low.subarray_node.dev_name()}) "
        "is expected to be in CONFIGURING obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        subarray_node_low.subarray_node,
        "obsState",
        ObsState.CONFIGURING,
    )


@then(
    "the command failure is reported by subarray with appropriate"
    + " error message"
)
def configure_command_reports_error_propagate(
    subarray_node_low: SubarrayNodeWrapperLow,
    event_tracer: TangoEventTracer,
):
    """
    Verify that the Configure command reports an error.

    This method subscribes to the 'longRunningCommandResult' event and asserts
      that the command times out and reports an error message indicating a
        error has propagated.
    """

    exception_message = (
        "Exception occurred on the following devices:"
        + f" {mccs_subarray_leaf_node}:"
        + " Exception occurred on device:"
        + f" {mccs_subarray1}:"
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
        pytest.unique_id[0],
        ResultCode.FAILED,
    )

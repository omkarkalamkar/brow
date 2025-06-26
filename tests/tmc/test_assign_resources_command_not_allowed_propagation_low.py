"""Test cases for AssignResources Command not allowed for LOW."""


import pytest
from assertpy import assert_that
from ska_control_model import ObsState
from ska_tango_testing.integration import TangoEventTracer, log_events
from tango import DevState

from tests.resources.test_harness.central_node_low import CentralNodeWrapperLow
from tests.resources.test_harness.constant import (
    COMMAND_NOT_ALLOWED_DEFECT,
    TIMEOUT,
    low_sdp_subarray_leaf_node,
    mccs_controller,
    mccs_master_leaf_node,
)
from tests.resources.test_harness.helpers import (
    wait_and_validate_device_attribute_value,
)
from tests.resources.test_harness.simulator_factory import SimulatorFactory
from tests.resources.test_harness.utils.common_utils import JsonFactory
from tests.resources.test_harness.utils.enums import SimulatorDeviceType
from tests.resources.test_support.common_utils.result_code import ResultCode
from tests.resources.test_support.common_utils.tmc_helpers import (
    prepare_json_args_for_centralnode_commands,
)


class TestAssignCommandNotAllowedPropagation:
    """Test the command not allowed error propagation for the assign resources
    command for TMC."""

    @pytest.mark.SKA_low
    def test_assign_command_not_allowed_propagation_csp_ln_low(
        self,
        central_node_low: CentralNodeWrapperLow,
        event_tracer: TangoEventTracer,
        simulator_factory: SimulatorFactory,
        command_input_factory: JsonFactory,
    ):
        """Verify command not allowed exception propagation from CSPLeafNodes
        ."""
        csp_subarray_sim = simulator_factory.get_or_create_simulator_device(
            SimulatorDeviceType.LOW_CSP_DEVICE
        )

        # Event Subscriptions
        event_tracer.subscribe_event(
            central_node_low.central_node, "telescopeState"
        )
        event_tracer.subscribe_event(
            central_node_low.central_node, "longRunningCommandResult"
        )
        event_tracer.subscribe_event(
            central_node_low.subarray_node, "obsState"
        )

        # Preparing input arguments
        assign_input_json = prepare_json_args_for_centralnode_commands(
            "assign_resources_low", command_input_factory
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

        # Setting Defects on Devices
        csp_subarray_sim.SetDefective(COMMAND_NOT_ALLOWED_DEFECT)

        _, unique_id = central_node_low.perform_action(
            "AssignResources", assign_input_json
        )

        exception_message = (
            "The invocation of the AssignResources command failed on Csp "
            + "Subarray Device low-csp/subarray/01"
        )
        log_events(
            {central_node_low.central_node: ["longRunningCommandResult"]}
        )

        assert_that(event_tracer).described_as(
            "FAILED ASSUMPTION ATER ASSIGN RESOURCES: "
            "Central Node device"
            f"({central_node_low.central_node.dev_name()}) "
            "is expected have longRunningCommandResult"
            "(ResultCode.FAILED,exception)",
        ).within_timeout(
            TIMEOUT
        ).has_desired_result_code_message_in_lrcr_event(
            central_node_low.central_node,
            [exception_message],
            unique_id[0],
            ResultCode.FAILED,
        )
        assert_that(event_tracer).described_as(
            "FAILED ASSUMPTION AFTER ASSIGN RESOURCES: "
            "Subarray Node device"
            f"({central_node_low.subarray_node.dev_name()}) "
            "is expected to be in FAULT obstate",
        ).within_timeout(TIMEOUT).has_change_event_occurred(
            central_node_low.subarray_node,
            "obsState",
            ObsState.FAULT,
        )

    @pytest.mark.SKA_low
    def test_assign_command_not_allowed_propagation_sdp_ln_low(
        self,
        central_node_low: CentralNodeWrapperLow,
        event_tracer: TangoEventTracer,
        simulator_factory: SimulatorFactory,
        command_input_factory: JsonFactory,
    ):
        """Verify command not allowed exception propagation from SDPLeafNodes
        ."""
        sdp_subarray_sim = simulator_factory.get_or_create_simulator_device(
            SimulatorDeviceType.LOW_SDP_DEVICE
        )

        # Event Subscriptions
        event_tracer.subscribe_event(
            central_node_low.central_node, "telescopeState"
        )
        event_tracer.subscribe_event(
            central_node_low.subarray_node, "obsState"
        )
        event_tracer.subscribe_event(
            central_node_low.central_node, "longRunningCommandResult"
        )
        event_tracer.subscribe_event(sdp_subarray_sim, "obsState")
        # Preparing input arguments
        assign_input_json = prepare_json_args_for_centralnode_commands(
            "assign_resources_low", command_input_factory
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

        # Setting Defects on Devices
        sdp_subarray_sim.SetDefective(COMMAND_NOT_ALLOWED_DEFECT)
        _, unique_id = central_node_low.perform_action(
            "AssignResources", assign_input_json
        )
        log_events(
            {
                central_node_low.central_node: ["longRunningCommandResult"],
                central_node_low.subarray_node: ["obsState"],
            }
        )
        exception_message = (
            "Exception occurred on the following devices: "
            + f"{low_sdp_subarray_leaf_node}: ska_tmc_common.exceptions"
            + ".CommandNotAllowed: Command is not allowed"
        )
        assert_that(event_tracer).described_as(
            "FAILED ASSUMPTION ATER ASSIGN RESOURCES: "
            "Central Node device"
            f"({central_node_low.central_node.dev_name()}) "
            "is expected have longRunningCommandResult"
            "(ResultCode.FAILED,exception)",
        ).within_timeout(
            TIMEOUT
        ).has_desired_result_code_message_in_lrcr_event(
            central_node_low.central_node,
            [exception_message],
            unique_id[0],
            ResultCode.FAILED,
        )
        assert_that(event_tracer).described_as(
            "FAILED ASSUMPTION AFTER ASSIGN RESOURCES: "
            "Subarray Node device"
            f"({central_node_low.subarray_node.dev_name()}) "
            "is expected to be in FAULT obstate",
        ).within_timeout(TIMEOUT).has_change_event_occurred(
            central_node_low.subarray_node,
            "obsState",
            ObsState.FAULT,
        )

    @pytest.mark.SKA_low
    def test_assign_command_not_allowed_propagation_mccs_ln_low(
        self,
        central_node_low: CentralNodeWrapperLow,
        event_tracer: TangoEventTracer,
        simulator_factory: SimulatorFactory,
        command_input_factory: JsonFactory,
    ):
        """Verify command not allowed exception propagation
        from MccsLeafNodes."""
        mccs_subarray_sim = simulator_factory.get_or_create_simulator_device(
            SimulatorDeviceType.LOW_SDP_DEVICE
        )
        mccs_master_sim = simulator_factory.get_or_create_simulator_device(
            SimulatorDeviceType.MCCS_MASTER_DEVICE
        )

        # Event Subscriptions
        event_tracer.subscribe_event(
            central_node_low.central_node, "telescopeState"
        )
        event_tracer.subscribe_event(
            central_node_low.subarray_node, "obsState"
        )
        event_tracer.subscribe_event(
            central_node_low.central_node, "longRunningCommandResult"
        )
        event_tracer.subscribe_event(mccs_subarray_sim, "obsState")
        # Preparing input arguments
        assign_input_json = prepare_json_args_for_centralnode_commands(
            "assign_resources_low", command_input_factory
        )

        log_events(
            {
                central_node_low.central_node: ["longRunningCommandResult"],
                mccs_subarray_sim: ["obsState"],
                central_node_low.subarray_node: ["obsState"],
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

        # Setting Defects on Devices
        mccs_master_sim.SetDefective(COMMAND_NOT_ALLOWED_DEFECT)
        # Execute Assign command and verify successful execution
        _, unique_id = central_node_low.perform_action(
            "AssignResources", assign_input_json
        )
        # Constructing the error message
        exception_message = (
            f"{mccs_master_leaf_node}: The invocation of the Allocate command"
            + f" is failed on MCCS Controller device {mccs_controller}"
        )

        exception_message2 = "ska_tmc_common.exceptions.CommandNotAllowed"

        assert_that(event_tracer).described_as(
            "FAILED ASSUMPTION AFTER ASSIGN RESOURCES: "
            "Central Node device"
            f"({central_node_low.central_node.dev_name()}) "
            "is expected have longRunningCommandResult"
            "(ResultCode.FAILED,exception)",
        ).within_timeout(
            TIMEOUT
        ).has_desired_result_code_message_in_lrcr_event(
            central_node_low.central_node,
            [exception_message, exception_message2],
            unique_id[0],
            ResultCode.FAILED,
        )
        assert wait_and_validate_device_attribute_value(
            central_node_low.subarray_node,
            "obsState",
            ObsState.EMPTY,
        )

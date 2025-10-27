"""Test Timeout for Configure command for SDP, CSP and MCCS Leaf Nodes."""
import json

import pytest
from assertpy import assert_that
from ska_control_model import ObsState, ResultCode
from ska_tango_testing.integration import TangoEventTracer, log_events
from tango import DevState

from tests.resources.test_harness.central_node_low import CentralNodeWrapperLow

# low_csp_subarray_leaf_node, low_sdp_subarray_leaf_node,
# mccs_subarray_leaf_node
from tests.resources.test_harness.constant import (
    INTERMEDIATE_CONFIGURING_STATE_DEFECT,
    TIMEOUT,
)
from tests.resources.test_harness.helpers import set_receive_address
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


class TestConfigureTimeout:
    """Tests for testing timeout for Configure command on LOW TMC."""

    @pytest.mark.SKA_low
    def test_configure_timeout_csp_ln(
        self,
        central_node_low: CentralNodeWrapperLow,
        subarray_node_low: SubarrayNodeWrapperLow,
        event_tracer: TangoEventTracer,
        simulator_factory: SimulatorFactory,
        command_input_factory: JsonFactory,
    ):
        """Test timeout on CSP Leaf Nodes for Configure command by inducing
        fault into the system."""
        csp_subarray_sim = simulator_factory.get_or_create_simulator_device(
            SimulatorDeviceType.LOW_CSP_DEVICE
        )
        # Event Subscriptions
        event_tracer.subscribe_event(subarray_node_low.subarray_node, "State")
        event_tracer.subscribe_event(
            subarray_node_low.subarray_node, "obsState"
        )
        event_tracer.subscribe_event(
            subarray_node_low.subarray_node, "longRunningCommandResult"
        )
        event_tracer.subscribe_event(
            central_node_low.central_node, "longRunningCommandResult"
        )
        event_tracer.subscribe_event(
            central_node_low.central_node, "telescopeState"
        )
        # Preparing input files
        assign_input_str = prepare_json_args_for_centralnode_commands(
            "assign_resources_low", command_input_factory
        )
        configure_input_str = prepare_json_args_for_commands(
            "configure_low", command_input_factory
        )
        log_events(
            {
                central_node_low.central_node: [
                    "longRunningCommandResult",
                    "telescopeState",
                ],
                subarray_node_low.subarray_node: [
                    "longRunningCommandResult",
                    "obsState",
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
        set_receive_address(central_node_low)
        _, unique_id = central_node_low.store_resources(assign_input_str)
        assert_that(event_tracer).described_as(
            "FAILED ASSUMPTION AFTER ASSIGN RESOURCES: "
            "Subarray Node device"
            f"({subarray_node_low.subarray_node.dev_name()}) "
            "is expected to be in IDLE obstate",
        ).within_timeout(TIMEOUT).has_change_event_occurred(
            subarray_node_low.subarray_node,
            "obsState",
            ObsState.IDLE,
        )
        # Inducing Fault
        csp_subarray_sim.SetDefective(INTERMEDIATE_CONFIGURING_STATE_DEFECT)

        _, unique_id = subarray_node_low.execute_transition(
            "Configure", configure_input_str
        )
        assert_that(event_tracer).described_as(
            "FAILED ASSUMPTION AFTER CONFIGURE COMMAND: "
            "Subarray Node device"
            f"({subarray_node_low.subarray_node.dev_name()}) "
            "is expected to be in FAULT obstate",
        ).within_timeout(TIMEOUT).has_change_event_occurred(
            subarray_node_low.subarray_node,
            "obsState",
            ObsState.FAULT,
        )
        exception_message = "Timeout has occurred, command failed"

        assert_that(event_tracer).described_as(
            "FAILED ASSUMPTION AFTER CONFIGURE COMMAND: "
            "Subarray Node device"
            f"({subarray_node_low.subarray_node.dev_name()}) "
            "is expected have longRunningCommandResult"
            "(ResultCode.FAILED,exception)",
        ).within_timeout(
            TIMEOUT
        ).has_desired_result_code_message_in_lrcr_event(
            subarray_node_low.subarray_node,
            [exception_message],
            unique_id[0],
            ResultCode.FAILED,
        )

    def test_configure_timeout_sdp_ln(
        self,
        central_node_low: CentralNodeWrapperLow,
        subarray_node_low: SubarrayNodeWrapperLow,
        event_tracer: TangoEventTracer,
        command_input_factory: JsonFactory,
        simulator_factory: SimulatorFactory,
    ):
        """Test timeout on SDP Leaf Nodes for Configure command by inducing
        fault into the system."""
        # Event Subscriptions
        event_tracer.subscribe_event(subarray_node_low.subarray_node, "State")
        event_tracer.subscribe_event(
            subarray_node_low.subarray_node, "obsState"
        )
        event_tracer.subscribe_event(
            subarray_node_low.subarray_node, "longRunningCommandResult"
        )
        event_tracer.subscribe_event(
            central_node_low.central_node, "longRunningCommandResult"
        )
        event_tracer.subscribe_event(
            central_node_low.central_node, "telescopeState"
        )
        sdp_sim = simulator_factory.get_or_create_simulator_device(
            SimulatorDeviceType.LOW_SDP_DEVICE
        )
        # Preparing input files
        assign_input_str = prepare_json_args_for_centralnode_commands(
            "assign_resources_low", command_input_factory
        )
        configure_input_str = prepare_json_args_for_commands(
            "configure_low", command_input_factory
        )
        log_events(
            {
                central_node_low.central_node: [
                    "longRunningCommandResult",
                    "telescopeState",
                ],
                subarray_node_low.subarray_node: [
                    "longRunningCommandResult",
                    "obsState",
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

        _, unique_id = central_node_low.store_resources(assign_input_str)
        assert_that(event_tracer).described_as(
            "FAILED ASSUMPTION AFTER ASSIGNRESOURCES COMMAND: "
            "Subarray Node device"
            f"({central_node_low.subarray_node.dev_name()}) "
            "is expected to be in IDLE obstate",
        ).within_timeout(TIMEOUT).has_change_event_occurred(
            central_node_low.subarray_node,
            "obsState",
            ObsState.IDLE,
        )
        sdp_sim.SetDelayInfo(json.dumps({"Configure": 55}))
        _, unique_id = subarray_node_low.execute_transition(
            "Configure", configure_input_str
        )
        assert_that(event_tracer).described_as(
            "FAILED ASSUMPTION AFTER CONFIGURE COMMAND: "
            "Subarray Node device"
            f"({subarray_node_low.subarray_node.dev_name()}) "
            "is expected to be in FAULT obstate",
        ).within_timeout(TIMEOUT).has_change_event_occurred(
            subarray_node_low.subarray_node,
            "obsState",
            ObsState.FAULT,
        )
        exception_message = "Timeout has occurred, command failed"
        sdp_ln_timeout_exception = (
            "Exception occurred on the following "
            f"devices: {subarray_node_low.sdp_subarray_leaf_node.dev_name()}"
        )
        assert_that(event_tracer).described_as(
            "FAILED ASSUMPTION AFTER CONFIGURE COMMAND: "
            "Subarray Node device"
            f"({subarray_node_low.subarray_node.dev_name()}) "
            "is expected have longRunningCommandResult"
            "(ResultCode.FAILED,exception)",
        ).within_timeout(52).has_desired_result_code_message_in_lrcr_event(
            subarray_node_low.subarray_node,
            [exception_message, sdp_ln_timeout_exception],
            unique_id[0],
            ResultCode.FAILED,
        )
        sdp_sim.ResetDelayInfo()

    @pytest.mark.SKA_low
    def test_configure_timeout_mccs_ln(
        self,
        central_node_low: CentralNodeWrapperLow,
        subarray_node_low: SubarrayNodeWrapperLow,
        event_tracer: TangoEventTracer,
        simulator_factory: SimulatorFactory,
        command_input_factory: JsonFactory,
    ):
        """Test timeout on Mccs Leaf Nodes for Configure command by inducing
        fault into the system."""
        mccs_subarray_sim = simulator_factory.get_or_create_simulator_device(
            SimulatorDeviceType.MCCS_SUBARRAY_DEVICE
        )
        # Event Subscriptions
        event_tracer.subscribe_event(
            central_node_low.central_node, "longRunningCommandResult"
        )
        event_tracer.subscribe_event(
            central_node_low.central_node, "telescopeState"
        )
        event_tracer.subscribe_event(
            subarray_node_low.subarray_node, "obsState"
        )
        event_tracer.subscribe_event(
            subarray_node_low.subarray_node, "longRunningCommandResult"
        )
        log_events(
            {
                central_node_low.central_node: [
                    "longRunningCommandResult",
                    "telescopeState",
                ],
                subarray_node_low.subarray_node: [
                    "longRunningCommandResult",
                    "obsState",
                ],
            }
        )
        # Preparing input files
        assign_input_str = prepare_json_args_for_centralnode_commands(
            "assign_resources_low", command_input_factory
        )
        configure_input_str = prepare_json_args_for_commands(
            "configure_low", command_input_factory
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

        # Inducing Fault
        mccs_subarray_sim.SetDefective(INTERMEDIATE_CONFIGURING_STATE_DEFECT)

        _, unique_id = subarray_node_low.execute_transition(
            "Configure", configure_input_str
        )
        assert_that(event_tracer).described_as(
            "FAILED ASSUMPTION AFTER CONFIGURE COMMAND: "
            "Subarray Node device"
            f"({subarray_node_low.subarray_node.dev_name()}) "
            "is expected to be in FAULT obstate",
        ).within_timeout(TIMEOUT).has_change_event_occurred(
            subarray_node_low.subarray_node,
            "obsState",
            ObsState.FAULT,
        )
        exception_message = "Timeout has occurred, command failed"
        assert_that(event_tracer).described_as(
            "FAILED ASSUMPTION AFTER CONFIGURE COMMAND: "
            "Subarray Node device"
            f"({subarray_node_low.subarray_node.dev_name()}) "
            "is expected have longRunningCommandResult"
            "(ResultCode.FAILED,exception)",
        ).within_timeout(
            TIMEOUT
        ).has_desired_result_code_message_in_lrcr_event(
            subarray_node_low.subarray_node,
            [exception_message],
            unique_id[0],
            ResultCode.FAILED,
        )

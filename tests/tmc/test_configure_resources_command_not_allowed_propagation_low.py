"""Test cases for Configure Command not allowed for LOW."""


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
)
from tests.resources.test_harness.simulator_factory import SimulatorFactory
from tests.resources.test_harness.subarray_node_low import (
    SubarrayNodeWrapperLow,
)
from tests.resources.test_harness.utils.common_utils import JsonFactory
from tests.resources.test_harness.utils.enums import SimulatorDeviceType
from tests.resources.test_support.common_utils.result_code import ResultCode
from tests.resources.test_support.common_utils.tmc_helpers import (
    prepare_json_args_for_centralnode_commands,
    prepare_json_args_for_commands,
)


class TestConfigureCommandNotAllowedPropagation:
    """Test the command not allowed error propagation for configure
    command for TMC."""

    @pytest.mark.SKA_low
    def test_configure_command_not_allowed_propagation_csp_ln_low(
        self,
        central_node_low: CentralNodeWrapperLow,
        subarray_node_low: SubarrayNodeWrapperLow,
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
            subarray_node_low.subarray_node, "longRunningCommandResult"
        )
        event_tracer.subscribe_event(
            subarray_node_low.subarray_node, "obsState"
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

        # Preparing input files
        configure_input_str = prepare_json_args_for_commands(
            "configure_low", command_input_factory
        )
        # Inducing Fault
        #
        # Setting Defects on Devices
        csp_subarray_sim.SetDefective(COMMAND_NOT_ALLOWED_DEFECT)

        _, pytest.unique_id = subarray_node_low.execute_transition(
            "Configure", configure_input_str
        )
        assert_that(event_tracer).described_as(
            'FAILED ASSUMPTION IN "WHEN" STEP: '
            '"Configure command is invoked on a defective CSP Subarray"'
            "Subarray Node device"
            f"({subarray_node_low.subarray_node.dev_name()}) "
            "is expected to be in FAULT obstate",
        ).within_timeout(TIMEOUT).has_change_event_occurred(
            subarray_node_low.subarray_node,
            "obsState",
            ObsState.IDLE,
        )

        exception_message = (
            " The invocation of the Configure command failed on Csp "
            + "Subarray Device low-csp/subarray/01"
        )

        log_events(
            {subarray_node_low.subarray_node: ["longRunningCommandResult"]}
        )

        assert_that(event_tracer).described_as(
            "FAILED ASSUMPTION AFTER CONFIGURE: "
            f"({subarray_node_low.subarray_node.dev_name()}) "
            "is expected have longRunningCommandResult"
            "(ResultCode.FAILED,exception)",
        ).within_timeout(
            TIMEOUT
        ).has_desired_result_code_message_in_lrcr_event(
            subarray_node_low.subarray_node,
            [exception_message],
            pytest.unique_id[0],
            ResultCode.FAILED,
        )

    @pytest.mark.SKA_low
    def test_configure_command_not_allowed_propagation_sdp_ln_low(
        self,
        central_node_low: CentralNodeWrapperLow,
        subarray_node_low: SubarrayNodeWrapperLow,
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
            central_node_low.central_node, "longRunningCommandResult"
        )

        event_tracer.subscribe_event(
            subarray_node_low.subarray_node, "longRunningCommandResult"
        )
        event_tracer.subscribe_event(
            subarray_node_low.subarray_node, "obsState"
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

        # Preparing input files
        configure_input_str = prepare_json_args_for_commands(
            "configure_low", command_input_factory
        )
        # Inducing Fault
        #
        # Setting Defects on Devices
        sdp_subarray_sim.SetDefective(COMMAND_NOT_ALLOWED_DEFECT)

        _, pytest.unique_id = subarray_node_low.execute_transition(
            "Configure", configure_input_str
        )
        assert_that(event_tracer).described_as(
            'FAILED ASSUMPTION IN "WHEN" STEP: '
            '"Configure command is invoked on a defective SDP Subarray"'
            "Subarray Node device"
            f"({subarray_node_low.subarray_node.dev_name()}) "
            "is expected to be in FAULT obstate",
        ).within_timeout(TIMEOUT).has_change_event_occurred(
            subarray_node_low.subarray_node,
            "obsState",
            ObsState.IDLE,
        )

        exception_message = (
            f"Exception occurred on the following devices:"
            f" {low_sdp_subarray_leaf_node}:"
            " ska_tmc_common.exceptions.CommandNotAllowed:"
            " Command is not allowed and Recovery Successful, "
            "Subarray transitioned back to IDLE"
        )

        log_events(
            {subarray_node_low.subarray_node: ["longRunningCommandResult"]}
        )

        assert_that(event_tracer).described_as(
            "FAILED ASSUMPTION AFTER CONFIGURE: "
            f"({subarray_node_low.subarray_node.dev_name()}) "
            "is expected have longRunningCommandResult"
            "(ResultCode.FAILED,exception)",
        ).within_timeout(
            TIMEOUT
        ).has_desired_result_code_message_in_lrcr_event(
            subarray_node_low.subarray_node,
            [exception_message],
            pytest.unique_id[0],
            ResultCode.FAILED,
        )

    @pytest.mark.SKA_low
    def test_configure_command_not_allowed_propagation_mccs_ln_low(
        self,
        central_node_low: CentralNodeWrapperLow,
        subarray_node_low: SubarrayNodeWrapperLow,
        event_tracer: TangoEventTracer,
        simulator_factory: SimulatorFactory,
        command_input_factory: JsonFactory,
    ):
        """Verify command not allowed exception propagation from MCCSLeafNodes
        ."""

        mccs_subarray_sim = simulator_factory.get_or_create_simulator_device(
            SimulatorDeviceType.MCCS_SUBARRAY_DEVICE
        )

        # Event Subscriptions
        event_tracer.subscribe_event(
            central_node_low.central_node, "telescopeState"
        )
        event_tracer.subscribe_event(
            central_node_low.central_node, "longRunningCommandResult"
        )

        event_tracer.subscribe_event(
            subarray_node_low.subarray_node, "longRunningCommandResult"
        )
        event_tracer.subscribe_event(
            subarray_node_low.subarray_node, "obsState"
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

        # Preparing input files
        configure_input_str = prepare_json_args_for_commands(
            "configure_low", command_input_factory
        )
        # Inducing Fault
        #
        # Setting Defects on Devices
        mccs_subarray_sim.SetDefective(COMMAND_NOT_ALLOWED_DEFECT)

        _, pytest.unique_id = subarray_node_low.execute_transition(
            "Configure", configure_input_str
        )
        assert_that(event_tracer).described_as(
            'FAILED ASSUMPTION IN "WHEN" STEP: '
            '"Configure command is invoked on a defective MCCS Subarray"'
            "Subarray Node device"
            f"({subarray_node_low.subarray_node.dev_name()}) "
            "is expected to be in FAULT obstate",
        ).within_timeout(TIMEOUT).has_change_event_occurred(
            subarray_node_low.subarray_node,
            "obsState",
            ObsState.IDLE,
        )

        exception_message = (
            "The invocation of the Configure command is"
            " failed on MCCS Subarray device"
            " low-mccs/subarray/01."
        )

        log_events(
            {subarray_node_low.subarray_node: ["longRunningCommandResult"]}
        )

        assert_that(event_tracer).described_as(
            "FAILED ASSUMPTION AFTER CONFIGURE: "
            f"({subarray_node_low.subarray_node.dev_name()}) "
            "is expected have longRunningCommandResult"
            "(ResultCode.FAILED,exception)",
        ).within_timeout(
            TIMEOUT
        ).has_desired_result_code_message_in_lrcr_event(
            subarray_node_low.subarray_node,
            [exception_message],
            pytest.unique_id[0],
            ResultCode.FAILED,
        )

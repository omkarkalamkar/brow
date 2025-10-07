"""
This module contains test cases for the low-level CentralNode functionality
related to the AssignResources command.It utilizes the pytest framework and
mocks certain components for testing purposes.
The test cases cover various scenarios, including the successful execution of
the AssignResources command,
verification of attribute updates, exception handling, and proper propagation
of exceptions.
"""
import json
import time

import pytest
from assertpy import assert_that
from ska_control_model import ObsState
from ska_tango_base.commands import ResultCode
from ska_tango_testing.integration import TangoEventTracer, log_events
from tango import DevState

from tests.resources.test_harness.central_node_low import CentralNodeWrapperLow
from tests.resources.test_harness.constant import tmc_low_subarraynode1
from tests.resources.test_harness.helpers import (
    generate_and_get_assign_resource_json,
    update_assign_json_with_empty_values,
)
from tests.resources.test_harness.simulator_factory import SimulatorFactory
from tests.resources.test_harness.utils.common_utils import JsonFactory
from tests.resources.test_harness.utils.enums import SimulatorDeviceType
from tests.resources.test_support.common_utils.tmc_helpers import (
    prepare_json_args_for_centralnode_commands,
)
from tests.resources.test_support.constant_low import (
    INTERMEDIATE_STATE_DEFECT,
    RESET_DEFECT,
    TIMEOUT,
)


class TestLowCentralNodeAssignResources:
    """TMC CentralNode Assign Resources by checking the state transitions of
    simulated master devices (CSP, SDP, MCCS) and the overall
      telescope state."""

    @pytest.mark.SKA_low
    def test_low_centralnode_assign_resources(
        self,
        central_node_low: CentralNodeWrapperLow,
        event_tracer: TangoEventTracer,
        simulator_factory: SimulatorFactory,
        command_input_factory: JsonFactory,
    ):
        """
        Test to verify transitions that are triggered by AssignResources
        command and followed by a completion transition
        assuming that external subsystems work fine.
        """
        assign_input_json = prepare_json_args_for_centralnode_commands(
            "assign_resources_low", command_input_factory
        )

        release_resource_json = prepare_json_args_for_centralnode_commands(
            "release_resources_low", command_input_factory
        )

        assigned_resources_json = generate_and_get_assign_resource_json(
            assign_input_json
        )

        assigned_resources_json_empty = update_assign_json_with_empty_values(
            assign_input_json
        )

        csp_subarray_sim = simulator_factory.get_or_create_simulator_device(
            SimulatorDeviceType.LOW_CSP_DEVICE
        )
        sdp_subarray_sim = simulator_factory.get_or_create_simulator_device(
            SimulatorDeviceType.LOW_SDP_DEVICE
        )
        mccs_controller_sim = simulator_factory.get_or_create_simulator_device(
            SimulatorDeviceType.MCCS_MASTER_DEVICE
        )

        mccs_subarray_sim = simulator_factory.get_or_create_simulator_device(
            SimulatorDeviceType.MCCS_SUBARRAY_DEVICE
        )

        event_tracer.subscribe_event(csp_subarray_sim, "State")
        event_tracer.subscribe_event(sdp_subarray_sim, "State")
        event_tracer.subscribe_event(mccs_controller_sim, "State")
        event_tracer.subscribe_event(
            central_node_low.central_node, "telescopeState"
        )
        event_tracer.subscribe_event(csp_subarray_sim, "obsState")
        event_tracer.subscribe_event(sdp_subarray_sim, "obsState")
        event_tracer.subscribe_event(mccs_subarray_sim, "obsState")
        event_tracer.subscribe_event(
            central_node_low.subarray_node, "obsState"
        )
        event_tracer.subscribe_event(
            central_node_low.subarray_node, "assignedResources"
        )
        event_tracer.subscribe_event(
            central_node_low.central_node, "longRunningCommandResult"
        )
        log_events(
            {
                central_node_low.central_node: [
                    "longRunningCommandResult",
                    "telescopeState",
                ],
                central_node_low.subarray_node: [
                    "obsState",
                    "assignedResources",
                ],
            }
        )
        # Execute ON Command
        central_node_low.move_to_on()

        assert_that(event_tracer).described_as(
            "FAILED ASSUMPTION AFTER STANDBY COMMAND: "
            "SDP Subarray device"
            f"({csp_subarray_sim.dev_name()}) "
            "is expected to be in State ON",
        ).within_timeout(TIMEOUT).has_change_event_occurred(
            csp_subarray_sim,
            "State",
            DevState.ON,
        )
        assert_that(event_tracer).described_as(
            "FAILED ASSUMPTION AFTER STANDBY COMMAND: "
            "MCCS Controller device"
            f"({sdp_subarray_sim.dev_name()}) "
            "is expected to be in State ON",
        ).within_timeout(TIMEOUT).has_change_event_occurred(
            mccs_controller_sim,
            "State",
            DevState.ON,
        )
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

        # Execute Assign command and check command completed successfully
        _, unique_id = central_node_low.perform_action(
            "AssignResources", assign_input_json
        )

        mccs_subarray_sim.SetDirectassignedResources(assigned_resources_json)

        assert_that(event_tracer).described_as(
            "FAILED ASSUMPTION AFTER ASSIGNRESOURCES COMMAND: "
            "SDP Subarray device"
            f"({sdp_subarray_sim.dev_name()}) "
            "is expected to be in IDLE obstate",
        ).within_timeout(TIMEOUT).has_change_event_occurred(
            sdp_subarray_sim,
            "obsState",
            ObsState.IDLE,
        )
        assert_that(event_tracer).described_as(
            "FAILED ASSUMPTION AFTER ASSIGNRESOURCES COMMAND: "
            "CSP Subarray device"
            f"({csp_subarray_sim.dev_name()}) "
            "is expected to be in IDLE obstate",
        ).within_timeout(TIMEOUT).has_change_event_occurred(
            csp_subarray_sim,
            "obsState",
            ObsState.IDLE,
        )
        assert_that(event_tracer).described_as(
            "FAILED ASSUMPTION AFTER ASSIGNRESOURCES COMMAND: "
            "MCCS Subarray device"
            f"({mccs_subarray_sim.dev_name()}) "
            "is expected to be in IDLE obstate",
        ).within_timeout(TIMEOUT).has_change_event_occurred(
            mccs_subarray_sim,
            "obsState",
            ObsState.IDLE,
        )
        assert_that(event_tracer).described_as(
            "FAILED ASSUMPTION AFTER ASSIGN RESOURCES: "
            "Subarray Node device"
            f"({central_node_low.subarray_node.dev_name()}) "
            "is expected to be in IDLE obstate",
        ).within_timeout(TIMEOUT).has_change_event_occurred(
            central_node_low.subarray_node,
            "obsState",
            ObsState.IDLE,
        )
        assert_that(event_tracer).described_as(
            "FAILED ASSUMPTION AFTER ASSIGNRESOURCES COMMAND: "
            "Central Node device"
            f"({central_node_low.central_node.dev_name()}) "
            "is expected have longRunningCommand as"
            '(unique_id,(ResultCode.OK,"Command Completed"))',
        ).within_timeout(TIMEOUT).has_change_event_occurred(
            central_node_low.central_node,
            "longRunningCommandResult",
            (
                unique_id[0],
                json.dumps((int(ResultCode.OK), "Command Completed")),
            ),
        )

        assert_that(event_tracer).described_as(
            "FAILED ASSUMPTION AFTER ASSIGN RESOURCES: "
            "Subarray Node device"
            f"({central_node_low.subarray_node.dev_name()}) "
            "is expected to have assignedResources input json",
        ).within_timeout(TIMEOUT).has_change_event_occurred(
            central_node_low.subarray_node,
            "assignedResources",
            (str(assigned_resources_json),),
        )

        # Execute release command and verify command completed successfully

        _, unique_id = central_node_low.perform_action(
            "ReleaseResources", release_resource_json
        )
        assert_that(event_tracer).described_as(
            "FAILED ASSUMPTION AFTER RELEASE_RESOURCES COMMAND: "
            "SDP Subarray device"
            f"({sdp_subarray_sim.dev_name()}) "
            "is expected to be in EMPTY obstate",
        ).within_timeout(TIMEOUT).has_change_event_occurred(
            sdp_subarray_sim,
            "obsState",
            ObsState.EMPTY,
        )
        assert_that(event_tracer).described_as(
            "FAILED ASSUMPTION AFTER RELEASE_RESOURCES COMMAND: "
            "CSP Subarray device"
            f"({csp_subarray_sim.dev_name()}) "
            "is expected to be in EMPTY obstate",
        ).within_timeout(TIMEOUT).has_change_event_occurred(
            csp_subarray_sim,
            "obsState",
            ObsState.EMPTY,
        )
        assert_that(event_tracer).described_as(
            "FAILED ASSUMPTION AFTER RELEASE_RESOURCES COMMAND: "
            "MCCS Subarray device"
            f"({mccs_subarray_sim.dev_name()}) "
            "is expected to be in EMPTY obstate",
        ).within_timeout(TIMEOUT).has_change_event_occurred(
            mccs_subarray_sim,
            "obsState",
            ObsState.EMPTY,
        )
        assert_that(event_tracer).described_as(
            "FAILED ASSUMPTION AFTER RELEASE_RESOURCES COMMAND: "
            "Subarray Node device"
            f"({central_node_low.subarray_node.dev_name()}) "
            "is expected to be in EMPTY obstate",
        ).within_timeout(TIMEOUT).has_change_event_occurred(
            central_node_low.subarray_node,
            "obsState",
            ObsState.EMPTY,
        )
        assert_that(event_tracer).described_as(
            "FAILED ASSUMPTION AFTER RELEASE_RESOURCES COMMAND: "
            "Central Node device"
            f"({central_node_low.central_node.dev_name()}) "
            "is expected have longRunningCommand as"
            '(unique_id,(ResultCode.OK,"Command Completed"))',
        ).within_timeout(TIMEOUT).has_change_event_occurred(
            central_node_low.central_node,
            "longRunningCommandResult",
            (
                unique_id[0],
                json.dumps((int(ResultCode.OK), "Command Completed")),
            ),
        )

        # Setting Assigned Resources empty

        mccs_subarray_sim.SetDirectassignedResources(
            assigned_resources_json_empty
        )
        assert_that(event_tracer).described_as(
            "FAILED ASSUMPTION AFTER RELEASE_RESOURCES COMMAND: "
            "Subarray Node device"
            f"({central_node_low.subarray_node.dev_name()}) "
            "is expected assignedResources to be empty",
        ).within_timeout(TIMEOUT).has_change_event_occurred(
            central_node_low.subarray_node,
            "assignedResources",
            (str(assigned_resources_json_empty),),
        )

    @pytest.mark.SKA_low
    def test_low_centralnode_assign_resources_exception_propagation(
        self,
        central_node_low: CentralNodeWrapperLow,
        event_tracer: TangoEventTracer,
        simulator_factory: SimulatorFactory,
        command_input_factory: JsonFactory,
    ):
        """
        Test to verify the exception received on longRunningCommandResult
        attribute when AssignResources command in invoked on CentralNode.

        Glossary:
        - "central_node_low": fixture for a TMC CentralNode Low under test
        which provides simulated master devices
        - "event_recorder": fixture for a MockTangoEventCallbackGroup
        for validating the subscribing and receiving events.
        - "simulator_factory": fixture for creating simulator devices for
        low Telescope respectively.
        - "command_input_factory": fixture for JsonFactory class,
        which provides json files for CentralNode
        """
        assign_input_json = prepare_json_args_for_centralnode_commands(
            "assign_resources_low", command_input_factory
        )
        mccs_subarray_sim = simulator_factory.get_or_create_simulator_device(
            SimulatorDeviceType.MCCS_SUBARRAY_DEVICE
        )

        event_tracer.subscribe_event(
            central_node_low.central_node, "telescopeState"
        )
        event_tracer.subscribe_event(
            central_node_low.subarray_node, "obsState"
        )
        event_tracer.subscribe_event(
            central_node_low.central_node, "longRunningCommandResult"
        )
        log_events(
            {
                central_node_low.central_node: [
                    "longRunningCommandResult",
                    "telescopeState",
                ],
                central_node_low.subarray_node: ["obsState"],
            }
        )
        # Execute ON Command
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
        # Setting device to defective

        mccs_subarray_sim.SetDefective(json.dumps(INTERMEDIATE_STATE_DEFECT))
        # Execute Assign command and check command completed successfully
        _, unique_id = central_node_low.perform_action(
            "AssignResources", assign_input_json
        )

        exception_message = (
            f"{tmc_low_subarraynode1}:"
            " Timeout has "
            "occurred, command failed"
        )

        assert_that(event_tracer).described_as(
            "FAILED ASSUMPTION AFTER ASSIGN_RESOURCES COMMAND: "
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
            "FAILED ASSUMPTION AFTER ASSIGN_RESOURCES COMMAND: "
            "Subarray Node device"
            f"({central_node_low.subarray_node.dev_name()}) "
            "is expected to be in FAULT obstate",
        ).within_timeout(TIMEOUT).has_change_event_occurred(
            central_node_low.subarray_node,
            "obsState",
            ObsState.FAULT,
        )

        mccs_subarray_sim.setDefective(json.dumps(RESET_DEFECT))

    @pytest.mark.skip("TBD")
    @pytest.mark.SKA_low
    def test_low_centralnode_release_resources_exception_propagation(
        self,
        central_node_low: CentralNodeWrapperLow,
        event_tracer: TangoEventTracer,
        simulator_factory: SimulatorFactory,
        command_input_factory: JsonFactory,
    ):
        """
        Test to verify the exception received on longRunningCommandResult
        attribute when AssignResources command in invoked on CentralNode.

        Glossary:
        - "central_node_low": fixture for a TMC CentralNode Low under test
        which provides simulated master devices
        - "event_recorder": fixture for a MockTangoEventCallbackGroup
        for validating the subscribing and receiving events.
        - "simulator_factory": fixture for creating simulator devices for
        low Telescope respectively.
        - "command_input_factory": fixture for JsonFactory class,
        which provides json files for CentralNode
        """
        assign_input_json = prepare_json_args_for_centralnode_commands(
            "assign_resources_low", command_input_factory
        )
        release_resource_json = prepare_json_args_for_centralnode_commands(
            "release_resources_low", command_input_factory
        )
        sdp_subarray_sim = simulator_factory.get_or_create_simulator_device(
            SimulatorDeviceType.LOW_SDP_DEVICE
        )

        event_tracer.subscribe_event(
            central_node_low.central_node, "telescopeState"
        )
        event_tracer.subscribe_event(
            central_node_low.subarray_node, "obsState"
        )
        event_tracer.subscribe_event(
            central_node_low.central_node,
            "longRunningCommandResult",
        )
        log_events(
            {
                central_node_low.central_node: [
                    "longRunningCommandResult",
                    "telescopeState",
                ],
                central_node_low.subarray_node: ["obsState"],
            }
        )
        # Execute ON Command and verify successful execution
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

        # Execute Assign command and verify successful execution
        _, unique_id = central_node_low.perform_action(
            "AssignResources", assign_input_json
        )
        assert_that(event_tracer).described_as(
            "FAILED ASSUMPTION AFTER ASSIGN RESOURCES: "
            "Subarray Node device"
            f"({central_node_low.subarray_node.dev_name()}) "
            "is expected to be in IDLE obstate",
        ).within_timeout(TIMEOUT).has_change_event_occurred(
            central_node_low.subarray_node,
            "obsState",
            ObsState.IDLE,
        )
        assert_that(event_tracer).described_as(
            "FAILED ASSUMPTION AFTER RELEASE_RESOURCES COMMAND: "
            "Central Node device"
            f"({central_node_low.central_node.dev_name()}) "
            "is expected have longRunningCommand as"
            '(unique_id,(ResultCode.OK,"Command Completed"))',
        ).within_timeout(TIMEOUT).has_change_event_occurred(
            central_node_low.central_node,
            "longRunningCommandResult",
            (
                unique_id[0],
                json.dumps((int(ResultCode.OK), "Command Completed")),
            ),
        )

        # Allowing Subarray Node to finish processing the Assign command
        # completion. Removing the sleep leads to timer thread for Release
        # being stopped by Assign cleanup
        time.sleep(1)

        # Setting device to defective
        sdp_subarray_sim.SetDelayInfo(json.dumps({"ReleaseAllResources": 55}))

        _, unique_id = central_node_low.perform_action(
            "ReleaseResources", release_resource_json
        )

        exception_message = (
            f"{central_node_low.sdp_subarray_leaf_node.dev_name()}:"
            " Timeout has occurred, command failed"
        )

        assert_that(event_tracer).described_as(
            "FAILED ASSUMPTION AFTER ASSIGN_RESOURCES COMMAND: "
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
            "FAILED ASSUMPTION AFTER RELEASE_RESOURCES COMMAND: "
            "Subarray Node device"
            f"({central_node_low.subarray_node.dev_name()}) "
            "is expected to be in FAULT obstate",
        ).within_timeout(TIMEOUT).has_change_event_occurred(
            central_node_low.subarray_node,
            "obsState",
            ObsState.FAULT,
        )
        sdp_subarray_sim.ResetDelayInfo()

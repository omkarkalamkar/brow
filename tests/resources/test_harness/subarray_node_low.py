import json
import logging
from time import sleep

from assertpy import assert_that
from ska_control_model import AdminMode, ObsState
from ska_ser_logging import configure_logging
from ska_tango_base.control_model import HealthState
from ska_tango_testing.integration import TangoEventTracer
from tango import DeviceProxy, DevState

from tests.resources.test_harness.constant import (
    device_dict_low,
    low_centralnode,
    low_csp_master,
    low_csp_subarray1,
    low_csp_subarray_leaf_node,
    low_sdp_master,
    low_sdp_subarray1,
    low_sdp_subarray_leaf_node,
    mccs_subarray1,
    mccs_subarray_leaf_node,
    quality_monitor1,
    tmc_low_subarraynode1,
)
from tests.resources.test_harness.event_recorder import EventRecorder
from tests.resources.test_harness.helpers import (
    check_subarray_obs_state,
    get_device_dict,
    update_eb_pb_ids,
    wait_for_partial_or_complete_abort,
)
from tests.resources.test_harness.utils.common_utils import JsonFactory
from tests.resources.test_harness.utils.constant import (
    ABORTED,
    IDLE,
    ON,
    READY,
)
from tests.resources.test_harness.utils.enums import SubarrayObsState
from tests.resources.test_harness.utils.obs_state_resetter_low import (
    ObsStateResetterFactory,
)
from tests.resources.test_harness.utils.sync_decorators import (
    sync_abort,
    sync_assign_resources,
    sync_configure,
    sync_end,
    sync_endscan,
    sync_release_resources,
    sync_restart,
)
from tests.resources.test_support.common_utils.common_helpers import Resource

TIMEOUT = 100

configure_logging(logging.DEBUG)
LOGGER = logging.getLogger(__name__)
RFC_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"
device_dict = {
    # TODO use this as as list when multiple subarray considered in testing
    "sdp_subarray": low_sdp_subarray1,
    "csp_subarray": low_csp_subarray1,
    "csp_master": low_csp_master,
    "tmc_subarraynode": tmc_low_subarraynode1,
    "sdp_master": low_sdp_master,
    "centralnode": low_centralnode,
    "mccs_subarray1": mccs_subarray1,
    "csp_subarray_leaf_node": low_csp_subarray_leaf_node,
    "sdp_subarray_leaf_node": low_sdp_subarray_leaf_node,
    "mccs_subarray_leaf_node": mccs_subarray_leaf_node,
    "mccs_subarray": mccs_subarray1,
}


class SubarrayNodeWrapperLow:
    """Subarray Node Low class which implement methods required for test cases
    to test subarray node.
    """

    def __init__(self) -> None:
        self.tmc_subarraynode1 = tmc_low_subarraynode1
        self.central_node = DeviceProxy(low_centralnode)
        self.subarray_node = DeviceProxy(tmc_low_subarraynode1)
        # Set timeout to 5 sec.
        # Sometimes command timeout with default 3 sec time
        self.subarray_node.set_timeout_millis(5000)
        self.csp_subarray_leaf_node = DeviceProxy(low_csp_subarray_leaf_node)
        self.sdp_subarray_leaf_node = DeviceProxy(low_sdp_subarray_leaf_node)
        self.mccs_subarray_leaf_node = DeviceProxy(mccs_subarray_leaf_node)
        self._state = DevState.OFF
        self._obs_state = SubarrayObsState.EMPTY
        self.csp_subarray1 = DeviceProxy(low_csp_subarray1)
        self.sdp_subarray1 = DeviceProxy(low_sdp_subarray1)
        self.mccs_subarray1 = DeviceProxy(mccs_subarray1)
        self.quality_monitor = DeviceProxy(quality_monitor1)
        self.subarray_devices = {
            "csp_subarray": DeviceProxy(low_csp_subarray1),
            "sdp_subarray": DeviceProxy(low_sdp_subarray1),
            "mccs_subarray": DeviceProxy(mccs_subarray1),
        }
        self.json_factory = JsonFactory()
        self.release_input = (
            self.json_factory.create_centralnode_configuration(
                "release_resources_low"
            )
        )
        # Subarray state
        self.ON_STATE = ON
        self.IDLE_OBS_STATE = IDLE
        self.READY_OBS_STATE = READY
        self.ABORTED_OBS_STATE = ABORTED
        self.event_recorder = EventRecorder()
        self.device_dict = get_device_dict(int(self.get_subarray_id()))

    @property
    def state(self) -> DevState:
        """TMC SubarrayNode operational state"""
        self._state = Resource(self.tmc_subarraynode1).get("State")
        return self._state

    @state.setter
    def state(self, value):
        """Sets value for TMC subarrayNode operational state

        Args:
            value (DevState): operational state value
        """
        self._state = value

    @property
    def obs_state(self):
        """TMC SubarrayNode observation state"""
        self._obs_state = Resource(self.tmc_subarraynode1).get("obsState")
        return self._obs_state

    @obs_state.setter
    def obs_state(self, value):
        """Sets value for TMC subarrayNode observation state

        Args:
            value (DevState): observation state value
        """
        self._obs_state = value

    @property
    def health_state(self) -> HealthState:
        """Telescope health state representing overall health of telescope"""
        self._health_state = Resource(self.tmc_subarraynode1).get(
            "healthState"
        )
        return self._health_state

    @health_state.setter
    def health_state(self, value):
        """Telescope health state representing overall health of telescope

        Args:
            value (HealthState): telescope health state value
        """
        self._health_state = value

    @property
    def obs_state(self):
        """TMC SubarrayNode observation state"""
        self._obs_state = Resource(self.tmc_subarraynode1).get("obsState")
        return self._obs_state

    @obs_state.setter
    def obs_state(self, value):
        """Sets value for TMC subarrayNode observation state

        Args:
            value (DevState): observation state value
        """
        self._obs_state = value

    @sync_configure(device_dict=device_dict_low)
    def store_configuration_data(self, input_json: str):
        """Invoke configure command on subarray Node
        Args:
            input_string (str): config input json
        Returns:
            (result, message): result, message tuple
        """
        result, message = self.subarray_node.Configure(input_json)
        LOGGER.info("Invoked Configure on SubarrayNode")
        return result, message

    @sync_end(device_dict=device_dict_low)
    def end_observation(self):
        result, message = self.subarray_node.End()
        LOGGER.info("Invoked End on SubarrayNode")
        return result, message

    @sync_abort(device_dict=device_dict_low)
    def abort_subarray(self):
        evt_tracer = TangoEventTracer()
        evt_tracer.subscribe_event(
            self.subarray_node, "longRunningCommandResult"
        )
        LOGGER.info("SubarrayNode LRCR subscribed")
        result, message = self.subarray_node.Abort()
        LOGGER.info("ABORT RESULT and Message: %s, %s", result, message)
        LOGGER.info(
            "SubarrayNode LRCR %s", self.subarray_node.longRunningCommandResult
        )
        assert_that(evt_tracer).within_timeout(
            TIMEOUT
        ).has_change_event_occurred(
            self.subarray_node,
            "longRunningCommandResult",
            (message[0], '[0, "Abort command completed"]'),
        )

        LOGGER.info("Invoked Abort on SubarrayNode")
        return result, message

    @sync_restart(device_dict=device_dict_low)
    def restart_subarray(self):
        result, message = self.subarray_node.Restart()
        LOGGER.info("Invoked Restart on SubarrayNode")
        return result, message

    @sync_assign_resources(device_dict=device_dict_low)
    def store_resources(self, assign_json: str):
        """Invoke Assign Resource command on subarray Node
        Args:
            assign_json (str): Assign resource input json
        """
        result, message = self.central_node.AssignResources(assign_json)
        LOGGER.info("Invoked AssignResources on CentralNode")
        return result, message

    @sync_release_resources(device_dict=device_dict_low)
    def release_resources_subarray(self):
        result, message = self.subarray_node.ReleaseAllResources()
        LOGGER.info("Invoked Release Resource on SubarrayNode")
        return result, message

    @sync_release_resources(device_dict=device_dict_low)
    def release_resources(self, input_string):
        """Invoke Release Resource command on central Node
        Args:
            input_string (str): Release resource input json
        """
        result, message = self.central_node.ReleaseResources(input_string)
        return result, message

    @sync_endscan(device_dict=device_dict_low)
    def remove_scan_data(self):
        result, message = self.subarray_node.EndScan()
        LOGGER.info("Invoked EndScan on SubarrayNode")
        return result, message

    def store_scan_data(self, input_string):
        result, message = self.subarray_node.Scan(input_string)
        LOGGER.info("Invoked Scan on SubarrayNode")
        return result, message

    def execute_transition(self, command_name: str, argin=None):
        """Execute provided command on subarray
        Args:
            command_name (str): Name of command to execute
        """
        if command_name is not None:
            if argin:
                result, message = self.subarray_node.command_inout(
                    command_name, argin
                )
                LOGGER.info(
                    "Invoked %s on SubarrayNode with argin: %s",
                    command_name,
                    argin,
                )
                return result, message
            else:
                result, message = self.subarray_node.command_inout(
                    command_name
                )
                LOGGER.info("Invoked %s on SubarrayNode.", command_name)
                return result, message

    def set_subarray_id(self, requested_subarray_id: str) -> None:
        """This method creates subarray devices for the requested subarray
        id"""
        subarray_id = str(requested_subarray_id).zfill(2)
        self.subarray_node = DeviceProxy(f"low-tmc/subarray/{subarray_id}")
        self.subarray_devices = {
            "csp_subarray": DeviceProxy(f"low-csp/subarray/{subarray_id}"),
            "sdp_subarray": DeviceProxy(f"low-sdp/subarray/{subarray_id}"),
            "mccs_subarray": DeviceProxy(f"low-mccs/subarray/{subarray_id}"),
        }
        self.csp_subarray_leaf_node = DeviceProxy(
            f"low-tmc/subarray-leaf-node-csp/{subarray_id}"
        )
        self.sdp_subarray_leaf_node = DeviceProxy(
            f"low-tmc/subarray-leaf-node-sdp/{subarray_id}"
        )
        self.mccs_subarray_leaf_node = DeviceProxy(
            f"low-tmc/subarray-leaf-node-mccs/{subarray_id}"
        )
        if 0 < int(requested_subarray_id) < 3:
            self.quality_monitor = DeviceProxy(
                f"low-tmc/subarray-quality-monitor/{subarray_id}"
            )
        self.device_dict = get_device_dict(int(requested_subarray_id))

    def get_device_proxy(self, device_name: str) -> DeviceProxy:
        """Returns the device proxy for the given device name.

        Args:
            device_name (str): The name of the device for which the proxy is
            required.

        Returns:
            DeviceProxy: The device proxy corresponding to the given device
            name.
        """
        return DeviceProxy(self.device_dict.get(device_name))

    def move_to_on(self):
        """Move the Subarray to On State"""
        if self.csp_subarray1.adminMode != AdminMode.ONLINE:
            self.csp_subarray1.adminMode = AdminMode.ONLINE
        if self.sdp_subarray1.adminMode != AdminMode.ONLINE:
            self.sdp_subarray1.adminMode = AdminMode.ONLINE
        if self.mccs_subarray1.adminMode != AdminMode.ONLINE:
            self.mccs_subarray1.adminMode = AdminMode.ONLINE
        result, message = self.subarray_node.On()
        LOGGER.info("Invoked ON on SubarrayNode")
        return result, message

    def move_to_off(self):
        # Move Subarray to OFF state
        Resource(self.tmc_subarraynode1).assert_attribute("State").equals("ON")
        result, message = self.subarray_node.Off()
        LOGGER.info("Invoked OFF on SubarrayNode")
        return result, message

    def _reset_simulator_devices(self):
        """Reset Simulator devices to it's original state"""

        sim_device_proxy_list = [
            self.sdp_subarray1,
            self.csp_subarray1,
            self.mccs_subarray1,
        ]

        for sim_device_proxy in sim_device_proxy_list:
            sim_device_proxy.ResetDelayInfo()
            sim_device_proxy.SetDirectHealthState(HealthState.UNKNOWN)
            sim_device_proxy.SetDefective(json.dumps({"enabled": False}))

    def force_change_of_obs_state(
        self,
        dest_state_name: str,
        assign_input_json: str = "",
        configure_input_json: str = "",
        scan_input_json: str = "",
    ) -> None:
        """Forces a change in the SubarrayNode's obsState to the provided
          obsState.
        This method creates an ObsStateResetter object using the provided
        destination obsState name and resets the SubarrayNode's state
        accordingly.
        Args:
            dest_state_name (str): The destination obsState to set for the
              SubarrayNode.
            assign_input_json (str, optional): JSON input for assignment
            configuration.
            Defaults to an empty string.
            configure_input_json (str, optional): JSON input for configuration
             settings.
            Defaults to an empty string.
            scan_input_json (str, optional): JSON input for scan configuration.
                Defaults to an empty string.
        Returns:
            None: This method does not return any value.
        Raises:
            Any specific exceptions that might be raised during the reset
            process.
        """
        factory_obj = ObsStateResetterFactory()
        obs_state_resetter = factory_obj.create_obs_state_resetter(
            dest_state_name, self
        )
        if assign_input_json:
            assign_input_json = update_eb_pb_ids(assign_input_json)
            obs_state_resetter.assign_input = assign_input_json
        if configure_input_json:
            obs_state_resetter.configure_input = configure_input_json
        if scan_input_json:
            obs_state_resetter.scan_input = scan_input_json
        obs_state_resetter.reset()
        self._clear_command_call_and_transition_data()

    def clear_all_data(self):
        """Method to clear the observations
        and put the SubarrayNode in EMPTY"""
        if self.obs_state in [
            "IDLE",
            "RESOURCING",
            "READY",
            "CONFIGURING",
            "SCANNING",
        ]:
            self.abort_subarray()
            self.restart_subarray()
        elif self.obs_state == "ABORTED":
            self.restart_subarray()

    def _clear_command_call_and_transition_data(self, clear_transition=False):
        """Clears the command call data"""

        for sim_device in [
            self.sdp_subarray1,
            self.csp_subarray1,
            self.mccs_subarray1,
        ]:
            sim_device.ClearCommandCallInfo()
            if clear_transition:
                sim_device.ResetTransitions()

    def tear_down(self):
        """Tear down after each test run"""
        subarray_id = int(self.get_subarray_id())
        LOGGER.info("Calling Tear down for subarray %s", subarray_id)
        LOGGER.info(
            "Current Subarray Node ObsState is: %s",
            self.subarray_node.obsState,
        )

        self._reset_simulator_devices()
        self._clear_command_call_and_transition_data(clear_transition=True)

        if self.subarray_node.obsState in [
            ObsState.SCANNING,
            ObsState.CONFIGURING,
            ObsState.RESOURCING,
            ObsState.READY,
        ]:
            # Invoke Abort and Restart
            LOGGER.info("Invoking Abort on Subarray %s", subarray_id)
            self.execute_transition("Abort")
            wait_for_partial_or_complete_abort(subarray_id=subarray_id)
            self.restart_subarray()
        elif self.subarray_node.obsState in [ObsState.ABORTED, ObsState.FAULT]:
            # Invoke Restart
            LOGGER.info("Invoking Restart on Subarray %s", subarray_id)
            self.restart_subarray()
        elif self.subarray_node.obsState == ObsState.IDLE:
            # Invoke Release
            LOGGER.info("Invoking Release Resources on Subarray")
            self.release_resources(self.release_input)

        else:
            if self.subarray_node.obsstate != ObsState.EMPTY:
                self.force_change_of_obs_state("EMPTY")

        assert check_subarray_obs_state("EMPTY")
        # Move Subarray to OFF state
        self.move_to_off()
        # Adding a small sleep to allow the systems to clean up processes
        sleep(1)

    def tear_down_all_subarrays(self):
        """Tear down for all subarrays after each test run"""
        for subarray_id in range(1, 17):
            self.set_subarray_id(subarray_id)
            self.tear_down()

    def set_scan_id(self, scan_id: int, input_str: str) -> str:
        """
        Set the scan_id for the scan input JSON.

        This method updates the scan input JSON string with the provided
          scan_id.

        Parameters:
        ----------
        scan_id : int
            The scan ID to set in the JSON input.
        input_str : str
            The JSON input string representing scan data.

        Returns:
        -------
        str
            The updated JSON string with the new scan_id.

        Raises:
        ------
        Exception
            If there is an error while updating the scan_id in the JSON input.
        """
        input_json = json.loads(input_str)
        try:
            input_json["scan_id"] = scan_id
        except Exception as e:
            LOGGER.exception("Exception occurred while setting scan id: %s", e)
            raise
        return json.dumps(input_json)

    def get_subarray_id(self) -> str:
        """Returns current subarray id from the subarray_node device proxy."""

        subarray_node = self.subarray_node.dev_name()
        return f"{subarray_node[-2:]}"

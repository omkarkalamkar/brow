import copy
import json
import logging
import os
import time
import uuid
from typing import Any

import pytest
import tango
from ska_control_model import AdminMode, ObsState
from ska_ser_logging import configure_logging
from ska_tango_base.commands import ResultCode
from ska_tango_base.control_model import HealthState
from ska_tango_testing.mock.placeholders import Anything
from tango import DeviceProxy

from tests.resources.test_harness.constant import (
    INTERMEDIATE_CONFIGURING_OBS_STATE_DEFECT,
    INTERMEDIATE_STATE_DEFECT,
    low_csp_subarray1,
    low_csp_subarray_leaf_node,
    low_sdp_subarray1,
    low_sdp_subarray_leaf_node,
    mccs_controller,
    mccs_pasdbus_prefix,
    mccs_prefix,
    mccs_subarray1,
    mccs_subarray_leaf_node,
    tmc_low_subarraynode1,
)
from tests.resources.test_harness.event_recorder import EventRecorder
from tests.resources.test_harness.utils.common_utils import JsonFactory
from tests.resources.test_harness.utils.enums import SimulatorDeviceType
from tests.resources.test_harness.utils.wait_helpers import Waiter, watch
from tests.resources.test_support.common_utils.common_helpers import Resource

configure_logging(logging.DEBUG)
LOGGER = logging.getLogger(__name__)
TIMEOUT = 20
EB_PB_ID_LENGTH = 16
SDP_SIMULATION_ENABLED = os.getenv("SDP_SIMULATION_ENABLED")
CSP_SIMULATION_ENABLED = os.getenv("CSP_SIMULATION_ENABLED")
MCCS_SIMULATION_ENABLED = os.getenv("MCCS_SIMULATION_ENABLED")


device_dict = {
    "sdp_subarray": low_sdp_subarray1,
    "csp_subarray": low_csp_subarray1,
    "mccs_subarray": mccs_subarray1,
    "tmc_subarraynode": tmc_low_subarraynode1,
    "csp_subarray_leaf_node": low_csp_subarray_leaf_node,
    "sdp_subarray_leaf_node": low_sdp_subarray_leaf_node,
    "mccs_subarray_leaf_node": mccs_subarray_leaf_node,
}


def check_subarray_instance(device, subarray_id):
    """
    Method to check subarray instance
    """
    subarray = str(device).split("/")
    subarray_instance = subarray[-1][-2]
    assert subarray_instance == subarray_id


def update_scan_type(configure_json: str, json_value: str) -> str:
    """
    Method to update json with different scan type

    :param configure_json: json to utilised to update values.
    :param json_value: new json value to be updated in json
    """
    input_json = json.loads(configure_json)
    input_json["sdp"]["scan_type"] = json_value
    input_json = json.dumps(input_json)
    return input_json


def update_scan_id(input_json: str, scan_id: int) -> str:
    """
    Method to update scan_id in input json..
    :param input_json: json to utilised to update values.

    :param json_value: new json value to be updated in json
    """
    input_json = json.loads(input_json)
    input_json["scan_id"] = int(scan_id)
    updated_json = json.dumps(input_json)
    return updated_json


def check_subarray_obs_state(obs_state: str = None, timeout: int = 50) -> bool:
    """
    Logs and checks if all subarray nodes have transitioned to the given
    obsState.

    Args:
        obs_state (str): The target obsState to check for all subarray nodes.
        timeout (int): Timeout for waiting for the state transition
        (in seconds).

    Returns:
        bool: True if all subarray nodes have transitioned to the given
        obsState, False otherwise.
    """
    LOGGER.info(
        f"{tmc_low_subarraynode1}.obsState : "
        + str(Resource(tmc_low_subarraynode1).get("obsState"))
    )
    LOGGER.info(
        f"{low_sdp_subarray1}.obsState : "
        + str(Resource(low_sdp_subarray1).get("obsState"))
    )
    LOGGER.info(
        f"{low_csp_subarray1}.obsState : "
        + str(Resource(low_csp_subarray1).get("obsState"))
    )
    LOGGER.info(
        f"{mccs_subarray1}.obsState : "
        + str(Resource(mccs_subarray1).get("obsState"))
    )

    the_waiter = Waiter(**device_dict)
    the_waiter.set_wait_for_obs_state(obs_state=obs_state)
    the_waiter.wait(timeout / 0.1)

    return all(
        [
            Resource(low_sdp_subarray1).get("obsState") == obs_state,
            Resource(mccs_subarray1).get("obsState") == obs_state,
            Resource(tmc_low_subarraynode1).get("obsState") == obs_state,
            Resource(low_csp_subarray1).get("obsState") == obs_state,
        ]
    )


def get_device_simulators(simulator_factory):
    """A method to get simulators for Subsystem devices

    Args:
        simulator_factory (fixture): fixture for SimulatorFactory class,
        which provides simulated subarray and master devices

    Returns:
        simulator(sim) objects
    """
    sdp_sim = simulator_factory.get_or_create_simulator_device(
        SimulatorDeviceType.LOW_SDP_DEVICE
    )
    csp_sim = simulator_factory.get_or_create_simulator_device(
        SimulatorDeviceType.LOW_CSP_DEVICE
    )
    return csp_sim, sdp_sim


def get_master_device_simulators(simulator_factory):
    """A method to get simulators for Subsystem master devices

    Args:
        simulator_factory (fixture): fixture for SimulatorFactory class,
        which provides simulated subarray and master devices

    Returns:
        simulator(sim) objects
    """
    csp_master_sim = simulator_factory.get_or_create_simulator_device(
        SimulatorDeviceType.LOW_CSP_MASTER_DEVICE
    )
    sdp_master_sim = simulator_factory.get_or_create_simulator_device(
        SimulatorDeviceType.LOW_SDP_MASTER_DEVICE
    )
    mccs_master_sim = simulator_factory.get_or_create_simulator_device(
        SimulatorDeviceType.MCCS_MASTER_DEVICE
    )
    return (csp_master_sim, sdp_master_sim, mccs_master_sim)


def get_device_simulator_with_given_name(simulator_factory, devices):
    """Get Device type based on device name and return device proxy
    Args:
        devices (list): simulator devices list
    """
    device_name_type_dict = {
        "csp subarray": SimulatorDeviceType.LOW_CSP_DEVICE,
        "sdp subarray": SimulatorDeviceType.LOW_SDP_DEVICE,
        "csp master": SimulatorDeviceType.LOW_CSP_MASTER_DEVICE,
        "sdp master": SimulatorDeviceType.LOW_SDP_MASTER_DEVICE,
        "mccs master": SimulatorDeviceType.MCCS_MASTER_DEVICE,
        "mccs subarray": SimulatorDeviceType.MCCS_SUBARRAY_DEVICE,
    }
    sim_device_proxy_list = []
    for device_name in devices:
        if device_name in device_name_type_dict:
            sim_device_type = device_name_type_dict[device_name]
            sim_device_proxy_list.append(
                simulator_factory.get_or_create_simulator_device(
                    sim_device_type
                )
            )
    return sim_device_proxy_list


def prepare_json_args_for_commands(
    args_for_command: str, command_input_factory: JsonFactory
) -> str:
    """This method return input json based on command args"""
    if args_for_command is not None:
        input_json = command_input_factory.create_subarray_configuration(
            args_for_command
        )
    else:
        input_json = None
    return input_json


def prepare_json_args_for_centralnode_commands(
    args_for_command: str, command_input_factory: JsonFactory
) -> str:
    """
    Prepares input JSON based on the command arguments for the Central Node.

    Args:
        args_for_command (str): Command arguments to generate the input JSON.
        command_input_factory (JsonFactory): Factory to generate JSON
         configurations.

    Returns:
        str: Generated input JSON string for the command.
    """
    if args_for_command is not None:
        input_json = command_input_factory.create_centralnode_configuration(
            args_for_command
        )
    else:
        input_json = None
    return input_json


def get_command_call_info(device: Any, command_name: str):
    """
    device: Tango Device Proxy Object

    """
    command_call_info = device.read_attribute("commandCallInfo").value
    LOGGER.info("Command info %s", command_call_info)
    command_info = [
        command_info
        for command_info in command_call_info
        if command_info[0] == command_name
    ]
    input_str = json.loads("".join(command_info[0][1].split()))

    received_command_call_data = (
        command_call_info[0][0],
        sorted(input_str),
    )
    return received_command_call_data


def set_subarray_to_given_obs_state(
    subarray_node,
    obs_state: str,
    event_recorder,
    command_input_factory,
):
    """
    Sets the Subarray node to the specified obsState and verifies state
    transitions.

    Args:
        subarray_node: The subarray node to modify.
        obs_state (str): The desired observation state to set.
        event_recorder: Utility to record and subscribe to events.
        command_input_factory: Factory to generate input commands for the
        transitions.

    Returns:
        None
    """
    match obs_state:
        case "RESOURCING":
            csp_subarray = DeviceProxy(low_csp_subarray1)
            csp_subarray.SetDefective(json.dumps(INTERMEDIATE_STATE_DEFECT))
            subarray_node.force_change_of_obs_state(obs_state)

            sdp_subarray = DeviceProxy(low_sdp_subarray1)
            event_recorder.subscribe_event(sdp_subarray, "obsState")
            assert event_recorder.has_change_event_occurred(
                sdp_subarray,
                "obsState",
                ObsState.IDLE,
            )
            csp_subarray.SetDefective(json.dumps({"enabled": False}))

        case "CONFIGURING":
            subarray_node.force_change_of_obs_state("IDLE")
            csp_subarray = DeviceProxy(low_csp_subarray1)
            csp_subarray.SetDefective(
                json.dumps(INTERMEDIATE_CONFIGURING_OBS_STATE_DEFECT)
            )
            configure_input = prepare_json_args_for_commands(
                "configure_low", command_input_factory
            )
            subarray_node.execute_transition("Configure", configure_input)

            sdp_subarray = DeviceProxy(low_sdp_subarray1)
            event_recorder.subscribe_event(sdp_subarray, "obsState")
            assert event_recorder.has_change_event_occurred(
                sdp_subarray,
                "obsState",
                ObsState.READY,
            )
            csp_subarray.SetDefective(json.dumps({"enabled": False}))


def device_received_this_command(
    device: Any, expected_command_name: str, expected_inp_str: str
):
    """Method to verify received command and command argument

    Args:
        device (Any): Tango Device Proxy Object
        expected_command_name (str): Command name received on simulator device
        expected_inp_str (str): Command argument received on simulator device

    Returns:
        Boolean: True if received data is equal to expected data.
    """
    received_command_call_data = get_command_call_info(
        device, expected_command_name
    )
    expected_input_str = json.loads("".join(expected_inp_str.split()))
    return received_command_call_data == (
        expected_command_name,
        sorted(expected_input_str),
    )


def check_for_device_event(
    device: DeviceProxy,
    attr_name: str,
    event_data: str,
    event_recorder: EventRecorder,
    command_name: str = "",
    unique_id: str = "",
) -> bool:
    """Method to check event from the device.

    Args:
        device (DeviceProxy): device proxy
        attr_name (str): attribute name
        event_data (str): event data to be searched
        event_recorder(EventRecorder): event recorder instance
        to check for events.
    """
    event_found: bool = False
    timeout: int = 300
    elapsed_time: float = 0
    start_time: float = time.time()
    while not event_found and elapsed_time < timeout:
        assertion_data = event_recorder.has_change_event_occurred(
            device,
            attribute_name=attr_name,
            attribute_value=(Anything),
            lookahead=1,
        )
        if command_name:
            is_command_event = assertion_data["attribute_value"][0].endswith(
                command_name
            )
        elif unique_id:
            is_command_event = (
                assertion_data["attribute_value"][0] == unique_id
            )
        if is_command_event:
            if (
                event_data
                in json.loads(assertion_data["attribute_value"][1])[1]
            ):
                event_found = True
                return event_found

        elapsed_time = time.time() - start_time

    return event_found


def get_recorded_commands(device: Any):
    """A method to get data from simulator device

    Args:
        device (Any): Tango Device Proxy Object

    Returns: List[tuple]
        recorded data from Simulator device
    """
    return device.read_attribute("commandCallInfo").value


def set_desired_health_state(
    sim_devices_list: list, health_state_value: HealthState
):
    """A method to set simulator devices healthState attribute

    Args:
        sim_devices_list: simulator devices list
        health_state_value: desired healthState value to set
    """

    for device in sim_devices_list:
        device.SetDirectHealthState(health_state_value)


def device_attribute_changed(
    device: Any,
    attribute_name_list: list,
    attribute_value_list: list,
    timeout: int,
):
    """
    Method to verify device attribute changed to speicified attribute value
    """

    waiter = Waiter()
    for attribute_name, attribute_value in zip(
        attribute_name_list, attribute_value_list
    ):
        waiter.waits.append(
            watch(Resource(device.dev_name())).to_become(
                attribute_name, attribute_value
            )
        )
    try:
        waiter.wait(timeout)
    except Exception:
        return False
    return True


def wait_and_validate_device_attribute_value(
    device: DeviceProxy,
    attribute_name: str,
    expected_value: str,
    is_json: bool = False,
    timeout: int = 300,
):
    """This method wait and validate if attribute value is equal to provided
    expected value
    """
    count = 0
    error = ""
    while count <= timeout:
        try:
            attribute_value = device.read_attribute(attribute_name).value
            logging.info(
                "%s current %s value: %s",
                device.name(),
                attribute_name,
                attribute_value,
            )
            if is_json and json.loads(attribute_value) == json.loads(
                expected_value
            ):
                return True
            elif attribute_value == expected_value:
                return True
        except Exception as e:
            # Device gets unavailable due to restart and the above command
            # tries to access the attribute resulting into exception
            # It keeps it printing till the attribute is accessible
            # the exception log is suppressed by storing into variable
            # the error is printed later into the log in case of failure
            error = e
        count += 10
        # When device restart it will at least take 10 sec to up again
        # so added 10 sec sleep and to avoid frequent attribute read.
        time.sleep(10)

    logging.exception(
        "Exception occurred while reading attribute %s and cnt is %s",
        error,
        count,
    )
    return False


def check_assigned_resources_attribute_value(
    device: DeviceProxy,
    attribute_name: str,
    expected_value: str,
    timeout: int = 10,
) -> bool:
    """
    This function will verify if assignedResources attribute is set
    as per expected value
    :param device: Tango Device Proxy
    :type device: DeviceProxy
    :param attribute_name: device attribute name
    :type attribute_name: str
    :param expected_value: expected value of attribute to check
    :type expected_value: str
    :param timeout: no of sec to check if expected value changed for device
    :type timeout: int
    :rtype: bool
    """
    count = 0
    while count <= timeout:
        attribute_value = device.read_attribute(attribute_name).value
        LOGGER.info(
            "Assign Resource device value %s and expected value %s",
            attribute_value,
            expected_value,
        )
        if attribute_value and json.loads(attribute_value[0]) == json.loads(
            expected_value
        ):
            return True
        count += 1
        time.sleep(1)
    return False


def get_simulated_devices_info() -> dict:
    """
    A method to get simulated devices present in low deployment.

    return: dict
    """

    is_csp_simulated = CSP_SIMULATION_ENABLED.lower() == "true"
    is_sdp_simulated = SDP_SIMULATION_ENABLED.lower() == "true"
    is_mccs_simulated = MCCS_SIMULATION_ENABLED.lower() == "true"
    return {
        "csp_and_sdp": all(
            [is_csp_simulated, is_sdp_simulated, not is_mccs_simulated]
        ),  # real MCCS enabled
        "csp_and_mccs": all(
            [is_csp_simulated, is_mccs_simulated, not is_sdp_simulated]
        ),  # real SDP enabled
        "sdp_and_mccs": all(
            [is_sdp_simulated, is_mccs_simulated, not is_csp_simulated]
        ),  # real CSP.LMC enabled
        "all_mocks": all(
            [
                is_csp_simulated,
                is_sdp_simulated,
                is_mccs_simulated,
            ]
        ),
    }


SIMULATED_DEVICES_DICT = get_simulated_devices_info()


def check_lrcr_events(
    event_recorder,
    device,
    command_name: str,
    result_code: ResultCode = ResultCode.OK,
    retries: int = 10,
):
    """Used to assert command name and result code in
       longRunningCommandResult event callbacks.

    Args:
        event_recorder (EventRecorder):fixture used to
        capture event callbacks
        device (str): device for which attribute needs to be checked
        command_name (str): command name to check
        result_code (ResultCode): result_code to check.
        Defaults to ResultCode.OK.
        retries (int):number of events to check. Defaults to 10.
    """
    COUNT = 0
    while COUNT <= retries:
        assertion_data = event_recorder.has_change_event_occurred(
            device, "longRunningCommandResult", Anything, lookahead=1
        )
        unique_id, result = assertion_data["attribute_value"]
        if unique_id.endswith(command_name):
            if result == str(result_code.value):
                LOGGER.debug("TRACKLOADSTATICOFF_UID: %s", unique_id)
                break
        COUNT = COUNT + 1
        if COUNT >= retries:
            pytest.fail("Assertion Failed")


def generate_id(prefix: str) -> str:
    """
    Generate a UUID-based numerical id with the given prefix
    :param prefix: the prefix for the unique id.
    :return: the generated id.
    """
    unique_id = str(int(uuid.uuid4().hex, 16))
    return f"{prefix}-{unique_id[:8]}-{unique_id[-5:]}"


def update_eb_pb_ids(input_json: str, json_id: str = "") -> str:
    """
    Method to generate different eb_id and pb_id
    :param input_json: json to utilised to update values.
    """
    input_json = json.loads(input_json)
    if json_id in ("eb_id", ""):
        input_json["sdp"]["execution_block"]["eb_id"] = generate_id("eb-test")

    if json_id in ("pb_id", ""):
        for pb in input_json["sdp"]["processing_blocks"]:
            pb["pb_id"] = generate_id("pb-test")
    input_json = json.dumps(input_json)
    return input_json


def update_multiple_scan_types(input_json):
    """Method to dynamically update scan types inside the JSON."""

    # Define your different scan type values here
    scan_types = [
        {
            "scan_type_id": ".default",
            "beams": {
                "vis0": {
                    "channels_id": "vis_channels",
                    "polarisations_id": "all",
                }
            },
        },
        {
            "scan_type_id": "target:a",
            "derive_from": ".default",
            "beams": {"vis0": {"field_id": "field_a"}},
        },
        {
            "scan_type_id": "calibration:b",
            "derive_from": ".default",
            "beams": {"vis0": {"field_id": "field_b"}},
        },
    ]

    # Update the scan types in the input JSON
    input_json["sdp"]["execution_block"]["scan_types"] = scan_types
    return input_json


def get_assign_json_id(input_json: str, json_id: str = "") -> list[str]:
    """
    Method to get different eb_id and pb_id
    :param input_json: json to utilised to update values.
    """
    input_json = json.loads(input_json)
    if json_id == "eb_id":
        return [input_json["sdp"]["execution_block"]["eb_id"]]

    elif json_id == "pb_id":
        return [pb["pb_id"] for pb in input_json["sdp"]["processing_blocks"]]


def retry_communication(device_proxy: DeviceProxy, timeout: int = 30) -> None:
    """
    Retry communication with the backend.

    NOTE: This is to be used for devices that do not know if the backend is
    available at the time of the call. For example, the daq_handler backend
    gRPC server may not be ready when we try to start communicating.
    In this case, we will retry connection.

    :param device_proxy: A 'tango.DeviceProxy' to the backend device.
    :param timeout: A max time in seconds before we give up trying
    """
    tick = 2
    if device_proxy.adminMode != AdminMode.ONLINE:
        terminate_time = time.time() + timeout
        while time.time() < terminate_time:
            try:
                device_proxy.adminMode = AdminMode.ONLINE
                if wait_and_validate_device_attribute_value(
                    device=device_proxy,
                    attribute_name="adminMode",
                    expected_value=AdminMode.ONLINE,
                    timeout=tick,
                ):
                    break
            except tango.DevFailed:
                print(
                    f"{device_proxy.dev_name()} failed to communicate "
                    "with backend."
                )
                time.sleep(tick)
        assert device_proxy.adminMode == AdminMode.ONLINE
    else:
        print(
            f"Device {device_proxy.dev_name()} is already ONLINE, "
            "nothing to do."
        )


def set_admin_mode_values_mccs():
    """Set the adminMode values of MCCS devices."""
    max_retries: int = 3
    if MCCS_SIMULATION_ENABLED.lower() == "false":
        controller = tango.DeviceProxy(mccs_controller)
        if controller.adminMode != AdminMode.ONLINE:
            db = tango.Database()
            pasd_bus_trls = db.get_device_exported(mccs_pasdbus_prefix)
            for pasd_bus_trl in pasd_bus_trls:
                pasdbus = tango.DeviceProxy(pasd_bus_trl)
                retry_communication(pasdbus, 30)

            device_trls = db.get_device_exported(mccs_prefix)
            devices = []
            for device_trl in device_trls:
                if "daq" in device_trl or "calibrationstore" in device_trl:
                    device = tango.DeviceProxy(device_trl)
                    retry_communication(device, 30)
                else:
                    device = tango.DeviceProxy(device_trl)
                    retry: int = 0
                    while (
                        device.adminMode != AdminMode.ONLINE
                        and retry <= max_retries
                    ):
                        try:
                            device.adminMode = AdminMode.ONLINE
                            devices.append(device)
                            time.sleep(0.1)
                        except tango.DevFailed as df:
                            LOGGER.info(
                                "Issue occurred during setting the admin "
                                "mode: %s",
                                df,
                            )
                            retry += 1
                            time.sleep(0.1)


def set_receive_address(central_node) -> None:
    """
    Sets the direct receive address for a central node's subarray.

    Args:
        central_node: The central node for which to set the receive address.

    Returns:
        None
    """
    receive_address = json.dumps(
        {
            "science_A": {
                "host": [[0, "192.168.0.1"], [2000, "192.168.0.1"]],
                "port": [[0, 9000, 1], [2000, 9000, 1]],
            },
            "target:a": {
                "vis0": {
                    "function": "visibilities",
                    "visibility_beam_id": 1,
                    "host": [
                        [0, "192.168.0.1"],
                    ],
                    "port": [
                        [0, 9000, 1],
                    ],
                    "mac": [
                        [0, "06-00-00-00-00-00"],
                    ],
                }
            },
            "calibration:b": {
                "vis0": {
                    "function": "visibilities",
                    "host": [
                        [0, "192.168.0.1"],
                        [400, "192.168.0.2"],
                        [744, "192.168.0.3"],
                        [1144, "192.168.0.4"],
                    ],
                    "port": [
                        [0, 9000, 1],
                        [400, 9000, 1],
                        [744, 9000, 1],
                        [1144, 9000, 1],
                    ],
                    "mac": [
                        [0, "06-00-00-00-00-00"],
                        [744, "06-00-00-00-00-01"],
                    ],
                }
            },
        }
    )
    central_node.subarray_devices["sdp_subarray"].SetDirectreceiveAddresses(
        receive_address
    )


def updated_assign_str(assign_json: str, station_id: int) -> str:
    """
    Returns a json with updated values for the given keys
    :returns: updated assign string
    """
    assign_json = json.loads(assign_json)

    for subarray_beam in assign_json["mccs"]["subarray_beams"]:
        for aperture in subarray_beam["apertures"]:
            aperture["station_id"] = station_id

    updated_assign_str = json.dumps(assign_json)
    return updated_assign_str


def remove_timing_beams(configure_json: str) -> str:
    """
    Removes the 'timing_beams' key from the configure JSON.

    Args:
        configure_json (str): Original JSON string.

    Returns:
        str: Modified JSON string without 'timing_beams'.
    """
    config_dict = json.loads(configure_json)
    config_dict_copy = copy.deepcopy(config_dict)

    if "timing_beams" in config_dict_copy["csp"]["lowcbf"]:
        del config_dict_copy["csp"]["lowcbf"]["timing_beams"]

    return json.dumps(config_dict_copy, indent=4)


def generate_and_get_assign_resource_json(assign_json: str) -> str:
    """
    Generates a JSON structure for assign resources based on the input JSON.

    Args:
        assign_json (str): The input JSON string containing resource
        assignments.

    Returns:
        str: JSON string representing the assign resources.
    """
    assign_json_dict = json.loads(assign_json)

    assign_json_mccs_block_modified = {
        "interface": (
            "https://schema.skao.int/ska-low-mccs-assignedresources/1.0"
        ),
        "subarray_beam_ids": [
            beam["subarray_beam_id"]
            for beam in assign_json_dict["mccs"]["subarray_beams"]
        ],
        "station_ids": [
            str(aperture["station_id"])
            for beam in assign_json_dict["mccs"]["subarray_beams"]
            for aperture in beam["apertures"]
        ],
        "apertures": [
            aperture["aperture_id"]
            for beam in assign_json_dict["mccs"]["subarray_beams"]
            for aperture in beam["apertures"]
        ],
        "channels": [32],
    }

    assign_json_mccs_block_modified["station_ids"].append("3")
    assign_json_mccs_block_modified["apertures"].extend(
        ["AP001.02", "AP002.02", "AP003.01"]
    )

    return json.dumps(assign_json_mccs_block_modified)


def update_assign_json_with_empty_values(assign_json: str) -> str:
    """
    Updates the given JSON to set specific fields to empty values.

    Args:
        assign_json (str): The input JSON string to be updated.

    Returns:
        str: JSON string with the specified fields set to empty.
    """
    assign_json_mccs_block_modified = json.loads(assign_json)

    assign_json_mccs_block_modified["subarray_beam_ids"] = []
    assign_json_mccs_block_modified["station_beam_ids"] = []
    assign_json_mccs_block_modified["station_ids"] = []
    assign_json_mccs_block_modified["apertures"] = []
    assign_json_mccs_block_modified["channels"] = [0]

    return json.dumps(assign_json_mccs_block_modified)


def modify_json_with_duplicate_ids(
    assign_json: str, duplicate_eb_id: str, duplicate_pb_id: str
) -> dict:
    """
    Modifies the input JSON by adding duplicate execution block ID (eb_id)
    and processing block ID (pb_id).

    Args:
        assign_json (str): Input JSON string containing resource assignments.
        duplicate_eb_id (str): Duplicate execution block ID to add.
        duplicate_pb_id (str): Duplicate processing block ID to add.

    Returns:
        dict: Modified JSON structure with duplicate IDs added.
    """
    # Load the input JSON string into a dictionary
    assign_json_duplicate_eb_pb_id = json.loads(assign_json)

    # Modify the eb_id and pb_id
    assign_json_duplicate_eb_pb_id["sdp"]["execution_block"][
        "eb_id"
    ] = duplicate_eb_id
    assign_json_duplicate_eb_pb_id["sdp"]["processing_blocks"][0][
        "pb_id"
    ] = duplicate_pb_id

    return json.dumps(assign_json_duplicate_eb_pb_id, indent=2)


def wait_for_partial_or_complete_abort(timeout: int = 110) -> None:
    """Wait for completion of Partial/Full abort on SubarrayNode by waiting for
    one of 3 states on all the devices - ABORTED, EMPTY, or FAULT until
    occurrence of timeout.

    :param timeout: Timeout value to wait for.
    """
    DEVICE_ATTRIBUTE_MAP = {
        DeviceProxy(tmc_low_subarraynode1): "obsState",
        DeviceProxy(low_csp_subarray_leaf_node): "cspSubarrayObsState",
        DeviceProxy(low_sdp_subarray_leaf_node): "sdpSubarrayObsState",
        DeviceProxy(mccs_subarray_leaf_node): "obsState",
    }
    event_recorder = EventRecorder()

    # Subscribing to events
    for dev_proxy, attribute_name in DEVICE_ATTRIBUTE_MAP.items():
        event_recorder.subscribe_event(dev_proxy, attribute_name, timeout=120)

    # Asserting Events
    for dev_proxy, attribute_name in DEVICE_ATTRIBUTE_MAP.items():
        if (
            dev_proxy.dev_name()
            == DeviceProxy(tmc_low_subarraynode1).dev_name()
        ):
            assert event_recorder.has_change_event_occurred_for_given_values(
                dev_proxy,
                attribute_name,
                [ObsState.FAULT, ObsState.ABORTED],
            )
        else:
            assert event_recorder.has_change_event_occurred_for_given_values(
                dev_proxy,
                attribute_name,
                [ObsState.FAULT, ObsState.ABORTED, ObsState.EMPTY],
            )

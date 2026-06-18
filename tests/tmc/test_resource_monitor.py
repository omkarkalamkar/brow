"""
Test case for verifying Resource Monitor updates when SubarrayNode assigned
resources change.
This test simulates a change in assigned resources and checks that the
ResourceMonitor device
reflects the update in its stationsData attribute
"""
import logging

import pytest
from pytest_bdd import given, scenario, then, when
from ska_ser_logging import configure_logging
from ska_tango_testing.integration import TangoEventTracer, log_events
from tango import DeviceProxy

from tests.resources.test_harness.helpers import (
    generate_and_get_assign_resource_json,
    wait_and_validate_device_attribute_value,
)
from tests.resources.test_harness.simulator_factory import SimulatorFactory
from tests.resources.test_harness.utils.common_utils import (
    JsonFactory,
    get_centralnode_input_json,
    get_subarray_input_json,
)
from tests.resources.test_harness.utils.enums import SimulatorDeviceType
from tests.resources.test_support.common_utils.tmc_helpers import (
    prepare_json_args_for_centralnode_commands,
)

configure_logging(logging.DEBUG)
LOGGER = logging.getLogger(__name__)

RESOURCE_MONITOR_FQDN = "low-tmc/resource-monitor/01"


@pytest.mark.SKA_low
@scenario(
    "features/tmc/resource_monitor.feature",
    "Test Resource Monitor updates when SubarrayNode and MCCS "
    "controller attributes change",
)
def test_resource_monitor_update():
    """BDD test scenario for Resource Monitor update on SN & MCCS controller
    attribute change"""


@given("the LOW SubarrayNode and ResourceMonitor devices are available")
def setup_devices(
    event_tracer: TangoEventTracer,
    simulator_factory: SimulatorFactory,
):
    """
    Set up the SubarrayNode and ResourceMonitor devices, subscribe to
    relevant events, and ensure the system is in the ON state.
    """
    resource_monitor = DeviceProxy(RESOURCE_MONITOR_FQDN)
    event_tracer.subscribe_event(resource_monitor, "stations")
    event_tracer.subscribe_event(resource_monitor, "stationBeams")
    log_events(
        {
            resource_monitor: ["stations", "stationBeams"],
        }
    )
    mccs_controller_sim = simulator_factory.get_or_create_simulator_device(
        SimulatorDeviceType.MCCS_MASTER_DEVICE
    )
    mccs_sim = simulator_factory.get_or_create_simulator_device(
        SimulatorDeviceType.MCCS_SUBARRAY_DEVICE
    )
    mccs_sim2 = simulator_factory.get_or_create_simulator_device(
        SimulatorDeviceType.MCCS_SUBARRAY_DEVICE2
    )

    # Store resource_monitor for later steps
    setup_devices.resource_monitor = resource_monitor
    setup_devices.mccs_controller = mccs_controller_sim
    setup_devices.mccs_sim = mccs_sim
    setup_devices.mccs_sim2 = mccs_sim2


@when(
    "the SubarrayNode assignedResources attribute "
    "changes after AssignResources command"
)
def trigger_sn_resource_change(
    command_input_factory: JsonFactory,
):
    """
    Simulate a change in the SubarrayNode assigned resources by invoking
    AssignResources and SetDirectassignedResources, and check obsState
    transitions to IDLE.
    """
    # Get required data from previous steps
    mccs_controller_sim = setup_devices.mccs_controller
    mccs_sim = setup_devices.mccs_sim
    mccs_sim2 = setup_devices.mccs_sim2

    # Fetch necessary JSON files data
    mccs_input = get_subarray_input_json("ResourceSummary_MCCS")
    assign_input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_low", command_input_factory
    )
    assign_input_json2 = prepare_json_args_for_centralnode_commands(
        "assign_resources_low_v4_1_02", command_input_factory
    )

    # Generate correct JSON for assigned resources
    assigned_resources = generate_and_get_assign_resource_json(
        assign_input_json
    )

    assigned_resources2 = generate_and_get_assign_resource_json(
        assign_input_json2
    )

    # Trigger attribute change via helper device methods
    mccs_controller_sim.SetDirectResourceSummary(mccs_input)
    mccs_sim.SetDirectassignedResources(assigned_resources)
    mccs_sim2.SetDirectassignedResources(assigned_resources2)

    # Save values for later re-use
    trigger_sn_resource_change.assigned_resources = assigned_resources
    trigger_sn_resource_change.assigned_resources2 = assigned_resources2


@then("the ResourceMonitor attributes should reflect assigned resources")
def check_resource_monitor_update():
    """
    Assert that the ResourceMonitor device's stationsData attribute has
    been updated to reflect the new assigned resources from the SubarrayNode.
    """

    # Get required data from previous steps
    resource_monitor = setup_devices.resource_monitor

    # Setup expected values. These values are setup manually as they can not be
    # generated from input values.
    expected_stations_data = """{"station_1": {"subarray_allocation": 1},
                              "station_2": {"subarray_allocation": 1},
                              "station_3": {"subarray_allocation": 2},
                              "station_4": {"subarray_allocation": 2},
                              "station_5": {"subarray_allocation": 2}}
                              """
    expected_stations_beam_data = """{
        "station_1": [{"station_beam": "01", "subarray_allocation": 1}],
        "station_2": [{"station_beam": "02", "subarray_allocation": 1}],
        "station_3": [{"station_beam": "01", "subarray_allocation": 2}],
        "station_4": [{"station_beam": "01", "subarray_allocation": 2}],
        "station_5": [{"station_beam": "02", "subarray_allocation": 2}]}
        """

    # Assert attribute values
    wait_and_validate_device_attribute_value(
        resource_monitor,
        "stations",
        expected_stations_data,
        is_json=True,
        sort_keys=True,
    )
    wait_and_validate_device_attribute_value(
        resource_monitor,
        "stationBeams",
        expected_stations_beam_data,
        is_json=True,
        sort_keys=True,
    )


@when(
    "the SubarrayNode assignedResources attribute changes after "
    "ReleaseResources command"
)
def trigger_sn_release_resource_change():
    """
    Function to trigger release resources across SN and MCCS controller device.
    """
    # Get required data from previous steps
    mccs_controller_sim = setup_devices.mccs_controller
    mccs_sim = setup_devices.mccs_sim
    mccs_sim2 = setup_devices.mccs_sim2

    release_mccs = get_subarray_input_json("ResourceSummary_MCCS_release")
    release_assign_resources = get_centralnode_input_json(
        "assign_resources_low_empty"
    )
    mccs_controller_sim.SetDirectResourceSummary(release_mccs)
    mccs_sim.SetDirectassignedResources(release_assign_resources)
    mccs_sim2.SetDirectassignedResources(release_assign_resources)


@then("the ResourceMonitor attributes should reflect released resources")
def check_resource_monitor_attributes_post_deallocation():
    """
    Function to assert resource monitor attributes post resources deallocation
    """
    # Get required data from previous steps
    resource_monitor = setup_devices.resource_monitor

    expected_stations_beam_data = """{
        "station_5": [{"station_beam": "02", "subarray_allocation": -1}],
        "station_3": [{"station_beam": "01", "subarray_allocation": -1}],
        "station_4": [{"station_beam": "01", "subarray_allocation": -1}],
        "station_1": [{"station_beam": "01", "subarray_allocation": -1}],
        "station_2": [{"station_beam": "02", "subarray_allocation": -1}]}"""
    expected_stations_data = """{"station_1": {"subarray_allocation": -1},
                              "station_2": {"subarray_allocation": -1},
                              "station_3": {"subarray_allocation": -1},
                              "station_4": {"subarray_allocation": -1},
                              "station_5": {"subarray_allocation": -1}}"""

    # Assert attribute values
    wait_and_validate_device_attribute_value(
        resource_monitor,
        "stations",
        expected_stations_data,
        is_json=True,
        sort_keys=True,
    )
    wait_and_validate_device_attribute_value(
        resource_monitor,
        "stationBeams",
        expected_stations_beam_data,
        is_json=True,
        sort_keys=True,
    )

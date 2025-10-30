"""
Test case for verifying Resource Monitor updates when SubarrayNode assigned
resources change.
This test simulates a change in assigned resources and checks that the
ResourceMonitor device
reflects the update in its stationsData attribute.
"""
import pytest
from assertpy import assert_that
from pytest_bdd import given, scenario, then, when
from ska_tango_testing.integration import TangoEventTracer, log_events
from tango import DeviceProxy
from ska_control_model import ObsState
from tests.resources.test_harness.central_node_low import CentralNodeWrapperLow
from tests.resources.test_harness.simulator_factory import SimulatorFactory

# from tests.resources.test_harness.subarray_node_low import (
#     SubarrayNodeWrapperLow,
# )
from tests.resources.test_harness.utils.common_utils import JsonFactory
from tests.resources.test_harness.utils.enums import SimulatorDeviceType
from tests.resources.test_support.common_utils.tmc_helpers import (
    prepare_json_args_for_centralnode_commands,
)
from tests.resources.test_support.constant_low import TIMEOUT

RESOURCE_MONITOR_FQDN = "low-tmc/resource_monitor/01"


@pytest.mark.test1
@pytest.mark.SKA_low
@scenario(
    "../features/tmc/resource_monitor.feature",
    "Test Resource Monitoring updates when SubarrayNode attributes change",
)
def test_resource_monitor_update():
    """BDD test scenario for Resource Monitor update on SN attribute change"""


@given("the LOW SubarrayNode and ResourceMonitoring devices are available")
def setup_devices(
    central_node_low: CentralNodeWrapperLow, event_tracer: TangoEventTracer
):
    """
    Set up the SubarrayNode and ResourceMonitor devices, subscribe to
    relevant events, and ensure the system is in the ON state.
    """
    resource_monitor = DeviceProxy(RESOURCE_MONITOR_FQDN)
    event_tracer.subscribe_event(
        central_node_low.subarray_node, "assignedResources"
    )
    event_tracer.subscribe_event(central_node_low.subarray_node, "obsState")
    event_tracer.subscribe_event(resource_monitor, "stationsData")
    log_events(
        {
            central_node_low.subarray_node: ["assignedResources"],
            resource_monitor: ["stationsData"],
        }
    )
    central_node_low.move_to_on()
    # Store resource_monitor for later steps
    setup_devices.resource_monitor = resource_monitor


@when("a change is triggered on the SubarrayNode assigned resources")
def trigger_sn_resource_change(
    central_node_low: CentralNodeWrapperLow,
    simulator_factory: SimulatorFactory,
    command_input_factory: JsonFactory,
    event_tracer: TangoEventTracer,
):
    """
    Simulate a change in the SubarrayNode assigned resources by invoking
    AssignResources and SetDirectassignedResources, and check obsState transitions to IDLE.
    """
    assign_input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_low", command_input_factory
    )
    central_node_low.perform_action(
        "AssignResources", assign_input_json
    )
    # Check that obsState transitions to IDLE after assigning resources
    assert_that(event_tracer).within_timeout(TIMEOUT).has_change_event_occurred(
        central_node_low.subarray_node,
        "obsState",
        ObsState.IDLE, 
    )
    mccs_sim = simulator_factory.get_or_create_simulator_device(
        SimulatorDeviceType.MCCS_SUBARRAY_DEVICE
    )
    # Generate correct JSON for assigned resources
    from tests.resources.test_harness.helpers import generate_and_get_assign_resource_json
    import json
    assigned_resources = json.loads(generate_and_get_assign_resource_json(assign_input_json))
    # Update station_ids to match expected keys in ResourceMonitor
    assigned_resources = {
                "subarray_beam_ids": ["1"],
                "station_beam_ids": ["1"],
                "station_ids": ["1", "2", "3"],
                "apertures": [
                    "AP001.01",
                    "AP001.02",
                    "AP002.01",
                    "AP002.02",
                    "AP003.01",
                ],
                "channels": [32],
            }
    # assigned_resources_json = json.loads(assigned_resources)
    mccs_sim.SetDirectassignedResources(assigned_resources)


@then(
    "the ResourceMonitoring stationsData attribute should reflect the change"
)
def check_resource_monitor_update(event_tracer: TangoEventTracer):
    """
    Assert that the ResourceMonitor device's stationsData attribute has
    been updated to reflect the new assigned resources from the SubarrayNode.
    """
    resource_monitor = setup_devices.resource_monitor
    # Get the assigned resources JSON from the previous step
    # For simplicity, reconstruct the expected dict from the same station_ids
    station_ids =  {
                "stations": {
                    "station_1": {"subarray_allocation": 1},
                    "station_2": {"subarray_allocation": 1},
                    "station_3": {"subarray_allocation": 1},
                }
            },
    # expected_stations_data = {
    #     "stations": {station_id: {"subarray_allocation": 1} for station_id in station_ids}
    # }
    assert_that(event_tracer).within_timeout(TIMEOUT).has_change_event_occurred(
        resource_monitor,
        "stationsData",
        station_ids,
    )

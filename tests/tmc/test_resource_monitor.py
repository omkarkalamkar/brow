"""
Test case for verifying Resource Monitor updates when SubarrayNode assigned
resources change.
This test simulates a change in assigned resources and checks that the
ResourceMonitor device
reflects the update in its stationsData attribute
"""
import json

import pytest
from assertpy import assert_that
from pytest_bdd import given, scenario, then, when
from ska_control_model import ObsState
from ska_tango_testing.integration import TangoEventTracer, log_events
from tango import DeviceProxy

from tests.conftest import LOGGER
from tests.resources.test_harness.central_node_low import CentralNodeWrapperLow
from tests.resources.test_harness.helpers import (
    generate_and_get_assign_resource_json,
)
from tests.resources.test_harness.simulator_factory import SimulatorFactory
from tests.resources.test_harness.utils.common_utils import JsonFactory
from tests.resources.test_harness.utils.enums import SimulatorDeviceType
from tests.resources.test_support.common_utils.tmc_helpers import (
    prepare_json_args_for_centralnode_commands,
)
from tests.resources.test_support.constant_low import TIMEOUT

RESOURCE_MONITOR_FQDN = "low-tmc/resource-monitor/01"


@pytest.mark.lowrm
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
    event_tracer.subscribe_event(resource_monitor, "stations")
    log_events(
        {
            central_node_low.subarray_node: ["assignedResources"],
            resource_monitor: ["stations"],
        }
    )
    central_node_low.move_to_on()
    # Store resource_monitor for later steps
    setup_devices.resource_monitor = resource_monitor


@when(
    "the SubarrayNode assignedResources attribute "
    "changes after AssignResources command"
)
def trigger_sn_resource_change(
    central_node_low: CentralNodeWrapperLow,
    simulator_factory: SimulatorFactory,
    command_input_factory: JsonFactory,
    event_tracer: TangoEventTracer,
):
    """
    Simulate a change in the SubarrayNode assigned resources by invoking
    AssignResources and SetDirectassignedResources, and check obsState
    transitions to IDLE.
    """
    mccs_input = {
        "resources": {
            "channel_blocks": {
                "available": {"count": 64},
                "allocated": {
                    "count": 32,
                    "usage": {
                        "low-mccs/subarray/01": 16,
                        "low-mccs/subarray/02": 16,
                    },
                },
                "by_station": {
                    "ci-1": {"total": 48, "available": 16, "allocated": 32},
                    "ci-2": {"total": 48, "available": 48, "allocated": 0},
                },
            },
            "station_beams": {
                "total": {"count": 8},
                "available": {"count": 4},
                "allocated": {
                    "count": 4,
                    "usage": {
                        "low-mccs/beam/ci-1-01": "low-mccs/subarray/01",
                        "low-mccs/beam/ci-1-02": "low-mccs/subarray/01",
                    },
                },
            },
            "subarray_beams": {
                "total": {"count": 4},
                "available": {"count": 2},
                "allocated": {
                    "count": 2,
                    "usage": {
                        "low-mccs/subarraybeam/01": "low-mccs/subarray/01",
                        "low-mccs/subarraybeam/02": "low-mccs/subarray/02",
                    },
                },
            },
        }
    }
    assign_input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_low", command_input_factory
    )
    central_node_low.perform_action("AssignResources", assign_input_json)

    # Check that obsState transitions to IDLE after assigning resources
    assert_that(event_tracer).within_timeout(
        TIMEOUT
    ).has_change_event_occurred(
        central_node_low.subarray_node,
        "obsState",
        ObsState.IDLE,
    )
    mccs_sim = simulator_factory.get_or_create_simulator_device(
        SimulatorDeviceType.MCCS_SUBARRAY_DEVICE
    )
    # Generate correct JSON for assigned resources
    assigned_resources = generate_and_get_assign_resource_json(
        assign_input_json
    )
    # mccs_controller_sim = simulator_factory.get_or_create_simulator_device(
    #     SimulatorDeviceType.MCCS_MASTER_DEVICE
    # )
    # mccs_input = json.dumps(mccs_input)
    # mccs_controller_sim.SetDirectResourceSummary(mccs_input)
    mccs_sim.SetDirectassignedResources((assigned_resources,))
    trigger_sn_resource_change.assigned_resources = assigned_resources


@then(
    "the ResourceMonitoring stationsData attribute should reflect the change"
)
def check_resource_monitor_update(event_tracer: TangoEventTracer):
    """
    Assert that the ResourceMonitor device's stationsData attribute has
    been updated to reflect the new assigned resources from the SubarrayNode.
    """
    # Get required data from previous steps
    resource_monitor = setup_devices.resource_monitor
    assigned_resources = json.loads(
        trigger_sn_resource_change.assigned_resources
    )
    expected_stations_data = {
        f"station_{station_id}": {"subarray_allocation": 1}
        for station_id in assigned_resources.get("station_ids")
    }
    assert_that(event_tracer).within_timeout(
        TIMEOUT
    ).has_change_event_occurred(
        resource_monitor, "stations", json.dumps(expected_stations_data)
    )
    attr_val = resource_monitor.read_attribute("stationBeams").value
    LOGGER.info("Attr val of attr val is %s", attr_val)

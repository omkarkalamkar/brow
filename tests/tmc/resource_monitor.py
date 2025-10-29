import json
import pytest
import tango
from assertpy import assert_that
from pytest_bdd import given, scenario, then, when
from ska_tmc_common import DevFactory
from ska_tango_testing.integration import TangoEventTracer

@pytest.mark.test1
@pytest.mark.SKA_low
@scenario(
    "../features/tmc/resource_monitor.feature",
    "Test Resource Monitoring attribute updates on SubarrayNode change",
)
def test_resource_monitoring_low_updates():
    """BDD test scenario for verifying Resource Monitoring attribute updates."""


@given("the LOW SubarrayHelper and ResourceMonitoring devices are available")
def setup_devices():
    """Set up device proxies for SubarrayHelper and ResourceMonitoring."""
    dev_factory = DevFactory()
    subarray_helper = dev_factory.get_device("ska_low/tm_subarray_helper/01")
    rm_device = dev_factory.get_device("ska_low/tm_resource_monitor/1")
    return subarray_helper, rm_device


@when("a change in assigned resources is triggered on the SubarrayHelper")
def trigger_subarray_change(setup_devices):
    """Trigger a change in SubarrayHelper that RM should reflect."""
    subarray_helper, _ = setup_devices
    assign_json = json.dumps({
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
    })
    subarray_helper.SetDirectassignedResources(assign_json)


@then("the ResourceMonitoring stationsData attribute should publish the updated event")
def verify_rm_event_update(setup_devices):
    """Verify that the ResourceMonitoring device sends updated stationsData event."""
    _, rm_device = setup_devices
    event_tracer = TangoEventTracer()

    # Subscribe to the RM attribute
    event_tracer.subscribe_event(rm_device, "stationsData")

    # Wait for the event
    assert_that(event_tracer).described_as(
        "ResourceMonitoring stationsData should publish an updated event"
    ).within_timeout(10).has_change_event_occurred(
        rm_device, "stationsData"
    )

    # Get the latest value from the event tracer
    latest_event = event_tracer.get_last_event(rm_device, "stationsData")
    parsed_value = json.loads(latest_event.value)

    expected_value = {
        "stations": {
            "station_1": {"subarray_allocation": 1},
            "station_2": {"subarray_allocation": 1},
            "station_3": {"subarray_allocation": 1},
        }
    }

    assert_that(parsed_value).is_equal_to(expected_value)
"""Test TMC-MCCS TelescopeOn functionality"""

import pytest
from pytest_bdd import given, scenario, then, when
from tango import DevState

from tests.resources.test_harness.helpers import get_master_device_simulators


@pytest.mark.tmc_mccs
@scenario(
    "../features/tmc_mccs/xtp-33991_tmc_mccs_on.feature",
    "StartUp Telescope with TMC and MCCS devices",
)
def test_tmc_mccs_telescope_on():
    """
    Test case to verify TMC-MCCS TelescopeOn() functionality
    """


@given("a Telescope consisting of TMC,MCCS,simulated SDP and simulated CSP")
def given_a_tmc(central_node_low, simulator_factory):
    """
    Given a TMC

    Args:
        simulator_factory: fixture for SimulatorFactory class,
        which provides simulated subarray and master devices
        event_recorder: fixture for EventRecorder class

    """
    (csp_master_sim, _, _) = get_master_device_simulators(simulator_factory)

    assert central_node_low.central_node.ping() > 0
    assert central_node_low.mccs_master.ping() > 0
    assert central_node_low.subarray_devices["mccs_subarray"].ping() > 0
    assert csp_master_sim.ping() > 0


@when("I startup the telescope")
def invoke_telescope_on(central_node_low):
    """A method to invoke TelescopeOn command"""
    central_node_low.move_to_on()


@then("the MCCS should transition to ON state")
def check_mccs_is_on(central_node_low, event_recorder):
    """A method to check MCCS controller and MCCS subarray states"""
    event_recorder.subscribe_event(central_node_low.mccs_master, "State")
    event_recorder.subscribe_event(
        central_node_low.subarray_devices["mccs_subarray"], "State"
    )
    assert event_recorder.has_change_event_occurred(
        central_node_low.mccs_master,
        "State",
        DevState.ON,
    )
    assert event_recorder.has_change_event_occurred(
        central_node_low.subarray_devices["mccs_subarray"],
        "State",
        DevState.ON,
    )


@then("the telescope state should change to ON")
def check_telescopestate(central_node_low, event_recorder):
    """A method to check CentralNode's telescopeState"""
    event_recorder.subscribe_event(
        central_node_low.central_node, "telescopeState"
    )
    assert event_recorder.has_change_event_occurred(
        central_node_low.central_node,
        "telescopeState",
        DevState.ON,
    )

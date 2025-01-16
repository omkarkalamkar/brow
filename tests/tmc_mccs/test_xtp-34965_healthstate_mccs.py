"""Test case for verifying TMC TelescopeHealthState transition based on MCCS
 Controller HealthState."""

import pytest
from pytest_bdd import given, parsers, scenario, when
from ska_tango_base.control_model import HealthState
from tango import DevState

from tests.conftest import adjust_controller_to_degraded_state
from tests.resources.test_harness.central_node_low import CentralNodeWrapperLow
from tests.resources.test_harness.constant import mccs_controller
from tests.resources.test_harness.helpers import (
    get_device_simulator_with_given_name,
)
from tests.resources.test_harness.simulator_factory import SimulatorFactory


@pytest.mark.tmc_mccs
@scenario(
    "../features/tmc_mccs/xtp-34965_healthstate_mccs.feature",
    "Verify CentralNode TelescopeHealthState",
)
def test_telescope_state_mccs_controller():
    """This test case sets up a Telescope consisting of TMC-MCCS, emulated CSP,
    and emulated SDP. It then changes the health state of specified simulator
    devices and checks if the telescope's health state is
    updated accordingly."""


@given("a Telescope consisting of TMC, MCCS, emulated SDP and emulated CSP")
def given_telescope_setup_with_simulators(
    central_node_low: CentralNodeWrapperLow,
    simulator_factory: SimulatorFactory,
):
    """Method to check TMC real devices and sub-system simulators

    Args:
        central_node_low (CentralNodeWrapperLow): Fixture for a
        TMC CentralNode under test
        simulator_factory (SimulatorFactory): Fixture for SimulatorFactory
        class, which provides simulated subarray and master devices
    """
    simulated_devices = get_device_simulator_with_given_name(
        simulator_factory, ["csp master", "sdp master"]
    )
    if len(simulated_devices) == 2:
        csp_master_sim = simulated_devices[0]
        sdp_master_sim = simulated_devices[1]
        assert csp_master_sim.ping() > 0
        assert sdp_master_sim.ping() > 0
    assert central_node_low.central_node.ping() > 0
    assert central_node_low.mccs_master.ping() > 0
    assert central_node_low.subarray_devices["mccs_subarray"].ping() > 0


@given("the Telescope is in ON state")
def check_telescope_is_in_on_state(
    central_node_low: CentralNodeWrapperLow, event_recorder
) -> None:
    """Ensure telescope is in ON state."""

    # The Admin mode for MCCS is set in the `move_to_on` method.
    central_node_low.move_to_on()
    event_recorder.subscribe_event(
        central_node_low.central_node, "telescopeState"
    )
    assert event_recorder.has_change_event_occurred(
        central_node_low.central_node,
        "telescopeState",
        DevState.ON,
        lookahead=10,
    )


@when(parsers.parse("The {devices} health state changes to {health_state}"))
def set_simulator_devices_health_states(
    devices: str,
    health_state: str,
    simulator_factory: SimulatorFactory,
):
    """Method to set the health state of specified simulator devices.

    Args:
        devices (list): Names of the devices whose health state will change.
        health_state (list): The new health states for the devices.
        simulator_factory (SimulatorFactory): Fixture for SimulatorFactory
          class.
        controller: The controller instance to adjust.
    """
    # Fetch the controller from the simulator factory or define it
    controller = get_device_simulator_with_given_name(
        simulator_factory, ["mccs master"]
    )[0]

    adjust_controller_to_degraded_state(controller)
    # Split the devices string into individual devices
    devices_list = devices.split(",")
    health_state_list = health_state.split(",")

    sim_devices_list = get_device_simulator_with_given_name(
        simulator_factory, devices_list
    )
    for sim_device, sim_health_state_val in list(
        zip(sim_devices_list, health_state_list)
    ):
        # Check if the device is not the Mccs controller
        if sim_device.dev_name not in [mccs_controller]:
            sim_device.SetDirectHealthState(HealthState[sim_health_state_val])


# @then -> ../conftest.py

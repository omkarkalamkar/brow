"""Test case for verifying TMC TelescopeHealthState transition based on SDP
 Controller HealthState."""

import pytest
from pytest_bdd import given, parsers, scenario, when
from ska_tango_base.control_model import HealthState

from tests.resources.test_harness.central_node_low import CentralNodeWrapperLow
from tests.resources.test_harness.constant import low_sdp_master
from tests.resources.test_harness.helpers import (
    get_device_simulator_with_given_name,
)
from tests.resources.test_harness.simulator_factory import SimulatorFactory


@pytest.mark.tmc_sdp_unhappy_path
@scenario(
    "../features/tmc_sdp/xtp-34895_health_state_sdp.feature",
    "Verify TMC TelescopeHealthState transition based on SDP Controller"
    + " HealthState",
)
def test_telescope_state_sdp_controller():
    """This test case sets up a Telescope consisting of TMC-SDP, emulated CSP,
    and emulated MCCS. It then changes the health state of specified simulator
    devices and checks if the telescope's health state is
    updated accordingly."""


@given("a Telescope consisting of TMC, SDP, simulated CSP and simulated MCCS")
def given_telescope_setup_with_simulators(
    central_node_low: CentralNodeWrapperLow,
    simulator_factory: SimulatorFactory,
):
    """Method to check TMC real devices and sub-system simulators

    Args:
        central_node_low (CentralNodeWrapperLow): fixture for a
        TMC CentralNode under test
        simulator_factory (_type_):fixture for SimulatorFactory class,
        which provides simulated subarray and master devices
    """
    simulated_devices = get_device_simulator_with_given_name(
        simulator_factory, ["csp master", "mccs master"]
    )
    if len(simulated_devices) == 2:
        csp_master_sim = simulated_devices[0]
        mccs_master_sim = simulated_devices[1]
        assert csp_master_sim.ping() > 0
        assert mccs_master_sim.ping() > 0
    assert central_node_low.central_node.ping() > 0
    assert central_node_low.sdp_master.ping() > 0
    assert central_node_low.subarray_devices["sdp_subarray"].ping() > 0


@when(parsers.parse("The {devices} health state changes to {health_state}"))
def set_simulator_devices_health_states(
    devices: str, health_state: str, simulator_factory: SimulatorFactory
):
    """Method to set the health state of specified simulator devices.

    Args:
        devices (list): Names of the devices whose health state will change.
        health_state (list): The new health states for the devices.
        simulator_factory (SimulatorFactory): Fixture for SimulatorFactory
          class.
    """
    # Split the devices string into individual devices
    devices_list = devices.split(",")
    health_state_list = health_state.split(",")

    sim_devices_list = get_device_simulator_with_given_name(
        simulator_factory, devices_list
    )
    for sim_device, sim_health_state_val in list(
        zip(sim_devices_list, health_state_list)
    ):
        # Check if the device is not the SDP controller
        if sim_device.dev_name not in [low_sdp_master]:
            sim_device.SetDirectHealthState(HealthState[sim_health_state_val])

"""Test TMC-SDP TelescopeOn functionality"""

import pytest
from pytest_bdd import given, scenario, then, when
from tango import DevState

from tests.resources.test_harness.helpers import get_master_device_simulators


@pytest.mark.tmc_sdp
@scenario(
    "../features/tmc_sdp/xtp-29228_start_up_tmc_sdp.feature",
    "Start up the telescope having TMC and SDP subsystems",
)
def test_tmc_sdp_telescope_on():
    """
    Test case to verify TMC-SDP TelescopeOn() functionality
    """


@given("a Telescope consisting of TMC, SDP, simulated CSP and simulated MCCS")
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
    assert central_node_low.sdp_master.ping() > 0
    assert central_node_low.subarray_devices["sdp_subarray"].ping() > 0
    assert csp_master_sim.ping() > 0
    assert central_node_low.are_sdp_components_online()


@when("I start up the telescope")
def invoke_telescope_on(central_node_low):
    """A method to invoke TelescopeOn command"""
    central_node_low.move_to_on()


@then("the SDP must go to ON state")
def check_sdp_is_on(central_node_low, event_recorder):
    """A method to check SDP controller and SDP subarray states"""
    event_recorder.subscribe_event(central_node_low.sdp_master, "State")
    event_recorder.subscribe_event(
        central_node_low.subarray_devices["sdp_subarray"], "State"
    )
    assert event_recorder.has_change_event_occurred(
        central_node_low.sdp_master,
        "State",
        DevState.ON,
    )
    assert event_recorder.has_change_event_occurred(
        central_node_low.subarray_devices["sdp_subarray"],
        "State",
        DevState.ON,
    )


@then("telescope state is ON")
def check_telescopestate(central_node_low, event_recorder):
    """A method to check CentralNode telescopeState"""
    event_recorder.subscribe_event(
        central_node_low.central_node, "telescopeState"
    )
    assert event_recorder.has_change_event_occurred(
        central_node_low.central_node,
        "telescopeState",
        DevState.ON,
    )

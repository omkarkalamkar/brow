"""Test module for TMC-SDP ShutDown functionality"""
import pytest
from pytest_bdd import given, scenario, then, when
from tango import DevState

from tests.resources.test_harness.helpers import get_master_device_simulators


@pytest.mark.tmc_csp
@scenario(
    "../features/tmc_csp/xtp-29686_standby.feature",
    "Standby the telescope having TMC and CSP subsystems",
)
def test_tmc_csp_standby_telescope():
    """
    Test case to verify TMC-CSP Standby functionality
    Glossary:
        - "central_node_low": fixture for a TMC CentralNode under test
        - "simulator_factory": fixture for SimulatorFactory class,
        which provides simulated subarray and master devices
        - "event_recorder": fixture for EventRecorder class
    """


@given("a Telescope consisting of TMC,CSP,simulated SDP and simulated MCCS")
def given_the_sut(central_node_low, subarray_node_low, simulator_factory):
    """
    Given a TMC and CSP in ON state
    """
    (_, sdp_master_sim, _) = get_master_device_simulators(simulator_factory)

    assert central_node_low.central_node.ping() > 0
    assert central_node_low.sdp_master.ping() > 0
    assert subarray_node_low.subarray_devices["sdp_subarray"].ping() > 0
    assert sdp_master_sim.ping() > 0


@given("telescope state is ON")
def check_tmc_csp_state_is_on(
    central_node_low, subarray_node_low, event_recorder
):
    """A method to check CentralNode.telescopeState"""
    event_recorder.subscribe_event(
        central_node_low.central_node, "telescopeState"
    )
    event_recorder.subscribe_event(central_node_low.csp_master, "State")
    event_recorder.subscribe_event(
        subarray_node_low.subarray_devices["csp_subarray"], "State"
    )
    central_node_low.move_to_on()
    assert event_recorder.has_change_event_occurred(
        central_node_low.csp_master,
        "State",
        DevState.ON,
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_devices["csp_subarray"],
        "State",
        DevState.ON,
    )
    assert event_recorder.has_change_event_occurred(
        central_node_low.central_node,
        "telescopeState",
        DevState.ON,
    )


@when("I invoke TelescopeStandby command")
def move_csp_to_standby(central_node_low):
    """A method to put CSP to STANDBY"""
    central_node_low.set_standby()


@then("telescope state is STANDBY")
def check_telescope_state_standby(central_node_low, event_recorder):
    """A method to check CentralNode.telescopeState"""
    assert event_recorder.has_change_event_occurred(
        central_node_low.central_node,
        "telescopeState",
        DevState.STANDBY,
    )


@then("the csp subarray and controller stays in ON state")
def check_csp_subarray_is_on(central_node_low, subarray_node_low):
    """A method to check CSP State"""
    assert (
        subarray_node_low.subarray_devices["csp_subarray"].State()
        == DevState.ON
    )
    assert central_node_low.csp_master.State() == DevState.ON

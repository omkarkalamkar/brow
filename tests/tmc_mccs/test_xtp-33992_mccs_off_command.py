"""Test module for TMC-MCCS ShutDown functionality"""

import pytest
from pytest_bdd import given, scenario, then, when
from tango import DevState


@pytest.mark.tmc_mccs
@scenario(
    "../features/tmc_mccs/xtp-33992_tmc_mccs_off.feature",
    "Switch off the telescope having TMC and MCCS subsystems",
)
def test_tmc_mccs_shutdown_telescope():
    """
    Test case to verify TMC-MCCS ShutDown functionality
    Glossary:
        - "central_node_low": fixture for a TMC CentralNode under test
        - "simulator_factory": fixture for SimulatorFactory class,
        which provides simulated subarray and master devices
        - "event_recorder": fixture for EventRecorder class
    """


@given("a Telescope consisting of TMC,MCCS,simulated SDP and simulated CSP")
def check_tmc_and_mccs_is_on(central_node_low, event_recorder):
    """
    Given a TMC and MCCS in ON state
    """
    event_recorder.subscribe_event(
        central_node_low.central_node, "telescopeState"
    )
    event_recorder.subscribe_event(central_node_low.mccs_master, "State")
    event_recorder.subscribe_event(
        central_node_low.subarray_devices["mccs_subarray"], "State"
    )

    if central_node_low.telescope_state != "ON":
        central_node_low.move_to_on()

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


@given("telescope state is ON")
def check_telescope_state_is_on(central_node_low, event_recorder):
    """A method to check CentralNode's telescopeState"""
    assert event_recorder.has_change_event_occurred(
        central_node_low.central_node,
        "telescopeState",
        DevState.ON,
    )


@when("I switch off the telescope")
def move_mccs_to_off(central_node_low):
    """A method to put MCCS to OFF"""
    central_node_low.move_to_off()


@then("the MCCS must go to OFF State")
def check_mccs_is_off(central_node_low, event_recorder):
    """A method to check MCCS State"""
    assert event_recorder.has_change_event_occurred(
        central_node_low.mccs_master,
        "State",
        DevState.OFF,
    )


@then("telescope state is OFF")
def check_telescope_state_off(central_node_low, event_recorder):
    """A method to check CentralNode;s telescopeState"""
    assert event_recorder.has_change_event_occurred(
        central_node_low.central_node,
        "telescopeState",
        DevState.OFF,
    )

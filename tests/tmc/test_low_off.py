"""
Module: test_low_off

This module defines a Pytest test class to verify the behavior of the
Off command on a Telescope Monitoring and Control (TMC) CentralNode Low.
The test includes checking the transitions triggered by the Off command and
validating the completion transitions assuming that external subsystems work
fine.
"""

import pytest
from assertpy import assert_that
from pytest_bdd import scenario, then, when
from ska_integration_test_harness.facades.csp_facade import CSPFacade
from ska_integration_test_harness.facades.mccs_facade import MCCSFacade
from ska_integration_test_harness.facades.sdp_facade import SDPFacade
from ska_integration_test_harness.facades.tmc_facade import TMCFacade
from ska_tango_testing.integration import TangoEventTracer
from tango import DevState

# Constants
TIMEOUT = 60


@pytest.mark.SKA_low
@scenario(
    "../features/tmc/check_off_command.feature",
    "Switch off the low telescope",
)
def test_telescope_off_command_flow():
    """
    Test case to verify OFF command on low telescope
    """


@when("I invoke the OFF command on the telescope")
def send_telescope_off_command(
    event_tracer: TangoEventTracer,
    tmc: TMCFacade,
):
    """Send the OFF command to the telescope."""
    event_tracer.clear_events()
    tmc.move_to_off(wait_termination=False)


@then("the SDP and MCCS go to OFF state")
def check_telescope_state_off(
    tmc: TMCFacade,
    sdp: SDPFacade,
    mccs: MCCSFacade,
    event_tracer: TangoEventTracer,
):
    """A method to check CentralNode.telescopeState"""
    assert_that(event_tracer).described_as(
        "FAILED ASSUMPTION AFTER OFF COMMAND: "
        "SDP devices"
        "are expected to be in State OFF",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        sdp.sdp_master,
        "State",
        DevState.OFF,
    ).has_change_event_occurred(
        sdp.sdp_subarray,
        "State",
        DevState.OFF,
    )

    assert_that(event_tracer).described_as(
        "FAILED ASSUMPTION AFTER OFFCOMMAND: "
        "MCCS devices"
        "are expected to be in State OFF",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        mccs.mccs_controller,
        "State",
        DevState.OFF,
    ).has_change_event_occurred(
        mccs.mccs_subarray,
        "State",
        DevState.OFF,
    )

    assert_that(event_tracer).described_as(
        "FAILED ASSUMPTION AFTER STANDBY COMMAND: "
        "Central Node device"
        f"({tmc.central_node.dev_name()}) "
        "is expected to be in TelescopeState UNKNOWN",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        tmc.central_node,
        "telescopeState",
        DevState.UNKNOWN,
    )


@then("the CSP remains in ON state")
def check_csp_on_state(
    csp: CSPFacade,
    event_tracer: TangoEventTracer,
):
    """Check CSP remains in ON state"""

    assert_that(event_tracer).described_as(
        "FAILED ASSUMPTION AFTER OFF COMMAND: "
        "CSP devices"
        "are expected to be in State ON",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        csp.csp_master,
        "State",
        DevState.ON,
    ).has_change_event_occurred(
        csp.csp_subarray,
        "State",
        DevState.ON,
    )

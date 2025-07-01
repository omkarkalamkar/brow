"""
Module: test_low_on

This module defines a Pytest test  to verify the behavior of the
On command on a Telescope Monitoring and Control (TMC) CentralNode Low.
The test includes checking the transitions triggered by the On command and
validating the completion transitions assuming that external subsystems work
fine.
"""

import pytest
from assertpy import assert_that
from pytest_bdd import given, scenario, then, when
from ska_control_model import AdminMode
from ska_integration_test_harness.facades.csp_facade import CSPFacade
from ska_integration_test_harness.facades.mccs_facade import MCCSFacade
from ska_integration_test_harness.facades.sdp_facade import SDPFacade
from ska_integration_test_harness.facades.tmc_facade import TMCFacade
from ska_tango_testing.integration import TangoEventTracer
from tango import DeviceProxy, DevState

from tests.resources.test_harness.constant import mccs_controller

# Constants
TIMEOUT = 100


@pytest.mark.SKA_low
@scenario(
    "../features/tmc/check_on_command.feature",
    "Starting up low telescope",
)
def test_telescope_on_command_flow():
    """
    Test case to verify ON command on low telescope
    """


@pytest.mark.aki
@scenario(
    "../features/tmc/check_on_command.feature",
    "Starting up low telescope if one subsystem in adminmode ENGINEERING",
)
def test_telescope_on_command_sdp_adminmode_engineering():
    """Test case to verify on command if sdp in adminmode ENGINEERING"""


@given("MCCS controller is in adminmode ENGINEERING")
def set_adminmode_mccs():
    """Set the adminmode of mccs"""
    mccs_proxy = DeviceProxy(mccs_controller)
    mccs_proxy.adminMode = AdminMode.ENGINEERING
    assert mccs_proxy.adminMode == AdminMode.ENGINEERING


@when("I invoke the ON command on the telescope")
def send_telescope_on_command(
    event_tracer: TangoEventTracer,
    tmc: TMCFacade,
):
    """Send the ON command to the telescope."""
    event_tracer.clear_events()
    tmc.move_to_on(wait_termination=True)


@then("the SDP, CSP and MCCS go to the ON state")
def verify_on_state(
    event_tracer: TangoEventTracer,
    csp: CSPFacade,
    sdp: SDPFacade,
    mccs: MCCSFacade,
):
    """A method to check Subsystem State"""
    assert_that(event_tracer).described_as(
        "FAILED ASSUMPTION AFTER ON COMMAND: "
        "CSP devices"
        "are expected to be in State ON",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        csp.csp_master,
        "State",
        DevState.ON,
    )

    assert_that(event_tracer).described_as(
        "FAILED ASSUMPTION AFTER ON COMMAND: "
        "SDP devices"
        "are expected to be in State ON",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        sdp.sdp_master,
        "State",
        DevState.ON,
    )

    assert_that(event_tracer).described_as(
        "FAILED ASSUMPTION AFTER ON COMMAND: "
        "MCCS devices"
        "are expected to be in State ON",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        mccs.mccs_controller,
        "State",
        DevState.ON,
    )


@then("the telescope go to the ON state")
def check_telescope_state(tmc: TMCFacade, event_tracer: TangoEventTracer):
    """A method to check CentralNode.telescopeState"""

    assert_that(event_tracer).described_as(
        "FAILED ASSUMPTION AFTER ON COMMAND: "
        "Central Node device"
        f"({tmc.central_node.dev_name()}) "
        "is expected to be in TelescopeState ON",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        tmc.central_node,
        "telescopeState",
        DevState.ON,
    )

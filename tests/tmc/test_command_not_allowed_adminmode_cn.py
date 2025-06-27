"""Test the command not allowed when adminmode NOT_FITTED/OFFLINE"""
import time

import pytest
import tango
from pytest_bdd import parsers, scenario, then, when
from ska_control_model import AdminMode
from ska_integration_test_harness.facades.tmc_facade import TMCFacade

from tests.resources.test_harness.constant import (
    low_csp_master,
    low_sdp_master,
    mccs_controller,
)
from tests.resources.test_harness.utils.my_file_json_input import (
    MyFileJSONInput,
)

TIMEOUT = 100
SUBSYSTEM_DEVICES = {
    "cspcontroller": low_csp_master,
    "sdpcontroller": low_sdp_master,
    "mccscontroller": mccs_controller,
}


@pytest.mark.aki
@scenario(
    "../features/tmc/check_cmd_not_allowed_adminmode.feature",
    "Command not allowed from CentralNode when subsystem adminmode "
    "is OFFLINE/NOT_FITTED",
)
def test_command_not_allowed():
    """
    Test case to verify command not allowed when adminMode OFFLINE/NOT_FITTED
    """


@when(
    parsers.parse(
        "the adminmode of subsystem controller {subsystem} is {adminmode}"
    )
)
def set_admin_mode(subsystem, adminmode):
    """Set the admin mode of a given subsystem."""
    device_name = SUBSYSTEM_DEVICES[subsystem]
    proxy = tango.DeviceProxy(device_name)
    mode_enum = AdminMode[adminmode]
    proxy.adminMode = mode_enum
    time.sleep(0.1)
    # Optional: Assert adminMode is set
    assert proxy.adminMode == mode_enum


@when(parsers.parse("I invoke command {command} on centralnode"))
def invoke_assignresources(
    tmc: TMCFacade,
    command,
):
    """Invokes command on TMC"""
    pytest.command_failed_exception = None

    try:
        if "AssignResources" in command:
            assign_input = MyFileJSONInput(
                "centralnode", "assign_resources_low"
            )
            tmc.assign_resources(assign_input)
        elif "ReleaseResources" in command:
            release_input = MyFileJSONInput(
                "centralnode", "release_resources_low"
            )
            tmc.release_resources(release_input)
        elif "On" in command:
            tmc.move_to_on()
        elif "Off" in command:
            tmc.move_to_off()
        else:
            raise ValueError(f"Unsupported command: {command}")
    except (tango.DevFailed, RuntimeError, ValueError) as e:
        pytest.command_failed_exception = e


@then("the centralnode rejects the command")
def centralnode_rejects_command():
    """Assert the previously invoked command was rejected due to adminMode."""
    exc = getattr(pytest, "command_failed_exception", None)
    assert (
        exc is not None
    ), "Expected the command to be rejected, but it succeeded"

    expected_message = (
        "One or more controller devices are in adminMode OFFLINE or NOT-FITTED"
    )

    # Handle both single and multiple DevError cases
    dev_errors = exc.args[0]
    if not isinstance(dev_errors, (list, tuple)):
        dev_errors = [dev_errors]

    error_messages = [err.desc for err in dev_errors]
    assert any(
        expected_message in msg for msg in error_messages
    ), f"Expected rejection message not found. Got: {error_messages}"
    # perform tear down
    for _, device in SUBSYSTEM_DEVICES.items():
        proxy = tango.DeviceProxy(device)
        proxy.adminMode = AdminMode.ONLINE

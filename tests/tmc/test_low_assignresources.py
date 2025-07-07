"""
Module: test_low_assignresources
"""
import pytest
from assertpy import assert_that
from pytest_bdd import given, scenario, then, when
from ska_control_model import AdminMode, ObsState
from ska_integration_test_harness.facades.csp_facade import CSPFacade
from ska_integration_test_harness.facades.mccs_facade import MCCSFacade
from ska_integration_test_harness.facades.sdp_facade import SDPFacade
from ska_integration_test_harness.facades.tmc_facade import TMCFacade
from ska_tango_testing.integration import TangoEventTracer
from tango import DeviceProxy

from tests.resources.test_harness.constant import (
    COMMAND_COMPLETED,
    low_sdp_subarray1,
)
from tests.resources.test_harness.helpers import check_subarray_obsstate
from tests.resources.test_harness.utils.my_file_json_input import (
    MyFileJSONInput,
)

TIMEOUT = 100


@pytest.mark.SKA_low
@scenario(
    "../features/tmc/check_assignresources_command.feature",
    "Assign resources to Low subarray",
)
def test_telescope_assign_resources():
    """
    Test case to verify AssignResources functionality
    """


@pytest.mark.SKA_low
@scenario(
    "../features/tmc/check_assignresources_command.feature",
    "Assign resources to Low subarray if one subarray "
    "in adminmode ENGINEERING",
)
def test_assignresources_command_sdp_adminmode_engineering():
    """Test case to verify assignresources
    command if sdp in adminmode ENGINEERING"""


@given("subarray is in the EMPTY ObsState")
def subarray_in_empty_obsstate(
    tmc: TMCFacade,
):
    """Checks if SubarrayNode's obsState attribute value is EMPTY"""
    assert tmc.subarray_node.obsState == ObsState.EMPTY


@given("sdp subarray is in adminmode ENGINEERING")
def set_adminmode_sdp():
    """Set the adminmode of sdp subarray"""
    sdp_proxy = DeviceProxy(low_sdp_subarray1)
    sdp_proxy.adminMode = AdminMode.ENGINEERING
    assert sdp_proxy.adminMode == AdminMode.ENGINEERING


@when("I assign resources to the subarray")
def invoke_assignresources(
    tmc: TMCFacade,
    event_tracer: TangoEventTracer,
):
    """Invokes AssignResources command on TMC"""
    assign_input = MyFileJSONInput("centralnode", "assign_resources_low")

    _, unique_id = tmc.assign_resources(assign_input)

    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "WHEN" STEP: '
        "'the subarray is in IDLE obsState'"
        "TMC Central Node device"
        f"({tmc.central_node.dev_name()}) "
        "is expected have longRunningCommand as"
        '(unique_id,(ResultCode.OK,"Command Completed"))',
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        tmc.central_node,
        "longRunningCommandResult",
        (unique_id[0], COMMAND_COMPLETED),
    )


@then(
    "the TMC, CSP, SDP, and MCCS subarrays"
    + " transition to the RESOURCING obsState"
)
def subsystem_subarrays_in_resourcing(
    tmc: TMCFacade,
    csp: CSPFacade,
    sdp: SDPFacade,
    mccs: MCCSFacade,
    event_tracer: TangoEventTracer,
):
    """Check if all subarrays are in RESOURCING obsState."""
    check_subarray_obsstate(
        tmc, csp, sdp, mccs, event_tracer, ObsState.RESOURCING
    )


@then("the TMC, CSP, SDP, and MCCS subarrays transition to the IDLE obsState")
def subsystems_subarray_idle(
    tmc: TMCFacade,
    csp: CSPFacade,
    sdp: SDPFacade,
    mccs: MCCSFacade,
    event_tracer: TangoEventTracer,
):
    """Check if all subarrays are in IDLE obsState."""
    check_subarray_obsstate(tmc, csp, sdp, mccs, event_tracer, ObsState.IDLE)
    sdp_proxy = DeviceProxy(low_sdp_subarray1)
    if sdp_proxy.adminMode != AdminMode.ONLINE:
        sdp_proxy.adminMode = AdminMode.ONLINE

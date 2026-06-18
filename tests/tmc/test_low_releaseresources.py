"""
Module: test_low_releaseresources
"""
import pytest
from assertpy import assert_that
from pytest_bdd import given, scenario, then, when
from ska_control_model import ObsState
from ska_integration_test_harness.facades.csp_facade import CSPFacade
from ska_integration_test_harness.facades.mccs_facade import MCCSFacade
from ska_integration_test_harness.facades.sdp_facade import SDPFacade
from ska_integration_test_harness.facades.tmc_facade import TMCFacade
from ska_tango_testing.integration import TangoEventTracer

from tests.resources.test_harness.constant import COMMAND_COMPLETED
from tests.resources.test_harness.helpers import check_subarray_obsstate
from tests.resources.test_harness.utils.my_file_json_input import (
    MyFileJSONInput,
)

TIMEOUT = 100


@pytest.mark.SKA_low
@scenario(
    "features/tmc/check_releaseresource.feature",
    "Release resources from Low subarray",
)
def test_telescope_releaseresources():
    """
    Test case to verify releaseResources functionality
    """


@given("subarray is in the IDLE obsState")
def invoke_assignresources(
    tmc: TMCFacade,
    csp: CSPFacade,
    sdp: SDPFacade,
    mccs: MCCSFacade,
    event_tracer: TangoEventTracer,
):
    """Invokes AssignResources command on TMC"""
    assign_input = MyFileJSONInput("centralnode", "assign_resources_low")

    _, unique_id = tmc.assign_resources(assign_input)

    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "GIVEN" STEP: '
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
    check_subarray_obsstate(tmc, csp, sdp, mccs, event_tracer, ObsState.IDLE)


@when("I release all resources assigned to it")
def invoke_release_resources(
    tmc: TMCFacade,
    event_tracer: TangoEventTracer,
):
    """Invokes ReleaseResources command on TMC"""
    release_input = MyFileJSONInput(
        "centralnode",
        "release_resources_low",
    )
    _, unique_id = tmc.release_resources(release_input)
    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "WHEN" STEP: '
        "'the subarray is in EMPTY obsState'"
        "TMC Central Node device"
        f"({tmc.central_node.dev_name()}) "
        "is expected have longRunningCommand as"
        '(unique_id,(ResultCode.OK,"Command Completed"))',
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        tmc.central_node,
        "longRunningCommandResult",
        (unique_id[0], COMMAND_COMPLETED),
    )


@then("the TMC, CSP, SDP, and MCCS subarrays transition to the EMPTY obsState")
def subsystem_subarrays_in_empty(
    tmc: TMCFacade,
    csp: CSPFacade,
    sdp: SDPFacade,
    mccs: MCCSFacade,
    event_tracer: TangoEventTracer,
):
    """Checks if Subarray's obsState attribute value is EMPTY"""
    check_subarray_obsstate(tmc, csp, sdp, mccs, event_tracer, ObsState.EMPTY)

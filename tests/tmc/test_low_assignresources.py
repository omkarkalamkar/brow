"""
Module: test_low_assignresources
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


@pytest.mark.testing
@pytest.mark.SKA_low
@scenario(
    "../features/tmc/check_assignresources_command.feature",
    "Assign resources to Low subarray",
)
def test_telescope_assign_resources():
    """
    Test case to verify AssignResources functionality
    """


# @given("the telescope is in the ON state") -> conftest


@given("subarray is in the EMPTY ObsState")
def subarray_in_empty_obsstate(
    tmc: TMCFacade,
):
    """Checks if SubarrayNode's obsState attribute value is EMPTY"""
    assert tmc.subarray_node.obsState == ObsState.EMPTY


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
    assigned_resources_json = MyFileJSONInput(
        "centralnode", "assign_resources_low"
    ).as_str()
    assert_that(event_tracer).described_as(
        "FAILED ASSUMPTION AFTER ASSIGN RESOURCES: "
        "Subarray Node device"
        f"({tmc.subarray_node.dev_name()}) "
        "is expected to have assignedResources input json",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        tmc.subarray_node,
        "assignedResources",
        assigned_resources_json,
    )

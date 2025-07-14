"""Test module to validate timeout behavior in the Restart command
when a defective subsystem (CSP, SDP, or MCCS) causes the command to fail.
"""
import json

import pytest
from assertpy import assert_that
from pytest_bdd import given, parsers, scenario, then, when
from ska_control_model import ObsState
from ska_integration_test_harness.facades.csp_facade import CSPFacade
from ska_integration_test_harness.facades.mccs_facade import MCCSFacade
from ska_integration_test_harness.facades.sdp_facade import SDPFacade
from ska_integration_test_harness.facades.tmc_facade import TMCFacade
from ska_integration_test_harness.inputs.test_harness_inputs import (
    TestHarnessInputs,
)
from ska_tango_testing.integration import TangoEventTracer

from tests.conftest import SubarrayTestContextData, _setup_event_subscriptions
from tests.resources.test_harness.constant import TIMEOUT_DEFECT

TIMEOUT = 60


@pytest.mark.SKA_fault
@pytest.mark.SKA_low
@scenario(
    "../features/tmc/error_propagation_timeout_abort.feature",
    "Timeout Reported by TMC Low Reset Command for Defective Subarray",
)
def test_tmc_command_timeout():
    """
    Test case to verify TMC Timeout functionality.
    """


exception_messages = {
    "CSP": (
        '[3, "Exception occurred on the following devices: '
        "low-tmc/subarray-leaf-node-csp/01: "
        'Timeout has occurred, command failed"]'
    ),
    "SDP": (
        '[3, "Exception occurred on the following devices: '
        "low-tmc/subarray-leaf-node-sdp/01: "
        'Timeout has occurred, command failed"]'
    ),
    "MCCS": (
        '[3, "Exception occurred on the following devices: '
        "low-tmc/subarray-leaf-node-mccs/01: "
        'Timeout has occurred, command failed"]'
    ),
}


@given("TMC subarray is in ABORTED ObsState")
def subarray_in_aborted_state(
    context_data: SubarrayTestContextData,
    tmc: TMCFacade,
    sdp: SDPFacade,
    csp: CSPFacade,
    mccs: MCCSFacade,
    event_tracer: TangoEventTracer,
    default_commands_inputs: TestHarnessInputs,
):
    """Ensure the subarray is in the initial obsstate state."""
    _setup_event_subscriptions(tmc, csp, sdp, mccs, event_tracer)
    context_data.starting_state = ObsState.ABORTED
    tmc.force_change_of_obs_state(
        ObsState.ABORTED,
        default_commands_inputs,
        wait_termination=True,
    )


@when(
    parsers.parse(
        "Restart is invoked on a defective subsystem {defective_subsystem}"
    )
)
def execute_command_restart(
    tmc: TMCFacade,
    context_data: SubarrayTestContextData,
    csp: CSPFacade,
    sdp: SDPFacade,
    mccs: MCCSFacade,
    defective_subsystem: str,
):
    """
    Simulates a timeout by setting the specified subsystem as defective
    or delayed, then triggers Restart.
    Args:
        tmc: TMCFacade instance to execute the Restart command.
        context_data: Context object to record action being tested.
        csp: CSPFacade instance.
        sdp: SDPFacade instance.
        mccs: MCCSFacade instance.
        defective_subsystem: The name of the defective subsystem.
    """
    if defective_subsystem == "CSP":
        csp.csp_subarray.SetDefective(TIMEOUT_DEFECT)
    elif defective_subsystem == "SDP":
        sdp.sdp_subarray.SetDelayInfo(json.dumps({"Restart": 135}))
    elif defective_subsystem == "MCCS":
        mccs.mccs_controller.SetDefective(TIMEOUT_DEFECT)
    context_data.when_action_name = "Restart"
    _, pytest.unique_id = tmc.subarray_node.Restart()


@then(
    parsers.parse(
        "the Timeout is reported by subarray with error message "
        "with {defective_subsystem}"
    )
)
def error_reporting(
    tmc: TMCFacade,
    csp: CSPFacade,
    sdp: SDPFacade,
    mccs: MCCSFacade,
    event_tracer: TangoEventTracer,
    defective_subsystem: str,
):
    """Validates that TMC's SubarrayNode correctly reports the timeout via
    longRunningCommandResult.
    Args:
        tmc: TMCFacade instance.
        csp: CSPFacade instance.
        sdp: SDPFacade instance.
        mccs: MCCSFacade instance.
        event_tracer: Used to monitor Tango events for error reporting.
        defective_subsystem: The subsystem name that triggered the timeout.
    """
    event_tracer.subscribe_event(tmc.mccs_subarray_leaf_node, "obsState")

    expected_msg = exception_messages[defective_subsystem]

    assert_that(event_tracer).within_timeout(
        TIMEOUT
    ).has_change_event_occurred(
        tmc.subarray_node,
        "longRunningCommandResult",
        (pytest.unique_id[0], expected_msg),
    )

    if defective_subsystem == "CSP":
        csp.csp_subarray.SetDefective(json.dumps({"enabled": False}))
        csp.csp_subarray.Restart()
        assert_that(event_tracer).within_timeout(
            TIMEOUT
        ).has_change_event_occurred(
            csp.csp_subarray, "obsState", ObsState.EMPTY
        )
    elif defective_subsystem == "SDP":
        sdp.sdp_subarray.ResetDelayInfo()
        sdp.sdp_subarray.Restart()
        assert_that(event_tracer).within_timeout(
            135
        ).has_change_event_occurred(
            sdp.sdp_subarray, "obsState", ObsState.EMPTY
        )
    elif defective_subsystem == "MCCS":
        mccs.mccs_controller.SetDefective(json.dumps({"enabled": False}))
        mccs.mccs_subarray.Restart()
        assert_that(event_tracer).within_timeout(
            TIMEOUT
        ).has_change_event_occurred(
            mccs.mccs_subarray, "obsState", ObsState.EMPTY
        )
        assert_that(event_tracer).within_timeout(
            TIMEOUT
        ).has_change_event_occurred(
            tmc.mccs_subarray_leaf_node, "obsState", ObsState.EMPTY
        )
    event_tracer.clear_events()

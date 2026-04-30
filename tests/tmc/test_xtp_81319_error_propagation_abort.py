"""Test case to verify error propagation functionality for the Abort command

This test module checks if the TMC SubarrayNode correctly propagates errors
when the `Abort` command is invoked on a defective subsystem
(CSP, SDP, or MCCS).It ensures that the TMC transitions to the FAULT
state and logs the expected error message.
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
from tests.resources.test_harness.constant import (
    ERROR_PROPAGATION_DEFECT,
    FAILED_RESULT_DEFECT,
)

TIMEOUT = 60


@pytest.mark.SKA_low
@scenario(
    "../features/tmc/error_propagation_timeout_abort.feature",
    "Error Propagation Reported by TMC Low Abort Command for "
    "Defective Subarray",
)
def test_tmc_command_error_propagation():
    """
    Verifies TMC error propagation on Abort command
    for defective subsystems (CSP, SDP, MCCS).
    """


exception_messages = {
    "CSP": (
        '[3, "Exception occurred on the following devices: '
        "low-tmc/subarray-leaf-node-csp/01: "
        "Exception occurred on devices: low-csp/subarray/01: "
        'Exception occurred, command failed."]'
    ),
    "SDP": (
        '[3, "Exception occurred on the following devices: '
        "low-tmc/subarray-leaf-node-sdp/01: "
        "Exception occurred on devices: low-sdp/subarray/01: "
        'Exception occurred, command failed."]'
    ),
    "MCCS": (
        '[3, "Exception occurred on the following devices: '
        "low-tmc/subarray-leaf-node-mccs/01: "
        "Exception occurred on devices: low-mcss/subarray/01: "
        'Exception occurred, command failed."]'
    ),
}


@given(
    parsers.parse(
        "TMC subarray is in initial ObsState for {defective_subsystem}"
    )
)
def subarray_in_initial_state(
    context_data: SubarrayTestContextData,
    tmc: TMCFacade,
    sdp: SDPFacade,
    csp: CSPFacade,
    mccs: MCCSFacade,
    event_tracer: TangoEventTracer,
    default_commands_inputs: TestHarnessInputs,
    defective_subsystem: str,
):
    """Ensure the subarray is in the initial obsstate state.
    Args:
        context_data: Subarray test context for maintaining state.
        tmc: TMC facade for controlling the SubarrayNode.
        sdp: SDP facade.
        csp: CSP facade.
        mccs: MCCS facade.
        event_tracer: Tango event subscription handlers.
        default_commands_inputs: Default command input data.
        defective_subsystem: Name of the subsystem marked as defective."""
    _setup_event_subscriptions(tmc, csp, sdp, mccs, event_tracer)
    target_state = (
        ObsState.READY if defective_subsystem == "MCCS" else ObsState.IDLE
    )
    context_data.starting_state = target_state

    tmc.force_change_of_obs_state(
        target_state,
        default_commands_inputs,
        wait_termination=True,
    )


@when(
    parsers.parse(
        "Abort is invoked on a defective subsystem {defective_subsystem}"
    )
)
def execute_command_abort(
    tmc: TMCFacade,
    context_data: SubarrayTestContextData,
    csp: CSPFacade,
    sdp: SDPFacade,
    mccs: MCCSFacade,
    defective_subsystem: str,
):
    """
    Invoke the Abort command on the TMC SubarrayNode with a faulty subsystem.
        Args:
        tmc: TMC SubarrayNode facade.
        context_data: Subarray test context object.
        csp: CSP facade.
        sdp: SDP facade.
        mccs: MCCS facade.
        defective_subsystem: Subsystem that will simulate a failure.
    """
    if defective_subsystem == "CSP":
        csp.csp_subarray.SetDefective(ERROR_PROPAGATION_DEFECT)
    elif defective_subsystem == "SDP":
        sdp.sdp_subarray.SetDefective(FAILED_RESULT_DEFECT)
    elif defective_subsystem == "MCCS":
        mccs.mccs_subarray.SetDefective(ERROR_PROPAGATION_DEFECT)
    context_data.when_action_name = "Abort"
    _, pytest.unique_id = tmc.subarray_node.Abort()


@then("TMC SubarrayNode obsstate changes to FAULT obsState")
def verify_fault_obsstate(
    tmc: TMCFacade,
    event_tracer: TangoEventTracer,
):
    """
    Verify the subarray's transition to the FAULT observation state.
    Args:
        tmc: TMC facade for the SubarrayNode.
        event_tracer: Event tracer to verify state changes.
    """
    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "THEN" STEP: '
        "'the tmc subarray must be in the ABORTING obsState' "
        "TMC Subarray device"
        f"({tmc.subarray_node.dev_name()}) "
        "is expected to be in ABORTING obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        tmc.subarray_node,
        "obsState",
        ObsState.ABORTING,
    )

    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "THEN" STEP: '
        "'the tmc subarray must be in the FAULT obsState' "
        "TMC Subarray device"
        f"({tmc.subarray_node.dev_name()}) "
        "is expected to be in FAULT obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        tmc.subarray_node,
        "obsState",
        ObsState.FAULT,
    )


@then(
    parsers.parse(
        "the command failure is reported by subarray with error message "
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
    """Check that the error is reported in the longRunningCommandResult of
    TMC due to subsystem failure.
    Args:
        tmc: TMC facade.
        csp: CSP facade.
        sdp: SDP facade.
        mccs: MCCS facade.
        event_tracer: Event tracer for state and result validation.
        defective_subsystem: Name of the defective subsystem being tested."""

    event_tracer.subscribe_event(tmc.mccs_subarray_leaf_node, "obsState")
    event_tracer.subscribe_event(
        tmc.csp_subarray_leaf_node, "cspSubarrayObsState"
    )
    event_tracer.subscribe_event(
        tmc.sdp_subarray_leaf_node, "sdpSubarrayObsState"
    )

    expected_msg = exception_messages[defective_subsystem]

    assert_that(event_tracer).within_timeout(
        TIMEOUT
    ).has_change_event_occurred(
        tmc.subarray_node,
        "longRunningCommandResult",
        (pytest.unique_id[0], expected_msg),
    )

    # Reset subsystem and bring it to ABORTED so TMC can be restarted
    if defective_subsystem == "CSP":
        csp.csp_subarray.SetDefective(json.dumps({"enabled": False}))
        csp.csp_subarray.Abort()
        assert_that(event_tracer).within_timeout(
            TIMEOUT
        ).has_change_event_occurred(
            csp.csp_subarray, "obsState", ObsState.ABORTED
        )
        assert_that(event_tracer).within_timeout(
            TIMEOUT
        ).has_change_event_occurred(
            tmc.csp_subarray_leaf_node, "cspSubarrayObsState", ObsState.ABORTED
        )
    elif defective_subsystem == "SDP":
        sdp.sdp_subarray.SetDefective(json.dumps({"enabled": False}))
        sdp.sdp_subarray.Abort()
        assert_that(event_tracer).within_timeout(
            TIMEOUT
        ).has_change_event_occurred(
            sdp.sdp_subarray, "obsState", ObsState.ABORTED
        )
        assert_that(event_tracer).within_timeout(
            TIMEOUT
        ).has_change_event_occurred(
            tmc.sdp_subarray_leaf_node, "sdpSubarrayObsState", ObsState.ABORTED
        )
    elif defective_subsystem == "MCCS":
        mccs.mccs_subarray.SetDefective(json.dumps({"enabled": False}))
        mccs.mccs_subarray.Abort()
        assert_that(event_tracer).within_timeout(
            TIMEOUT
        ).has_change_event_occurred(
            mccs.mccs_subarray, "obsState", ObsState.ABORTED
        )
        assert_that(event_tracer).within_timeout(
            TIMEOUT
        ).has_change_event_occurred(
            tmc.mccs_subarray_leaf_node, "obsState", ObsState.ABORTED
        )
    tmc.restart()
    assert_that(event_tracer).within_timeout(
        TIMEOUT
    ).has_change_event_occurred(tmc.subarray_node, "obsState", ObsState.EMPTY)

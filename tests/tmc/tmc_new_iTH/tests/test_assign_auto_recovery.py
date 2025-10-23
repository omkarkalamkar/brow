import copy
import json
import logging

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
from ska_tango_testing.mock.placeholders import Anything

from tests.resources.test_support.constant_low import (
    FAILED_RESULT_DEFECT,
    FAILED_RESULT_DEFECT_EMPTY,
    SDP_BACK_TO_INITIAL_STATE,
)
from tests.tmc.tmc_new_iTH.conftest import TestContextData
from tests.tmc.tmc_new_iTH.utils import (
    TIMEOUT,
    reset_defects,
    setup_event_subscriptions,
)

FAILED_DEVICE_MAP = {
    "CSP": "low-tmc/subarray-leaf-node-csp/01",
    "SDP": "low-tmc/subarray-leaf-node-sdp/01",
    "MCCS": "low-tmc/subarray-leaf-node-mccs/01",
}


@pytest.mark.aki
@scenario(
    "../tmc/tmc_new_iTH/features/assignresources_auto_recovery.feature",
    "TMC Perform Auto Recovery when AssignResources Failed",
)
def test_configure_auto_recovery():
    """BDD test scenario to verify auto recovery when assignresources failed"""


@pytest.mark.aki
@scenario(
    "../tmc/tmc_new_iTH/features/assignresources_auto_recovery.feature",
    "TMC Auto Recovery Failed",
)
def test_auto_recovery_failed():
    """
    BDD test scenario for verifying auto recovery Failed
    """


@given("a subarray is in the EMPTY obsState")
def verify_tmc_subarray_observation_state_empty(
    event_tracer: TangoEventTracer,
    tmc: TMCFacade,
    csp: CSPFacade,
    sdp: SDPFacade,
    mccs: MCCSFacade,
    context_data: TestContextData,
):
    setup_event_subscriptions(tmc, csp, sdp, mccs, event_tracer)
    tmc.move_to_on(wait_termination=True)
    context_data.csp_obsstate = ObsState.EMPTY
    context_data.sdp_obsstate = ObsState.EMPTY
    context_data.mccs_obsstate = ObsState.EMPTY


@when(
    parsers.parse(
        "I AssignResources to subarray with " "defective {failed_devices}"
    )
)
def invoke_assign_resources_command(
    tmc: TMCFacade,
    sdp: SDPFacade,
    csp: CSPFacade,
    default_commands_inputs: TestHarnessInputs,
    event_tracer: TangoEventTracer,
    failed_devices: str,
):
    """Invokes configure command on the TMC Subarray."""
    # Set device defective
    for failed_device in failed_devices.split(","):
        logging.info("Setting Failed result %s", failed_device)
        if failed_device == "SDP":
            sdp.sdp_subarray.SetDefective(
                json.dumps(SDP_BACK_TO_INITIAL_STATE)
            )
        elif failed_device == "CSP":
            failed_result_defect = copy.deepcopy(FAILED_RESULT_DEFECT_EMPTY)
            failed_result_defect["target_obsstates"] = [ObsState.IDLE]
            csp.csp_subarray.SetDefective(json.dumps(failed_result_defect))
    _, pytest.unique_id = tmc.AssignResources(
        default_commands_inputs.assign_input, wait_termination=False
    )
    assert_that(event_tracer).described_as(
        "TMC Subarray Leaf Node"
        "ObsState attribute value should move "
        " to RESOURCING."
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        tmc.subarray_node,
        "obsState",
        ObsState.RESOURCING,
    )


@then(
    parsers.parse(
        "AssignResources command fails on {failed_devices} "
        "Subarray Leaf Node"
    )
)
def verify_configure_failed_on_subarray_leaf_node(
    event_tracer: TangoEventTracer, tmc: TMCFacade, failed_devices: str
):
    """Verifies that configure failed on subarray leaf node."""
    for failed_device in failed_devices.split(","):
        # if pytest.is_successive_configure:
        if failed_device == "CSP":
            error_message = (
                '[3, "Exception occurred on device: low-csp/subarray/01"]'
            )
        elif failed_device == "MCCS":
            error_message = (
                '[3, "Exception occurred on device: low-mccs/subarray/01"]'
            )
        elif failed_device == "SDP":
            error_message = '[3, "Device defective."]'
        # else:
        #     error_message = '[3, "Device defective."]'
        assert_that(event_tracer).described_as(
            "TMC Subarray Leaf Node "
            f"({tmc.subarray_node}) "
            "is expected to report a"
            "longRunningCommand successful failure."
        ).within_timeout(20).has_change_event_occurred(
            FAILED_DEVICE_MAP[failed_device],
            "longRunningCommandResult",
            (Anything, error_message),
        )


@then(
    parsers.parse(
        "auto recovery fails due to {auto_recovery_failed_devices} failure"
    )
)
def verify_auto_recovery_failed_on_subarray_leaf_node(
    event_tracer: TangoEventTracer,
    csp: CSPFacade,
    mccs: MCCSFacade,
    auto_recovery_failed_devices: str,
):
    """Verifies that configure failed on subarray leaf node."""

    for auto_recovery_failed_device in auto_recovery_failed_devices.split(","):
        if auto_recovery_failed_device == "CSP":
            # First assert configure is successful
            assert_that(event_tracer).described_as(
                "CSP Subarray Leaf Node"
                "ObsState attribute value should move "
                " to READY."
            ).within_timeout(TIMEOUT).has_change_event_occurred(
                csp.csp_subarray,
                "obsState",
                ObsState.CONFIGURING,
            )
            assert_that(event_tracer).described_as(
                "CSP Subarray Leaf Node"
                "ObsState attribute value should move "
                " to READY."
            ).within_timeout(TIMEOUT).has_change_event_occurred(
                csp.csp_subarray,
                "obsState",
                ObsState.READY,
            )
            csp.csp_subarray.SetDefective(json.dumps(FAILED_RESULT_DEFECT))
        elif auto_recovery_failed_device == "MCCS":
            # First assert configure is successful
            assert_that(event_tracer).described_as(
                "MCCS Subarray"
                "ObsState attribute value should move "
                " to CONFIGURING."
            ).within_timeout(TIMEOUT).has_change_event_occurred(
                mccs.mccs_subarray,
                "obsState",
                ObsState.CONFIGURING,
            )
            assert_that(event_tracer).described_as(
                "MCCS Subarray"
                "ObsState attribute value should move "
                " to READY."
            ).within_timeout(TIMEOUT).has_change_event_occurred(
                mccs.mccs_subarray,
                "obsState",
                ObsState.READY,
            )
            failed_result = copy.deepcopy(FAILED_RESULT_DEFECT)
            failed_result["target_obsstates"] = [ObsState.READY]
            mccs.mccs_subarray.SetDefective(json.dumps(failed_result))


@then(
    "a subarray perform auto recovery and transition Subarray Obs State "
    + "to EMPTY"
)
def verify_tmc_subarray_to_empty(
    event_tracer: TangoEventTracer, tmc: TMCFacade
):
    """Verifies that tmc subarray moved to EMPTY."""
    assert_that(event_tracer).described_as(
        "TMC Subarray Leaf Node)"
        "ObsState attribute value should move "
        " to EMPTY."
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        tmc.subarray_node,
        "obsState",
        ObsState.EMPTY,
    )


@then("TMC Subarray Obs State transition to FAULT Obs State")
def verify_tmc_subarray_to_fault(
    event_tracer: TangoEventTracer,
    tmc: TMCFacade,
    csp: CSPFacade,
    sdp: SDPFacade,
    mccs: MCCSFacade,
):
    """Verifies that tmc subarray moved to FAULT."""
    assert_that(event_tracer).described_as(
        "TMC Subarray Leaf Node)"
        "ObsState attribute value should move "
        " to FAULT."
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        tmc.subarray_node,
        "obsState",
        ObsState.FAULT,
    )
    reset_defects(csp, sdp, mccs)


@then(
    parsers.parse(
        "{failed_devices} Failure is reported on Long Running Command Result"
    )
)
def verify_tmc_subarray_lrcr_failed(
    event_tracer: TangoEventTracer,
    tmc: TMCFacade,
    csp: CSPFacade,
    sdp: SDPFacade,
    mccs: MCCSFacade,
    failed_devices: str,
):
    """Verifies that tmc subarray lrcr failed."""
    if pytest.is_successive_configure:
        failed_message = (
            "Exception occurred on the following devices: "
            "low-tmc/subarray-leaf-node-csp/01: Exception occurred "
            "on device: low-csp/subarray/01 and Recovery Successful, "
            "Subarray transitioned back to READY with previous configuration."
        )
    else:
        failed_message = (
            "Exception occurred on the following devices: "
            "low-tmc/subarray-leaf-node-sdp/01: Device defective. "
            "and Recovery Successful, "
            "Subarray transitioned back to IDLE"
        )
    assert_that(event_tracer).described_as(
        "TMC Subarray Leaf Node "
        f"({tmc.subarray_node}) "
        "is expected to report a"
        "longRunningCommand successful failure."
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        tmc.subarray_node,
        "longRunningCommandResult",
        (pytest.unique_id[0], f'[3, "{failed_message}"]'),
    )
    reset_defects(csp, sdp, mccs)

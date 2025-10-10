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
from ska_tango_base.commands import ResultCode
from ska_tango_testing.integration import TangoEventTracer
from ska_tango_testing.mock.placeholders import Anything

from tests.resources.test_support.constant_low import SDP_BACK_TO_INITIAL_STATE
from tests.tmc.tmc_new_iTH.utils import TIMEOUT, setup_event_subscriptions

FAILED_DEVICE_MAP = {
    "CSP": "low-tmc/subarray-leaf-node-csp/01",
    "SDP": "low-tmc/subarray-leaf-node-sdp/01",
    "MCCS": "low-tmc/subarray-leaf-node-mccs/01",
}


@pytest.mark.SKA_low
@scenario(
    "../tmc/tmc_new_iTH/features/configure_auto_recovery.feature",
    "TMC Perform Auto Recovery when Configure Failed",
)
def test_configure_auto_recovery():
    """BDD test scenario for verifying auto recovery when configure failed"""


@given("a subarray is in the IDLE obsState")
def verify_tmc_subarray_observation_state_idle(
    event_tracer: TangoEventTracer,
    tmc: TMCFacade,
    csp: CSPFacade,
    sdp: SDPFacade,
    mccs: MCCSFacade,
    default_commands_inputs: TestHarnessInputs,
):
    setup_event_subscriptions(tmc, csp, sdp, mccs, event_tracer)
    tmc.force_change_of_obs_state(
        ObsState.IDLE, default_commands_inputs, wait_termination=True
    )


@when(
    parsers.parse("I configure it for a scan with defective {failed_devices}")
)
def invoke_configure_command(
    tmc: TMCFacade,
    sdp: SDPFacade,
    default_commands_inputs: TestHarnessInputs,
    failed_devices: list,
):
    """Invokes configure command on the TMC Subarray."""
    # Set device defective
    for failed_device in failed_devices:
        if failed_device == "SDP":
            sdp.sdp_subarray.SetDefective(
                json.dumps(SDP_BACK_TO_INITIAL_STATE)
            )
    tmc.configure(
        default_commands_inputs.configure_input, wait_termination=False
    )


@then(parsers.parse("configure failed on {failed_devices} Subarray Leaf Node"))
def verify_configure_failed_on_subarray_leaf_node(
    event_tracer: TangoEventTracer, tmc: TMCFacade, failed_devices: list
):
    """Verifies that configure failed on subarray leaf node."""

    for failed_device in failed_devices:
        assert_that(event_tracer).described_as(
            "TMC Subarray Leaf Node "
            f"({tmc.subarray_node}) "
            "is expected to report a"
            "longRunningCommand successful failure."
        ).within_timeout(20).has_change_event_occurred(
            FAILED_DEVICE_MAP[failed_device],
            "longRunningCommandResult",
            (Anything, (ResultCode.FAILED,)),
        )


@then(
    parsers.parse(
        "{failed_devices} Subarray Leaf Node transition to IDLE Obs state"
    )
)
def verify_subarray_leaf_node_to_idle(
    event_tracer: TangoEventTracer, tmc: TMCFacade, failed_devices: list
):
    """Verifies that configure failed on subarray leaf node."""
    for failed_device in failed_devices:
        assert_that(event_tracer).described_as(
            f"Subarray device ({FAILED_DEVICE_MAP[failed_device]})"
            "ObsState attribute value should move "
            f" to IDLE."
        ).within_timeout(TIMEOUT).has_change_event_occurred(
            FAILED_DEVICE_MAP[failed_device],
            "obsState",
            ObsState.IDLE,
        )


@then(
    "a subarray perform auto recovery and transition Subarray "
    "Obs State to IDLE"
)
def verify_tmc_subarray_to_idle(
    event_tracer: TangoEventTracer, tmc: TMCFacade
):
    """Verifies that tmc subarray moved to IDLE."""
    assert_that(event_tracer).described_as(
        "TMC Subarray Leaf Node)"
        "ObsState attribute value should move "
        " to IDLE."
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        tmc.subarray_node,
        "obsState",
        ObsState.IDLE,
    )

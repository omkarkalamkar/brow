import time

import pytest
from pytest_bdd import given, parsers, scenario
from ska_control_model import ObsState
from ska_integration_test_harness.facades.csp_facade import CSPFacade
from ska_integration_test_harness.facades.sdp_facade import SDPFacade
from ska_integration_test_harness.facades.tmc_facade import TMCFacade
from ska_integration_test_harness.inputs.test_harness_inputs import (
    TestHarnessInputs,
)
from ska_tango_testing.integration import TangoEventTracer, log_events


@pytest.mark.SKA_low
@scenario(
    "../features/tmc/check_error_propagation_ith.feature",
    "TMC subarray reports errors during interactions with CSP or SDP subarray",
)
def test_tmc_command_error_propagation():
    """
    Test case to verify TMC Error Propagation functionality.
    """


@given("the telescope is in ON state")
def given_the_telescope_is_in_on_state(
    tmc: TMCFacade,
):
    """Ensure the telescope is in ON state."""
    tmc.move_to_on(wait_termination=True)
    time.sleep(5)


@given(parsers.parse("TMC subarray is in ObsState {obs_state}"))
def subarray_in_idle_state(
    context_fixt: SubarrayTestContextData,
    tmc: TMCFacade,
    default_commands_inputs: TestHarnessInputs,
    obs_state,
):
    """Ensure the subarray is in the EMPTY state."""
    context_fixt.starting_state = ObsState.EMPTY

    tmc.force_change_of_obs_state(
        obs_state,
        default_commands_inputs,
        wait_termination=True,
    )

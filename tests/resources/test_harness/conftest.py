"""Configurations needed for the tests using the new harness."""

import os
from dataclasses import dataclass
from typing import Any

import pytest
from assertpy import assert_that
from pytest_bdd import parsers, then
from ska_control_model import ObsState, ResultCode
from ska_integration_test_harness.facades.csp_facade import CSPFacade
from ska_integration_test_harness.facades.sdp_facade import SDPFacade
from ska_integration_test_harness.facades.tmc_facade import TMCFacade
from ska_integration_test_harness.init.test_harness_builder import (
    TestHarnessBuilder,
)
from ska_integration_test_harness.inputs.test_harness_inputs import (
    TestHarnessInputs,
)
from ska_integration_test_harness.structure.telescope_wrapper import (
    TelescopeWrapper,
)
from ska_tango_testing.integration import TangoEventTracer, log_events

from tests.resources.test_harness.utils.my_file_json_input import (
    MyFileJSONInput,
)

ASSERTIONS_TIMEOUT = 60

# ------------------------------------------------------------
# Test Harness fixtures


@pytest.fixture
def default_commands_inputs() -> TestHarnessInputs:
    """Default JSON inputs for TMC commands."""
    return TestHarnessInputs(
        assign_input=MyFileJSONInput("centralnode", "assign_resources_low"),
        configure_input=MyFileJSONInput("subarray", "configure_low"),
        scan_input=MyFileJSONInput("subarray", "scan_low"),
        release_input=MyFileJSONInput("centralnode", "release_resources_low"),
    )


@pytest.fixture
def telescope_wrapper(
    default_commands_inputs: TestHarnessInputs,
) -> TelescopeWrapper:
    """Create an unique test harness with proxies to all devices."""
    test_harness_builder = TestHarnessBuilder()

    # import from a configuration file device names and emulation directives
    # for TMC, CSP, SDP and MCCS
    test_harness_builder.read_config_file(
        "tests/resources/test_harness/test_harness_config.yaml"
    )
    test_harness_builder.validate_configurations()

    # set the default inputs for the TMC commands,
    # which will be used for teardown procedures
    test_harness_builder.set_default_inputs(default_commands_inputs)
    test_harness_builder.validate_default_inputs()
    test_harness_builder.set_kubernetes_namespace(os.getenv("KUBE_NAMESPACE"))

    # build the wrapper of the telescope and it's sub-systems
    telescope = test_harness_builder.build()
    telescope.actions_default_timeout = 120
    yield telescope

    # after a test is completed, reset the telescope to its initial state
    # (obsState=READY, telescopeState=OFF, no resources assigned)
    telescope.tear_down()


@pytest.fixture
def tmc(telescope_wrapper: TelescopeWrapper) -> TMCFacade:
    """Create a facade to TMC devices."""
    return TMCFacade(telescope_wrapper)


@pytest.fixture
def csp(telescope_wrapper: TelescopeWrapper):
    """Create a facade to CSP devices."""
    return CSPFacade(telescope_wrapper)


@pytest.fixture
def sdp(telescope_wrapper: TelescopeWrapper):
    """Create a facade to SDP devices."""
    return SDPFacade(telescope_wrapper)


# ----------------------------------------------------------
# Tango event tracer


@pytest.fixture
def event_tracer() -> TangoEventTracer:
    """Create an event tracer."""
    return TangoEventTracer(
        event_enum_mapping={"obsState": ObsState},
    )


# ------------------------------------------------------------
# Other fixtures and common steps


@dataclass
class SubarrayTestContextData:
    """A class to store shared variables between steps."""

    starting_state: ObsState | None = None
    """The state of the system before the WHEN step."""

    expected_next_state: ObsState | None = None
    """The expected state to be reached if no WHEN step is executed.

    It is meaningful when the starting state is transient and so it will
    automatically change to another state (different both from the starting
    state and the expected next state).

    Leave empty if the starting state is not transient.
    """

    when_action_result: Any | None = None
    """The result of the WHEN step command."""

    when_action_name: str | None = None
    """The name of the Tango command executed in the WHEN step."""

    def is_starting_state_transient(self) -> bool:
        """Check if the starting state is transient."""
        return self.expected_next_state is not None


@pytest.fixture
def context_fixt() -> SubarrayTestContextData:
    """A collection of variables shared between steps.

    The shared variables are the following:

    - previous_state: the previous state of the subarray.
    - expected_next_state: the expected next state of the subarray (specified
        only if the previous st
    - trigger: the trigger that caused the state change.

    :return: the shared variables.
    """
    return SubarrayTestContextData()


def _setup_event_subscriptions(
    tmc: TMCFacade,
    csp: CSPFacade,
    sdp: SDPFacade,
    event_tracer: TangoEventTracer,
):
    """Subscribe TMC, CSP and SDP devices to track and log obsState events.

    :param tmc: the TMC facade.
    :param csp: the CSP facade.
    :param sdp: the SDP facade.
    :param event_tracer: the event tracer.
    """
    event_tracer.subscribe_event(tmc.subarray_node, "obsState")
    event_tracer.subscribe_event(csp.csp_subarray, "obsState")
    event_tracer.subscribe_event(sdp.sdp_subarray, "obsState")
    event_tracer.subscribe_event(tmc.central_node, "longRunningCommandResult")
    event_tracer.subscribe_event(tmc.subarray_node, "longRunningCommandResult")

    log_events(
        {
            tmc.subarray_node: [
                "obsState",
                "longRunningCommandResult",
            ],
            csp.csp_subarray: ["obsState"],
            sdp.sdp_subarray: ["obsState", "commandCallInfo"],
            tmc.central_node: ["longRunningCommandResult"],
        },
        event_enum_mapping={"obsState": ObsState},
    )


# ----------------------------------------------------------
# Common Then steps (verify LRC completion)


def _get_long_run_command_id(context_fixt: SubarrayTestContextData) -> str:
    return context_fixt.when_action_result[1][0]


def _get_expected_long_run_command_result(context_fixt) -> tuple[str, str]:
    return (
        _get_long_run_command_id(context_fixt),
        f'[{ResultCode.OK.value}, "Command Completed"]',
    )


@then(
    parsers.parse(
        "the central node reports a longRunningCommand successful completion"
    )
)
def verify_long_running_command_result_on_central_node(
    context_fixt,
    tmc: TMCFacade,
    event_tracer: TangoEventTracer,
):
    """
    Verify the successful completion of a longRunningCommand on central node.

    This step checks that the TMC Central Node reports a successful completion
    of a longRunningCommand. It uses the event_tracer to assert that a change
    event occurred on the longRunningCommandResult attribute within a specified
    timeout. The expected result is derived from the context fixture.
    """
    assert_that(event_tracer).described_as(
        "TMC Central Node "
        f"({tmc.central_node}) "
        "is expected to report a"
        "longRunningCommand successful completion."
    ).within_timeout(ASSERTIONS_TIMEOUT).has_change_event_occurred(
        tmc.central_node,
        "longRunningCommandResult",
        _get_expected_long_run_command_result(context_fixt),
    )


@then(
    parsers.parse(
        "the subarray {subarray} reports "
        "a longRunningCommand successful completion"
    )
)
def verify_long_running_command_result_on_subarray(
    context_fixt,
    tmc: TMCFacade,
    event_tracer: TangoEventTracer,
):
    """
    Verify the successful completion of a longRunningCommand on the subarray.

    This step checks that the TMC Subarray Node reports a successful completion
    of a longRunningCommand. It uses the event_tracer to assert that a change
    event occurred on the longRunningCommandResult attribute within a specified
    timeout. The expected result is derived from the context fixture.
    """
    assert_that(event_tracer).described_as(
        "TMC Subarray Node "
        f"({tmc.subarray_node}) "
        "is expected to report a"
        "longRunningCommand successful completion."
    ).within_timeout(ASSERTIONS_TIMEOUT).has_change_event_occurred(
        tmc.subarray_node,
        "longRunningCommandResult",
        _get_expected_long_run_command_result(context_fixt),
    )

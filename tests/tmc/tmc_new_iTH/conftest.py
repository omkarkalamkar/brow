"""Configurations needed for the tests using the new harness."""

import os
from dataclasses import dataclass
from typing import Any

import pytest
from assertpy import assert_that
from ska_control_model import AdminMode, ObsState
from ska_integration_test_harness.facades.csp_facade import CSPFacade
from ska_integration_test_harness.facades.mccs_facade import MCCSFacade
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
from ska_tango_testing.integration import TangoEventTracer
from tango import DeviceProxy

from tests.resources.test_harness.constant import (
    low_csp_subarray1,
    low_sdp_subarray1,
    mccs_controller,
    mccs_subarray1,
)
from tests.resources.test_harness.utils.my_file_json_input import (
    MyFileJSONInput,
)
from tests.tmc.tmc_new_iTH.utils import TIMEOUT


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


@pytest.fixture
def mccs(telescope_wrapper: TelescopeWrapper):
    """Create a facade to MCCS devices."""
    return MCCSFacade(telescope_wrapper)


@dataclass
class TestContextData:
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

    csp_obsstate: ObsState | None = None
    sdp_obsstate: ObsState | None = None
    mccs_obsstate: ObsState | None = None


@pytest.fixture
def context_data() -> TestContextData:
    """A collection of variables shared between steps.

    The shared variables are the following:

    - previous_state: the previous state of the subarray.
    - expected_next_state: the expected next state of the subarray (specified
        only if the previous st
    - trigger: the trigger that caused the state change.

    :return: the shared variables.
    """
    return TestContextData()


def get_long_run_command_id(context_data: TestContextData) -> str:
    return context_data.when_action_result[1][0]


def _tear_down(tmc: TMCFacade, event_tracer: TangoEventTracer):
    """Function to handle TMC tear down in observation
    state FAULT.

    :param tmc: TMCFacade object to invoke TMC commands
    :type tmc: TMCFacade
    :param event_tracer: TangoEventTracer object for event handling
    :type event_tracer: TangoEventTracer
    """
    if tmc.subarray_node.obsState == ObsState.FAULT:
        tmc.restart(wait_termination=True)
        assert_that(event_tracer).described_as(
            f"TMC Subarray Node device ({tmc.subarray_node})"
            "ObsState attribute value should move "
            f"from {ObsState.FAULT} to EMPTY."
        ).within_timeout(TIMEOUT).has_change_event_occurred(
            tmc.subarray_node, "obsState", ObsState.EMPTY
        )


@pytest.fixture
def telescope_wrapper(
    default_commands_inputs: TestHarnessInputs,
    event_tracer: TangoEventTracer,
) -> TelescopeWrapper:
    """Create an unique test harness with proxies to all devices."""
    test_harness_builder = TestHarnessBuilder()

    # import from a configuration file device names and emulation directives
    # for TMC, CSP, SDP and MCCS
    test_harness_builder.read_config_file(
        "../../../../app/tests/resources/test_harness/test_harness_config.yaml"
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
    _tear_down(telescope.tmc, event_tracer)
    telescope.tear_down()


@pytest.fixture
def event_tracer() -> TangoEventTracer:
    """Create an event tracer."""
    return TangoEventTracer(
        event_enum_mapping={"obsState": ObsState},
    )


@pytest.fixture
def admin_mode() -> None:
    csp_subarray1 = DeviceProxy(low_csp_subarray1)
    sdp_subarray1 = DeviceProxy(low_sdp_subarray1)
    mccs_subarray = DeviceProxy(mccs_subarray1)
    mccs_control = DeviceProxy(mccs_controller)
    mccs_control.adminMode = 0
    mccs_control.on()
    if csp_subarray1.adminMode != AdminMode.ONLINE:
        csp_subarray1.adminMode = AdminMode.ONLINE
    if sdp_subarray1.adminMode != AdminMode.ONLINE:
        sdp_subarray1.adminMode = AdminMode.ONLINE
    if mccs_subarray.adminMode != AdminMode.ONLINE:
        mccs_subarray.adminMode = AdminMode.ONLINE

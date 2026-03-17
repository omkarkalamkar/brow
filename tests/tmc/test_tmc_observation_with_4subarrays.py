"""
This module defines a Pytest BDD test scenario for the successful execution of
Scan Command of a Low Telescope Subarray in the Telescope Monitoring and
Control (TMC) system.
"""
import json
import logging

import pytest
from assertpy import assert_that
from pytest_bdd import given, scenario, then, when
from ska_control_model import ObsState
from ska_ser_logging import configure_logging
from ska_tango_testing.integration import TangoEventTracer, log_events
from tango import DevState

from tests.resources.test_harness.central_node_low import CentralNodeWrapperLow
from tests.resources.test_harness.constant import TIMEOUT
from tests.resources.test_harness.subarray_node_low import (
    SubarrayNodeWrapperLow,
)
from tests.resources.test_harness.utils.common_utils import JsonFactory
from tests.resources.test_support.common_utils.result_code import ResultCode
from tests.resources.test_support.common_utils.tmc_helpers import (
    prepare_json_args_for_centralnode_commands,
    prepare_json_args_for_commands,
)

configure_logging(logging.DEBUG)
LOGGER = logging.getLogger(__name__)


@pytest.mark.sah1883
@pytest.mark.SKA_low
@scenario(
    "../features/tmc/tmc_observation_with_four_subarray.feature",
    "Execute observations simultaneously on four subarrays",
)
def test_tmc_observation_with_four_subarrays():
    """BDD test scenario for verifying successful observation on
    four subarrays consecutively."""


@given("the telescope is in the ON state")
def given_a_telescope_is_in_on(
    central_node_low: CentralNodeWrapperLow, event_tracer: TangoEventTracer
):
    """
    This method invokes On command from central node and verifies
    the state of telescope after the invocation.
    Args:
        central_node (CentralNodeWrapperLow): Object of Central node wrapper
        event_tracer(TangoEventTracer): object of TangoEventTracer used for
        managing the device events
    """
    event_tracer.subscribe_event(
        central_node_low.central_node, "telescopeState"
    )
    event_tracer.subscribe_event(
        central_node_low.central_node, "longRunningCommandResult"
    )
    event_tracer.subscribe_event(central_node_low.subarray_node, "obsState")
    log_events(
        {
            central_node_low.central_node: [
                "telescopeState",
                "longRunningCommandResult",
            ],
            central_node_low.subarray_node: ["obsState"],
        }
    )
    central_node_low.set_subarray_id(2)
    event_tracer.subscribe_event(central_node_low.subarray_node, "obsState")
    log_events(
        {
            central_node_low.subarray_node: ["obsState"],
        }
    )
    central_node_low.set_subarray_id(3)
    event_tracer.subscribe_event(central_node_low.subarray_node, "obsState")
    log_events(
        {
            central_node_low.subarray_node: ["obsState"],
        }
    )
    central_node_low.set_subarray_id(4)
    event_tracer.subscribe_event(central_node_low.subarray_node, "obsState")
    log_events(
        {
            central_node_low.subarray_node: ["obsState"],
        }
    )
    central_node_low.set_subarray_id(1)
    central_node_low.move_to_on()
    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "GIVEN" STEP: '
        "'the telescope is is ON state'"
        "Central Node device"
        f"({central_node_low.central_node.dev_name()}) "
        "is expected to be in TelescopeState ON",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        central_node_low.central_node,
        "telescopeState",
        DevState.ON,
    )


@given("all the subarrays are in the EMPTY ObsState")
def verify_subarrays_in_empty(
    central_node_low: CentralNodeWrapperLow,
    event_tracer: TangoEventTracer,
):
    """Verifies subarray in EMPTY ObsState."""
    central_node_low.set_subarray_id(1)
    assert_that(event_tracer).described_as(
        "TMC subarray device"
        f"({central_node_low.subarray_node.dev_name()}) "
        "is expected to be in EMPTY obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        central_node_low.subarray_node,
        "obsState",
        ObsState.EMPTY,
    )
    central_node_low.set_subarray_id(2)
    assert_that(event_tracer).described_as(
        "TMC subarray device"
        f"({central_node_low.subarray_node.dev_name()}) "
        "is expected to be in EMPTY obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        central_node_low.subarray_node,
        "obsState",
        ObsState.EMPTY,
    )
    central_node_low.set_subarray_id(3)
    assert_that(event_tracer).described_as(
        "TMC subarray device"
        f"({central_node_low.subarray_node.dev_name()}) "
        "is expected to be in EMPTY obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        central_node_low.subarray_node,
        "obsState",
        ObsState.EMPTY,
    )
    central_node_low.set_subarray_id(4)
    assert_that(event_tracer).described_as(
        "TMC subarray device"
        f"({central_node_low.subarray_node.dev_name()}) "
        "is expected to be in EMPTY obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        central_node_low.subarray_node,
        "obsState",
        ObsState.EMPTY,
    )


@given(
    "I Assign subarray 1 with station beam 1, "
    "subarray 2 with station beam 2, subarray 3 "
    "with pst beam 1 and subarray 4 with pst beam 2"
)
def invoke_assign_resources(
    central_node_low: CentralNodeWrapperLow,
    command_input_factory: JsonFactory,
    event_tracer: TangoEventTracer,
    # station_beam_subarray1: str,
    # station_beam_subarray2: str,
    # pst_beam_subarray3: str,
    # pst_beam_subarray4: str,
):
    """Assigns and verifies subarrays in IDLE ObsState."""

    # LOGGER.info("station_beam_subarray1: %s", station_beam_subarray1)
    # LOGGER.info("station_beam_subarray2: %s", station_beam_subarray2)
    # LOGGER.info("pst_beam_subarray3: %s", pst_beam_subarray3)
    # LOGGER.info("pst_beam_subarray4: %s", pst_beam_subarray4)
    assign_input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_low", command_input_factory
    )
    assign_input_json_subarray1 = json.loads(assign_input_json)
    LOGGER.info(
        "apertures data: %s",
        assign_input_json_subarray1["mccs"]["subarray_beams"][0]["apertures"][
            1
        ],
    )
    del assign_input_json_subarray1["mccs"]["subarray_beams"][0]["apertures"][
        1
    ]

    assign_input_json_subarray1["csp"]["pss"]["pss_beam_ids"] = []
    assign_input_json_subarray1["csp"]["pst"]["pst_beam_ids"] = []
    LOGGER.info("assign_input_json_subarray1: %s", assign_input_json_subarray1)
    central_node_low.set_subarray_id(1)
    _, unique_id = central_node_low.perform_action(
        "AssignResources", json.dumps(assign_input_json_subarray1)
    )

    # Assigning subarray 2
    central_node_low.set_subarray_id(2)
    assign_input_json_subarray2 = json.loads(assign_input_json)

    assign_input_json_subarray2["subarray_id"] = 2

    LOGGER.info(
        "apertures data: %s",
        assign_input_json_subarray2["mccs"]["subarray_beams"][0]["apertures"][
            0
        ],
    )
    del assign_input_json_subarray2["mccs"]["subarray_beams"][0]["apertures"][
        0
    ]

    assign_input_json_subarray2["csp"]["pss"]["pss_beam_ids"] = []
    assign_input_json_subarray2["csp"]["pst"]["pst_beam_ids"] = []
    LOGGER.info("assign_input_json_subarray2: %s", assign_input_json_subarray2)

    _, unique_id2 = central_node_low.perform_action(
        "AssignResources", json.dumps(assign_input_json_subarray2)
    )
    assert_that(event_tracer).described_as(
        "Central Node device"
        f"({central_node_low.central_node.dev_name()}) "
        "is expected have longRunningCommand as"
        '(unique_id,(ResultCode.OK,"Command Completed"))',
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        central_node_low.central_node,
        "longRunningCommandResult",
        (
            unique_id[0],
            json.dumps((int(ResultCode.OK), "Command Completed")),
        ),
    )
    assert_that(event_tracer).described_as(
        "Central Node device"
        f"({central_node_low.central_node.dev_name()}) "
        "is expected have longRunningCommand as"
        '(unique_id,(ResultCode.OK,"Command Completed"))',
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        central_node_low.central_node,
        "longRunningCommandResult",
        (
            unique_id2[0],
            json.dumps((int(ResultCode.OK), "Command Completed")),
        ),
    )

    central_node_low.set_subarray_id(1)
    assert_that(event_tracer).described_as(
        "Subarray Node device"
        f"({central_node_low.subarray_node.dev_name()}) "
        "is expected to be in IDLE obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        central_node_low.subarray_node,
        "obsState",
        ObsState.IDLE,
    )

    central_node_low.set_subarray_id(2)
    assert_that(event_tracer).described_as(
        "Subarray Node device"
        f"({central_node_low.subarray_node.dev_name()}) "
        "is expected to be in IDLE obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        central_node_low.subarray_node,
        "obsState",
        ObsState.IDLE,
    )


@given("I configure all the subarrays")
def invoke_configure_command(
    subarray_node_low: SubarrayNodeWrapperLow,
    command_input_factory: JsonFactory,
    event_tracer: TangoEventTracer,
):
    """Invokes configure command on the TMC Subarrays
    and verifies TMC moving to CONFIGURING."""

    configure_json = prepare_json_args_for_commands(
        "configure_low", command_input_factory
    )

    configure_json_subarray1 = json.loads(configure_json)
    LOGGER.info(
        "appertures[1]: %s",
        configure_json_subarray1["mccs"]["subarray_beams"][0]["apertures"][1],
    )
    del configure_json_subarray1["mccs"]["subarray_beams"][0]["apertures"][1]
    del configure_json_subarray1["mccs"]["subarray_beams"][1]
    del configure_json_subarray1["mccs"]["subarray_beams"][2]
    del configure_json_subarray1["mccs"]["subarray_beams"][3]
    del configure_json_subarray1["mccs"]["subarray_beams"][4]
    del configure_json_subarray1["mccs"]["subarray_beams"][5]
    del configure_json_subarray1["mccs"]["subarray_beams"][6]
    del configure_json_subarray1["mccs"]["subarray_beams"][7]
    del configure_json_subarray1["csp"]["lowcbf"]["timing_beams"]
    del configure_json_subarray1["csp"]["lowcbf"]["search_beams"]
    del configure_json_subarray1["csp"]["pst"]
    del configure_json_subarray1["csp"]["pss"]
    configure_json_subarray1["csp"]["lowcbf"]["stations"]["stns"] = [[1, 1]]

    LOGGER.info("SA1 Configure %s", configure_json_subarray1)
    # Configuring subarray 1
    subarray_node_low.set_subarray_id(1)

    event_tracer.subscribe_event(
        subarray_node_low.subarray_node, "longRunningCommandResult"
    )

    _, pytest.configure_id = subarray_node_low.store_configuration_data(
        json.dumps(configure_json_subarray1)
    )

    assert_that(event_tracer).described_as(
        "TMC Subarray Node 1 ObsState should move to CONFIGURING"
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        subarray_node_low.subarray_node,
        "obsState",
        ObsState.CONFIGURING,
    )

    configure_json_subarray2 = json.loads(configure_json)
    LOGGER.info(
        "appertures[0]: %s",
        configure_json_subarray2["mccs"]["subarray_beams"][1]["apertures"][0],
    )
    configure_json_subarray2["mccs"]["subarray_beams"][1]["apertures"] = {
        "aperture_id": "AP002.01",
        "weighting_key_ref": "aperture2",
    }
    del configure_json_subarray2["mccs"]["subarray_beams"][0]
    del configure_json_subarray2["mccs"]["subarray_beams"][2]
    del configure_json_subarray2["mccs"]["subarray_beams"][3]
    del configure_json_subarray2["mccs"]["subarray_beams"][4]
    del configure_json_subarray2["mccs"]["subarray_beams"][5]
    del configure_json_subarray2["mccs"]["subarray_beams"][6]
    del configure_json_subarray2["mccs"]["subarray_beams"][7]
    del configure_json_subarray2["csp"]["lowcbf"]["timing_beams"]
    del configure_json_subarray2["csp"]["lowcbf"]["search_beams"]
    del configure_json_subarray2["csp"]["pst"]
    del configure_json_subarray2["csp"]["pss"]
    configure_json_subarray2["csp"]["lowcbf"]["stations"]["stns"] = [[2, 1]]
    LOGGER.info("SA2 Configure %s", configure_json_subarray2)

    # Configuring subarray 2
    subarray_node_low.set_subarray_id(2)

    event_tracer.subscribe_event(
        subarray_node_low.subarray_node, "longRunningCommandResult"
    )

    _, pytest.configure_id2 = subarray_node_low.store_configuration_data(
        json.dumps(configure_json_subarray2)
    )

    assert_that(event_tracer).described_as(
        "TMC Subarray Node 2 ObsState should move to CONFIGURING"
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        subarray_node_low.subarray_node,
        "obsState",
        ObsState.CONFIGURING,
    )


@given("the Subarrays are configured successfully")
def verify_subarray_in_ready_observation_state(
    subarray_node_low: SubarrayNodeWrapperLow,
    event_tracer: TangoEventTracer,
):
    """Verifies the observation states of SDP,CSP and MCCS
    after command Configure.
    """
    subarray_node_low.set_subarray_id(1)
    expected_lrcr = (
        pytest.configure_id[0],
        json.dumps((int(ResultCode.OK), "Command Completed")),
    )

    assert_that(event_tracer).described_as(
        "TMC Subarray Node 1 ObsState should move to READY"
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        subarray_node_low.subarray_node,
        "obsState",
        ObsState.READY,
    )
    assert_that(event_tracer).described_as(
        "TMC Subarray Node 1 longRunningCommandResult should indicate "
        "successful completion of Configure command"
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        subarray_node_low.subarray_node,
        "longRunningCommandResult",
        expected_lrcr,
    )

    subarray_node_low.set_subarray_id(2)
    expected_lrcr = (
        pytest.configure_id2[0],
        json.dumps((int(ResultCode.OK), "Command Completed")),
    )
    assert_that(event_tracer).described_as(
        "TMC Subarray Node 2 ObsState should move to READY"
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        subarray_node_low.subarray_node,
        "obsState",
        ObsState.READY,
    )
    assert_that(event_tracer).described_as(
        "TMC Subarray Node 2 longRunningCommandResult should indicate "
        "successful completion of Configure command"
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        subarray_node_low.subarray_node,
        "longRunningCommandResult",
        expected_lrcr,
    )


@when("I start scan on all the subarrays")
def send_scan(
    command_input_factory: JsonFactory,
    subarray_node_low: SubarrayNodeWrapperLow,
    event_tracer: TangoEventTracer,
):
    """Send a Scan command to the subarray."""
    scan_input_json = prepare_json_args_for_commands(
        "scan_low", command_input_factory
    )
    subarray_node_low.set_subarray_id(1)
    subarray_node_low.execute_transition("Scan", scan_input_json)

    assert_that(event_tracer).described_as(
        "TMC Subarray Node 1 ObsState should move to SCANNING"
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        subarray_node_low.subarray_node,
        "obsState",
        ObsState.SCANNING,
    )

    subarray_node_low.set_subarray_id(2)
    subarray_node_low.execute_transition("Scan", scan_input_json)

    assert_that(event_tracer).described_as(
        "TMC Subarray Node 1 ObsState should move to SCANNING"
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        subarray_node_low.subarray_node,
        "obsState",
        ObsState.SCANNING,
    )


@then("the subarrays transition to READY on scan completion")
def check_scan_completion(
    subarray_node_low: SubarrayNodeWrapperLow,
    event_tracer: TangoEventTracer,
):
    """Verify that the subarray is in the READY obsState."""

    subarray_node_low.set_subarray_id(1)
    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "THEN" STEP: '
        "'the subarray must be in the SCANNING obsState until finished'"
        "Subarray Node device"
        f"({subarray_node_low.subarray_node.dev_name()}) "
        "is expected to be in READY obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        subarray_node_low.subarray_node,
        "obsState",
        ObsState.READY,
    )

    subarray_node_low.set_subarray_id(2)
    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "THEN" STEP: '
        "'the subarray must be in the SCANNING obsState until finished'"
        "Subarray Node device"
        f"({subarray_node_low.subarray_node.dev_name()}) "
        "is expected to be in READY obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        subarray_node_low.subarray_node,
        "obsState",
        ObsState.READY,
    )


@then("I end the observations on all the Subarrays")
def send_end_command(
    subarray_node_low: SubarrayNodeWrapperLow,
    event_tracer: TangoEventTracer,
):
    """Send a End command to the subarrays."""

    subarray_node_low.set_subarray_id(1)
    _, unique_id = subarray_node_low.end_observation()

    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "WHEN" STEP: '
        '"I end the observation"'
        "Subarray Node device"
        f"({subarray_node_low.subarray_node.dev_name()}) "
        "is expected to be in IDLE obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        subarray_node_low.subarray_node,
        "obsState",
        ObsState.IDLE,
    )
    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "WHEN" STEP: '
        '"I end the observation"'
        "Subarray Node device"
        f"({subarray_node_low.subarray_node.dev_name()}) "
        "is expected have longRunningCommand as"
        '(unique_id,(ResultCode.OK,"Command Completed"))',
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        subarray_node_low.subarray_node,
        "longRunningCommandResult",
        (
            unique_id[0],
            json.dumps((int(ResultCode.OK), "Command Completed")),
        ),
    )

    subarray_node_low.set_subarray_id(2)
    _, unique_id2 = subarray_node_low.end_observation()

    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "WHEN" STEP: '
        '"I end the observation"'
        "Subarray Node device"
        f"({subarray_node_low.subarray_node.dev_name()}) "
        "is expected to be in IDLE obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        subarray_node_low.subarray_node,
        "obsState",
        ObsState.IDLE,
    )
    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "WHEN" STEP: '
        '"I end the observation"'
        "Subarray Node device"
        f"({subarray_node_low.subarray_node.dev_name()}) "
        "is expected have longRunningCommand as"
        '(unique_id,(ResultCode.OK,"Command Completed"))',
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        subarray_node_low.subarray_node,
        "longRunningCommandResult",
        (
            unique_id2[0],
            json.dumps((int(ResultCode.OK), "Command Completed")),
        ),
    )


@then("I release resources from all the subarrays")
def send_release_resources_command(
    command_input_factory: JsonFactory,
    event_tracer: TangoEventTracer,
    central_node_low: CentralNodeWrapperLow,
):
    """Send a ReleaseResources command to the subarrays."""

    release_resource_json = prepare_json_args_for_centralnode_commands(
        "release_resources_low", command_input_factory
    )

    central_node_low.set_subarray_id(1)
    _, unique_id = central_node_low.perform_action(
        "ReleaseResources", release_resource_json
    )

    central_node_low.set_subarray_id(2)

    release_input_json_subarray2 = json.loads(release_resource_json)

    release_input_json_subarray2["subarray_id"] = 2
    _, unique_id2 = central_node_low.perform_action(
        "ReleaseResources", release_input_json_subarray2
    )

    assert_that(event_tracer).described_as(
        "Central Node device"
        f"({central_node_low.central_node.dev_name()}) "
        "is expected have longRunningCommand as"
        '(unique_id,(ResultCode.OK,"Command Completed"))',
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        central_node_low.central_node,
        "longRunningCommandResult",
        (
            unique_id[0],
            json.dumps((int(ResultCode.OK), "Command Completed")),
        ),
    )

    assert_that(event_tracer).described_as(
        "Central Node device"
        f"({central_node_low.central_node.dev_name()}) "
        "is expected have longRunningCommand as"
        '(unique_id,(ResultCode.OK,"Command Completed"))',
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        central_node_low.central_node,
        "longRunningCommandResult",
        (
            unique_id2[0],
            json.dumps((int(ResultCode.OK), "Command Completed")),
        ),
    )
    central_node_low.set_subarray_id(1)
    assert_that(event_tracer).described_as(
        "Subarray Node device"
        f"({central_node_low.subarray_node.dev_name()}) "
        "is expected to be in EMPTY obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        central_node_low.subarray_node,
        "obsState",
        ObsState.EMPTY,
    )
    central_node_low.set_subarray_id(2)
    assert_that(event_tracer).described_as(
        "Subarray Node device"
        f"({central_node_low.subarray_node.dev_name()}) "
        "is expected to be in EMPTY obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        central_node_low.subarray_node,
        "obsState",
        ObsState.EMPTY,
    )

    central_node_low.move_to_off()
    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "GIVEN STEP: '
        '"a TMC'
        "Central Node device"
        f"({central_node_low.central_node.dev_name()}) "
        "is expected to be in TelescopeState ON",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        central_node_low.central_node,
        "telescopeState",
        DevState.OFF,
    )

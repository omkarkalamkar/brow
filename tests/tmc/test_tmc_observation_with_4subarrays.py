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
    # Subcribe to CentralNode telescopeState and LRCR attributes
    event_tracer.subscribe_event(
        central_node_low.central_node, "telescopeState"
    )
    event_tracer.subscribe_event(
        central_node_low.central_node, "longRunningCommandResult"
    )
    log_events(
        {
            central_node_low.central_node: [
                "telescopeState",
                "longRunningCommandResult",
            ],
        }
    )
    event_tracer.clear_events()

    # Subscribe to obsState of all the four subarrays
    for subarray_id in [1, 2, 3, 4]:
        central_node_low.set_subarray_id(subarray_id)
        event_tracer.subscribe_event(
            central_node_low.subarray_node, "obsState"
        )
        log_events(
            {
                central_node_low.subarray_node: ["obsState"],
            }
        )
        # Set all the mock subsystem subarrays in State ON
        central_node_low.set_values_with_all_mocks(DevState.ON)

    # Execute TelescopeOn command
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
    for subarray_id in [1, 2, 3, 4]:
        central_node_low.set_subarray_id(subarray_id)
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
):
    """Assigns and verifies subarrays in IDLE ObsState."""
    assign_input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_low", command_input_factory
    )
    assign_unique_ids = []
    # Assign Station beam 1 to Subarray 1
    assign_input_json_subarray1 = json.loads(assign_input_json)
    assign_input_json_subarray1["mccs"]["subarray_beams"] = [
        {
            "subarray_beam_id": 1,
            "apertures": [{"station_id": 1, "aperture_id": "AP001.01"}],
            "number_of_channels": 8,
        }
    ]
    assign_input_json_subarray1["csp"]["pss"]["pss_beam_ids"] = []
    assign_input_json_subarray1["csp"]["pst"]["pst_beam_ids"] = []
    LOGGER.info("assign_input_json_subarray1: %s", assign_input_json_subarray1)
    central_node_low.set_subarray_id(1)
    _, unique_id = central_node_low.perform_action(
        "AssignResources", json.dumps(assign_input_json_subarray1)
    )
    assign_unique_ids.append(unique_id)
    # Assign Station beam 2 to Subarray 2
    central_node_low.set_subarray_id(2)
    assign_input_json_subarray2 = json.loads(assign_input_json)
    assign_input_json_subarray2["subarray_id"] = 2
    assign_input_json_subarray2["mccs"]["subarray_beams"] = [
        {
            "subarray_beam_id": 2,
            "apertures": [{"station_id": 2, "aperture_id": "AP002.01"}],
            "number_of_channels": 8,
        }
    ]
    assign_input_json_subarray2["csp"]["pss"]["pss_beam_ids"] = []
    assign_input_json_subarray2["csp"]["pst"]["pst_beam_ids"] = []
    LOGGER.info("assign_input_json_subarray2: %s", assign_input_json_subarray2)
    _, unique_id2 = central_node_low.perform_action(
        "AssignResources", json.dumps(assign_input_json_subarray2)
    )
    assign_unique_ids.append(unique_id2)
    # Assign PST beam 1 to Subarray 3
    assign_input_json_subarray3 = json.loads(assign_input_json)
    assign_input_json_subarray3["subarray_id"] = 3
    assign_input_json_subarray3["mccs"]["subarray_beams"] = [
        {
            "subarray_beam_id": 3,
            "apertures": [{"station_id": 3, "aperture_id": "AP003.01"}],
            "number_of_channels": 8,
        }
    ]
    assign_input_json_subarray3["csp"]["pss"]["pss_beam_ids"] = []
    LOGGER.info("assign_input_json_subarray3: %s", assign_input_json_subarray3)
    central_node_low.set_subarray_id(3)
    _, unique_id3 = central_node_low.perform_action(
        "AssignResources", json.dumps(assign_input_json_subarray3)
    )
    assign_unique_ids.append(unique_id3)
    # Assign PST beam 2 to Subarray 4
    assign_input_json_subarray4 = json.loads(assign_input_json)
    assign_input_json_subarray4["subarray_id"] = 4
    assign_input_json_subarray4["mccs"]["subarray_beams"] = [
        {
            "subarray_beam_id": 4,
            "apertures": [{"station_id": 4, "aperture_id": "AP004.01"}],
            "number_of_channels": 8,
        }
    ]
    assign_input_json_subarray4["csp"]["pss"]["pss_beam_ids"] = []
    assign_input_json_subarray4["csp"]["pst"]["pst_beam_ids"] = [2]
    LOGGER.info("assign_input_json_subarray4: %s", assign_input_json_subarray4)
    central_node_low.set_subarray_id(4)
    _, unique_id4 = central_node_low.perform_action(
        "AssignResources", json.dumps(assign_input_json_subarray4)
    )
    assign_unique_ids.append(unique_id4)
    LOGGER.info("AssignResources Unique IDs: %s", assign_unique_ids)

    # Check if all the AssignResources commands are completed on CentralNode
    for unique_id in assign_unique_ids:
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
    # Check if all the Subarrays are in obsState IDLE
    for subarray_id in [1, 2, 3, 4]:
        central_node_low.set_subarray_id(subarray_id)
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
    pytest.configure_unique_ids = {}
    # Execute Configure command on Subarray 1
    configure_json_subarray1 = json.loads(configure_json)
    configure_json_subarray1["mccs"]["subarray_beams"] = [
        {
            "subarray_beam_id": 1,
            "update_rate": 0.0,
            "logical_bands": [
                {"start_channel": 80, "number_of_channels": 16},
                {"start_channel": 384, "number_of_channels": 16},
            ],
            "apertures": [
                {"aperture_id": "AP001.01", "weighting_key_ref": "aperture2"}
            ],
            "field": {
                "target_name": "Polaris Australis",
                "reference_frame": "icrs",
                "attrs": {"c1": 180.0, "c2": 45.0},
            },
        }
    ]
    del configure_json_subarray1["csp"]["lowcbf"]["timing_beams"]
    del configure_json_subarray1["csp"]["lowcbf"]["search_beams"]
    del configure_json_subarray1["csp"]["pst"]
    del configure_json_subarray1["csp"]["pss"]
    configure_json_subarray1["csp"]["lowcbf"]["stations"]["stns"] = [[1, 1]]
    LOGGER.info("Subarray 1 Configure JSON: %s", configure_json_subarray1)
    subarray_node_low.set_subarray_id(1)
    _, configure_id = subarray_node_low.store_configuration_data(
        json.dumps(configure_json_subarray1)
    )
    pytest.configure_unique_ids[1] = configure_id
    # Execute Configure command on Subarray 2
    configure_json_subarray2 = json.loads(configure_json)
    configure_json_subarray2["mccs"]["subarray_beams"] = [
        {
            "subarray_beam_id": 2,
            "update_rate": 0.0,
            "logical_bands": [
                {"start_channel": 96, "number_of_channels": 16},
                {"start_channel": 400, "number_of_channels": 16},
            ],
            "apertures": [
                {"aperture_id": "AP002.01", "weighting_key_ref": "aperture2"}
            ],
            "field": {
                "target_name": "Polaris Australis",
                "reference_frame": "icrs",
                "attrs": {"c1": 181.0, "c2": 46.0},
            },
        }
    ]
    del configure_json_subarray2["csp"]["lowcbf"]["timing_beams"]
    del configure_json_subarray2["csp"]["lowcbf"]["search_beams"]
    del configure_json_subarray2["csp"]["pst"]
    del configure_json_subarray2["csp"]["pss"]
    configure_json_subarray2["csp"]["lowcbf"]["stations"]["stns"] = [[2, 1]]
    configure_json_subarray2["csp"]["lowcbf"]["stations"]["stn_beams"] = [
        {"beam_id": 2, "freq_ids": [400]}
    ]
    LOGGER.info("Subarray 2 Configure JSON: %s", configure_json_subarray2)
    subarray_node_low.set_subarray_id(2)
    _, configure_id2 = subarray_node_low.store_configuration_data(
        json.dumps(configure_json_subarray2)
    )
    pytest.configure_unique_ids[2] = configure_id2
    # Execute Configure command on Subarray 3
    configure_json_subarray3 = json.loads(configure_json)
    configure_json_subarray3["mccs"]["subarray_beams"] = [
        {
            "subarray_beam_id": 3,
            "update_rate": 0.0,
            "logical_bands": [
                {"start_channel": 112, "number_of_channels": 16},
                {"start_channel": 416, "number_of_channels": 16},
            ],
            "apertures": [
                {"aperture_id": "AP003.01", "weighting_key_ref": "aperture2"},
            ],
            "field": {
                "target_name": "Polaris Australis",
                "reference_frame": "icrs",
                "attrs": {"c1": 181.0, "c2": 46.0},
            },
        }
    ]
    configure_json_subarray3["csp"]["lowcbf"]["timing_beams"]["beams"] = [
        {
            "pst_beam_id": 1,
            "field": {
                "target_name": "PSR J0024-7204R",
                "reference_frame": "icrs",
                "attrs": {
                    "c1": 6.023625,
                    "c2": -72.08128333,
                    "pm_c1": 4.8,
                    "pm_c2": -3.3,
                },
            },
            "stn_beam_id": 3,
            "stn_weights": [0.9, 1.0, 1.0, 1.0, 0.9, 1.0],
        }
    ]
    del configure_json_subarray3["csp"]["lowcbf"]["search_beams"]
    del configure_json_subarray3["csp"]["pst"]["beams"][1]
    del configure_json_subarray3["csp"]["pss"]
    configure_json_subarray3["csp"]["lowcbf"]["stations"]["stns"] = [[3, 1]]
    configure_json_subarray3["csp"]["lowcbf"]["stations"]["stn_beams"] = [
        {"beam_id": 3, "freq_ids": [400]}
    ]
    LOGGER.info("Subarray 3 Configure JSON: %s", configure_json_subarray3)
    subarray_node_low.set_subarray_id(3)
    _, configure_id3 = subarray_node_low.store_configuration_data(
        json.dumps(configure_json_subarray3)
    )
    pytest.configure_unique_ids[3] = configure_id3
    # Execute Configure command on Subarray 4
    configure_json_subarray4 = json.loads(configure_json)
    configure_json_subarray4["mccs"]["subarray_beams"] = [
        {
            "subarray_beam_id": 4,
            "update_rate": 0.0,
            "logical_bands": [
                {"start_channel": 112, "number_of_channels": 16},
                {"start_channel": 416, "number_of_channels": 16},
            ],
            "apertures": [
                {"aperture_id": "AP004.01", "weighting_key_ref": "aperture2"},
            ],
            "field": {
                "target_name": "Polaris Australis",
                "reference_frame": "icrs",
                "attrs": {"c1": 181.0, "c2": 46.0},
            },
        }
    ]
    configure_json_subarray4["csp"]["lowcbf"]["timing_beams"]["beams"] = [
        {
            "pst_beam_id": 2,
            "field": {
                "target_name": "PSR J0024-7204R",
                "reference_frame": "icrs",
                "attrs": {
                    "c1": 6.023625,
                    "c2": -72.08128333,
                    "pm_c1": 4.8,
                    "pm_c2": -3.3,
                },
            },
            "stn_beam_id": 4,
            "stn_weights": [0.9, 1.0, 1.0, 1.0, 0.9, 1.0],
        }
    ]
    del configure_json_subarray4["csp"]["lowcbf"]["search_beams"]
    del configure_json_subarray4["csp"]["pst"]["beams"][0]
    del configure_json_subarray4["csp"]["pss"]
    configure_json_subarray4["csp"]["lowcbf"]["stations"]["stns"] = [[4, 1]]
    configure_json_subarray4["csp"]["lowcbf"]["stations"]["stn_beams"] = [
        {"beam_id": 4, "freq_ids": [400]}
    ]
    LOGGER.info("Subarray 4 Configure JSON: %s", configure_json_subarray4)
    subarray_node_low.set_subarray_id(4)
    _, configure_id4 = subarray_node_low.store_configuration_data(
        json.dumps(configure_json_subarray4)
    )
    pytest.configure_unique_ids[4] = configure_id4
    LOGGER.info("Configure unique IDs: %s", pytest.configure_unique_ids)
    # Check if all the Subarrays are in obsState CONFIGURING
    for subarray_id in [1, 2, 3, 4]:
        subarray_node_low.set_subarray_id(subarray_id)
        event_tracer.subscribe_event(
            subarray_node_low.subarray_node, "longRunningCommandResult"
        )
        assert_that(event_tracer).described_as(
            "TMC Subarray Node ObsState should move to CONFIGURING"
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
    # Check if all the Subarrays are in obsState READY and LRCR OK
    for subarray_id, unique_id in pytest.configure_unique_ids.items():
        subarray_node_low.set_subarray_id(subarray_id)
        expected_lrcr = (
            unique_id[0],
            json.dumps((int(ResultCode.OK), "Command Completed")),
        )
        assert_that(event_tracer).described_as(
            "TMC Subarray Node ObsState should move to READY"
        ).within_timeout(TIMEOUT).has_change_event_occurred(
            subarray_node_low.subarray_node,
            "obsState",
            ObsState.READY,
        )
        assert_that(event_tracer).described_as(
            "TMC Subarray Node longRunningCommandResult should indicate "
            "successful completion of Configure command"
        ).within_timeout(TIMEOUT).has_change_event_occurred(
            subarray_node_low.subarray_node,
            "longRunningCommandResult",
            expected_lrcr,
        )
    event_tracer.clear_events()


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
    # Execute Scan command on all the Subarrays
    for subarray_id in [1, 2, 3, 4]:
        subarray_node_low.set_subarray_id(subarray_id)
        subarray_node_low.execute_transition("Scan", scan_input_json)

        assert_that(event_tracer).described_as(
            "TMC Subarray Node ObsState should move to SCANNING"
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

    # Check if Scan is completed on all the subarrays
    for subarray_id in [1, 2, 3, 4]:
        subarray_node_low.set_subarray_id(subarray_id)
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

    # Execute End command on all the Subarrays
    for subarray_id in [1, 2, 3, 4]:
        subarray_node_low.set_subarray_id(subarray_id)
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
    release_unique_ids = []
    for subarray_id in [1, 2, 3, 4]:
        central_node_low.set_subarray_id(subarray_id)
        release_input_json_subarray = json.loads(release_resource_json)
        release_input_json_subarray["subarray_id"] = subarray_id
        _, unique_id = central_node_low.perform_action(
            "ReleaseResources", json.dumps(release_input_json_subarray)
        )
        release_unique_ids.append(unique_id)
    LOGGER.info("ReleaseResources unique IDs: %s", release_unique_ids)
    # Check if all the ReleaseResources commands on CentralNode are completed
    for unique_id in release_unique_ids:
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

    # Check if all the subarrays are in EMPTY ObsState
    for subarray_id in [1, 2, 3, 4]:
        central_node_low.set_subarray_id(subarray_id)
        assert_that(event_tracer).described_as(
            "Subarray Node device"
            f"({central_node_low.subarray_node.dev_name()}) "
            "is expected to be in EMPTY obstate",
        ).within_timeout(TIMEOUT).has_change_event_occurred(
            central_node_low.subarray_node,
            "obsState",
            ObsState.EMPTY,
        )

    # Execute TelescopeOff command
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

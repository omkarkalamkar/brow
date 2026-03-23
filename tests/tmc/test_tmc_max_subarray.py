"""
This module defines a Pytest BDD test scenario for the successful execution of
observation for a Low Telescope Subarray in the Telescope Monitoring and
Control (TMC) system.Here Subarry will be using 68 stations,
2 PST and 3 PSS beams
"""
import json
import logging
import time

import pytest
from assertpy import assert_that
from pytest_bdd import given, scenario, then, when
from ska_control_model import ObsState
from ska_tango_testing.integration import TangoEventTracer, log_events
from ska_telmodel.schema import validate as telmodel_validate
from tango import DevState

from tests.resources.test_harness.central_node_low import CentralNodeWrapperLow
from tests.resources.test_harness.constant import (
    INITIAL_LOW_DELAY_JSON,
    LOW_DELAYMODEL_VERSION,
    TIMEOUT,
)
from tests.resources.test_harness.subarray_node_low import (
    SubarrayNodeWrapperLow,
)
from tests.resources.test_harness.utils.common_utils import (
    JsonFactory,
    get_centralnode_input_json,
)
from tests.resources.test_support.common_utils.result_code import ResultCode
from tests.resources.test_support.common_utils.tmc_helpers import (
    prepare_json_args_for_centralnode_commands,
    prepare_json_args_for_commands,
)

logger = logging.getLogger(__name__)


@pytest.mark.SKA_low
@scenario(
    "../features/tmc/check_tmc_max_subarray_XTP-105118.feature",
    "Execute Scan Lifecycle with max resources",
)
def test_tmc_scan_command():
    """BDD test scenario for verifying successful execution of
    the Low Scan command in a TMC."""


@given("a Low telescope in ON state")
def given_tmc(
    central_node_low: CentralNodeWrapperLow, event_tracer: TangoEventTracer
):
    """Set up a TMC and ensure it is in the ON state."""
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
            central_node_low.subarray_node: ["obsState"],
        }
    )
    event_tracer.subscribe_event(central_node_low.subarray_node, "obsState")
    central_node_low.move_to_on()
    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "GIVEN STEP: '
        '"a TMC'
        "Central Node device"
        f"({central_node_low.central_node.dev_name()}) "
        "is expected to be in TelescopeState ON",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        central_node_low.central_node,
        "telescopeState",
        DevState.ON,
    )
    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "GIVEN STEP: '
        '"a TMC'
        "Subarray Node device"
        f"({central_node_low.subarray_node.dev_name()}) "
        f"is expected to be in EMPTY obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        central_node_low.subarray_node,
        "obsState",
        ObsState.EMPTY,
    )


@given("a subarray in READY obsState")
def given_subarray_in_ready(
    command_input_factory: JsonFactory,
    central_node_low: CentralNodeWrapperLow,
    event_tracer: TangoEventTracer,
    subarray_node_low: SubarrayNodeWrapperLow,
):
    """Set up a subarray in the READY obsState."""

    event_tracer.subscribe_event(
        subarray_node_low.subarray_node, "longRunningCommandResult"
    )
    log_events({subarray_node_low.subarray_node: ["longRunningCommandResult"]})
    assign_input_json = prepare_json_args_for_centralnode_commands(
        "assign_8beams_68_stations", command_input_factory
    )
    _, unique_id = central_node_low.store_resources(assign_input_json)
    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "GIVEN" STEP: '
        "'a subarray in READY obsState'"
        "Subarray Node device"
        f"({central_node_low.subarray_node.dev_name()}) "
        "is expected to be in IDLE obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        central_node_low.subarray_node,
        "obsState",
        ObsState.IDLE,
    )
    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "GIVEN" STEP: '
        "'a subarray in READY obsState'"
        "Subarray Node device"
        f"({central_node_low.central_node.dev_name()}) "
        "is expected have longRunningCommand as"
        '(unique_id,(ResultCode.OK,"Command Completed"))',
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        central_node_low.central_node,
        "longRunningCommandResult",
        (unique_id[0], json.dumps((int(ResultCode.OK), "Command Completed"))),
    )

    # Set sdp_subarray_proxy and assign rreceive address

    receive_address = get_centralnode_input_json(
        "ReceiveAddresses_with_68_stations"
    )
    central_node_low.subarray_devices[
        "sdp_subarray"
    ].SetDirectreceiveAddresses(receive_address)

    configure_input_json = prepare_json_args_for_commands(
        "configure_8beams_68_stations", command_input_factory
    )
    _, unique_id = subarray_node_low.store_configuration_data(
        configure_input_json
    )
    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "GIVEN" STEP: '
        "'a subarray in READY obsState'"
        "Subarray Node device"
        f"({central_node_low.subarray_node.dev_name()}) "
        "is expected to be in READY obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        central_node_low.subarray_node,
        "obsState",
        ObsState.READY,
    )
    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "GIVEN" STEP: '
        "'a subarray in READY obsState'"
        "Subarray Node device"
        f"({central_node_low.subarray_node.dev_name()}) "
        "is expected have longRunningCommand as"
        '(unique_id,(ResultCode.OK,"Command Completed"))',
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        central_node_low.subarray_node,
        "longRunningCommandResult",
        (unique_id[0], json.dumps((int(ResultCode.OK), "Command Completed"))),
    )


@given(
    "the delay for the 8 station beams, PSS beams, and PST beams are updated"
)
def delay_models_ready(
    subarray_node_low: SubarrayNodeWrapperLow,
):
    """delay model attributes check"""

    wait_time = time.time() + 10

    pssattributes = [f"delayModelPSSBeam{str(i)}" for i in range(1, 4)]
    pstattributes = [f"delayModelPSTBeam{str(i)}" for i in range(1, 3)]

    stationbeamattributes = [
        f"delaymodelstationbeam0{str(i)}" for i in range(1, 9)
    ]

    attributes = pssattributes + pstattributes + stationbeamattributes
    generated_delay_model_json = INITIAL_LOW_DELAY_JSON
    for attribute in attributes:
        while time.time() < wait_time:

            generated_delay_model = (
                subarray_node_low.csp_subarray_leaf_node.read_attribute(
                    attribute
                ).value
            )
            if (
                generated_delay_model is None
                or str(generated_delay_model).strip() == ""
            ):

                continue

            generated_delay_model_json = json.loads(generated_delay_model)
            logging.debug(
                "Generated %s Delay Model json: %s",
                attribute,
                generated_delay_model_json,
            )
            if generated_delay_model_json != INITIAL_LOW_DELAY_JSON:
                break
            time.sleep(1)

        assert (
            generated_delay_model_json != INITIAL_LOW_DELAY_JSON
        ), f"{attribute} has not been updated from initial values"
        assert len(generated_delay_model_json["station_beam_delays"]) == 68

        for expected_station_id, delay in enumerate(
            generated_delay_model_json["station_beam_delays"], start=1
        ):
            assert delay.get("station_id") == expected_station_id, (
                f"{attribute} has incorrect station_id order at index "
                f"{expected_station_id - 1}: expected {expected_station_id}, "
                f"got {delay.get('station_id')}"
            )

        telmodel_validate(
            version=LOW_DELAYMODEL_VERSION,
            config=generated_delay_model_json,
            strictness=2,
        )


@when("I command it to scan for a given period")
def send_scan(
    command_input_factory: JsonFactory,
    subarray_node_low: SubarrayNodeWrapperLow,
):
    """Send a Scan command to the subarray."""
    scan_input_json = prepare_json_args_for_commands(
        "scan_low", command_input_factory
    )
    subarray_node_low.execute_transition("Scan", scan_input_json)


@then(
    "after the scan duration they transition back to READY observation state"
)
def check_scan_completion(
    subarray_node_low: SubarrayNodeWrapperLow,
    event_tracer: TangoEventTracer,
):
    """Verify that the subarray is in the SCANNING obsState."""
    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "THEN" STEP: '
        "'the subarray must be in the SCANNING obsState until finished'"
        "Subarray Node device"
        f"({subarray_node_low.subarray_node.dev_name()}) "
        "is expected to be in SCANNING obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        subarray_node_low.subarray_node,
        "obsState",
        ObsState.SCANNING,
    )
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

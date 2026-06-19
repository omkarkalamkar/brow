"""
This module defines a Pytest BDD test scenario for checking the
delay value generation for PSS beams with different station beam IDs.
The scenario verifies that TMC generates delay models only for the
station beams that are actually used by the configured PSS beams.
"""
import json
import logging
import time

import pytest
from assertpy import assert_that
from pytest_bdd import given, scenario, then, when
from ska_control_model import ObsState
from ska_tango_base.commands import ResultCode
from ska_tango_testing.integration import TangoEventTracer, log_events
from ska_telmodel.schema import validate as telmodel_validate
from tango import DevState

from tests.resources.test_harness.central_node_low import CentralNodeWrapperLow
from tests.resources.test_harness.constant import (
    INITIAL_LOW_DELAY_JSON,
    LOW_DELAYMODEL_VERSION,
    TIMEOUT,
)
from tests.resources.test_harness.helpers import (
    prepare_json_args_for_centralnode_commands,
    prepare_json_args_for_commands,
    set_receive_address,
)
from tests.resources.test_harness.subarray_node_low import (
    SubarrayNodeWrapperLow,
)
from tests.resources.test_harness.utils.common_utils import JsonFactory

logger = logging.getLogger(__name__)


@pytest.mark.SKA_low
@scenario(
    "../features/tmc/tmc_pss_beams_different_stn.feature",
    "TMC generates delay values for different station beams",
)
def test_pss_beams_different_stn():
    """
    Test to verify that delay values are generated only for the
    station beams that are actually used by PSS beams.
    """


@given("the telescope is in the ON state")
def given_telescope_is_in_on_state(
    central_node_low: CentralNodeWrapperLow, event_tracer: TangoEventTracer
):
    """Method to check if telescope is in ON State"""
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
    central_node_low.move_to_on()
    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "GIVEN" STEP: '
        "'the telescope is in ON state'"
        "Central Node device"
        f"({central_node_low.central_node.dev_name()}) "
        "is expected to be in TelescopeState ON",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        central_node_low.central_node,
        "telescopeState",
        DevState.ON,
    )


@given("subarray is in obsState IDLE")
def subarray_in_idle_obsstate(
    central_node_low: CentralNodeWrapperLow,
    subarray_node_low: SubarrayNodeWrapperLow,
    event_tracer: TangoEventTracer,
    command_input_factory: JsonFactory,
) -> None:
    """Checks subarray is in obsState IDLE."""
    event_tracer.subscribe_event(subarray_node_low.subarray_node, "obsState")
    event_tracer.subscribe_event(
        subarray_node_low.subarray_node, "longRunningCommandResult"
    )
    log_events(
        {
            subarray_node_low.subarray_node: [
                "obsState",
                "longRunningCommandResult",
            ],
        }
    )
    set_receive_address(central_node_low)
    assign_input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_low", command_input_factory
    )
    _, unique_id = central_node_low.store_resources(assign_input_json)
    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "GIVEN" STEP: '
        '"subarray is in obsState IDLE"'
        "Subarray Node device"
        f"({subarray_node_low.subarray_node.dev_name()}) "
        "is expected to be in IDLE obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        subarray_node_low.subarray_node,
        "obsState",
        ObsState.IDLE,
    )
    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "GIVEN" STEP: '
        '"subarray is in obsState IDLE"'
        "Central Node device"
        f"({subarray_node_low.subarray_node.dev_name()}) "
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


@when("I configure the subarray with PSS beams using different station beams")
def invoke_configure_command_with_different_stn(
    subarray_node_low: SubarrayNodeWrapperLow,
    event_tracer: TangoEventTracer,
    command_input_factory: JsonFactory,
) -> None:
    """Invoke Configure command with PSS beams having
    different station beam IDs."""
    configure_input_json = prepare_json_args_for_commands(
        "configure_low_with_pss_beams_different_stn", command_input_factory
    )
    _, unique_id = subarray_node_low.store_configuration_data(
        configure_input_json
    )
    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "WHEN" STEP: '
        '"I configure the subarray with PSS beams'
        'using different station beams"'
        "Subarray Node device"
        f"({subarray_node_low.subarray_node.dev_name()}) "
        "is expected to be in READY obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        subarray_node_low.subarray_node,
        "obsState",
        ObsState.READY,
    )
    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "WHEN" STEP: '
        '"I configure the subarray with PSS beams'
        'using different station beams"'
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


@then(
    "CSP Subarray Leaf Node generates delay values only for used station beams"
)
def verify_delay_generated_for_used_stn_beams(
    subarray_node_low: SubarrayNodeWrapperLow,
):
    """
    Verifies that CSPSLN generates delay models for station beams 1 and 2
    which are the only station beams used by the
    PSS beams in the configuration. PSS beam 1 and 2 use stn_beam_id 1,
    PSS beam 3 uses stn_beam_id 2.
    """
    wait_time = time.time() + 10
    # check for pss beams configured to subarray
    station_id_mapping = {
        "delayModelPSSBeam1": 1,
        "delayModelPSSBeam2": 1,
        "delayModelPSSBeam3": 2,
    }
    attributes = [f"delayModelPSSBeam{str(i)}" for i in range(1, 4)]
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
        assert len(generated_delay_model_json["station_beam_delays"]) == 1
        assert (
            generated_delay_model_json["station_beam_delays"][0]["station_id"]
            == station_id_mapping[attribute]
        ), f"{attribute} has not been updated with correct station_id"

        telmodel_validate(
            version=LOW_DELAYMODEL_VERSION,
            config=generated_delay_model_json,
            strictness=2,
        )

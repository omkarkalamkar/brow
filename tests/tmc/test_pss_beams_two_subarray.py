"""
This module defines a BDD (Behavior-Driven Development) test scenario
using pytest-bdd to verify the behavior of the TMC system to execute
two observations simultaneously where two subarrays are allocated
PSS beams without sharing.
"""


import json
import logging
import time

import pytest
from assertpy import assert_that
from pytest_bdd import given, parsers, scenario, then, when
from ska_control_model import ObsState
from ska_tango_base.commands import ResultCode
from ska_tango_testing.integration import TangoEventTracer, log_events
from ska_telmodel.schema import validate as telmodel_validate
from tango import DevState

from tests.resources.test_harness.central_node_low import CentralNodeWrapperLow
from tests.resources.test_harness.constant import (
    INITIAL_LOW_DELAY_JSON,
    LOW_DELAYMODEL_VERSION,
)
from tests.resources.test_harness.simulator_factory import SimulatorFactory
from tests.resources.test_harness.subarray_node_low import (
    SubarrayNodeWrapperLow,
)
from tests.resources.test_harness.utils.common_utils import JsonFactory
from tests.resources.test_harness.utils.enums import SimulatorDeviceType
from tests.resources.test_support.common_utils.tmc_helpers import (
    prepare_json_args_for_centralnode_commands,
    prepare_json_args_for_commands,
)
from tests.resources.test_support.constant_low import TIMEOUT
from tests.tmc.tmc_new_iTH.utils import PSS_BEAMS_CONFIG


@pytest.mark.SKA_low
@scenario(
    "../features/tmc/pss_beams_two_subarray.feature",
    "Execute two observations simultaneously where two subarrays are "
    "allocated PSS beams without sharing in TMC Low",
)
def test_pss_beams_two_subarray():
    """BDD test scenario for verifying pss beams with two subarrays."""


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


@given("subarray 1 and 2 are in the EMPTY ObsState")
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


@when(
    parsers.parse(
        "I Assign subarray 1 with pss beams {pss_beams_subarray1} and "
        "subarray 2 with pss beams {pss_beams_subarray2}"
    )
)
def invoke_assign_resources(
    central_node_low: CentralNodeWrapperLow,
    command_input_factory: JsonFactory,
    event_tracer: TangoEventTracer,
    simulator_factory: SimulatorFactory,
    pss_beams_subarray1: str,
    pss_beams_subarray2: str,
):
    """Assigns and verifies subarrays in IDLE ObsState."""
    assign_input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_low", command_input_factory
    )
    assign_data = json.loads(assign_input_json)

    pss_beams_start, pss_beams_end = list(
        map(int, pss_beams_subarray1.split("-"))
    )
    assign_data["csp"]["pss"]["pss_beam_ids"] = list(
        range(pss_beams_start, pss_beams_end + 1)
    )
    _, pytest.unique_id = central_node_low.perform_action(
        "AssignResources", json.dumps(assign_data)
    )

    # Assigning subarray 2
    central_node_low.set_subarray_id(2)
    assign_data = json.loads(assign_input_json)

    assign_data["subarray_id"] = 2
    pss_beams_start, pss_beams_end = list(
        map(int, pss_beams_subarray2.split("-"))
    )
    assign_data["csp"]["pss"]["pss_beam_ids"] = list(
        range(pss_beams_start, pss_beams_end + 1)
    )
    _, pytest.unique_id2 = central_node_low.perform_action(
        "AssignResources", json.dumps(assign_data)
    )

    central_node_low.set_subarray_id(1)
    assert_that(event_tracer).described_as(
        "Central Node device"
        f"({central_node_low.central_node.dev_name()}) "
        "is expected have longRunningCommand as"
        '(unique_id,(ResultCode.OK,"Command Completed"))',
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        central_node_low.central_node,
        "longRunningCommandResult",
        (
            pytest.unique_id[0],
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
            pytest.unique_id2[0],
            json.dumps((int(ResultCode.OK), "Command Completed")),
        ),
    )

    central_node_low.set_subarray_id(1)
    sdp_sim = simulator_factory.get_or_create_simulator_device(
        SimulatorDeviceType.LOW_SDP_DEVICE
    )
    csp_sim = simulator_factory.get_or_create_simulator_device(
        SimulatorDeviceType.LOW_CSP_DEVICE
    )
    mccs_sim = simulator_factory.get_or_create_simulator_device(
        SimulatorDeviceType.MCCS_SUBARRAY_DEVICE
    )
    event_tracer.subscribe_event(csp_sim, "obsState")
    event_tracer.subscribe_event(sdp_sim, "obsState")
    event_tracer.subscribe_event(mccs_sim, "obsState")

    event_tracer.subscribe_event(
        central_node_low.csp_subarray_leaf_node, "cspSubarrayObsState"
    )
    event_tracer.subscribe_event(
        central_node_low.sdp_subarray_leaf_node, "sdpSubarrayObsState"
    )
    event_tracer.subscribe_event(
        central_node_low.mccs_subarray_leaf_node, "obsState"
    )
    log_events(
        {
            csp_sim: ["obsState"],
            sdp_sim: ["obsState"],
            central_node_low.csp_subarray_leaf_node: ["cspSubarrayObsState"],
            central_node_low.sdp_subarray_leaf_node: ["sdpSubarrayObsState"],
            central_node_low.mccs_subarray_leaf_node: ["obsState"],
        }
    )
    assert_that(event_tracer).described_as(
        "Subarray Node device"
        f"({central_node_low.subarray_node.dev_name()}) "
        "is expected to be in IDLE obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        central_node_low.subarray_node,
        "obsState",
        ObsState.IDLE,
    )
    assert_that(event_tracer).described_as(
        "SDP subarray device"
        f"({sdp_sim.dev_name()}) "
        "is expected to be in IDLE obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        sdp_sim,
        "obsState",
        ObsState.IDLE,
    )
    assert_that(event_tracer).described_as(
        "SDP subarray leaf device"
        f"({central_node_low.sdp_subarray_leaf_node.dev_name()}) "
        "is expected to be in IDLE obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        central_node_low.sdp_subarray_leaf_node,
        "sdpSubarrayObsState",
        ObsState.IDLE,
    )
    assert_that(event_tracer).described_as(
        "CSP subarray leaf device"
        f"({central_node_low.csp_subarray_leaf_node.dev_name()}) "
        "is expected to be in IDLE obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        central_node_low.csp_subarray_leaf_node,
        "cspSubarrayObsState",
        ObsState.IDLE,
    )
    assert_that(event_tracer).described_as(
        "CSP subarray device"
        f"({csp_sim.dev_name()}) "
        "is expected to be in IDLE obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        csp_sim,
        "obsState",
        ObsState.IDLE,
    )
    assert_that(event_tracer).described_as(
        "MCCS subarray leaf device"
        f"({central_node_low.mccs_subarray_leaf_node.dev_name()}) "
        "is expected to be in IDLE obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        central_node_low.mccs_subarray_leaf_node,
        "obsState",
        ObsState.IDLE,
    )
    assert_that(event_tracer).described_as(
        "MCCS subarray device"
        f"({mccs_sim.dev_name()}) "
        "is expected to be in IDLE obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        mccs_sim,
        "obsState",
        ObsState.IDLE,
    )
    central_node_low.set_subarray_id(2)
    sdp_sim2 = simulator_factory.get_or_create_simulator_device(
        SimulatorDeviceType.LOW_SDP_DEVICE2
    )
    csp_sim2 = simulator_factory.get_or_create_simulator_device(
        SimulatorDeviceType.LOW_CSP_DEVICE2
    )
    mccs_sim2 = simulator_factory.get_or_create_simulator_device(
        SimulatorDeviceType.MCCS_SUBARRAY_DEVICE2
    )
    event_tracer.subscribe_event(csp_sim2, "obsState")
    event_tracer.subscribe_event(sdp_sim2, "obsState")
    event_tracer.subscribe_event(mccs_sim2, "obsState")

    event_tracer.subscribe_event(
        central_node_low.csp_subarray_leaf_node, "cspSubarrayObsState"
    )
    event_tracer.subscribe_event(
        central_node_low.sdp_subarray_leaf_node, "sdpSubarrayObsState"
    )
    event_tracer.subscribe_event(
        central_node_low.mccs_subarray_leaf_node, "obsState"
    )
    log_events(
        {
            csp_sim2: ["obsState"],
            sdp_sim2: ["obsState"],
            mccs_sim2: ["obsState"],
            central_node_low.csp_subarray_leaf_node: ["cspSubarrayObsState"],
            central_node_low.sdp_subarray_leaf_node: ["sdpSubarrayObsState"],
            central_node_low.mccs_subarray_leaf_node: ["obsState"],
        }
    )
    assert_that(event_tracer).described_as(
        "Subarray Node device"
        f"({central_node_low.subarray_node.dev_name()}) "
        "is expected to be in IDLE obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        central_node_low.subarray_node,
        "obsState",
        ObsState.IDLE,
    )
    assert_that(event_tracer).described_as(
        "SDP subarray device"
        f"({sdp_sim2.dev_name()}) "
        "is expected to be in IDLE obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        sdp_sim2,
        "obsState",
        ObsState.IDLE,
    )
    assert_that(event_tracer).described_as(
        "SDP subarray leaf device"
        f"({central_node_low.sdp_subarray_leaf_node.dev_name()}) "
        "is expected to be in IDLE obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        central_node_low.sdp_subarray_leaf_node,
        "sdpSubarrayObsState",
        ObsState.IDLE,
    )
    assert_that(event_tracer).described_as(
        "MCCS subarray leaf device"
        f"({central_node_low.mccs_subarray_leaf_node.dev_name()}) "
        "is expected to be in IDLE obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        central_node_low.mccs_subarray_leaf_node,
        "obsState",
        ObsState.IDLE,
    )
    assert_that(event_tracer).described_as(
        "MCCS subarray device"
        f"({mccs_sim2.dev_name()}) "
        "is expected to be in IDLE obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        mccs_sim2,
        "obsState",
        ObsState.IDLE,
    )


@then("invoking Configure command on both subarrays TMC moves to CONFIGURING")
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

    configure_data = json.loads(configure_json)
    # Configuring subarray 1
    subarray_node_low.set_subarray_id(1)

    search_beams_key = PSS_BEAMS_CONFIG["beams"]
    pss_beam_key = PSS_BEAMS_CONFIG["beam"]
    configure_data["csp"]["search_beams"]["beams"] = search_beams_key[:15]
    configure_data["csp"]["pss"]["beam"] = pss_beam_key[:15]

    event_tracer.subscribe_event(
        subarray_node_low.subarray_node, "longRunningCommandResult"
    )

    pytest.configure_id = subarray_node_low.store_configuration_data(
        json.dumps(configure_data)
    )

    assert_that(event_tracer).described_as(
        "TMC Subarray Node 1 ObsState should move to CONFIGURING"
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        subarray_node_low.subarray_node,
        "obsState",
        ObsState.CONFIGURING,
    )

    configure_data = json.loads(configure_json)
    # Configuring subarray 2
    subarray_node_low.set_subarray_id(2)

    configure_data["csp"]["search_beams"]["beams"] = search_beams_key[16:]
    configure_data["csp"]["pss"]["beam"] = pss_beam_key[16:]

    event_tracer.subscribe_event(
        subarray_node_low.subarray_node, "longRunningCommandResult"
    )

    pytest.configure_id2 = subarray_node_low.store_configuration_data(
        json.dumps(configure_data)
    )

    assert_that(event_tracer).described_as(
        "TMC Subarray Node 2 ObsState should move to CONFIGURING"
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        subarray_node_low,
        "obsState",
        ObsState.CONFIGURING,
    )


@then("the Subarray is configured successfully")
def verify_sdp_csp_mccs_in_ready_observation_state(
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
        "TMC Subarray Node 1 longRunningCommandResult should indicate "
        "successful completion of Configure command"
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        subarray_node_low.subarray_node,
        "longRunningCommandResult",
        expected_lrcr,
    )
    assert_that(event_tracer).described_as(
        f", CSP Subarray device "
        f"({subarray_node_low.csp_subarray_leaf_node}) "
        f", MCCS Subarray device "
        f"({subarray_node_low.mccs_subarray_leaf_node}) "
        f"and SDP Subarray device "
        f"({subarray_node_low.sdp_subarray_leaf_node}) "
        "ObsState attribute values should be READY."
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        subarray_node_low.csp_subarray_leaf_node,
        "obsState",
        ObsState.READY,
    ).has_change_event_occurred(
        subarray_node_low.mccs_subarray_leaf_node,
        "obsState",
        ObsState.READY,
    ).has_change_event_occurred(
        subarray_node_low.sdp_subarray_leaf_node,
        "obsState",
        ObsState.READY,
    )

    subarray_node_low.set_subarray_id(2)
    expected_lrcr = (
        pytest.configure_id2[0],
        json.dumps((int(ResultCode.OK), "Command Completed")),
    )

    assert_that(event_tracer).described_as(
        "TMC Subarray Node 2 longRunningCommandResult should indicate "
        "successful completion of Configure command"
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        subarray_node_low.subarray_node,
        "longRunningCommandResult",
        expected_lrcr,
    )
    assert_that(event_tracer).described_as(
        f", CSP Subarray device "
        f"({subarray_node_low.csp_subarray_leaf_node}) "
        f", MCCS Subarray device "
        f"({subarray_node_low.mccs_subarray_leaf_node}) "
        f"and SDP Subarray device "
        f"({subarray_node_low.sdp_subarray_leaf_node}) "
        "ObsState attribute values should be READY."
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        subarray_node_low.csp_subarray_leaf_node,
        "obsState",
        ObsState.READY,
    ).has_change_event_occurred(
        subarray_node_low.mccs_subarray_leaf_node,
        "obsState",
        ObsState.READY,
    ).has_change_event_occurred(
        subarray_node_low.sdp_subarray_leaf_node,
        "obsState",
        ObsState.READY,
    )


@then("CSPSLN generates updated delay model for pss beams")
def verify_cspsln_delay_model_updated(
    subarray_node_low: SubarrayNodeWrapperLow,
):
    """
    Verifies that CSPSLN has generated / updated delay models
    on some configured pss beam attributes after successful Configure.
    """
    wait_time = time.time() + 5
    attributes = [f"delayModelPSSBeam{str(i)}" for i in range(1, 31)]
    generated_delay_model_json = INITIAL_LOW_DELAY_JSON
    for attribute in attributes:
        while time.time() < wait_time:
            generated_delay_model = (
                subarray_node_low.csp_subarray_leaf_node.read_attribute(
                    attribute
                ).value
            )
            generated_delay_model_json = json.loads(generated_delay_model)
            logging.info(
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

        telmodel_validate(
            version=LOW_DELAYMODEL_VERSION,
            config=generated_delay_model_json,
            strictness=2,
        )

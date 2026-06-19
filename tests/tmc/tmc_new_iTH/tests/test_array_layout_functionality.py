import json
import logging
import time

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
from ska_telmodel.data import TMData
from ska_telmodel.schema import validate as telmodel_validate
from tango import DeviceProxy

from tests.resources.test_harness.constant import (
    INITIAL_LOW_DELAY_JSON,
    LOW_DELAYMODEL_VERSION,
    TIMEOUT,
)
from tests.resources.test_harness.helpers import (
    wait_and_validate_device_attribute_value,
)
from tests.tmc.tmc_new_iTH.conftest import TestContextData
from tests.tmc.tmc_new_iTH.utils import setup_event_subscriptions

# from tango import DeviceProxy


@pytest.mark.test_end
@scenario(
    "xtp_94138_array_layout.feature",
    "Array layout functionality in TMC Low",
)
def test_array_layout_functionality():
    """BDD test scenario for verifying array layout functionality."""


@given("the telescope is in ON state")
def verify_tmc_subarray_observation_state_empty(
    event_tracer: TangoEventTracer,
    tmc: TMCFacade,
    csp: CSPFacade,
    sdp: SDPFacade,
    mccs: MCCSFacade,
    context_data: TestContextData,
):
    setup_event_subscriptions(tmc, csp, sdp, mccs, event_tracer)
    event_tracer.subscribe_event(tmc.subarray_node, "arraylayouturl")
    tmc.move_to_on(wait_termination=True)
    context_data.csp_obsstate = ObsState.EMPTY
    context_data.sdp_obsstate = ObsState.EMPTY
    context_data.mccs_obsstate = ObsState.EMPTY


@when(
    parsers.re(
        r"I invoke AssignResources on the TMC central node with "
        r"below array layout:\s*"
        r"(?P<table>(?:\s*\|[^\n]*\|)*\s*)"
    )
)
def invoke_assign_resources_command(
    tmc: TMCFacade,
    event_tracer: TangoEventTracer,
    default_commands_inputs: TestHarnessInputs,
    table: str,
):
    """Invokes AssignResources command with array layout on the
    TMC Subarray."""

    logging.info("Invoking AssignResources command on TMC Subarray")

    # Parse table data from the raw string
    rows = [row.strip().split("|") for row in table.strip().split("\n")]
    # Remove empty strings from split
    rows = [[cell.strip() for cell in row if cell.strip()] for row in rows]

    # Convert to dictionary
    table_dict = {}
    for row in rows:
        if len(row) >= 2:  # Ensure row has key-value pair
            table_dict[row[0]] = row[1]

    telmodel = {
        "source_uris": [table_dict["source_uris"]],
        "array_layout_path": table_dict["array_layout_path"],
    }

    pytest.source_uris = telmodel["source_uris"]
    pytest.array_layout_path = telmodel["array_layout_path"]

    logging.info(
        f"Invoking AssignResources command on TMC Subarray "
        f"with array layout: {telmodel}"
    )
    # Load the base JSON from file
    json_input = default_commands_inputs.assign_input
    # Parse its data into a dict
    json_input_data = json.loads(json_input.as_str())

    json_input_data["telmodel"] = telmodel

    logging.info(f"AssignResources input data: {json_input_data}")

    _, pytest.unique_id = tmc.central_node.AssignResources(
        json.dumps(json_input_data),
    )

    assert_that(event_tracer).described_as(
        "TMC Subarray Leaf Node"
        "ObsState attribute value should move "
        " to IDLE."
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        tmc.subarray_node,
        "obsState",
        ObsState.IDLE,
    )


@then(
    'TMC central node "arraylayouturl" attribute is updated with layout data'
)
def verify_subarray_array_layout(
    event_tracer: TangoEventTracer,
    tmc: TMCFacade,
):
    """Verifies the arrayLayout attribute of TMC Subarray Node
    after command AssignResources.
    """

    assert_that(event_tracer).described_as(
        f"TMC Subarray Node device ({tmc.subarray_node})"
        "arrayLayout attribute holds downloaded layout data."
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        tmc.subarray_node,
        "arraylayouturl",
        Anything,
    )

    source_uris = json.loads(tmc.central_node.defaultarraylayouturl)[
        "source_uris"
    ]

    layout_path = json.loads(tmc.central_node.defaultarraylayouturl)[
        "array_layout_path"
    ]

    # Verify array layout links
    assert pytest.source_uris == source_uris
    assert pytest.array_layout_path == layout_path

    array_layout_data = TMData(source_uris)[layout_path].get_dict()

    for antenna_data in array_layout_data["receptors"]:
        assert "station_id" in antenna_data
        if (
            antenna_data["station_id"] != 0
        ):  # antenna id 0 assertion is skipped as it leads to assert 0
            assert antenna_data["station_id"]


@then(
    "invoking Configure command on TMC starts delay calculation on TMC CSPSLN"
)
def delay_calculation_on_cspsln_starts(
    tmc: TMCFacade,
    default_commands_inputs: TestHarnessInputs,
    event_tracer: TangoEventTracer,
):
    """Verifies that the MCCS commandCallInfo json has record of
    non-sidereal objects.
    """

    tmc.configure(
        default_commands_inputs.configure_input,
        wait_termination=True,
    )
    assert_that(event_tracer).described_as(
        "TMC Subarray Leaf Node"
        "ObsState attribute value should move "
        " to CONFIGURING."
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        tmc.subarray_node,
        "obsState",
        ObsState.READY,
    )

    # validate delay model
    wait_time = time.time() + 5
    attributes = [
        f"delayModelStationBeam{str(i).zfill(2)}" for i in range(1, 9)
    ]
    generated_delay_model_json = INITIAL_LOW_DELAY_JSON
    for attribute in attributes:
        while time.time() < wait_time:
            generated_delay_model = tmc.csp_subarray_leaf_node.read_attribute(
                attribute
            ).value
            generated_delay_model_json = json.loads(generated_delay_model)
            logging.info(
                "Generated %s (poll): %s",
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


@then("TMC is able to memorize the array layout link on restart")
def tmc_able_to_memorize_the_array_layout(
    tmc: TMCFacade, default_commands_inputs: TestHarnessInputs
):
    """
    Verifies that TMC is able to memorize the array layout
    link on restart.
    """

    # Subarray node should remember the array layout link
    assert (
        pytest.source_uris
        == json.loads(tmc.subarray_node.arraylayouturl)["source_uris"]
    )
    assert (
        pytest.array_layout_path
        == json.loads(tmc.subarray_node.arraylayouturl)["array_layout_path"]
    )

    tmc.force_change_of_obs_state(
        ObsState.EMPTY, default_commands_inputs, wait_termination=True
    )

    # cn_versionId = tmc.central_node.versionId

    # # Restart TMC central node device server
    cn_device_server = DeviceProxy(
        f"dserver/{tmc.central_node.info().server_id}"
    )

    cn_device_server.restartserver()

    assert wait_and_validate_device_attribute_value(
        tmc.central_node,
        "defaultarraylayouturl",
        expected_value=json.dumps(
            {
                "source_uris": pytest.source_uris,
                "array_layout_path": pytest.array_layout_path,
            }
        ),
        is_json=True,
    )

    assert wait_and_validate_device_attribute_value(
        tmc.central_node,
        "arraylayouturl",
        expected_value=json.dumps(
            {
                "source_uris": pytest.source_uris,
                "array_layout_path": pytest.array_layout_path,
            }
        ),
        is_json=True,
    )

    assert tmc.subarray_node.obsstate == ObsState.EMPTY
    assert tmc.csp_subarray_leaf_node.cspsubarrayobsstate == ObsState.EMPTY
    assert tmc.sdp_subarray_leaf_node.sdpsubarrayobsstate == ObsState.EMPTY
    assert tmc.mccs_subarray_leaf_node.obsstate == ObsState.EMPTY

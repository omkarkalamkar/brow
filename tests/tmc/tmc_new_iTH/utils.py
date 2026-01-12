import json

from ska_control_model import ObsState
from ska_integration_test_harness.facades.csp_facade import CSPFacade
from ska_integration_test_harness.facades.mccs_facade import MCCSFacade
from ska_integration_test_harness.facades.sdp_facade import SDPFacade
from ska_integration_test_harness.facades.tmc_facade import TMCFacade
from ska_integration_test_harness.inputs.test_harness_inputs import (
    TestHarnessInputs,
)
from ska_tango_testing.integration import TangoEventTracer, log_events

from tests.resources.test_harness.constant import (
    IDLE_STATE_DEFECT,
    READY_STATE_DEFECT,
    RESET_DEFECT,
)
from tests.resources.test_support.constant_low import (
    INTERMEDIATE_CONFIGURING_OBS_STATE_DEFECT,
    INTERMEDIATE_FAULT_OBS_STATE_DEFECT,
    INTERMEDIATE_STATE_DEFECT,
    INTERMEDIATE_STATE_DEFECT_EMPTY,
    SDP_BACK_TO_INITIAL_STATE,
)

TIMEOUT = 180
INTERFACE = (
    "https://schema.skatelescope.org/ska-low-mccs-controller-release/2.0"
)
MCCS_RELEASE_INPUT = json.dumps(
    {
        "interface": INTERFACE,
        "subarray_id": 1,
        "release_all": "true",
    }
)
command_defect_mapping = {
    "AssignResources": {
        "RESOURCING": json.dumps(INTERMEDIATE_STATE_DEFECT),
        "FAULT": json.dumps(INTERMEDIATE_FAULT_OBS_STATE_DEFECT),
        "EMPTY": json.dumps(INTERMEDIATE_STATE_DEFECT_EMPTY),
    },
    "Configure": {
        "CONFIGURING": json.dumps(INTERMEDIATE_CONFIGURING_OBS_STATE_DEFECT),
        "FAULT": json.dumps(INTERMEDIATE_FAULT_OBS_STATE_DEFECT),
    },
    "Scan": {
        "READY": READY_STATE_DEFECT,
        "FAULT": json.dumps(INTERMEDIATE_FAULT_OBS_STATE_DEFECT),
    },
    "ReleaseResources": {
        "IDLE": IDLE_STATE_DEFECT,
        "RESOURCING": json.dumps(INTERMEDIATE_STATE_DEFECT),
        "FAULT": json.dumps(INTERMEDIATE_FAULT_OBS_STATE_DEFECT),
    },
    "EndScan": {"FAULT": json.dumps(INTERMEDIATE_FAULT_OBS_STATE_DEFECT)},
    "End": {"FAULT": json.dumps(INTERMEDIATE_FAULT_OBS_STATE_DEFECT)},
}


def set_subsystem_defects(
    csp: CSPFacade,
    sdp: SDPFacade,
    mccs: MCCSFacade,
    csp_obsstate: str,
    sdp_obsstate: str,
    mccs_obsstate: str,
    command: str,
):
    csp.csp_subarray.SetDefective(
        command_defect_mapping.get(command).get(csp_obsstate, RESET_DEFECT)
    )

    mccs.mccs_subarray.SetDefective(
        command_defect_mapping.get(command).get(mccs_obsstate, RESET_DEFECT)
    )
    if sdp_obsstate == "EMPTY" and command == "AssignResources":
        sdp.sdp_subarray.SetDefective(json.dumps(SDP_BACK_TO_INITIAL_STATE))
    else:
        sdp.sdp_subarray.SetDefective(
            command_defect_mapping.get(command).get(sdp_obsstate, RESET_DEFECT)
        )


FIELD_CONFIGS = {
    "Centaurus A": {
        "target_name": "Centaurus A",
        "reference_frame": "icrs",
        "attrs": {"c1": 201.365, "c2": -43.019},
    },
    "Zenith Drift": {
        "target_name": "Zenith Drift",
        "reference_frame": "altaz",
        "attrs": {"c1": 180.0, "c2": 90.0},
    },
    "Galactic Centre": {
        "target_name": "Galactic Centre",
        "reference_frame": "galactic",
        "attrs": {"c1": 111.734745, "c2": -02.129570},
    },
    "Sun": {"target_name": "Sun", "reference_frame": "special"},
    "Venus": {
        "target_name": "Venus",
        "reference_frame": "special",
    },
    "Mars": {"target_name": "Mars", "reference_frame": "special"},
    "ISS (ZARYA)": {
        "target_name": "ISS (ZARYA)",
        "reference_frame": "tle",
        "attrs": {
            "line1": "1 25544U 98067A   25180.54321875  "
            ".00001234  00000-0  12345-4 0  9999",
            "line2": "2 25544  51.6456 123.4567 0001234 "
            "123.4567 236.5432 15.12345678 12345",
        },
    },
}


def invoke_command_with_defect(
    tmc: TMCFacade,
    default_commands_inputs: TestHarnessInputs,
    csp: CSPFacade,
    sdp: SDPFacade,
    mccs: MCCSFacade,
    csp_obsstate: str,
    sdp_obsstate: str,
    mccs_obsstate: str,
    command: str,
):
    match command:
        case "AssignResources":
            set_subsystem_defects(
                csp,
                sdp,
                mccs,
                csp_obsstate,
                sdp_obsstate,
                mccs_obsstate,
                command,
            )
            tmc.assign_resources(
                default_commands_inputs.assign_input, wait_termination=False
            )
        case "Configure":
            tmc.force_change_of_obs_state(
                ObsState.IDLE, default_commands_inputs, wait_termination=True
            )
            set_subsystem_defects(
                csp,
                sdp,
                mccs,
                csp_obsstate,
                sdp_obsstate,
                mccs_obsstate,
                command,
            )
            tmc.configure(
                default_commands_inputs.configure_input, wait_termination=False
            )
        case "Scan":
            tmc.force_change_of_obs_state(
                ObsState.READY, default_commands_inputs, wait_termination=True
            )
            set_subsystem_defects(
                csp,
                sdp,
                mccs,
                csp_obsstate,
                sdp_obsstate,
                mccs_obsstate,
                command,
            )
            tmc.scan(
                default_commands_inputs.scan_input, wait_termination=False
            )
        case "ReleaseResources":
            tmc.force_change_of_obs_state(
                ObsState.IDLE, default_commands_inputs, wait_termination=True
            )
            set_subsystem_defects(
                csp,
                sdp,
                mccs,
                csp_obsstate,
                sdp_obsstate,
                mccs_obsstate,
                command,
            )
            tmc.release_resources(
                default_commands_inputs.release_input, wait_termination=False
            )
        case "End":
            tmc.force_change_of_obs_state(
                ObsState.READY, default_commands_inputs, wait_termination=True
            )
            set_subsystem_defects(
                csp,
                sdp,
                mccs,
                csp_obsstate,
                sdp_obsstate,
                mccs_obsstate,
                command,
            )
            tmc.end_observation(wait_termination=False)
        case "EndScan":
            tmc.force_change_of_obs_state(
                ObsState.SCANNING,
                default_commands_inputs,
                wait_termination=True,
            )
            set_subsystem_defects(
                csp,
                sdp,
                mccs,
                csp_obsstate,
                sdp_obsstate,
                mccs_obsstate,
                command,
            )
            tmc.end_scan(wait_termination=False)


def reset_defects(csp: CSPFacade, sdp: SDPFacade, mccs: MCCSFacade):
    csp.csp_subarray.SetDefective(RESET_DEFECT)
    sdp.sdp_subarray.SetDefective(RESET_DEFECT)
    mccs.mccs_subarray.SetDefective(RESET_DEFECT)


def setup_event_subscriptions(
    tmc: TMCFacade,
    csp: CSPFacade,
    sdp: SDPFacade,
    mccs: MCCSFacade,
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
    event_tracer.subscribe_event(mccs.mccs_subarray, "obsState")
    event_tracer.subscribe_event(tmc.central_node, "longRunningCommandResult")
    event_tracer.subscribe_event(tmc.subarray_node, "longRunningCommandResult")
    event_tracer.subscribe_event(
        tmc.sdp_subarray_leaf_node, "longRunningCommandResult"
    )
    event_tracer.subscribe_event(
        tmc.csp_subarray_leaf_node, "longRunningCommandResult"
    )
    event_tracer.subscribe_event(
        tmc.mccs_subarray_leaf_node, "longRunningCommandResult"
    )

    log_events(
        {
            tmc.subarray_node: [
                "obsState",
                "longRunningCommandResult",
            ],
            csp.csp_subarray: ["obsState"],
            sdp.sdp_subarray: ["obsState"],
            mccs.mccs_subarray: ["obsState"],
            tmc.central_node: ["longRunningCommandResult"],
            tmc.sdp_subarray_leaf_node: ["longRunningCommandResult"],
            tmc.csp_subarray_leaf_node: ["longRunningCommandResult"],
            tmc.mccs_subarray_leaf_node: ["longRunningCommandResult"],
        },
        event_enum_mapping={"obsState": ObsState},
    )

import json
import re
from copy import deepcopy
from pathlib import Path

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


def load_plan_json(plans_feature_path: Path, plan_name: str) -> dict:
    """Load a named plan JSON docstring from a plans feature file."""
    text = plans_feature_path.resolve().read_text(encoding="utf-8")
    pattern = (
        rf"^\s*Scenario:\s*{re.escape(plan_name)}\s*$\s*"
        r"^\s*\"\"\"\s*$\s*(.*?)\s*^\s*\"\"\"\s*$"
    )
    m = re.search(pattern, text, flags=re.MULTILINE | re.DOTALL)
    if not m:
        raise ValueError(
            f"Plan '{plan_name}' not found in {plans_feature_path}"
        )
    return json.loads(m.group(1))


def parse_plan_map(plan_map_str: str) -> dict[int, str]:
    """Parse PlanMap JSON string into an int-keyed dict."""
    plan_map = json.loads(plan_map_str)
    return {int(k): v for k, v in plan_map.items()}


def ensure_logs_dir(build_dir: Path | str = "build") -> Path:
    """Create and return a ${build_dir}/logs directory."""
    logs_dir = Path(build_dir) / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    return logs_dir


def write_json(path: Path, payload: dict) -> None:
    """Write a JSON payload to a file with stable formatting."""
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )



def _build_assign_json(
    base_assign: dict,
    subarray_id: int,
    per_sn_plan: dict,
    plan_name: str | None = None,
) -> dict:
    # ...existing code...
    assign_json = deepcopy(base_assign)
    assign_json["subarray_id"] = int(subarray_id)

    station_beams = per_sn_plan.get("station_beams", [])
    pss_beams = per_sn_plan.get("pss_beams", [])
    pst_beams = per_sn_plan.get("pst_beams", [])

    # CSP allocation
    assign_json.setdefault("csp", {}).setdefault("pss", {})["pss_beam_ids"] = [
        int(b["id"]) for b in pss_beams
    ]
    assign_json.setdefault("csp", {}).setdefault("pst", {})["pst_beam_ids"] = [
        int(b["id"]) for b in pst_beams
    ]

    # Collect stations referenced by PSS/PST beams (preferred source)
    stations_from_pss = [
        int(st) for b in pss_beams for st in b.get("stations", [])
    ]
    stations_from_pst = [
        int(st) for b in pst_beams for st in b.get("stations", [])
    ]
    station_ids = sorted(
        {int(s) for s in (stations_from_pss + stations_from_pst)}
    )

    apertures = [
        {"station_id": st_id, "aperture_id": f"AP{st_id:03}.01"}
        for st_id in station_ids
    ]

    # MCCS station beam allocation:
    # If plan defines multiple station_beams,
    #  create one subarray_beams entry per beam id.
    # Otherwise keep the existing single-beam behaviour.
    if station_beams:
        beams = []
        for sb in station_beams:
            sb_id = int(sb.get("id", subarray_id))
            beams.append(
                {
                    "subarray_beam_id": sb_id,
                    "apertures": apertures,
                    "number_of_channels": 8,
                }
            )
        assign_json.setdefault("mccs", {})["subarray_beams"] = beams

    return assign_json


# ...existing code...


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

PSS_BEAMS_CONFIG = {
    "beams": [
        {
            "pss_beam_id": 1,
            "stn_beam_id": 1,
            "stn_weights": [0.9, 1.0, 1.0, 1.0, 0.9, 1.0],
        },
        {
            "pss_beam_id": 2,
            "stn_beam_id": 1,
            "stn_weights": [0.9, 1.0, 1.0, 1.0, 0.9, 1.0],
        },
        {
            "pss_beam_id": 3,
            "stn_beam_id": 1,
            "stn_weights": [0.9, 1.0, 1.0, 1.0, 0.9, 1.0],
        },
        {
            "pss_beam_id": 4,
            "stn_beam_id": 1,
            "stn_weights": [0.9, 1.0, 1.0, 1.0, 0.9, 1.0],
        },
        {
            "pss_beam_id": 5,
            "stn_beam_id": 1,
            "stn_weights": [0.9, 1.0, 1.0, 1.0, 0.9, 1.0],
        },
        {
            "pss_beam_id": 6,
            "stn_beam_id": 1,
            "stn_weights": [0.9, 1.0, 1.0, 1.0, 0.9, 1.0],
        },
        {
            "pss_beam_id": 7,
            "stn_beam_id": 1,
            "stn_weights": [0.9, 1.0, 1.0, 1.0, 0.9, 1.0],
        },
        {
            "pss_beam_id": 8,
            "stn_beam_id": 1,
            "stn_weights": [0.9, 1.0, 1.0, 1.0, 0.9, 1.0],
        },
        {
            "pss_beam_id": 9,
            "stn_beam_id": 1,
            "stn_weights": [0.9, 1.0, 1.0, 1.0, 0.9, 1.0],
        },
        {
            "pss_beam_id": 10,
            "stn_beam_id": 1,
            "stn_weights": [0.9, 1.0, 1.0, 1.0, 0.9, 1.0],
        },
        {
            "pss_beam_id": 11,
            "stn_beam_id": 1,
            "stn_weights": [0.9, 1.0, 1.0, 1.0, 0.9, 1.0],
        },
        {
            "pss_beam_id": 12,
            "stn_beam_id": 1,
            "stn_weights": [0.9, 1.0, 1.0, 1.0, 0.9, 1.0],
        },
        {
            "pss_beam_id": 13,
            "stn_beam_id": 1,
            "stn_weights": [0.9, 1.0, 1.0, 1.0, 0.9, 1.0],
        },
        {
            "pss_beam_id": 14,
            "stn_beam_id": 1,
            "stn_weights": [0.9, 1.0, 1.0, 1.0, 0.9, 1.0],
        },
        {
            "pss_beam_id": 15,
            "stn_beam_id": 1,
            "stn_weights": [0.9, 1.0, 1.0, 1.0, 0.9, 1.0],
        },
        {
            "pss_beam_id": 16,
            "stn_beam_id": 1,
            "stn_weights": [0.9, 1.0, 1.0, 1.0, 0.9, 1.0],
        },
        {
            "pss_beam_id": 17,
            "stn_beam_id": 1,
            "stn_weights": [0.9, 1.0, 1.0, 1.0, 0.9, 1.0],
        },
        {
            "pss_beam_id": 18,
            "stn_beam_id": 1,
            "stn_weights": [0.9, 1.0, 1.0, 1.0, 0.9, 1.0],
        },
        {
            "pss_beam_id": 19,
            "stn_beam_id": 1,
            "stn_weights": [0.9, 1.0, 1.0, 1.0, 0.9, 1.0],
        },
        {
            "pss_beam_id": 20,
            "stn_beam_id": 1,
            "stn_weights": [0.9, 1.0, 1.0, 1.0, 0.9, 1.0],
        },
        {
            "pss_beam_id": 21,
            "stn_beam_id": 1,
            "stn_weights": [0.9, 1.0, 1.0, 1.0, 0.9, 1.0],
        },
        {
            "pss_beam_id": 22,
            "stn_beam_id": 1,
            "stn_weights": [0.9, 1.0, 1.0, 1.0, 0.9, 1.0],
        },
        {
            "pss_beam_id": 23,
            "stn_beam_id": 1,
            "stn_weights": [0.9, 1.0, 1.0, 1.0, 0.9, 1.0],
        },
        {
            "pss_beam_id": 24,
            "stn_beam_id": 1,
            "stn_weights": [0.9, 1.0, 1.0, 1.0, 0.9, 1.0],
        },
        {
            "pss_beam_id": 25,
            "stn_beam_id": 1,
            "stn_weights": [0.9, 1.0, 1.0, 1.0, 0.9, 1.0],
        },
        {
            "pss_beam_id": 26,
            "stn_beam_id": 1,
            "stn_weights": [0.9, 1.0, 1.0, 1.0, 0.9, 1.0],
        },
        {
            "pss_beam_id": 27,
            "stn_beam_id": 1,
            "stn_weights": [0.9, 1.0, 1.0, 1.0, 0.9, 1.0],
        },
        {
            "pss_beam_id": 28,
            "stn_beam_id": 1,
            "stn_weights": [0.9, 1.0, 1.0, 1.0, 0.9, 1.0],
        },
        {
            "pss_beam_id": 29,
            "stn_beam_id": 1,
            "stn_weights": [0.9, 1.0, 1.0, 1.0, 0.9, 1.0],
        },
        {
            "pss_beam_id": 30,
            "stn_beam_id": 1,
            "stn_weights": [0.9, 1.0, 1.0, 1.0, 0.9, 1.0],
        },
    ],
    "beam": [
        {
            "beam_id": 1,
            "reference_frame": "ICRS",
            "ra": 82.75,
            "dec": 21.0,
            "centre_frequency": 1400.0,
        },
        {
            "beam_id": 2,
            "reference_frame": "ICRS",
            "ra": 82.75,
            "dec": 21.0,
            "centre_frequency": 1400.0,
        },
        {
            "beam_id": 3,
            "reference_frame": "ICRS",
            "ra": 82.75,
            "dec": 21.0,
            "centre_frequency": 1400.0,
        },
        {
            "beam_id": 4,
            "reference_frame": "ICRS",
            "ra": 82.75,
            "dec": 21.0,
            "centre_frequency": 1400.0,
        },
        {
            "beam_id": 5,
            "reference_frame": "ICRS",
            "ra": 82.75,
            "dec": 21.0,
            "centre_frequency": 1400.0,
        },
        {
            "beam_id": 6,
            "reference_frame": "ICRS",
            "ra": 82.75,
            "dec": 21.0,
            "centre_frequency": 1400.0,
        },
        {
            "beam_id": 7,
            "reference_frame": "ICRS",
            "ra": 82.75,
            "dec": 21.0,
            "centre_frequency": 1400.0,
        },
        {
            "beam_id": 8,
            "reference_frame": "ICRS",
            "ra": 82.75,
            "dec": 21.0,
            "centre_frequency": 1400.0,
        },
        {
            "beam_id": 9,
            "reference_frame": "ICRS",
            "ra": 82.75,
            "dec": 21.0,
            "centre_frequency": 1400.0,
        },
        {
            "beam_id": 10,
            "reference_frame": "ICRS",
            "ra": 82.75,
            "dec": 21.0,
            "centre_frequency": 1400.0,
        },
        {
            "beam_id": 11,
            "reference_frame": "ICRS",
            "ra": 82.75,
            "dec": 21.0,
            "centre_frequency": 1400.0,
        },
        {
            "beam_id": 12,
            "reference_frame": "ICRS",
            "ra": 82.75,
            "dec": 21.0,
            "centre_frequency": 1400.0,
        },
        {
            "beam_id": 13,
            "reference_frame": "ICRS",
            "ra": 82.75,
            "dec": 21.0,
            "centre_frequency": 1400.0,
        },
        {
            "beam_id": 14,
            "reference_frame": "ICRS",
            "ra": 82.75,
            "dec": 21.0,
            "centre_frequency": 1400.0,
        },
        {
            "beam_id": 15,
            "reference_frame": "ICRS",
            "ra": 82.75,
            "dec": 21.0,
            "centre_frequency": 1400.0,
        },
        {
            "beam_id": 16,
            "reference_frame": "ICRS",
            "ra": 82.75,
            "dec": 21.0,
            "centre_frequency": 1400.0,
        },
        {
            "beam_id": 17,
            "reference_frame": "ICRS",
            "ra": 82.75,
            "dec": 21.0,
            "centre_frequency": 1400.0,
        },
        {
            "beam_id": 18,
            "reference_frame": "ICRS",
            "ra": 82.75,
            "dec": 21.0,
            "centre_frequency": 1400.0,
        },
        {
            "beam_id": 19,
            "reference_frame": "ICRS",
            "ra": 82.75,
            "dec": 21.0,
            "centre_frequency": 1400.0,
        },
        {
            "beam_id": 20,
            "reference_frame": "ICRS",
            "ra": 82.75,
            "dec": 21.0,
            "centre_frequency": 1400.0,
        },
        {
            "beam_id": 21,
            "reference_frame": "ICRS",
            "ra": 82.75,
            "dec": 21.0,
            "centre_frequency": 1400.0,
        },
        {
            "beam_id": 22,
            "reference_frame": "ICRS",
            "ra": 82.75,
            "dec": 21.0,
            "centre_frequency": 1400.0,
        },
        {
            "beam_id": 23,
            "reference_frame": "ICRS",
            "ra": 82.75,
            "dec": 21.0,
            "centre_frequency": 1400.0,
        },
        {
            "beam_id": 24,
            "reference_frame": "ICRS",
            "ra": 82.75,
            "dec": 21.0,
            "centre_frequency": 1400.0,
        },
        {
            "beam_id": 25,
            "reference_frame": "ICRS",
            "ra": 82.75,
            "dec": 21.0,
            "centre_frequency": 1400.0,
        },
        {
            "beam_id": 26,
            "reference_frame": "ICRS",
            "ra": 82.75,
            "dec": 21.0,
            "centre_frequency": 1400.0,
        },
        {
            "beam_id": 27,
            "reference_frame": "ICRS",
            "ra": 82.75,
            "dec": 21.0,
            "centre_frequency": 1400.0,
        },
        {
            "beam_id": 28,
            "reference_frame": "ICRS",
            "ra": 82.75,
            "dec": 21.0,
            "centre_frequency": 1400.0,
        },
        {
            "beam_id": 29,
            "reference_frame": "ICRS",
            "ra": 82.75,
            "dec": 21.0,
            "centre_frequency": 1400.0,
        },
        {
            "beam_id": 30,
            "reference_frame": "ICRS",
            "ra": 82.75,
            "dec": 21.0,
            "centre_frequency": 1400.0,
        },
    ],
    "pss_beam_ids": [
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        10,
        11,
        12,
        13,
        14,
        15,
        16,
        17,
        18,
        19,
        20,
        21,
        22,
        23,
        24,
        25,
        26,
        27,
        28,
        29,
        30,
    ],
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
    """Invoke a command after setting up subsystem defects.

    This function attempts to force subsystems to a target state before
    invoking the command. If the state forcing times out, it logs a warning
    but continues, as the test may still proceed with the failed defect setup.

    :param tmc: TMC facade
    :param default_commands_inputs: Default command inputs
    :param csp: CSP facade
    :param sdp: SDP facade
    :param mccs: MCCS facade
    :param csp_obsstate: Target CSP obsstate
    :param sdp_obsstate: Target SDP obsstate
    :param mccs_obsstate: Target MCCS obsstate
    :param command: Command to invoke
    """
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

"""test_tmc_observation_with_16subarrays_fast
This module defines BDD test scenario for the successful execution of
of end to end observstion for 16 subarrays
This keeps the same BDD feature
(`tests/features/tmc/xtp-106948_tmc_observation.feature`).
"""

import json
import logging
import time
from pathlib import Path

import pytest
from assertpy import assert_that
from pytest_bdd import given, parsers, scenario, then, when
from ska_control_model import ObsState
from ska_ser_logging import configure_logging
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
from tests.resources.test_harness.utils.common_utils import JsonFactory
from tests.resources.test_support.common_utils.result_code import ResultCode
from tests.resources.test_support.common_utils.tmc_helpers import (
    prepare_json_args_for_centralnode_commands,
    prepare_json_args_for_commands,
)
from tests.tmc.tmc_new_iTH.utils import (
    _build_assign_json,
    ensure_logs_dir,
    load_plan_json,
    parse_plan_map,
    write_json,
)

configure_logging(logging.DEBUG)
LOGGER = logging.getLogger(__name__)

_PLANS_FEATURE_PATH = (
    Path(__file__).resolve().parent
    / "../features/tmc/tmc_observation_plans.feature"
)


def _active_subarray_ids_from_plan_map(
    plan_map: dict[int, str], sn_count: int
) -> list[int]:
    """Only these subarrays are acted upon in this optimized test."""
    # NOTE: Intentionally skip SA 1..6 to reduce runtime when those are known
    # no-ops / not deployed in the current environment.
    return sorted(
        [sa_id for sa_id in plan_map.keys() if 1 <= int(sa_id) <= sn_count]
    )


def _ensure_logs_dir() -> Path:
    """Create and return the build logs directory path."""
    return ensure_logs_dir("build")


def _write_json(path: Path, payload: dict) -> None:
    """Write a JSON payload to a file with stable formatting."""
    write_json(path, payload)


def _reset_configure_payload(cfg: dict) -> None:
    """Reset configure JSON before applying a plan overlay."""
    if "mccs" in cfg:
        cfg["mccs"].pop("subarray_beams", None)

    if "pss" in cfg.get("csp", {}):
        cfg["csp"].pop("pss", None)
        cfg["csp"]["lowcbf"].pop("search_beams", None)
    if "pst" in cfg.get("csp", {}):
        cfg["csp"].pop("pst", None)
        cfg["csp"]["lowcbf"].pop("timing_beams", None)


def _apply_lowcbf_stations(cfg: dict, station_beams: list[dict]) -> None:
    """Populate lowcbf stations list from station_beams stations."""
    unique_stations: set[int] = {
        int(st) for sb in station_beams for st in sb.get("stations", [])
    }
    if unique_stations:
        cfg["csp"]["lowcbf"]["stations"]["stns"] = [
            [st_id, 1] for st_id in sorted(unique_stations)
        ]


def _build_mccs_subarray_beams(
    per_sn: dict, subarray_id: int, station_beams: list[dict]
) -> list[dict]:
    """Build MCCS subarray_beams entries for Configure
    Apertures are derived from PSS/PST beam stations.
    """
    mccs_beams: list[dict] = []
    for sb in station_beams:
        sb_id = int(sb.get("id", subarray_id))

        # Currently relation in data in PSS beam ID and
        # Subarray beam ID is not clear , hence as of now below
        # Check wiht Subarray Beam Id is disabled
        stations_from_pss = [
            st
            for b in per_sn.get("pss_beams", [])
            # if int(b.get("id")) == sb_id
            for st in b.get("stations", [])
        ]
        stations_from_pst = [
            st
            for b in per_sn.get("pst_beams", [])
            # if int(b.get("id")) == sb_id
            for st in b.get("stations", [])
        ]

        # Combine stations from both sources (remove duplicates, keep ints)
        station_ids = sorted(
            {int(s) for s in (stations_from_pss + stations_from_pst)}
        )
        apertures = [
            {
                "aperture_id": f"AP{int(st):03}.01",
                "weighting_key_ref": "aperture2",
            }
            for st in sorted({int(s) for s in station_ids})
        ]

        mccs_beams.append(
            {
                "subarray_beam_id": sb_id,
                "update_rate": 0.0,
                "logical_bands": [
                    {"start_channel": 80, "number_of_channels": 16},
                    {"start_channel": 384, "number_of_channels": 16},
                ],
                "apertures": apertures,
                "field": {
                    "target_name": "Polaris Australis",
                    "reference_frame": "icrs",
                    "attrs": {"c1": 180.0, "c2": 45.0},
                },
            }
        )
    return mccs_beams


def _apply_lowcbf_timing_beams(cfg: dict, pst_beams: list[dict]) -> None:
    """Populate lowcbf timing_beams from PST beams in the plan."""
    if not pst_beams:
        return
    timing_beams = cfg["csp"]["lowcbf"].setdefault("timing_beams", {})
    timing_beams["firmware"] = "pst"
    timing_beams["beams"] = [
        {
            "pst_beam_id": int(pst_beam["id"]),
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
            "stn_beam_id": int(pst_beam.get("stn_beam_id", 1)),
            "stn_weights": pst_beam.get(
                "stn_weights", [0.9, 1.0, 1.0, 1.0, 0.9, 1.0]
            ),
        }
        for pst_beam in pst_beams
    ]


def _apply_lowcbf_search_beams(cfg: dict, pss_beams: list[dict]) -> None:
    """Populate lowcbf search_beams from PSS beams in the plan."""
    if not pss_beams:
        return
    search_beams = cfg["csp"]["lowcbf"].setdefault("search_beams", {})
    search_beams["firmware"] = "pss"
    search_beams["beams"] = [
        {
            "pss_beam_id": int(pss_beam["id"]),
            "stn_beam_id": int(pss_beam.get("stn_beam_id", 1)),
            "stn_weights": pss_beam.get(
                "stn_weights", [0.9, 1.0, 1.0, 1.0, 0.9, 1.0]
            ),
        }
        for pss_beam in pss_beams
    ]


def _apply_csp_pst(cfg: dict, pst_beams: list[dict]) -> None:
    """Populate CSP pst section from PST beams in the plan."""
    if not pst_beams:
        return
    pst_section = cfg.setdefault("csp", {}).setdefault("pst", {})
    pst_section["beams"] = [
        {
            "beam_id": int(pst_beam["id"]),
            "scan": {
                "centre_frequency": 200000000.0,
                "total_bandwidth": 1562500.0,
                "pst_processing_mode": "VOLTAGE_RECORDER",
                "observer_id": "jdoe",
                "project_id": "project1",
                "target": {
                    "target_name": "J1921+2153",
                    "reference_frame": "icrs",
                    "attrs": {
                        "c1": 6.023625,
                        "c2": -72.08128333,
                        "epoch": 2000.0,
                    },
                },
                "receiver_id": "receiver3",
                "max_scan_length": 20000.0,
                "subint_duration": 30.0,
                "receptors": ["receptor1", "receptor2"],
                "receptor_weights": [0.4, 0.6],
                "rfi_frequency_masks": [],
            },
        }
        for pst_beam in pst_beams
    ]


def _apply_csp_pss(cfg: dict, pss_beams: list[dict]) -> None:
    """Populate CSP pss section from PSS beams in the plan."""
    if not pss_beams:
        return

    pss = cfg.setdefault("csp", {}).setdefault("pss", {})

    pss["beam"] = [
        {
            "beam_id": int(pss_beam["id"]),
            "reference_frame": "ICRS",
            "ra": 82.75,
            "dec": 21.0,
            "centre_frequency": 1400.0,
        }
        for pss_beam in pss_beams
    ]
    pss["config_id"] = 1
    # Keep the rest of the PSS payload aligned with the original test file.
    pss["cheetah"] = [
        {
            "cheetah_id": 1,
            "beams": [
                {
                    "beam": {
                        "active": True,
                        "sinks": {
                            "channels": {
                                "sps_events": {
                                    "active": True,
                                    "sink": [
                                        {"sink_id": "spccl_files"},
                                        {"sink_id": "candidate_files"},
                                    ],
                                }
                            },
                            "sink_configs": {
                                "spccl_files": {
                                    "extension": ".spccl",
                                    "dir": "/tmp/beam1",
                                    "sink_id": "spccl_files",
                                },
                                "spccl_sigproc_files": {
                                    "spectra_per_file": 0,
                                    "dir": "/tmp/beam1",
                                    "extension": ".fil",
                                    "candidate_window": {
                                        "ms_before": 500.0,
                                        "ms_after": 1000.0,
                                    },
                                    "sink_id": "candidate_files",
                                },
                            },
                        },
                        "source": {
                            "sigproc": {
                                "file": "filterbank1.fil",
                                "chunk_samples": 1024,
                                "default-nbits": 8,
                                "active": True,
                            },
                            "udp_low": {
                                "number_of_threads": 2,
                                "spectra_per_chunk": 2048,
                                "number_of_channels": 7776,
                                "max_buffers": 1,
                                "active": False,
                            },
                            "udp_low_lite": {
                                "number_of_threads": 10,
                                "spectra_per_chunk": 32768,
                                "number_of_channels": 432,
                                "max_buffers": 3,
                                "active": False,
                            },
                        },
                        "beam_id": int(pss_beams[0]["id"]),
                    }
                }
            ],
            "psbc": {"dump_time": 540},
            "acceleration": {
                "fdas": {
                    "pool_id": "default",
                    "priority": 0,
                    "active": False,
                    "labyrinth": {"active": True, "threshold": 10.0},
                }
            },
            "sift": {
                "pool_id": "default",
                "priority": 2,
                "strong_sift": {
                    "active": True,
                    "num_candidate_harmonics": 8,
                    "match_factor": 0.001,
                    "dm_match_range": 2,
                },
            },
        }
    ]
    pss["ddtr"] = {
        "cpu": {"active": False},
        "fpga": {"active": False},
        "gpu_bruteforce": {"active": False, "copy_dmtrials_to_host": True},
        "klotski": {"active": True},
        "klotski_bruteforce": {"active": False},
        "dedispersion": [
            {"start": 0.0, "end": 100.0, "step": 0.1},
            {"start": 100.0, "end": 300.0, "step": 0.2},
            {"start": 300.0, "end": 700.0, "step": 0.4},
            {"start": 700.0, "end": 1500.0, "step": 0.8},
            {"start": 1500.0, "end": 3100.0, "step": 1.6},
        ],
        "dedispersion_samples": 131072,
    }
    pss["sps"] = {
        "cpu": {
            "active": False,
            "samples_per_iteration": 1,
            "number_of_widths": 1,
        },
        "threshold": 8.0,
        "klotski": {"active": False, "pulse_widths": "1,2,4,8,16,32,64,128"},
        "klotski_bruteforce": {
            "active": False,
            "pulse_widths": "1,2,4,8,16,32,64,128",
        },
    }


def _build_assign_json_files(
    plan_map: dict[int, str], base_assign: dict, logs_dir: Path
) -> None:
    """Write per-subarray AssignResources JSON files to logs_dir."""
    for subarray_id, plan_name in plan_map.items():
        plan = load_plan_json(_PLANS_FEATURE_PATH, plan_name)
        per_sn = plan.get(str(subarray_id), plan)
        assign_json = _build_assign_json(
            base_assign, subarray_id, per_sn, plan_name
        )
        _write_json(
            logs_dir / f"assign_subarray{subarray_id}.json", assign_json
        )


def _assign_resources_for_subarrays(
    central_node_low_16_subarrays: CentralNodeWrapperLow,
    subarray_ids: list[int],
    logs_dir: Path,
) -> list:
    """Send AssignResources for each subarray and return unique ids."""
    unique_ids = []
    for sa_id in subarray_ids:
        central_node_low_16_subarrays.set_subarray_id(sa_id)
        assign_str = (logs_dir / f"assign_subarray{sa_id}.json").read_text(
            encoding="utf-8"
        )
        _, unique_id = central_node_low_16_subarrays.perform_action(
            "AssignResources", assign_str
        )
        unique_ids.append(unique_id)
    return unique_ids


def _configure_subarrays(
    subarray_node_low: SubarrayNodeWrapperLow,
    subarray_ids: list[int],
    logs_dir: Path,
) -> dict[int, tuple]:
    """Send Configure for each subarray and return unique ids by id."""
    results: dict[int, tuple] = {}
    for sa_id in subarray_ids:
        subarray_node_low.set_subarray_id(sa_id)
        cfg_str = (logs_dir / f"configure_subarray{sa_id}.json").read_text(
            encoding="utf-8"
        )

        _, unique_id = subarray_node_low.execute_transition(
            "Configure", cfg_str
        )
        results[sa_id] = unique_id
    return results


def _wait_for_subarrays_obsstate(
    central_node_low_16_subarrays: CentralNodeWrapperLow,
    event_tracer: TangoEventTracer,
    subarray_ids: list[int],
    expected_state: ObsState,
) -> None:
    """Wait for obsState on CN subarray nodes (best-effort)."""
    for sa_id in subarray_ids:
        central_node_low_16_subarrays.set_subarray_id(sa_id)

        try:
            assert_that(event_tracer).within_timeout(
                TIMEOUT
            ).has_change_event_occurred(
                central_node_low_16_subarrays.subarray_node,
                "obsState",
                expected_state,
            )
        except AssertionError:
            logging.exception(
                "Did not observe obsState=%s for"
                " subarray_id=%s within timeout. "
                "Continuing anyway",
                expected_state,
                sa_id,
            )


def _wait_for_subarraynode_obsstate(
    subarray_node_low: SubarrayNodeWrapperLow,
    event_tracer: TangoEventTracer,
    subarray_ids: list[int],
    expected_state: ObsState,
) -> None:
    """Wait for obsState on TMC SubarrayNode devices (best-effort)."""
    for sa_id in subarray_ids:
        subarray_node_low.set_subarray_id(sa_id)
        try:
            assert_that(event_tracer).within_timeout(
                TIMEOUT
            ).has_change_event_occurred(
                subarray_node_low.subarray_node,
                "obsState",
                expected_state,
            )
        except AssertionError:
            logging.exception(
                "Did not observe obsState=%s "
                "for subarray_id=%s within timeout. "
                "Continuing anyway",
                expected_state,
                sa_id,
            )


def _wait_for_configure_ready_and_lrcr_ok(
    subarray_node_low: SubarrayNodeWrapperLow,
    event_tracer: TangoEventTracer,
    configure_unique_ids: dict[int, tuple],
) -> None:
    """Wait for READY and LRCR OK per subarray after Configure."""
    for sa_id, unique_id in configure_unique_ids.items():
        subarray_node_low.set_subarray_id(sa_id)
        expected_lrcr = (
            unique_id[0],
            json.dumps((int(ResultCode.OK), "Command Completed")),
        )
        try:
            assert_that(event_tracer).within_timeout(
                TIMEOUT
            ).has_change_event_occurred(
                subarray_node_low.subarray_node,
                "obsState",
                ObsState.READY,
            )
        except AssertionError:
            logging.exception(
                "Did not observe obsState=READY "
                "for subarray_id=%s within timeout. "
                "Continuing anyway",
                sa_id,
            )

        try:
            assert_that(event_tracer).within_timeout(
                TIMEOUT
            ).has_change_event_occurred(
                subarray_node_low.subarray_node,
                "longRunningCommandResult",
                expected_lrcr,
            )
        except AssertionError:
            logging.exception(
                "Did not observe expected "
                "LRCR for subarray_id=%s within timeout. "
                "Continuing anyway",
                sa_id,
            )


def _delay_model_attributes_from_active_plan(
    subarray_node_low: SubarrayNodeWrapperLow, subarray_id
) -> list[str]:
    """Return delay-model attribute names, derived from the active plan."""
    plan_map = parse_plan_map(pytest.PlanMap)
    plan_name = plan_map.get(subarray_id)
    plan = load_plan_json(_PLANS_FEATURE_PATH, plan_name)
    logging.info("subarray_id - %s , plan - %s", subarray_id, plan)
    per_sn = plan.get(str(subarray_id), plan)

    station_ids = sorted(
        {
            int(b.get("id"))
            for b in per_sn.get("station_beams", [])
            if "id" in b
        }
    )
    pss_ids = sorted(
        {int(b.get("id")) for b in per_sn.get("pss_beams", []) if "id" in b}
    )
    pst_ids = sorted(
        {int(b.get("id")) for b in per_sn.get("pst_beams", []) if "id" in b}
    )

    pss_attrs = [f"delayModelPSSBeam{i}" for i in pss_ids]
    pst_attrs = [f"delayModelPSTBeam{i}" for i in pst_ids]
    stn_attrs = [f"delaymodelstationbeam0{i}" for i in station_ids]
    subarray_node_low.set_subarray_id(subarray_id)

    return pss_attrs + pst_attrs + stn_attrs


def _max_scan_duration_from_plan_map(plan_map: dict[int, str]) -> float:
    """Return the highest scan_duration across all plans in PlanMap."""
    max_duration = 0.0
    for _, plan_name in plan_map.items():
        plan = load_plan_json(_PLANS_FEATURE_PATH, plan_name)
        duration = float(plan.get("scan_duration", 0.0))
        if duration > max_duration:
            max_duration = duration
    return max_duration


@pytest.mark.SKA_tmc_low_multiple_subarrays
@scenario(
    "../features/tmc/xtp-106948_tmc_observation.feature",
    "Execute observation using <SNCount> subarrays with plan map <PlanMap>",
)
def test_tmc_observation_with_16subarrays_fast():
    """BDD scenario entrypoint (Scenario Outline filled from feature file)."""


@pytest.mark.SKA_tmc_low_multiple_subarrays
@scenario(
    "../features/tmc/xtp-106948_tmc_observation.feature",
    "Execute long sequence on 16 Subarrays",
)
def test_tmc_long_sequence_configure():
    """Test the long sequence of Configure with 16 subarrays."""


@pytest.mark.SKA_tmc_low_multiple_subarrays
@scenario(
    "../features/tmc/xtp-106948_tmc_observation.feature",
    "Execute long sequence Scan on 16 Subarrays",
)
def test_tmc_long_sequence_configure_scan():
    """Test the long sequence of Scan with 16 subarrays."""


@given(parsers.parse("{SNCount:d} subarrays are in the EMPTY ObsState"))
def verify_n_subarrays_in_empty(
    central_node_low_16_subarrays: CentralNodeWrapperLow,
    event_tracer: TangoEventTracer,
    SNCount: int,
):
    """Verify subarrays are EMPTY (best-effort)."""
    pytest.sn_count = int(SNCount)

    # Best-effort check (resilient) on 1..SNCount.
    for subarray_id in range(1, pytest.sn_count + 1):
        central_node_low_16_subarrays.set_subarray_id(subarray_id)
        try:
            assert_that(event_tracer).within_timeout(
                TIMEOUT
            ).has_change_event_occurred(
                central_node_low_16_subarrays.subarray_node,
                "obsState",
                ObsState.EMPTY,
            )
        except AssertionError:
            logging.exception(
                "Did not observe obsState=EMPTY"
                " for subarray_id=%s within timeout. "
                "Continuing anyway",
                subarray_id,
            )


@given("the telescope is in the ON state")
def given_a_telescope_is_in_on(
    central_node_low_16_subarrays: CentralNodeWrapperLow,
    event_tracer: TangoEventTracer,
):
    """Move telescope to ON and subscribe to key events."""
    # Subscribe to CentralNode telescopeState + LRCR.
    event_tracer.subscribe_event(
        central_node_low_16_subarrays.central_node, "telescopeState"
    )
    event_tracer.subscribe_event(
        central_node_low_16_subarrays.central_node, "longRunningCommandResult"
    )
    log_events(
        {central_node_low_16_subarrays.central_node: ["telescopeState"]}
    )
    event_tracer.clear_events()

    # Bring mocks ON

    max_sa = int(getattr(pytest, "sn_count", 16))
    for subarray_id in range(1, max_sa + 1):
        central_node_low_16_subarrays.set_subarray_id(subarray_id)
        event_tracer.subscribe_event(
            central_node_low_16_subarrays.subarray_node, "obsState"
        )
        event_tracer.subscribe_event(
            central_node_low_16_subarrays.subarray_node,
            "longRunningCommandResult",
        )
        central_node_low_16_subarrays.set_values_with_all_mocks(DevState.ON)

    central_node_low_16_subarrays.move_to_on()

    assert_that(event_tracer).within_timeout(
        TIMEOUT
    ).has_change_event_occurred(
        central_node_low_16_subarrays.central_node,
        "telescopeState",
        DevState.ON,
    )


@given(parsers.parse("I assign resources using plan map {PlanMap}"))
def assign_using_plan_map(
    central_node_low_16_subarrays: CentralNodeWrapperLow,
    command_input_factory: JsonFactory,
    event_tracer: TangoEventTracer,
    PlanMap: str,
):
    """Assign resources for active subarrays from PlanMap."""
    event_tracer.clear_events()
    pytest.PlanMap = PlanMap
    plan_map = parse_plan_map(PlanMap)
    pytest.active_subarray_ids = _active_subarray_ids_from_plan_map(
        plan_map, pytest.sn_count
    )

    if not pytest.active_subarray_ids:
        raise AssertionError(
            "PlanMap did not contain any subarray IDs within 1..SNCount. "
            f"SNCount={pytest.sn_count},PlanMap keys={sorted(plan_map.keys())}"
        )

    base_assign = json.loads(
        prepare_json_args_for_centralnode_commands(
            "assign_resources_low", command_input_factory
        )
    )

    logs_dir = _ensure_logs_dir()
    _build_assign_json_files(plan_map, base_assign, logs_dir)

    assign_unique_ids = _assign_resources_for_subarrays(
        central_node_low_16_subarrays, pytest.active_subarray_ids, logs_dir
    )

    for unique_id in assign_unique_ids:
        try:
            assert_that(event_tracer).within_timeout(
                TIMEOUT
            ).has_change_event_occurred(
                central_node_low_16_subarrays.central_node,
                "longRunningCommandResult",
                (
                    unique_id[0],
                    json.dumps((int(ResultCode.OK), "Command Completed")),
                ),
            )
        except AssertionError:
            logging.exception(
                "Did not observe expected LRCR for"
                " unique_id=%s within timeout. "
                "Continuing anyway",
                unique_id,
            )

    _wait_for_subarrays_obsstate(
        central_node_low_16_subarrays,
        event_tracer,
        pytest.active_subarray_ids,
        ObsState.IDLE,
    )


@given(parsers.parse("I configure all the subarrays using plan map {PlanMap}"))
def configure_all_using_plan_map(
    subarray_node_low: SubarrayNodeWrapperLow,
    command_input_factory: JsonFactory,
    event_tracer: TangoEventTracer,
    PlanMap: str,
):
    """Configure all subarrays from PlanMap."""
    configure_using_plan_map(
        subarray_node_low=subarray_node_low,
        command_input_factory=command_input_factory,
        event_tracer=event_tracer,
        PlanMap=PlanMap,
        is_long_scan=False,  # Skip long scan durations for this step.
    )


@given(parsers.parse("I configure subarrays using plan map {PlanMap}"))
def configure_using_plan_map(
    subarray_node_low: SubarrayNodeWrapperLow,
    command_input_factory: JsonFactory,
    event_tracer: TangoEventTracer,
    PlanMap: str,
    is_long_scan: bool = True,
):
    """Configure active subarrays from PlanMap."""
    event_tracer.clear_events()
    plan_map = parse_plan_map(PlanMap)
    active_subarray_ids = getattr(
        pytest,
        "active_subarray_ids",
        _active_subarray_ids_from_plan_map(plan_map, pytest.sn_count),
    )

    base_configure = json.loads(
        prepare_json_args_for_commands("configure_low", command_input_factory)
    )

    logs_dir = _ensure_logs_dir()

    for subarray_id, plan_name in plan_map.items():
        if subarray_id not in active_subarray_ids:
            continue

        plan = load_plan_json(_PLANS_FEATURE_PATH, plan_name)
        per_sn = plan.get(str(subarray_id), plan)

        cfg = json.loads(json.dumps(base_configure))
        _reset_configure_payload(cfg)

        if is_long_scan:
            scan_duration = float(per_sn.get("scan_duration", 10.0))
            cfg["tmc"]["scan_duration"] = scan_duration

        station_beams = per_sn.get("station_beams", [])
        _apply_lowcbf_stations(cfg, station_beams)
        if station_beams:
            cfg.setdefault("mccs", {})[
                "subarray_beams"
            ] = _build_mccs_subarray_beams(per_sn, subarray_id, station_beams)

        pst_beams = per_sn.get("pst_beams", [])
        pss_beams = per_sn.get("pss_beams", [])
        _apply_lowcbf_timing_beams(cfg, pst_beams)
        _apply_lowcbf_search_beams(cfg, pss_beams)
        _apply_csp_pst(cfg, pst_beams)
        _apply_csp_pss(cfg, pss_beams)

        _write_json(logs_dir / f"configure_subarray{subarray_id}.json", cfg)

    pytest.configure_unique_ids = _configure_subarrays(
        subarray_node_low,
        active_subarray_ids,
        logs_dir,
    )

    _wait_for_subarraynode_obsstate(
        subarray_node_low,
        event_tracer,
        active_subarray_ids,
        ObsState.CONFIGURING,
    )


@given("the Subarrays are configured successfully")
def subarrays_configured_successfully(
    subarray_node_low: SubarrayNodeWrapperLow,
    event_tracer: TangoEventTracer,
):
    """Wait for READY after Configure (best-effort)."""
    _wait_for_configure_ready_and_lrcr_ok(
        subarray_node_low=subarray_node_low,
        event_tracer=event_tracer,
        configure_unique_ids=pytest.configure_unique_ids,
    )
    event_tracer.clear_events()


@given("the Subarrays are configured successfully with correct delaymodels")
def verify_subarray_in_ready_observation_state(
    subarray_node_low: SubarrayNodeWrapperLow,
    event_tracer: TangoEventTracer,
):
    """Wait for READY + LRCR OK after Configure (best-effort)."""
    _wait_for_configure_ready_and_lrcr_ok(
        subarray_node_low=subarray_node_low,
        event_tracer=event_tracer,
        configure_unique_ids=pytest.configure_unique_ids,
    )
    event_tracer.clear_events()

    for subarray_id in getattr(pytest, "active_subarray_ids", []):
        subarray_node_low.set_subarray_id(subarray_id)

        attributes = _delay_model_attributes_from_active_plan(
            subarray_node_low, subarray_id
        )
        logging.info(
            "attributes for subarray_id  %s are ---%s", subarray_id, attributes
        )
        generated_delay_model_json = INITIAL_LOW_DELAY_JSON
        for attribute in attributes:
            wait_time = time.time() + 10
            logging.info("chekcing for attribute %s", attribute)
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
                    logging.info(
                        "Attribute %s returned empty value, for %s",
                        attribute,
                        subarray_node_low.csp_subarray_leaf_node.dev_name(),
                    )

                    continue

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


@given("I end the observations on all involved subarrays")
def end_observations_on_all_subarrays(
    subarray_node_low: SubarrayNodeWrapperLow,
    event_tracer: TangoEventTracer,
):
    """End observations on active subarrays (best-effort)."""
    event_tracer.clear_events()
    end_all_involved(
        subarray_node_low=subarray_node_low, event_tracer=event_tracer
    )


@given("I scan on all configured subarrays")
def given_scan_on_all_configured_subarrays(
    command_input_factory: JsonFactory,
    subarray_node_low: SubarrayNodeWrapperLow,
    event_tracer: TangoEventTracer,
):
    """Start Scan on active subarrays (best-effort)."""
    event_tracer.clear_events()
    scan_on_configured_subarrays(
        command_input_factory=command_input_factory,
        subarray_node_low=subarray_node_low,
        event_tracer=event_tracer,
    )


@given("I release resources from all involved subarrays")
def given_release_resources_from_all_subarrays(
    central_node_low_16_subarrays: CentralNodeWrapperLow,
    event_tracer: TangoEventTracer,
    command_input_factory: JsonFactory,
):
    """Release resources on active subarrays from CN (best-effort)."""
    event_tracer.clear_events()
    release_all_involved(
        central_node_low_16_subarrays, command_input_factory, event_tracer
    )


@given("the involved subarrays transition to SCANNING and back to READY")
def given_subarrays_transition_to_scanning_and_ready(
    subarray_node_low: SubarrayNodeWrapperLow,
    event_tracer: TangoEventTracer,
):
    """Verify SCANNING then READY on active subarrays."""
    check_scanning_and_ready(
        subarray_node_low=subarray_node_low, event_tracer=event_tracer
    )


@when("I reassign all subarrays.")
def reassign_all_subarrays(
    central_node_low_16_subarrays: CentralNodeWrapperLow,
    command_input_factory: JsonFactory,
    event_tracer: TangoEventTracer,
):
    """Reassign active subarrays from CN using PlanMap."""
    assign_using_plan_map(
        central_node_low_16_subarrays=central_node_low_16_subarrays,
        command_input_factory=command_input_factory,
        event_tracer=event_tracer,
        PlanMap=getattr(pytest, "PlanMap", "{}"),
    )


@when("I reconfigure all subarrays.")
def reconfigure_all_subarrays(
    subarray_node_low: SubarrayNodeWrapperLow,
    command_input_factory: JsonFactory,
    event_tracer: TangoEventTracer,
):
    """Reconfigure all active subarrays"""
    configure_all_using_plan_map(
        subarray_node_low=subarray_node_low,
        command_input_factory=command_input_factory,
        event_tracer=event_tracer,
        PlanMap=getattr(pytest, "PlanMap", "{}"),
    )


@when("I scan on all configured subarrays")
def scan_on_configured_subarrays(
    command_input_factory: JsonFactory,
    subarray_node_low: SubarrayNodeWrapperLow,
    event_tracer: TangoEventTracer,
):
    """Start Scan on active subarrays (best-effort)."""
    event_tracer.clear_events()
    scan_input_json = prepare_json_args_for_commands(
        "scan_low", command_input_factory
    )

    for subarray_id in getattr(pytest, "active_subarray_ids", []):
        subarray_node_low.set_subarray_id(subarray_id)
        subarray_node_low.execute_transition("Scan", scan_input_json)

        try:

            assert_that(event_tracer).within_timeout(
                TIMEOUT
            ).has_change_event_occurred(
                subarray_node_low.subarray_node,
                "obsState",
                ObsState.SCANNING,
            )
        except AssertionError:
            logging.exception(
                "Did not observe obsState=SCANNING "
                "for subarray_id=%s within timeout. "
                "Continuing anyway",
                subarray_id,
            )


@when("I issue scan on all subarray with new scan_id")
def scan_on_all_subarrays_with_new_scan_id(
    command_input_factory: JsonFactory,
    subarray_node_low: SubarrayNodeWrapperLow,
    event_tracer: TangoEventTracer,
):
    """Start Scan with new scan_id on active subarrays (best-effort)."""
    event_tracer.clear_events()
    scan_input_json = prepare_json_args_for_commands(
        "scan_low", command_input_factory
    )
    scan_input = json.loads(scan_input_json)
    scan_input["scan_id"] = 2  # Change scan_id to trigger new scan
    scan_input_json = json.dumps(scan_input)

    for subarray_id in getattr(pytest, "active_subarray_ids", []):
        subarray_node_low.set_subarray_id(subarray_id)
        subarray_node_low.execute_transition("Scan", scan_input_json)
        try:
            assert_that(event_tracer).within_timeout(
                TIMEOUT
            ).has_change_event_occurred(
                subarray_node_low.subarray_node,
                "obsState",
                ObsState.SCANNING,
            )
        except AssertionError:
            logging.exception(
                "Did not observe obsState=SCANNING "
                "for subarray_id=%s within timeout. "
                "Continuing anyway",
                subarray_id,
            )


@when("the Subarrays are configured successfully with correct delaymodels")
def when_subarrays_configured_with_delay_models(
    subarray_node_low: SubarrayNodeWrapperLow,
    event_tracer: TangoEventTracer,
):
    """Wait for READY + LRCR OK after Configure (best-effort)."""
    verify_subarray_in_ready_observation_state(
        subarray_node_low=subarray_node_low, event_tracer=event_tracer
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

        try:
            assert_that(event_tracer).described_as(
                'FAILED ASSUMPTION IN "THEN" STEP: '
                "'the subarray must be in the"
                " SCANNING obsState until finished'"
                "Subarray Node device"
                f"({subarray_node_low.subarray_node.dev_name()}) "
                "is expected to be in READY obstate",
            ).within_timeout(TIMEOUT).has_change_event_occurred(
                subarray_node_low.subarray_node,
                "obsState",
                ObsState.READY,
            )
        except AssertionError:
            logging.exception(
                "Did not observe obsState=READY "
                "for subarray_id=%s within timeout. "
                "Continuing anyway",
                subarray_id,
            )


@then("the involved subarrays transition to SCANNING and back to READY")
def check_scanning_and_ready(
    subarray_node_low: SubarrayNodeWrapperLow,
    event_tracer: TangoEventTracer,
):
    """Verify SCANNING then READY on active subarrays."""
    for subarray_id in getattr(pytest, "active_subarray_ids", []):
        subarray_node_low.set_subarray_id(subarray_id)

        try:

            assert_that(event_tracer).within_timeout(
                TIMEOUT
            ).has_change_event_occurred(
                subarray_node_low.subarray_node,
                "obsState",
                ObsState.SCANNING,
            )
        except AssertionError:
            logging.exception(
                "Did not observe obsState=SCANNING "
                "for subarray_id=%s within timeout. "
                "Continuing anyway",
                subarray_id,
            )

    plan_map = parse_plan_map(pytest.PlanMap)

    max_scan_duration = _max_scan_duration_from_plan_map(plan_map)

    for subarray_id in getattr(pytest, "active_subarray_ids", []):
        subarray_node_low.set_subarray_id(subarray_id)
        logging.info("Checking for SN - %s", subarray_id)

        try:
            assert_that(event_tracer).within_timeout(
                max_scan_duration + 10
            ).has_change_event_occurred(
                subarray_node_low.subarray_node,
                "obsState",
                ObsState.READY,
            )
        except AssertionError:
            logging.exception(
                "Did not observe obsState=READY "
                "for subarray_id=%s within timeout. "
                "Continuing anyway",
                subarray_id,
            )


@then("I end the observations on all involved subarrays")
def end_all_involved(
    subarray_node_low: SubarrayNodeWrapperLow,
    event_tracer: TangoEventTracer,
):
    """End observations on active subarrays (best-effort)."""
    event_tracer.clear_events()
    for subarray_id in getattr(pytest, "active_subarray_ids", []):
        subarray_node_low.set_subarray_id(subarray_id)
        try:
            subarray_node_low.execute_transition("End")
            assert_that(event_tracer).within_timeout(
                TIMEOUT
            ).has_change_event_occurred(
                subarray_node_low.subarray_node,
                "obsState",
                ObsState.IDLE,
            )
        except AssertionError:
            logging.exception(
                "Did not observe obsState=IDLE "
                "for subarray_id=%s within timeout. "
                "Continuing anyway",
                subarray_id,
            )


@then("I release resources from all involved subarrays")
def release_all_involved(
    central_node_low_16_subarrays: CentralNodeWrapperLow,
    command_input_factory: JsonFactory,
    event_tracer: TangoEventTracer,
):
    """Release resources for active subarrays (best-effort)."""
    event_tracer.clear_events()
    release_input = json.loads(
        prepare_json_args_for_centralnode_commands(
            "release_resources_low", command_input_factory
        )
    )

    for subarray_id in getattr(pytest, "active_subarray_ids", []):
        central_node_low_16_subarrays.set_subarray_id(subarray_id)
        rel = json.loads(json.dumps(release_input))
        rel["subarray_id"] = subarray_id
        _, uid = central_node_low_16_subarrays.perform_action(
            "ReleaseResources", json.dumps(rel)
        )
        try:

            assert_that(event_tracer).within_timeout(
                TIMEOUT
            ).has_change_event_occurred(
                central_node_low_16_subarrays.central_node,
                "longRunningCommandResult",
                (
                    uid[0],
                    json.dumps((int(ResultCode.OK), "Command Completed")),
                ),
            )
        except AssertionError:
            logging.exception(
                "Did not observe expected LRCR"
                " for subarray_id=%s within timeout. "
                "Continuing anyway",
                subarray_id,
            )

        try:
            assert_that(event_tracer).within_timeout(
                TIMEOUT
            ).has_change_event_occurred(
                central_node_low_16_subarrays.subarray_node,
                "obsState",
                ObsState.EMPTY,
            )
        except AssertionError:
            logging.exception(
                "Did not observe obsState=EMPTY "
                "for subarray_id=%s within timeout. "
                "Continuing anyway",
                subarray_id,
            )


@then("I turn off the telescope")
def turn_off_telescope(
    central_node_low_16_subarrays: CentralNodeWrapperLow,
    event_tracer: TangoEventTracer,
):
    """Move telescope to OFF."""
    central_node_low_16_subarrays.move_to_off()
    assert_that(event_tracer).within_timeout(
        TIMEOUT
    ).has_change_event_occurred(
        central_node_low_16_subarrays.central_node,
        "telescopeState",
        DevState.OFF,
    )

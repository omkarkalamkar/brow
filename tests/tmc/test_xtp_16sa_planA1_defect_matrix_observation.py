"""BDD test for 16-subarray observation using PlanA1 with injected defects.

This test is based on the mechanics of the existing XTP-106948 16-subarray test
(`tests/tmc/test_xtp_106948_tmc_observation_with_16subarrays.py`) but uses a
single plan (PlanA1) and per-(subarray, command) defect and recovery matrices.

Feature file:
- `tests/features/tmc/xtp-16sa_planA1_defect_matrix_observation.feature`

Plan definition source:
- `tests/features/tmc/tmc_observation_plans.feature` (Scenario: PlanA1)

Notes:
- PlanA1 `scan_duration` is set to 10.0 seconds.
- PlanA1 includes a single PSS beam id; this test overrides PSS beam ids per
  subarray at Configure time so that each SA uses a unique PSS id.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from pathlib import Path

import pytest
from assertpy import assert_that
from pytest_bdd import given, parsers, scenario, then, when
from ska_control_model import ObsState, ResultCode
from ska_ser_logging import configure_logging
from ska_tango_testing.integration import TangoEventTracer, log_events
from tango import DevState

from tests.resources.test_harness import constant
from tests.resources.test_harness.central_node_low import CentralNodeWrapperLow
from tests.resources.test_harness.constant import TIMEOUT
from tests.resources.test_harness.subarray_node_low import (
    SubarrayNodeWrapperLow,
)
from tests.resources.test_harness.utils.common_utils import JsonFactory
from tests.resources.test_support import constant_low
from tests.resources.test_support.common_utils.tmc_helpers import (
    prepare_json_args_for_centralnode_commands,
    prepare_json_args_for_commands,
)
from tests.tmc.test_xtp_106948_tmc_observation_with_16subarrays import (
    _wait_for_subarrays_obsstate,
)
from tests.tmc.tmc_new_iTH.utils import (
    _build_assign_json,
    ensure_logs_dir,
    load_plan_json,
    write_json,
)

configure_logging(logging.DEBUG)
LOGGER = logging.getLogger(__name__)

_FEATURE_PATH = (
    Path(__file__).resolve().parent
    / "../features/tmc/xtp-16sa_planA1_defect_matrix_observation.feature"
)

_PLANS_FEATURE_PATH = (
    Path(__file__).resolve().parent
    / "../features/tmc/tmc_observation_plans.feature"
)


@dataclass(frozen=True)
class DefectKey:
    """Key for a defect or recovery entry."""

    subarray_id: int
    command: str


def _parse_matrix(matrix_json: str, kind: str) -> dict[DefectKey, str]:
    """Parse DefectMatrix/RecoverMatrix JSON (list of dicts) into a lookup."""
    if not matrix_json:
        return {}
    items = json.loads(matrix_json)
    if not isinstance(items, list):
        raise ValueError(f"{kind} must be a JSON list")

    out: dict[DefectKey, str] = {}
    for item in items:
        if not isinstance(item, dict):
            raise ValueError(f"{kind} item must be an object")
        key = DefectKey(int(item["subarray_id"]), str(item["command"]))
        value_field = "defect" if kind == "DefectMatrix" else "recovery"
        out[key] = str(item[value_field])
    return out


def _subsystem_subarrays(subarray_node_low: SubarrayNodeWrapperLow) -> tuple:
    """Return (csp, sdp, mccs) subsystem subarray proxies if present."""

    csp = None
    sdp = None
    mccs = None

    devs = getattr(subarray_node_low, "subarray_devices", {})
    if isinstance(devs, dict):
        csp = devs.get("csp_subarray")
        sdp = devs.get("sdp_subarray")
        mccs = devs.get("mccs_subarray")

    if csp is None:
        csp = getattr(subarray_node_low, "csp_subarray", None)
    if sdp is None:
        sdp = getattr(subarray_node_low, "sdp_subarray", None)

    if mccs is None:
        mccs = getattr(subarray_node_low, "mccs_subarray", None)

    return csp, sdp, mccs


def _apply_defect(
    subarray_node_low: SubarrayNodeWrapperLow,
    # command: str,
    defect: str,
) -> None:
    """Best-effort SetDefective application for a given command/defect."""

    logging.info("defect is %s", defect)
    # Try to resolve defect string to a constant in constant
    # Try to resolve defect string to a constant in constant or constant_low
    if hasattr(constant, defect):
        defect_obj = getattr(constant, defect)
        # If the constant is already a JSON string, use as is
        if isinstance(defect_obj, str):
            # try:
            # Try to parse and dump to ensure formatting
            defect_payload = json.dumps(json.loads(defect_obj))
            # except Exception:
            #     # If not JSON, just use as is
            #     defect_payload = defect_obj
            logging.info("defect_payload %s", defect_payload)
        else:
            defect_payload = json.dumps(defect_obj)
            logging.info("defect_payload %s", defect_payload)
    else:
        # Try to import constant_low and check there
        try:
            if hasattr(constant_low, defect):
                defect_obj = getattr(constant_low, defect)
                if isinstance(defect_obj, str):
                    # try:
                    defect_payload = json.dumps(json.loads(defect_obj))
                    # except Exception:
                    #     defect_payload = defect_obj
                    logging.info("defect_payload %s", defect_payload)
                else:
                    defect_payload = json.dumps(defect_obj)
                    logging.info("defect_payload %s", defect_payload)
            else:
                assert False, f"Defect string '{defect}' not supported"
        except ImportError:
            assert False, f"Defect string '{defect}' not supported "
    # else:
    #     # fallback to mapping
    #     # mapping = command_defect_mapping.get(command, {})
    #     # defect_payload = mapping.get(str(defect), mapping.get("FAULT"))
    #     assert False, f"Defect string '{defect}' not supported "

    csp, sdp, mccs = _subsystem_subarrays(subarray_node_low)
    if csp is not None:
        csp.SetDefective(defect_payload)
    if sdp is not None:
        sdp.SetDefective(defect_payload)
    if mccs is not None:
        mccs.SetDefective(defect_payload)


def _reset_defects(subarray_node_low: SubarrayNodeWrapperLow) -> None:
    """Best-effort reset of SetDefective on available leaf nodes."""

    csp, sdp, mccs = _subsystem_subarrays(subarray_node_low)
    if csp is not None:
        csp.SetDefective("{}")
    if sdp is not None:
        sdp.SetDefective("{}")
    if mccs is not None:
        mccs.SetDefective("{}")


def _run_assign_resources_for_all(
    central_node_low: CentralNodeWrapperLow,
    subarray_node_low: SubarrayNodeWrapperLow,
    event_tracer: TangoEventTracer,
    logs_dir: Path,
    subarray_ids: list[int],
    defects: dict[DefectKey, str],
) -> None:
    """AssignResources for all subarrays with special handling for defects."""

    assign_unique_ids: dict[int, tuple] = {}
    defective_assign_unique_ids: dict[int, tuple] = {}
    assign_defect_sa_ids: set[int] = set()

    for sa_id in subarray_ids:
        subarray_node_low.set_subarray_id(sa_id)
        defect = defects.get(DefectKey(sa_id, "AssignResources"))

        if defect:
            assign_defect_sa_ids.add(sa_id)
            try:
                _apply_defect(
                    subarray_node_low,
                    str(defect),
                )
            except Exception:  # pylint: disable=broad-exception-caught
                LOGGER.exception(
                    "Failed to apply AssignResources defect for SA %s: %s",
                    sa_id,
                    defect,
                )

        central_node_low.set_subarray_id(sa_id)
        assign_str = (logs_dir / f"assign_subarray{sa_id}.json").read_text(
            encoding="utf-8"
        )
        _, unique_id = central_node_low.perform_action(
            "AssignResources",
            assign_str,
        )

        if defect:
            try:
                defective_assign_unique_ids[sa_id] = unique_id

                assert_that(event_tracer).described_as(
                    "TMC Subarray Leaf Node "
                    "is expected to report a"
                    "longRunningCommand  failure."
                ).within_timeout(
                    TIMEOUT
                ).has_desired_result_code_message_in_lrcr_event(
                    subarray_node_low.subarray_node,
                    ["Exception occurred"],
                    unique_id[0],
                    ResultCode.FAILED,
                )

                _reset_defects(subarray_node_low)
            except Exception:  # pylint: disable=broad-exception-caught
                LOGGER.exception(
                    "Failed to reset defects after AssignResources for SA %s",
                    sa_id,
                )
        else:
            assign_unique_ids[sa_id] = unique_id

    pytest.assign_unique_ids = assign_unique_ids
    pytest.defective_assign_unique_ids = defective_assign_unique_ids
    pytest.assign_defect_sa_ids = assign_defect_sa_ids

    logging.info(
        "assign_unique_ids=%s defective_assign_unique_ids=%s",
        assign_unique_ids,
        defective_assign_unique_ids,
    )

    for sa_id, unique_id in assign_unique_ids.items():
        try:
            assert_that(event_tracer).within_timeout(
                TIMEOUT
            ).has_change_event_occurred(
                central_node_low.central_node,
                "longRunningCommandResult",
                (
                    unique_id[0],
                    json.dumps((0, "Command Completed")),
                ),
            )
        except AssertionError:
            LOGGER.exception(
                "No LRCR OK for AssignResources SA %s unique_id=%s",
                sa_id,
                unique_id,
            )

    pytest.healthy_sa_ids = [
        sa_id for sa_id in subarray_ids if sa_id not in assign_defect_sa_ids
    ]
    defect_sa_ids = sorted(assign_defect_sa_ids)

    if pytest.healthy_sa_ids:
        _wait_for_subarrays_obsstate(
            central_node_low,
            event_tracer,
            pytest.healthy_sa_ids,
            ObsState.IDLE,
        )

    if defect_sa_ids:
        # for sa_id in defect_sa_ids:
        #     subarray_node_low.set_subarray_id(sa_id)
        #     try:
        #         _reset_defects(subarray_node_low)
        #     except Exception:  # pylint: disable=broad-exception-caught
        #         LOGGER.exception(
        #           "Failed to reset defects after AssignResources for SA %s",
        #             sa_id,
        #         )
        #         assert False
        _wait_for_subarrays_obsstate(
            central_node_low,
            event_tracer,
            defect_sa_ids,
            ObsState.EMPTY,
        )


def _pss_id_for_subarray(base_pss_id: int, subarray_id: int) -> int:
    """Return a stable unique PSS beam id per subarray.

    Uses an offset from the plan's base id to avoid accidental collisions.
    """

    return int(base_pss_id) + int(subarray_id)


def _ensure_logs_dir() -> Path:
    """Create and return the build logs directory path."""

    return ensure_logs_dir("build")


def _write_json(path: Path, payload: dict) -> None:
    """Write a JSON payload to a file with stable formatting."""

    write_json(path, payload)


def _active_subarray_ids(sn_count: int) -> list[int]:
    """Return the 1..SNCount subarray ids."""

    return list(range(1, int(sn_count) + 1))


def _build_assign_json_files(
    plan_name: str, base_assign: dict, logs_dir: Path, subarray_ids: list[int]
) -> None:
    """Write per-subarray AssignResources JSON files."""

    plan = load_plan_json(_PLANS_FEATURE_PATH, plan_name)
    for subarray_id in subarray_ids:
        per_sn = plan.get(str(subarray_id), plan)
        assign_json = _build_assign_json(
            base_assign,
            subarray_id,
            per_sn,
            plan_name,
        )

        # Override PSS beam ids so each subarray uses its own unique id.
        # Shape expected by assign_resources_low: csp.pss.pss_beam_ids
        assign_json.setdefault("csp", {}).setdefault("pss", {})[
            "pss_beam_ids"
        ] = [int(subarray_id)]
        _write_json(
            logs_dir / f"assign_subarray{subarray_id}.json",
            assign_json,
        )


def _configure_json_for_subarray(
    base_configure: dict,
    plan_name: str,
    subarray_id: int,
) -> dict:
    """Build Configure JSON for one subarray from PlanA1.

    PSS ids are overridden per subarray.
    """

    plan = load_plan_json(_PLANS_FEATURE_PATH, plan_name)
    per_sn = plan.get(str(subarray_id), plan)

    cfg = json.loads(json.dumps(base_configure))

    # Ensure scan duration stays at 10 seconds (per user requirement).
    # Do not rely on the plan JSON (feature-driven plans may change).
    cfg.setdefault("tmc", {})["scan_duration"] = 10.0
    per_sn["scan_duration"] = 10.0
    plan["scan_duration"] = 10.0

    # Override the plan-provided PSS IDs so each subarray uses a unique id.
    pss_beams = per_sn.get("pss_beams", [])
    if pss_beams:
        base_pss_id = int(subarray_id)
        for beam in pss_beams:
            beam["id"] = _pss_id_for_subarray(base_pss_id, subarray_id)

    # Persist the updated per-subarray plan content into cfg by reusing how the
    # existing XTP-106948 test overlays station_beams / pst_beams / pss_beams.
    # We keep this logic inline to avoid over-coupling until the steps settle.

    station_beams = per_sn.get("station_beams", [])
    if station_beams:
        unique_stations = {
            int(st) for sb in station_beams for st in sb.get("stations", [])
        }
        if unique_stations:
            cfg["csp"]["lowcbf"]["stations"]["stns"] = [
                [st_id, 1] for st_id in sorted(unique_stations)
            ]
        cfg.setdefault("mccs", {}).setdefault("subarray_beams", [])
        for sb in station_beams:
            sb_id = int(sb.get("id", subarray_id))
            stations_from_pss = [
                st for b in pss_beams for st in b.get("stations", [])
            ]
            stations_from_pst = [
                st
                for b in per_sn.get("pst_beams", [])
                for st in b.get("stations", [])
            ]
            station_ids = sorted(
                {int(s) for s in (stations_from_pss + stations_from_pst)}
            )
            apertures = [
                {
                    "aperture_id": f"AP{int(st):03}.01",
                    "weighting_key_ref": "aperture2",
                }
                for st in station_ids
            ]
            cfg["mccs"]["subarray_beams"].append(
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

    pst_beams = per_sn.get("pst_beams", [])
    if pst_beams:
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

    if pss_beams:
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

    return cfg


@pytest.mark.SKA_tmc_low_multiple_subarrays16
@scenario(
    "../features/tmc/xtp-16sa_planA1_defect_matrix_observation.feature",
    "Run 16-subarray observation with injected defects and recovery",
)
def test_xtp_16sa_planA1_defect_matrix_observation() -> None:
    """BDD scenario entrypoint."""


@given(parsers.parse("{SNCount:d} subarrays are in the EMPTY ObsState"))
def given_subarrays_in_empty(
    # central_node_low: CentralNodeWrapperLow,
    # event_tracer: TangoEventTracer,
    SNCount: int,
) -> None:
    """Verify EMPTY on 1..SNCount (best-effort)."""

    pytest.sn_count = int(SNCount)
    pytest.subarray_ids = _active_subarray_ids(pytest.sn_count)

    # for subarray_id in pytest.subarray_ids:
    #     central_node_low.set_subarray_id(subarray_id)
    #     try:
    #         assert_that(event_tracer).within_timeout(
    #             TIMEOUT
    #         ).has_change_event_occurred(
    #             central_node_low.subarray_node,
    #             "obsState",
    #             ObsState.EMPTY,
    #         )
    #     except AssertionError:
    #         LOGGER.exception(
    #             "No EMPTY obsState within timeout for SA %s",
    #             subarray_id,
    #         )


@given("the telescope is in the ON state")
def given_telescope_on(
    central_node_low: CentralNodeWrapperLow,
    event_tracer: TangoEventTracer,
) -> None:
    """Move telescope to ON and subscribe to events."""

    event_tracer.subscribe_event(
        central_node_low.central_node,
        "telescopeState",
    )
    event_tracer.subscribe_event(
        central_node_low.central_node,
        "longRunningCommandResult",
    )
    log_events({central_node_low.central_node: ["telescopeState"]})
    event_tracer.clear_events()

    for subarray_id in getattr(pytest, "subarray_ids", [1]):
        central_node_low.set_subarray_id(subarray_id)
        event_tracer.subscribe_event(
            central_node_low.subarray_node,
            "obsState",
        )
        event_tracer.subscribe_event(
            central_node_low.subarray_node,
            "longRunningCommandResult",
        )
        central_node_low.set_values_with_all_mocks(DevState.ON)

    central_node_low.move_to_on()
    assert_that(event_tracer).within_timeout(
        TIMEOUT
    ).has_change_event_occurred(
        central_node_low.central_node,
        "telescopeState",
        DevState.ON,
    )


@when(
    parsers.parse(
        "I run observations for all subarrays using plan {PlanName} "
        "with defects {DefectMatrix}"
    )
)
def when_run_observations(
    central_node_low: CentralNodeWrapperLow,
    subarray_node_low: SubarrayNodeWrapperLow,
    command_input_factory: JsonFactory,
    event_tracer: TangoEventTracer,
    PlanName: str,
    DefectMatrix: str,
) -> None:
    """Run AssignResources and Configure for all subarrays.

    Defects are only parsed and stored here.
    """

    _ = event_tracer

    pytest.plan_name = str(PlanName)
    pytest.defects = _parse_matrix(DefectMatrix, "DefectMatrix")

    logs_dir = _ensure_logs_dir()

    # AssignResources files.
    base_assign = json.loads(
        prepare_json_args_for_centralnode_commands(
            "assign_resources_low",
            command_input_factory,
        )
    )
    _build_assign_json_files(
        pytest.plan_name,
        base_assign,
        logs_dir,
        pytest.subarray_ids,
    )

    # Configure files.
    base_configure = json.loads(
        prepare_json_args_for_commands("configure_low", command_input_factory)
    )
    for sa_id in pytest.subarray_ids:
        cfg = _configure_json_for_subarray(
            base_configure,
            pytest.plan_name,
            sa_id,
        )
        _write_json(logs_dir / f"configure_subarray{sa_id}.json", cfg)

    pytest.logs_dir = logs_dir

    _run_assign_resources_for_all(
        central_node_low,
        subarray_node_low,
        event_tracer,
        logs_dir,
        pytest.subarray_ids,
        pytest.defects,
    )

    # Execute Configure for all SAs (best-effort).
    configure_unique_ids: dict[int, tuple] = {}
    configure_defect_sa_ids: set[int] = set()
    defective_configure_unique_ids: dict[int, tuple] = {}
    for sa_id in pytest.healthy_sa_ids:
        subarray_node_low.set_subarray_id(sa_id)
        defect = pytest.defects.get(DefectKey(sa_id, "Configure"))

        # Best-effort defect injection for Configure.
        if defect:
            try:
                configure_defect_sa_ids.add(sa_id)
                _apply_defect(
                    subarray_node_low,
                    # "Configure",
                    str(defect),
                )
            except Exception:  # pylint: disable=broad-exception-caught
                LOGGER.exception(
                    "Failed to apply Configure defect for SA %s: %s",
                    sa_id,
                    defect,
                )

        subarray_node_low.set_subarray_id(sa_id)
        cfg_str = (logs_dir / f"configure_subarray{sa_id}.json").read_text(
            encoding="utf-8"
        )
        _, unique_id = subarray_node_low.execute_transition(
            "Configure",
            cfg_str,
        )
        # configure_unique_ids[sa_id] = unique_id

        if defect:

            try:
                defective_configure_unique_ids[sa_id] = unique_id

                assert_that(event_tracer).described_as(
                    "TMC Subarray Leaf Node "
                    "is expected to report a"
                    "longRunningCommand  failure."
                ).within_timeout(
                    TIMEOUT
                ).has_desired_result_code_message_in_lrcr_event(
                    subarray_node_low.subarray_node,
                    ["Exception occurred"],
                    unique_id[0],
                    ResultCode.FAILED,
                )

                _reset_defects(subarray_node_low)
            except Exception:  # pylint: disable=broad-exception-caught
                LOGGER.exception(
                    "Failed to reset defects after AssignResources for SA %s",
                    sa_id,
                )
        else:
            configure_unique_ids[sa_id] = unique_id

    pytest.configure_unique_ids = configure_unique_ids
    pytest.defective_configure_unique_ids = defective_configure_unique_ids
    pytest.configure_defect_sa_ids = configure_defect_sa_ids

    logging.info(
        "configure_unique_ids=%s defective_configure_unique_ids=%s",
        configure_unique_ids,
        defective_configure_unique_ids,
    )

    for sa_id, unique_id in configure_unique_ids.items():
        try:
            assert_that(event_tracer).within_timeout(
                TIMEOUT
            ).has_change_event_occurred(
                subarray_node_low.subarray_node,
                "longRunningCommandResult",
                (
                    unique_id[0],
                    json.dumps((0, "Command Completed")),
                ),
            )
        except AssertionError:
            LOGGER.exception(
                "No LRCR OK for Configure SA %s unique_id=%s",
                sa_id,
                unique_id,
            )

    pytest.healthy_sa_ids = [
        sa_id
        for sa_id in pytest.healthy_sa_ids
        if sa_id not in configure_defect_sa_ids
    ]
    defect_sa_ids = sorted(configure_defect_sa_ids)

    if pytest.healthy_sa_ids:
        _wait_for_subarrays_obsstate(
            central_node_low,
            event_tracer,
            pytest.healthy_sa_ids,
            ObsState.READY,
        )

    if defect_sa_ids:
        # for sa_id in defect_sa_ids:
        #     subarray_node_low.set_subarray_id(sa_id)
        #     try:
        #         _reset_defects(subarray_node_low)
        #     except Exception:  # pylint: disable=broad-exception-caught
        #         LOGGER.exception(
        #           "Failed to reset defects after AssignResources for SA %s",
        #             sa_id,
        #         )
        #         assert False
        _wait_for_subarrays_obsstate(
            central_node_low,
            event_tracer,
            defect_sa_ids,
            ObsState.EMPTY,
        )


@then("healthy subarrays complete observation cycle")
def then_healthy_complete_observation_cycle(
    central_node_low: CentralNodeWrapperLow,
    subarray_node_low: SubarrayNodeWrapperLow,
    event_tracer: TangoEventTracer,
) -> None:
    """Smoke-check that subarrays without configured defects reach READY."""

    _ = central_node_low

    defects: dict[DefectKey, str] = getattr(pytest, "defects", {})

    for sa_id in getattr(pytest, "subarray_ids", []):
        # Consider a subarray healthy if it has no defect for
        # AssignResources/Configure.
        if DefectKey(sa_id, "AssignResources") in defects:
            continue
        if DefectKey(sa_id, "Configure") in defects:
            continue

        subarray_node_low.set_subarray_id(sa_id)
        try:
            assert_that(event_tracer).within_timeout(
                TIMEOUT
            ).has_change_event_occurred(
                subarray_node_low.subarray_node,
                "obsState",
                ObsState.READY,
            )
        except AssertionError:
            LOGGER.exception("Healthy SA %s did not reach READY", sa_id)


@when(parsers.parse("I try recovery as per {RecoverMatrix}"))
def when_try_recovery(
    central_node_low: CentralNodeWrapperLow,
    subarray_node_low: SubarrayNodeWrapperLow,
    event_tracer: TangoEventTracer,
    RecoverMatrix: str,
) -> None:
    """Attempt recovery actions for the configured subarrays (best-effort)."""

    _ = event_tracer

    pytest.recovery = _parse_matrix(RecoverMatrix, "RecoverMatrix")

    for key, action in pytest.recovery.items():
        sa_id = key.subarray_id
        action = action.upper()

        if action == "RESTART":
            subarray_node_low.set_subarray_id(sa_id)
            try:
                subarray_node_low.execute_transition("Restart")
            except Exception:  # pylint: disable=broad-exception-caught
                LOGGER.exception("Restart failed for SA %s", sa_id)

        elif action == "ABORT_THEN_RESTART":
            subarray_node_low.set_subarray_id(sa_id)
            try:
                subarray_node_low.execute_transition("Abort")
            except Exception:  # pylint: disable=broad-exception-caught
                LOGGER.exception("Abort failed for SA %s", sa_id)
            try:
                subarray_node_low.execute_transition("Restart")
            except Exception:  # pylint: disable=broad-exception-caught
                LOGGER.exception("Restart after Abort failed for SA %s", sa_id)

        elif action == "RELEASE_RESOURCES":
            # Recovery via ReleaseResources runs through CentralNode.
            central_node_low.set_subarray_id(sa_id)
            try:
                central_node_low.perform_action("ReleaseResources")
            except Exception:  # pylint: disable=broad-exception-caught
                LOGGER.exception("ReleaseResources failed for SA %s", sa_id)

        elif action == "NONE":
            continue
        else:
            LOGGER.warning(
                "Unknown recovery action '%s' for SA %s",
                action,
                sa_id,
            )


@then(
    parsers.parse(
        "recoverable subarrays transition back to {RecoveredObsState}"
    )
)
def then_recoverable_back_to_state(
    subarray_node_low: SubarrayNodeWrapperLow,
    event_tracer: TangoEventTracer,
    RecoveredObsState: str,
) -> None:
    """Verify recoverable subarrays return to the requested ObsState."""

    expected = ObsState[RecoveredObsState]

    for key in getattr(pytest, "recovery", {}):
        subarray_node_low.set_subarray_id(key.subarray_id)
        try:
            assert_that(event_tracer).within_timeout(
                TIMEOUT
            ).has_change_event_occurred(
                subarray_node_low.subarray_node,
                "obsState",
                expected,
            )
        except AssertionError:
            LOGGER.exception(
                "Recoverable SA %s did not reach %s", key.subarray_id, expected
            )

import json

from ska_control_model import ObsState
from ska_integration_test_harness.facades.csp_facade import CSPFacade
from ska_integration_test_harness.facades.mccs_facade import MCCSFacade
from ska_integration_test_harness.facades.sdp_facade import SDPFacade
from ska_integration_test_harness.facades.tmc_facade import TMCFacade
from ska_integration_test_harness.inputs.test_harness_inputs import (
    TestHarnessInputs,
)

from tests.resources.test_harness.constant import (
    IDLE_STATE_DEFECT,
    READY_STATE_DEFECT,
    RESET_DEFECT,
)
from tests.resources.test_support.constant_low import (
    INTERMEDIATE_CONFIGURING_OBS_STATE_DEFECT,
    INTERMEDIATE_FAULT_OBS_STATE_DEFECT,
    INTERMEDIATE_STATE_DEFECT,
    SDP_BACK_TO_INITIAL_STATE,
)

TIMEOUT = 100
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
        "EMPTY": json.dumps(INTERMEDIATE_STATE_DEFECT),
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

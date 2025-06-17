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
    COMMAND_FAILED_WITH_EXCEPTION_OBSSTATE_EMPTY,
    INTERMEDIATE_SCANNING_STATE_DEFECT,
    RESET_DEFECT,
)
from tests.resources.test_support.constant_low import (
    INTERMEDIATE_CONFIGURING_OBS_STATE_DEFECT,
    INTERMEDIATE_FAULT_OBS_STATE_DEFECT,
    INTERMEDIATE_STATE_DEFECT,
)

command_defect_mapping = {
    "AssignResources": {
        "RESOURCING": json.dumps(INTERMEDIATE_STATE_DEFECT),
        "FAULT": json.dumps(INTERMEDIATE_FAULT_OBS_STATE_DEFECT),
        "EMPTY": COMMAND_FAILED_WITH_EXCEPTION_OBSSTATE_EMPTY,
    },
    "Configure": {
        "CONFIGURING": json.dumps(INTERMEDIATE_CONFIGURING_OBS_STATE_DEFECT),
        "FAULT": INTERMEDIATE_FAULT_OBS_STATE_DEFECT,
    },
    "Scan": {
        "SCANNING": INTERMEDIATE_SCANNING_STATE_DEFECT,
        "FAULT": INTERMEDIATE_FAULT_OBS_STATE_DEFECT,
    },
}


def set_subsystem_defects(
    csp: CSPFacade,
    sdp: SDPFacade,
    mccs: MCCSFacade,
    CSP_obsState: str,
    SDP_obsState: str,
    MCCS_obsState: str,
    command: str,
):
    csp.csp_subarray.SetDefective(
        command_defect_mapping.get(command).get(CSP_obsState, RESET_DEFECT)
    )
    sdp.sdp_subarray.SetDefective(
        command_defect_mapping.get(command).get(SDP_obsState, RESET_DEFECT)
    )
    mccs.mccs_subarray.SetDefective(
        command_defect_mapping.get(command).get(MCCS_obsState, RESET_DEFECT)
    )


def invoke_command_with_defect(
    tmc: TMCFacade,
    default_commands_inputs: TestHarnessInputs,
    csp: CSPFacade,
    sdp: SDPFacade,
    mccs: MCCSFacade,
    CSP_obsState: str,
    SDP_obsState: str,
    MCCS_obsState: str,
    command: str,
):
    match command:
        case "AssignResources":
            set_subsystem_defects(
                csp,
                sdp,
                mccs,
                CSP_obsState,
                SDP_obsState,
                MCCS_obsState,
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
                CSP_obsState,
                SDP_obsState,
                MCCS_obsState,
                command,
            )
            tmc.configure(
                default_commands_inputs.configure_input, wait_termination=False
            )
        case "SCAN":
            tmc.force_change_of_obs_state(
                ObsState.READY, default_commands_inputs, wait_termination=True
            )
            set_subsystem_defects(
                csp,
                sdp,
                mccs,
                CSP_obsState,
                SDP_obsState,
                MCCS_obsState,
                command,
            )
            tmc.scan(
                default_commands_inputs.scan_input, wait_termination=False
            )


def reset_defects(csp: CSPFacade, sdp: SDPFacade, mccs: MCCSFacade):
    csp.csp_subarray.SetDefective(RESET_DEFECT)
    sdp.sdp_subarray.SetDefective(RESET_DEFECT)
    mccs.mccs_subarray.SetDefective(RESET_DEFECT)

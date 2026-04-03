"""Define Constants
"""
import json

from ska_control_model import ObsState, ResultCode

from tests.resources.test_harness.utils.enums import (
    FaultType,
    SimulatorDeviceType,
)

COMMAND_COMPLETED = json.dumps([ResultCode.OK, "Command Completed"])

TIMEOUT = 80
COMMAND_FAILED_WITH_EXCEPTION_OBSSTATE_IDLE = {
    "enabled": True,
    "fault_type": FaultType.FAILED_RESULT,
    "error_message": "Default exception.",
    "result": ResultCode.FAILED,
    "target_obsstates": [ObsState.CONFIGURING, ObsState.IDLE],
}

INTERMEDIATE_CONFIGURING_OBS_STATE_DEFECT = {
    "enabled": True,
    "fault_type": FaultType.STUCK_IN_INTERMEDIATE_STATE,
    "error_message": "Device stuck in intermediate state",
    "result": ResultCode.FAILED,
    "intermediate_state": ObsState.CONFIGURING,
}

OBS_STATE_CONFIGURING_STUCK_DEFECT = {
    "enabled": True,
    "fault_type": FaultType.STUCK_IN_OBSTATE,
    "error_message": "Device stuck in configuring state",
    "result": ResultCode.FAILED,
    "intermediate_state": ObsState.CONFIGURING,
}

INTERMEDIATE_STATE_DEFECT = {
    "enabled": True,
    "fault_type": FaultType.STUCK_IN_INTERMEDIATE_STATE,
    "error_message": "Device stuck in intermediate state",
    "result": ResultCode.FAILED,
    "intermediate_state": ObsState.RESOURCING,
}

INTERMEDIATE_CONFIGURING_STATE_DEFECT = json.dumps(
    {
        "enabled": True,
        "fault_type": FaultType.STUCK_IN_INTERMEDIATE_STATE,
        "error_message": "Device stuck in intermediate state",
        "result": ResultCode.FAILED,
        "intermediate_state": ObsState.CONFIGURING,
    }
)

INTERMEDIATE_SCANNING_STATE_DEFECT = json.dumps(
    {
        "enabled": True,
        "fault_type": FaultType.STUCK_IN_INTERMEDIATE_STATE,
        "error_message": "Device stuck in intermediate state",
        "result": ResultCode.FAILED,
        "intermediate_state": ObsState.SCANNING,
    }
)

READY_STATE_DEFECT = json.dumps(
    {
        "enabled": True,
        "fault_type": FaultType.STUCK_IN_INTERMEDIATE_STATE,
        "error_message": "Device stuck in intermediate state",
        "result": ResultCode.FAILED,
        "intermediate_state": ObsState.READY,
    }
)

IDLE_STATE_DEFECT = json.dumps(
    {
        "enabled": True,
        "fault_type": FaultType.STUCK_IN_INTERMEDIATE_STATE,
        "error_message": "Device stuck in intermediate state",
        "result": ResultCode.FAILED,
        "intermediate_state": ObsState.IDLE,
    }
)

OBS_STATE_RESOURCING_STUCK_DEFECT = {
    "enabled": True,
    "fault_type": FaultType.STUCK_IN_OBSTATE,
    "error_message": "Device stuck in Resourcing state",
    "result": ResultCode.FAILED,
    "intermediate_state": ObsState.RESOURCING,
}

INTERMEDIATE_OBSSTATE_EMPTY_DEFECT = {
    "enabled": True,
    "fault_type": FaultType.STUCK_IN_INTERMEDIATE_STATE,
    "error_message": "Device stuck in intermediate state",
    "result": ResultCode.FAILED,
    "intermediate_state": ObsState.EMPTY,
}

COMMAND_FAILED_WITH_EXCEPTION_OBSSTATE_EMPTY = {
    "enabled": True,
    "fault_type": FaultType.FAILED_RESULT,
    "error_message": "Default exception.",
    "result": ResultCode.FAILED,
    "target_obsstates": [ObsState.RESOURCING, ObsState.EMPTY],
}


FAILED_RESULT_DEFECT = json.dumps(
    {
        "enabled": True,
        "fault_type": FaultType.FAILED_RESULT,
        "error_message": "Device is defective, cannot process command",
        "result": ResultCode.FAILED,
    }
)

ERROR_PROPAGATION_DEFECT = json.dumps(
    {
        "enabled": True,
        "fault_type": FaultType.LONG_RUNNING_EXCEPTION,
        "error_message": "Exception occurred, command failed.",
        "result": ResultCode.FAILED,
    }
)
RESET_DEFECT = json.dumps(
    {
        "enabled": False,
        "fault_type": FaultType.FAILED_RESULT,
        "error_message": "Default exception.",
        "result": ResultCode.FAILED,
    }
)


FAILED_DEFECT = json.dumps(
    {
        "enabled": True,
        "fault_type": FaultType.FAILED_RESULT,
        "error_message": "Default exception.",
        "result": ResultCode.FAILED,
    }
)

COMMAND_FAILED_WITH_EXCEPTION_OBSSTATE_IDLE = {
    "enabled": True,
    "fault_type": FaultType.FAILED_RESULT,
    "error_message": "Default exception.",
    "result": ResultCode.FAILED,
    "target_obsstates": [ObsState.RESOURCING, ObsState.IDLE],
}

COMMAND_NOT_ALLOWED_DEFECT = json.dumps(
    {
        "enabled": True,
        "fault_type": FaultType.COMMAND_NOT_ALLOWED,
        "error_message": "Command is not allowed",
        "result": ResultCode.FAILED,
    }
)

TIMEOUT_DEFECT = json.dumps(
    {
        "enabled": True,
        "fault_type": FaultType.STUCK_IN_INTERMEDIATE_STATE,
        "error_message": "Device stuck in intermediate state",
        "result": ResultCode.FAILED,
        "intermediate_state": ObsState.RESOURCING,
    }
)

low_centralnode = "low-tmc/central-node/0"
tmc_low_subarraynode1 = "low-tmc/subarray/01"
tmc_low_subarraynode2 = "low-tmc/subarray/02"
tmc_low_subarraynode3 = "low-tmc/subarray/03"
tmc_low_subarraynode4 = "low-tmc/subarray/04"
tmc_low_subarraynode5 = "low-tmc/subarray/05"
tmc_low_subarraynode6 = "low-tmc/subarray/06"
tmc_low_subarraynode7 = "low-tmc/subarray/07"
tmc_low_subarraynode8 = "low-tmc/subarray/08"
tmc_low_subarraynode9 = "low-tmc/subarray/09"
tmc_low_subarraynode10 = "low-tmc/subarray/10"
tmc_low_subarraynode11 = "low-tmc/subarray/11"
tmc_low_subarraynode12 = "low-tmc/subarray/12"
tmc_low_subarraynode13 = "low-tmc/subarray/13"
tmc_low_subarraynode14 = "low-tmc/subarray/14"
tmc_low_subarraynode15 = "low-tmc/subarray/15"
tmc_low_subarraynode16 = "low-tmc/subarray/16"
low_csp_master_leaf_node = "low-tmc/leaf-node-csp/0"
low_sdp_master_leaf_node = "low-tmc/leaf-node-sdp/0"
mccs_master_leaf_node = "low-tmc/leaf-node-mccs/0"
low_csp_subarray_leaf_node = "low-tmc/subarray-leaf-node-csp/01"
low_csp_subarray_leaf_node2 = "low-tmc/subarray-leaf-node-csp/02"
low_csp_subarray_leaf_node3 = "low-tmc/subarray-leaf-node-csp/03"
low_csp_subarray_leaf_node4 = "low-tmc/subarray-leaf-node-csp/04"
low_csp_subarray_leaf_node5 = "low-tmc/subarray-leaf-node-csp/05"
low_csp_subarray_leaf_node6 = "low-tmc/subarray-leaf-node-csp/06"
low_csp_subarray_leaf_node7 = "low-tmc/subarray-leaf-node-csp/07"
low_csp_subarray_leaf_node8 = "low-tmc/subarray-leaf-node-csp/08"
low_csp_subarray_leaf_node9 = "low-tmc/subarray-leaf-node-csp/09"
low_csp_subarray_leaf_node10 = "low-tmc/subarray-leaf-node-csp/10"
low_csp_subarray_leaf_node11 = "low-tmc/subarray-leaf-node-csp/11"
low_csp_subarray_leaf_node12 = "low-tmc/subarray-leaf-node-csp/12"
low_csp_subarray_leaf_node13 = "low-tmc/subarray-leaf-node-csp/13"
low_csp_subarray_leaf_node14 = "low-tmc/subarray-leaf-node-csp/14"
low_csp_subarray_leaf_node15 = "low-tmc/subarray-leaf-node-csp/15"
low_csp_subarray_leaf_node16 = "low-tmc/subarray-leaf-node-csp/16"
low_sdp_subarray_leaf_node = "low-tmc/subarray-leaf-node-sdp/01"
low_sdp_subarray_leaf_node2 = "low-tmc/subarray-leaf-node-sdp/02"
low_sdp_subarray_leaf_node3 = "low-tmc/subarray-leaf-node-sdp/03"
low_sdp_subarray_leaf_node4 = "low-tmc/subarray-leaf-node-sdp/04"
low_sdp_subarray_leaf_node = "low-tmc/subarray-leaf-node-sdp/01"
low_sdp_subarray_leaf_node2 = "low-tmc/subarray-leaf-node-sdp/02"
low_sdp_subarray_leaf_node3 = "low-tmc/subarray-leaf-node-sdp/03"
low_sdp_subarray_leaf_node4 = "low-tmc/subarray-leaf-node-sdp/04"
low_sdp_subarray_leaf_node5 = "low-tmc/subarray-leaf-node-sdp/05"
low_sdp_subarray_leaf_node6 = "low-tmc/subarray-leaf-node-sdp/06"
low_sdp_subarray_leaf_node7 = "low-tmc/subarray-leaf-node-sdp/07"
low_sdp_subarray_leaf_node8 = "low-tmc/subarray-leaf-node-sdp/08"
low_sdp_subarray_leaf_node9 = "low-tmc/subarray-leaf-node-sdp/09"
low_sdp_subarray_leaf_node10 = "low-tmc/subarray-leaf-node-sdp/10"
low_sdp_subarray_leaf_node11 = "low-tmc/subarray-leaf-node-sdp/11"
low_sdp_subarray_leaf_node12 = "low-tmc/subarray-leaf-node-sdp/12"
low_sdp_subarray_leaf_node13 = "low-tmc/subarray-leaf-node-sdp/13"
low_sdp_subarray_leaf_node14 = "low-tmc/subarray-leaf-node-sdp/14"
low_sdp_subarray_leaf_node15 = "low-tmc/subarray-leaf-node-sdp/15"
low_sdp_subarray_leaf_node16 = "low-tmc/subarray-leaf-node-sdp/16"
mccs_subarray_leaf_node = "low-tmc/subarray-leaf-node-mccs/01"
mccs_subarray_leaf_node2 = "low-tmc/subarray-leaf-node-mccs/02"
mccs_subarray_leaf_node3 = "low-tmc/subarray-leaf-node-mccs/03"
mccs_subarray_leaf_node4 = "low-tmc/subarray-leaf-node-mccs/04"
mccs_subarray_leaf_node5 = "low-tmc/subarray-leaf-node-mccs/05"
mccs_subarray_leaf_node6 = "low-tmc/subarray-leaf-node-mccs/06"
mccs_subarray_leaf_node7 = "low-tmc/subarray-leaf-node-mccs/07"
mccs_subarray_leaf_node8 = "low-tmc/subarray-leaf-node-mccs/08"
mccs_subarray_leaf_node9 = "low-tmc/subarray-leaf-node-mccs/09"
mccs_subarray_leaf_node10 = "low-tmc/subarray-leaf-node-mccs/10"
mccs_subarray_leaf_node11 = "low-tmc/subarray-leaf-node-mccs/11"
mccs_subarray_leaf_node12 = "low-tmc/subarray-leaf-node-mccs/12"
mccs_subarray_leaf_node13 = "low-tmc/subarray-leaf-node-mccs/13"
mccs_subarray_leaf_node14 = "low-tmc/subarray-leaf-node-mccs/14"
mccs_subarray_leaf_node15 = "low-tmc/subarray-leaf-node-mccs/15"
mccs_subarray_leaf_node16 = "low-tmc/subarray-leaf-node-mccs/16"
low_sdp_subarray1 = "low-sdp/subarray/01"
low_sdp_subarray2 = "low-sdp/subarray/02"
low_sdp_subarray3 = "low-sdp/subarray/03"
low_sdp_subarray4 = "low-sdp/subarray/04"
low_sdp_subarray5 = "low-sdp/subarray/05"
low_sdp_subarray6 = "low-sdp/subarray/06"
low_sdp_subarray7 = "low-sdp/subarray/07"
low_sdp_subarray8 = "low-sdp/subarray/08"
low_sdp_subarray9 = "low-sdp/subarray/09"
low_sdp_subarray10 = "low-sdp/subarray/10"
low_sdp_subarray11 = "low-sdp/subarray/11"
low_sdp_subarray12 = "low-sdp/subarray/12"
low_sdp_subarray13 = "low-sdp/subarray/13"
low_sdp_subarray14 = "low-sdp/subarray/14"
low_sdp_subarray15 = "low-sdp/subarray/15"
low_sdp_subarray16 = "low-sdp/subarray/16"

low_csp_subarray1 = "low-csp/subarray/01"
low_csp_subarray2 = "low-csp/subarray/02"
low_csp_subarray3 = "low-csp/subarray/03"
low_csp_subarray4 = "low-csp/subarray/04"
low_csp_subarray5 = "low-csp/subarray/05"
low_csp_subarray6 = "low-csp/subarray/06"
low_csp_subarray7 = "low-csp/subarray/07"
low_csp_subarray8 = "low-csp/subarray/08"
low_csp_subarray9 = "low-csp/subarray/09"
low_csp_subarray10 = "low-csp/subarray/10"
low_csp_subarray11 = "low-csp/subarray/11"
low_csp_subarray12 = "low-csp/subarray/12"
low_csp_subarray13 = "low-csp/subarray/13"
low_csp_subarray14 = "low-csp/subarray/14"
low_csp_subarray15 = "low-csp/subarray/15"
low_csp_subarray16 = "low-csp/subarray/16"

low_sdp_master = "low-sdp/control/0"
low_csp_master = "low-csp/control/0"
mccs_controller = "low-mccs/control/control"

mccs_subarray1 = "low-mccs/subarray/01"
mccs_subarray2 = "low-mccs/subarray/02"
mccs_subarray3 = "low-mccs/subarray/03"
mccs_subarray4 = "low-mccs/subarray/04"
mccs_subarray5 = "low-mccs/subarray/05"
mccs_subarray6 = "low-mccs/subarray/06"
mccs_subarray7 = "low-mccs/subarray/07"
mccs_subarray8 = "low-mccs/subarray/08"
mccs_subarray9 = "low-mccs/subarray/09"
mccs_subarray10 = "low-mccs/subarray/10"
mccs_subarray11 = "low-mccs/subarray/11"
mccs_subarray12 = "low-mccs/subarray/12"
mccs_subarray13 = "low-mccs/subarray/13"
mccs_subarray14 = "low-mccs/subarray/14"
mccs_subarray15 = "low-mccs/subarray/15"
mccs_subarray16 = "low-mccs/subarray/16"


processor1 = "low-cbf/processor/0.0.0"
mccs_pasdbus_prefix = "low-mccs/pasdbus/*"
mccs_prefix = "low-mccs/*"
mccs_subarraybeam = "low-mccs/subarraybeam/01"
pst = "low-pst/beam/01"

device_dict_low = {
    "csp_master": low_csp_master,
    "tmc_subarraynode": tmc_low_subarraynode1,
    "sdp_master": low_sdp_master,
    "mccs_master": mccs_controller,
    "sdp_subarray": low_sdp_subarray1,
    "csp_subarray": low_csp_subarray1,
    "sdp_subarray_leaf_node": low_sdp_subarray_leaf_node,
    "csp_subarray_leaf_node": low_csp_subarray_leaf_node,
    "mccs_master_leaf_node": mccs_master_leaf_node,
    "mccs_subarray_leaf_node": mccs_subarray_leaf_node,
    "mccs_subarray": mccs_subarray1,
    "central_node": low_centralnode,
}

SIMULATOR_DEVICE_FQDN_DICT = {
    SimulatorDeviceType.LOW_SDP_DEVICE: [low_sdp_subarray1],
    SimulatorDeviceType.LOW_CSP_DEVICE: [low_csp_subarray1],
    SimulatorDeviceType.LOW_SDP_DEVICE2: [low_sdp_subarray2],
    SimulatorDeviceType.LOW_CSP_DEVICE2: [low_csp_subarray2],
    SimulatorDeviceType.LOW_SDP_MASTER_DEVICE: [low_sdp_master],
    SimulatorDeviceType.LOW_CSP_MASTER_DEVICE: [low_csp_master],
    SimulatorDeviceType.MCCS_MASTER_DEVICE: [mccs_controller],
    SimulatorDeviceType.MCCS_SUBARRAY_DEVICE: [mccs_subarray1],
    SimulatorDeviceType.MCCS_SUBARRAY_DEVICE2: [mccs_subarray2],
}

LOW_DELAYMODEL_VERSION = "https://schema.skao.int/ska-low-csp-delaymodel/1.1"

INITIAL_LOW_DELAY_JSON = {
    "interface": "https://schema.skao.int/ska-low-csp-delaymodel/1.1",
    "start_validity_sec": 0.1,
    "cadence_sec": 0.1,
    "validity_period_sec": 0.1,
    "config_id": "",
    "subarray": 1,
    "station_beam_delays": [
        {
            "station_id": 1,
            "substation_id": 1,
            "xypol_coeffs_ns": [],
            "ypol_offset_ns": 0.0,
        },
        {
            "station_id": 1,
            "substation_id": 1,
            "xypol_coeffs_ns": [],
            "ypol_offset_ns": 0.0,
        },
    ],
}

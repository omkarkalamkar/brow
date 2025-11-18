"""This module contain constants for low devices"""
import json

from ska_control_model import ObsState, ResultCode

from tests.resources.test_support.common_utils.result_code import FaultType

centralnode = "low-tmc/central-node/0"
tmc_subarraynode1 = "low-tmc/subarray/01"
tmc_subarraynode2 = "low-tmc/subarray/02"
tmc_subarraynode3 = "low-tmc/subarray/03"
tmc_csp_master_leaf_node = "low-tmc/leaf-node-csp/0"
tmc_sdp_master_leaf_node = "low-tmc/leaf-node-sdp/0"
tmc_csp_subarray_leaf_node = "low-tmc/subarray-leaf-node-csp/01"
tmc_sdp_subarray_leaf_node = "low-tmc/subarray-leaf-node-sdp/01"
sdp_subarray1 = "low-sdp/subarray/01"
sdp_subarray2 = "low-sdp/subarray/02"
sdp_subarray3 = "low-sdp/subarray/03"
csp_subarray1 = "low-csp/subarray/01"
csp_subarray2 = "low-csp/subarray/02"
csp_subarray3 = "low-csp/subarray/03"
sdp_master = "low-sdp/control/0"
csp_master = "low-csp/control/0"
TIMEOUT = 80
DEVICE_STATE_STANDBY_INFO = {
    sdp_subarray1: ["DISABLE", "OFF"],
    sdp_master: ["DISABLE", "STANDBY", "OFF"],
    csp_master: ["DISABLE", "STANDBY", "OFF"],
    csp_subarray1: ["DISABLE", "OFF"],
}

DEVICE_STATE_ON_INFO = {
    sdp_subarray1: ["ON"],
    sdp_master: ["ON"],
    csp_master: ["ON"],
    csp_subarray1: ["ON"],
    centralnode: ["ON"],
}
EVENT_DEFECT = json.dumps(
    {"enabled": True, "fault_type": FaultType.EVENT_NOT_RECEIVED}
)
RECEIVE_ADDRESSES = json.dumps(
    {
        "science_A": {
            "vis0": {
                "function": "visibilities",
                "host": [[0, "192.168.0.1"], [2000, "192.168.0.2"]],
                "port": [[0, 9000], [20, 9001]],
            }
        },
        "target:a": {
            "vis0": {
                "function": "visibilities",
                "host": [[0, "192.168.0.1"], [2000, "192.168.0.2"]],
                "port": [[0, 9000], [20, 9001]],
            }
        },
        "calibration:b": {
            "vis0": {
                "function": "visibilities",
                "host": [[0, "192.168.0.1"], [2000, "192.168.0.2"]],
                "port": [[0, 9000], [20, 9001]],
            }
        },
    }
)
DEVICE_STATE_OFF_INFO = {
    sdp_subarray1: ["OFF"],
    sdp_master: ["OFF"],
    csp_master: ["OFF"],
    csp_subarray1: ["OFF"],
}

DEVICE_OBS_STATE_IDLE_INFO = {
    sdp_subarray1: ["IDLE"],
    tmc_subarraynode1: ["IDLE"],
    csp_subarray1: ["IDLE"],
}

DEVICE_OBS_STATE_EMPTY_INFO = {
    sdp_subarray1: ["EMPTY"],
    tmc_subarraynode1: ["EMPTY"],
    csp_subarray1: ["EMPTY"],
}

DEVICE_OBS_STATE_READY_INFO = {
    sdp_subarray1: ["READY"],
    tmc_subarraynode1: ["READY"],
    csp_subarray1: ["READY"],
}

DEVICE_OBS_STATE_SCANNING_INFO = {
    sdp_subarray1: ["SCANNING"],
    tmc_subarraynode1: ["SCANNING"],
    csp_subarray1: ["SCANNING"],
}

DEVICE_OBS_STATE_ABORT_INFO = {
    sdp_subarray1: ["ABORTED"],
    tmc_subarraynode1: ["ABORTED"],
    csp_subarray1: ["ABORTED"],
}

DEVICE_HEALTH_STATE_OK_INFO = {
    tmc_csp_subarray_leaf_node: "OK",
    centralnode: "OK",
    tmc_csp_master_leaf_node: "OK",
    tmc_sdp_master_leaf_node: "OK",
    tmc_sdp_subarray_leaf_node: "OK",
}

ON_OFF_DEVICE_COMMAND_DICT = {
    # TODO use this as as list when multiple subarray considered in testing
    "sdp_subarray": sdp_subarray1,
    "csp_subarray": csp_subarray1,
    "csp_master": csp_master,
    "tmc_subarraynode": tmc_subarraynode1,
    "sdp_master": sdp_master,
    "central_node": centralnode,
    "tmc_csp_subarray_leaf_node": tmc_csp_subarray_leaf_node,
}


DEVICE_LIST_FOR_CHECK_DEVICES = [
    centralnode,
    csp_subarray1,
    sdp_subarray1,
    tmc_subarraynode1,
    tmc_csp_master_leaf_node,
    tmc_csp_subarray_leaf_node,
    tmc_sdp_master_leaf_node,
    tmc_sdp_subarray_leaf_node,
]

INTERMEDIATE_STATE_DEFECT = {
    "enabled": True,
    "fault_type": FaultType.STUCK_IN_INTERMEDIATE_STATE,
    "error_message": "Device stuck in intermediate state",
    "result": ResultCode.FAILED,
    "intermediate_state": ObsState.RESOURCING,
}

INTERMEDIATE_STATE_DEFECT_EMPTY = {
    "enabled": True,
    "fault_type": FaultType.STUCK_IN_INTERMEDIATE_STATE,
    "error_message": "Device stuck in intermediate state",
    "result": ResultCode.FAILED,
    "intermediate_state": ObsState.EMPTY,
}

FAILED_RESULT_DEFECT = {
    "enabled": True,
    "fault_type": FaultType.FAILED_RESULT,
    "error_message": "Device defective.",
    "result": ResultCode.QUEUED,
    "target_obsstates": [ObsState.IDLE],
}

FAILED_RESULT_DEFECT_EMPTY = {
    "enabled": True,
    "fault_type": FaultType.FAILED_RESULT,
    "error_message": "Device defective.",
    "result": ResultCode.QUEUED,
    "target_obsstates": [ObsState.EMPTY],
}

SDP_BACK_TO_INITIAL_STATE = {
    "enabled": True,
    "fault_type": FaultType.SDP_BACK_TO_INITIAL_STATE,
    "error_message": "Device defective.",
    "result": ResultCode.FAILED,
    "target_obsstates": [ObsState.EMPTY],
}

COMMAND_FAILED_WITH_SDP_EXCEPTION_OBSSTATE_EMPTY = {
    "enabled": True,
    "fault_type": FaultType.SDP_BACK_TO_INITIAL_STATE,
    "error_message": "Default exception.",
    "result": ResultCode.FAILED,
    "target_obsstates": [ObsState.RESOURCING, ObsState.EMPTY],
}

RESET_DEFECT = {"enabled": False}

COMMAND_NOT_ALLOWED_DEFECT = {
    "enabled": True,
    "fault_type": FaultType.COMMAND_NOT_ALLOWED,
    "error_message": "Exception to test exception propagation",
    "result": ResultCode.FAILED,
}
FAULT_DEFECT = json.dumps(
    {
        "enabled": True,
        "fault_type": FaultType.STUCK_IN_INTERMEDIATE_STATE,
        "error_message": "Device stuck in intermediate state",
        "result": ResultCode.FAILED,
        "intermediate_state": ObsState.FAULT,
    }
)

DEVICE_OBS_STATE_ABORT_IN_EMPTY_SDP = {
    csp_subarray1: ["ABORTED"],
    tmc_subarraynode1: ["ABORTED"],
}

DEVICE_OBS_STATE_ABORT_IN_EMPTY_CSP = {
    sdp_subarray1: ["ABORTED"],
    tmc_subarraynode1: ["ABORTED"],
}
INTERMEDIATE_CONFIGURING_OBS_STATE_DEFECT = {
    "enabled": True,
    "fault_type": FaultType.STUCK_IN_INTERMEDIATE_STATE,
    "error_message": "Device stuck in intermediate state",
    "result": ResultCode.FAILED,
    "intermediate_state": ObsState.CONFIGURING,
}

INTERMEDIATE_FAULT_OBS_STATE_DEFECT = {
    "enabled": True,
    "fault_type": FaultType.STUCK_IN_INTERMEDIATE_STATE,
    "error_message": "Device stuck in intermediate state",
    "result": ResultCode.FAILED,
    "intermediate_state": ObsState.FAULT,
}

INTERMEDIATE_SDP_FAULT_OBS_STATE_DEFECT = {
    "enabled": True,
    "fault_type": FaultType.FAILED_RESULT,
    "error_message": "Device stuck in intermediate state",
    "result": ResultCode.FAILED,
    "intermediate_state": ObsState.FAULT,
}

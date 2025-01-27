"""Enum to used in tests
"""
import enum
from enum import IntEnum, unique


@unique
class SubarrayState(IntEnum):
    ON = 0
    OFF = 1
    FAULT = 8
    INIT = 9
    UNKNOWN = 13


@unique
class SubarrayObsState(IntEnum):
    EMPTY = 0
    RESOURCING = 1
    IDLE = 2
    CONFIGURING = 3
    READY = 4
    SCANNING = 5


@unique
class SimulatorDeviceType(IntEnum):
    LOW_CSP_DEVICE = 5
    LOW_SDP_DEVICE = 6
    LOW_CSP_MASTER_DEVICE = 7
    LOW_SDP_MASTER_DEVICE = 8
    MCCS_MASTER_DEVICE = 9
    MCCS_SUBARRAY_DEVICE = 10


class FaultType(enum.IntEnum):
    """Enum class for raising various exceptions from helper devices."""

    COMMAND_NOT_ALLOWED_AFTER_QUEUING = 6
    NONE = 0
    COMMAND_NOT_ALLOWED = 1
    FAILED_RESULT = 2
    LONG_RUNNING_EXCEPTION = 3
    STUCK_IN_INTERMEDIATE_STATE = 4
    STUCK_IN_OBSTATE = 5

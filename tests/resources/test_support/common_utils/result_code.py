# -*- coding: utf-8 -*-
#
# This file is part of the SKA Control System project.
#
# Distributed under the terms of the BSD 3-clause new license.
# See LICENSE.txt for more info.
#
"""This module defines an enumerated type for a command result code."""

import enum


class ResultCode(enum.IntEnum):
    """Python enumerated type for command result codes."""

    OK = 0
    """The command was executed successfully."""

    STARTED = 1
    """The command has been accepted and will start immediately."""

    QUEUED = 2
    """The command has been accepted and will be executed at a future time."""

    FAILED = 3
    """The command could not be executed."""

    UNKNOWN = 4
    """The status of the command is not known."""

    REJECTED = 5
    """The command execution has been rejected."""

    NOT_ALLOWED = 6
    """The command is not allowed to be executed."""

    ABORTED = 7
    """The command in progress has been aborted."""


class FaultType(enum.IntEnum):
    """Enum class for raising various exceptions from helper devices."""

    NONE = 0
    COMMAND_NOT_ALLOWED = 1
    FAILED_RESULT = 2
    LONG_RUNNING_EXCEPTION = 3
    STUCK_IN_INTERMEDIATE_STATE = 4
    STUCK_IN_OBSTATE = 5
    SDP_BACK_TO_INITIAL_STATE = 13

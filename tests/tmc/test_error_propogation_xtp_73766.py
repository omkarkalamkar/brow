"""
Test case to verify error propagation functionality for
the End / Scan /EndScan command

This test case verifies that one of  the MCCS/CSP/SDP Subarray
is identified as defective,
 and the required command is executed on the TMC Low,
 then Subarry node
   reports an error.
"""


import pytest

# from assertpy import assert_that
# from pytest_bdd import given, scenario, then, when
from pytest_bdd import scenario

# from ska_control_model import ObsState, ResultCode
# from ska_tango_testing.integration import TangoEventTracer, log_events
# from tango import DevState
#
# from tests.resources.test_harness.central_node_low
# import CentralNodeWrapperLow
# from tests.resources.test_harness.constant import (
#     ERROR_PROPAGATION_DEFECT,
#     TIMEOUT,
#     mccs_subarray_leaf_node,
# )
# from tests.resources.test_harness.simulator_factory import SimulatorFactory
# from tests.resources.test_harness.subarray_node_low import (
#     SubarrayNodeWrapperLow,
# )
# from tests.resources.test_harness.utils.common_utils import JsonFactory
# from tests.resources.test_harness.utils.enums import SimulatorDeviceType
# from tests.resources.test_support.common_utils.tmc_helpers import (
#     prepare_json_args_for_centralnode_commands,
#     prepare_json_args_for_commands,
# )


@pytest.mark.SKA_low
@scenario(
    "../features/tmc/check_error_propagation.feature",
    "Error Propagation Reported by TMC Low End/EndScan/Scan "
    "Commands for Defective Subarray",
)
def test_tmc_command_error_propagation():
    """
    Test case to verify TMC Error Propagation functionality.
    """

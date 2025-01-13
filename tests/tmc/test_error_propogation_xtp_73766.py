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
from pytest_bdd import scenario


@pytest.mark.SKA_low12
@scenario(
    "../features/tmc/check_error_propagation.feature",
    "Error Propagation Reported by TMC Low End/EndScan/Scan "
    "Commands for Defective Subarray",
)
def test_tmc_command_error_propagation():
    """
    Test case to verify TMC Error Propagation functionality.
    """

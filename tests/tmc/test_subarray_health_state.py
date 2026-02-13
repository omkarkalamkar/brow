"""Test Subarray Node Health State"""

import pytest
from pytest_bdd import scenario


@pytest.mark.healthinfo
@pytest.mark.SKA_low
@scenario(
    "../features/tmc/check_subarray_healthstate.feature",
    "Subarray health reflects correct aggregated healthstate of "
    "CSP, SDP, and MCCS subarrays",
)
def test_subarray_health_combined_states():
    """Test subarray node healthstate based on CSP, SDP, MCCS"""

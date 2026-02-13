"""Test Subarray Node Health State"""

import pytest
from pytest_bdd import parsers, scenario, then


@pytest.mark.healthinfo
@pytest.mark.SKA_low
@scenario(
    "../features/tmc/check_healthinfo.feature",
    "Subarray health reflects correct healthinfo"
    " of CSP, SDP, and MCCS subarrays",
)
def test_subarray_health_combined_states():
    """Test subarray node healthinfo based on CSP, SDP, MCCS healthstate"""


@then(
    parsers.parse(
        "the Subarray Node healthinfo should be {expected_health_info}"
    )
)
def check_subarray_node_health_info(
    event_recorder, subarray_node_low, expected_health_info
):
    """Check the subarray healthinfo"""
    event_recorder.subscribe_event(
        subarray_node_low.subarray_node, "healthInfo"
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_node,
        "healthInfo",
        expected_health_info,
    )

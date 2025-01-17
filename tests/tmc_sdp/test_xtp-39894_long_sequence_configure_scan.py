"""Test TMC Low executes configure-scan sequence of commands successfully"""

import pytest
from pytest_bdd import scenario


@pytest.mark.tmc_sdp
@scenario(
    "../features/tmc_sdp/xtp_39894_tmc_sdp_long_sequence.feature",
    "TMC Low executes configure-scan sequence of commands successfully",
)
def test_tmc_sdp_long_sequences():
    """
    TMC Low executes configure-scan sequence of commands successfully
    """

"""Test cases for AssignResources and ReleaseResources
 Command for low"""
import logging

import pytest
from ska_ser_logging import configure_logging

from tests.resources.test_harness.central_node_low import CentralNodeWrapperLow

configure_logging(logging.DEBUG)
LOGGER = logging.getLogger(__name__)


@pytest.mark.SKA_low
def test_array_layout_file_provided_updates(
    central_node_low: CentralNodeWrapperLow,
):
    """Verify the arrayLayoutFileProvided attribute updates"""
    LOGGER.info(
        "CentralNode Low Initial arrayLayoutFileProvided: %s",
        central_node_low.arrayLayoutFileProvided,
    )
    assert central_node_low.arrayLayoutFileProvided is True

    url = '{"source_uris":[""],"array_layout_path":""}'
    LOGGER.info("URL is: %s", url)
    central_node_low.DefaultArrayLayoutURL = url
    assert central_node_low.arrayLayoutFileProvided is False

    url = (
        '{"source_uris":["gitlab://gitlab.com/ska-telescope/'
        + 'ska-telmodel-data?main#tmdata"],"array_layout_path":'
        + '"instrument/ska1_low/layout/low-layout.json"}'
    )
    LOGGER.info("URL is: %s", url)
    central_node_low.DefaultArrayLayoutURL = url
    assert central_node_low.arrayLayoutFileProvided is True

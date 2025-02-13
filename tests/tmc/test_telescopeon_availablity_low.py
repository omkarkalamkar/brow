"""
This module contains test cases related to the execution of commands
(AssignResources, ReleaseResources, TelescopeOn) while the corresponding pods
are manually deleted.
"""
import pytest
from tango import DeviceProxy

from tests.resources.test_support.constant_low import (
    centralnode,
    tmc_subarraynode1,
)

# Note:These test case will pass only when any of the node
# is deleted explicitly
# Hence this test will be skipped on pipeline
# Sample command to delete is
# while true;
# do kubectl delete pod/subarraynode-02-0 -n ska-tmc-integration; sleep 3;
# done


@pytest.mark.skip(reason="This test case needs pods deletion")
@pytest.mark.SKA_low
def test_assign(json_factory):
    """AssignResources  is executed while pods are deleted."""

    assign_json = json_factory("assign_resource_low")
    central_node = DeviceProxy(centralnode)
    _, message = central_node.AssignResources(assign_json)
    assert "Subarray low-tmc/subarray/01 is not available" in str(message)


@pytest.mark.skip(reason="This test case needs pods deletion")
@pytest.mark.SKA_low
def test_release(json_factory):
    """ReleaseResources is executed while pods are deleted."""

    release_json = json_factory("release_resource_low")
    central_node = DeviceProxy(centralnode)
    _, message = central_node.ReleaseResources(release_json)

    assert "Subarray low-tmc/subarray/01 is not available" in str(message)


@pytest.mark.skip(reason="This test case needs pods deletion")
@pytest.mark.SKA_low
def test_telescope_on():
    """On Command  is executed while pods are deleted."""
    central_node = DeviceProxy(centralnode)

    # works fine when pods are deleted
    with pytest.raises(Exception) as info:
        # tmc.set_to_on()
        central_node.TelescopeOn()

    assert "not available" in str(info.value)


@pytest.mark.skip(reason="This test case needs pods deletion")
@pytest.mark.SKA_low
def test_assign_sn_entrypoint_low(json_factory):
    """AssignResources is executed while pods are deleted."""
    assign_json = json_factory("assign_resource_low")

    tmcsubarraynode1 = DeviceProxy(tmc_subarraynode1)
    with pytest.raises(Exception) as info:
        tmcsubarraynode1.AssignResources(assign_json)

    assert "Tmc Subarray is not available" in str(info.value)


@pytest.mark.skip(reason="This test case needs pods deletion")
@pytest.mark.SKA_low
def test_release_sn_entrypoint_low():
    """ReleaseResources is executed while pods are deleted."""

    tmcsubarraynode1 = DeviceProxy(tmc_subarraynode1)
    with pytest.raises(Exception) as info:
        tmcsubarraynode1.ReleaseAllResources()

    assert "Tmc Subarray is not available" in str(info.value)

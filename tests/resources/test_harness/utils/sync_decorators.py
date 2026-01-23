import functools
from contextlib import contextmanager

from tests.resources.test_harness.utils.wait_helpers import Waiter
from tests.resources.test_support.common_utils.base_utils import DeviceUtils
from tests.resources.test_support.common_utils.common_helpers import Resource

TIMEOUT = 500


def sync_set_to_on(device_dict: dict):
    def decorator_sync_set_to_on(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            the_waiter = Waiter(**device_dict)
            the_waiter.set_wait_for_telescope_on()
            result = func(*args, **kwargs)
            the_waiter.wait(TIMEOUT)
            return result

        return wrapper

    return decorator_sync_set_to_on


def sync_set_to_off(device_dict: dict):
    def decorator_sync_set_to_off(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            the_waiter = Waiter(**device_dict)
            the_waiter.set_wait_for_going_to_off()
            result = func(*args, **kwargs)
            the_waiter.wait(TIMEOUT)
            return result

        return wrapper

    return decorator_sync_set_to_off


# defined as a context manager
@contextmanager
def sync_going_to_off(timeout=50, **kwargs):
    the_waiter = Waiter(**kwargs)
    the_waiter.set_wait_for_going_to_off()
    yield
    the_waiter.wait(timeout)


def sync_set_to_standby(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        the_waiter = Waiter(**kwargs)
        the_waiter.set_wait_for_going_to_standby()
        result = func(*args, **kwargs)
        the_waiter.wait(TIMEOUT)
        return result

    return wrapper


def sync_release_resources(device_dict, timeout=200):
    def decorator_sync_release_resources(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            the_waiter = Waiter(**device_dict)
            the_waiter.set_wait_for_going_to_empty()
            result = func(*args, **kwargs)
            the_waiter.wait(timeout)
            return result

        return wrapper

    return decorator_sync_release_resources


def sync_assign_resources(device_dict):
    # defined as a decorator
    def decorator_sync_assign_resources(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            device = DeviceUtils(
                obs_state_device_names=[
                    device_dict.get("csp_subarray"),
                    device_dict.get("sdp_subarray"),
                    device_dict.get("tmc_subarraynode"),
                ]
            )
            device.check_devices_obsState("EMPTY")
            set_wait_for_obsstate = kwargs.get("set_wait_for_obsstate", True)
            result = func(*args, **kwargs)
            if set_wait_for_obsstate:
                the_waiter = Waiter(**device_dict)
                the_waiter.set_wait_for_assign_resources()
                the_waiter.wait(500)
            return result

        return wrapper

    return decorator_sync_assign_resources


def sync_abort(device_dict, timeout=1000):
    # define as a decorator
    def decorator_sync_abort(func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            device_dict = self.device_dict
            the_waiter = Waiter(**device_dict)
            the_waiter.set_wait_for_aborted()
            result = func(self, *args, **kwargs)
            the_waiter.wait(timeout)
            return result

        return wrapper

    return decorator_sync_abort


def sync_restart(device_dict, timeout=500):
    # define as a decorator
    def decorator_sync_restart(func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            device_dict = self.device_dict
            the_waiter = Waiter(**device_dict)
            the_waiter.set_wait_for_going_to_empty()
            result = func(self, *args, **kwargs)
            the_waiter.wait(timeout)
            return result

        return wrapper

    return decorator_sync_restart


def sync_configure(device_dict):
    # defined as a decorator
    def decorator_sync_configure(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            invoked_from_ready = False
            the_waiter = Waiter(**device_dict)
            if Resource(device_dict.get("tmc_subarraynode")) == "READY":
                invoked_from_ready = True
            result = func(*args, **kwargs)
            if invoked_from_ready:
                the_waiter.set_wait_for_configuring()
                the_waiter.wait(500)
            the_waiter.set_wait_for_configure()
            the_waiter.wait(800)
            return result

        return wrapper

    return decorator_sync_configure


def sync_end(device_dict):
    # defined as a decorator
    def decorator_sync_end(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            the_waiter = Waiter(**device_dict)
            the_waiter.set_wait_for_idle()
            result = func(*args, **kwargs)
            the_waiter.wait(200)
            return result

        return wrapper

    return decorator_sync_end


def sync_endscan(device_dict):
    # defined as a decorator
    def decorator_sync_endscan(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            the_waiter = Waiter(**device_dict)
            the_waiter.set_wait_for_ready()
            result = func(*args, **kwargs)
            the_waiter.wait(200)
            return result

        return wrapper

    return decorator_sync_endscan

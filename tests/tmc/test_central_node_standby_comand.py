"""
Module: test_low_central_node_standby_command

This module defines a Pytest test class to verify the behavior of the Standby
command on a Telescope Monitoring and Control (TMC) CentralNode Low.
The test includes checking the transitions triggered by the Standby command
and validating the completion transitions, assuming that external subsystems
work fine.
"""

import pytest
from assertpy import assert_that
from ska_tango_testing.integration import TangoEventTracer, log_events
from tango import DevState

from tests.resources.test_harness.central_node_low import CentralNodeWrapperLow
from tests.resources.test_harness.constant import TIMEOUT
from tests.resources.test_harness.simulator_factory import SimulatorFactory
from tests.resources.test_harness.utils.enums import SimulatorDeviceType


class TestLowCentralNodeStandbyCommand:
    """Validates the behavior of the Standby command on the
    TMC CentralNode Low by checking the state transitions of simulated master
    devices(CSP, SDP, MCCS) and the overall telescope state.
    """

    @pytest.mark.SKA_low
    def test_low_central_node_standby_command(
        self,
        central_node_low: CentralNodeWrapperLow,
        event_tracer: TangoEventTracer,
        simulator_factory: SimulatorFactory,
    ):
        """
        Test to verify transitions that are triggered by Standby
        command and followed by a completion transition
        assuming that external subsystems work fine.
        Glossary:
        - "central_node_low": fixture for a TMC CentralNode Low under test
        which provides simulated master devices
        - "event_recorder": fixture for a MockTangoEventCallbackGroup
        for validating the subscribing and receiving events.
        - "simulator_factory": fixture for creating simulator devices for
        low Telescope respectively.
        """
        csp_master_sim = simulator_factory.get_or_create_simulator_device(
            SimulatorDeviceType.LOW_CSP_MASTER_DEVICE
        )
        sdp_master_sim = simulator_factory.get_or_create_simulator_device(
            SimulatorDeviceType.LOW_SDP_MASTER_DEVICE
        )
        mccs_master_sim = simulator_factory.get_or_create_simulator_device(
            SimulatorDeviceType.MCCS_MASTER_DEVICE
        )
        event_tracer.subscribe_event(csp_master_sim, "State")
        event_tracer.subscribe_event(sdp_master_sim, "State")
        event_tracer.subscribe_event(mccs_master_sim, "State")
        event_tracer.subscribe_event(
            central_node_low.central_node, "telescopeState"
        )
        central_node_low.move_to_on()
        log_events(
            {
                central_node_low.central_node: ["telescopeState"],
                sdp_master_sim: ["State"],
                csp_master_sim: ["State"],
                mccs_master_sim: ["State"],
            }
        )
        assert_that(event_tracer).described_as(
            "FAILED ASSUMPTION AFTER ON COMMAND: "
            "Central Node device"
            f"({central_node_low.central_node.dev_name()}) "
            "is expected to be in TelescopeState ON",
        ).within_timeout(TIMEOUT).has_change_event_occurred(
            central_node_low.central_node,
            "telescopeState",
            DevState.ON,
        )
        central_node_low.set_standby()
        assert_that(event_tracer).described_as(
            "FAILED ASSUMPTION AFTER STANDBY COMMAND: "
            "SDP Controller device"
            f"({sdp_master_sim.dev_name()}) "
            "is expected to be in State ON",
        ).within_timeout(TIMEOUT).has_change_event_occurred(
            sdp_master_sim,
            "State",
            DevState.STANDBY,
        )
        assert_that(event_tracer).described_as(
            "FAILED ASSUMPTION AFTER STANDBY COMMAND: "
            "CSP Controller device"
            f"({csp_master_sim.dev_name()}) "
            "is expected to be in State ON",
        ).within_timeout(TIMEOUT).has_change_event_occurred(
            csp_master_sim,
            "State",
            DevState.STANDBY,
        )
        assert_that(event_tracer).described_as(
            "FAILED ASSUMPTION AFTER STANDBY COMMAND: "
            "MCCS Controller device"
            f"({mccs_master_sim.dev_name()}) "
            "is expected to be in State ON",
        ).within_timeout(TIMEOUT).has_change_event_occurred(
            mccs_master_sim,
            "State",
            DevState.STANDBY,
        )
        assert_that(event_tracer).described_as(
            "FAILED ASSUMPTION AFTER STANDBY COMMAND: "
            "Central Node device"
            f"({central_node_low.central_node.dev_name()}) "
            "is expected to be in TelescopeState STANDBY",
        ).within_timeout(TIMEOUT).has_change_event_occurred(
            central_node_low.central_node,
            "telescopeState",
            DevState.STANDBY,
        )

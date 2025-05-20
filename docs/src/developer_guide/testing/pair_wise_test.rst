######################################
TMC LOW integration Testing guidelines
######################################

****************************
Pair wise testing / Real-SDP
****************************

Pair wise testing is way of testing the TMC code with real SDP subsystem in place. 
using latest `test harness` implemented. 

Commands implemented
^^^^^^^^^^^^^^^^^^^^
To test with tmc_sdp execute the command::

    make k8s-test MARK=tmc_sdp SDP_SIMULATION_ENABLED=false

* ``ON`` - Testing On command on TMC with Real-SDP in place.
* ``Off`` - Testing Off command on TMC  with Real-SDP in place.
* ``AssignResources`` -  Testing AssignResources command on TMC with Real-SDP in place.
* ``ReleaseResources``- Testing ReleaseResources command on TMC with Real-SDP in place.
* ``Standby`` - Testing StandBy command on TMC with Real-SDP in place.
* ``Configure``- Testing Configure command on TMC with real SDP controller and SDP Subarrays and mocked/simulated CSP and Mccs subsystems.
* ``End`` - Testing End command on TMC with real SDP controller and SDP Subarrays and mocked/simulated CSP and Mccs subsystems.
* ``Scan`` - Testing Scan command on TMC with Real-SDP in place.
* ``EndScan`` - Testing EndScan command on TMC with Real-SDP in place.
* ``Abort`` - Testing Abort command on TMC with Real-SDP in place.
* ``Restart`` - Testing Restart command TMC with Real-SDP in place.

Negative Scenario implemented
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* ``HealthState.DEGRADED Scenario``


        - Testing TMC-SDP to verification of the TelescopeHealthState transition.
        - In the Telescope Monitoring and Control TMC system based on the health state changes of the SDP Controller. 
        - The scenario simulates a telescope setup consisting of Real SDP, and simulated devices for the CSP and the MCCS.

Long command sequence implementation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* ``TMC Low executes configure-scan sequence of commands successfully`` - Testing TMC-SDP long sequence for configure-scan functionality by parameterizing the scan_types and scan_ids
* ``TMC Low executes multiple scans with same configuration successfully`` - Testing TMC-SDP long sequence for multiple scans functionality by parameterizing the scan_types and scan_ids
* ``TMC Low executes multiple scans with different resources and configurations``-  Testing TMC-SDP long sequence for multiple scan functionality by parameterizing new scan_type and new scan_ids

****************************
Pair wise testing / Real-CSP
****************************

Pair wise testing is way of testing the TMC code with real CSP subsystem in place. 
using latest `test harness` implemented. 

Commands implemented
^^^^^^^^^^^^^^^^^^^^
To test with tmc_csp execute the command::

    `make k8s-test MARK=tmc_csp CSP_SIMULATION_ENABLED=false`

* ``ON`` - Testing On command on TMC with Real-CSP in place.
* ``Standby`` - Testing Standby command on TMC with Real-CSP in place.
* ``AssignResources`` - Testing AssignResources command on TMC with Real-CSP in place.
* ``ReleaseResources``- Testing ReleaseResources command on TMC with Real-CSP in place.
* ``Configure``- Testing Configure command on TMC with real CSP controller and CSP Subarrays and mocked/simulated SDP and Mccs subsystems.
* ``End`` - Testing End command on TMC with real CSP controller and CSP Subarrays and mocked/simulated SDP and Mccs subsystems.
* ``Scan``- Testing Scan command on TMC with real CSP controller and CSP Subarrays and mocked/simulated SDP and Mccs subsystems.
* ``EndScan`` - Testing EndScan command on TMC with real CSP controller and CSP Subarrays and mocked/simulated SDP and Mccs subsystems.
* ``Abort`` - Testing Abort command on TMC with real CSP controller and CSP Subarrays and mocked/simulated SDP and Mccs subsystems.
* ``Restart`` - Testing Restart command on TMC with real CSP controller and CSP Subarrays and mocked/simulated SDP and Mccs subsystems.


*****************************
Pair wise testing / Real-MCCS
*****************************

Pair wise testing is way of testing the TMC code with real MCCS subsystem in place using latest `test harness` implemented.

Commands implemented
^^^^^^^^^^^^^^^^^^^^
To test with tmc_mccs execute the command::

    `make k8s-test MARK=tmc_mccs MCCS_SIMULATION_ENABLED=false`

* ``ON`` - Testing On command on TMC with Real-MCCS in place.
* ``Off`` - Testing Off command on TMC  with Real-MCCS in place.
* ``AssignResources`` - Testing AssignResources command on TMC with Real-MCCS in place.
* ``ReleaseResources``- Testing ReleaseResources command on TMC with Real-MCCS in place.
* ``Configure``- Testing Configure command on TMC with real MCCS controller and MCCS Subarrays and mocked/simulated SDP and CSP subsystems.
* ``End`` - Testing End command on TMC with real MCCS controller and MCCS Subarrays and mocked/simulated SDP and CSP subsystems.
* ``Scan``- Testing Scan command on TMC with real MCCS controller and MCCS Subarrays and mocked/simulated SDP and CSP subsystems.
* ``EndScan`` - Testing EndScan command on TMC with real MCCS controller and MCCS Subarrays and mocked/simulated SDP and CSP subsystems.

Negative Scenario implemented
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* ``HealthState.DEGRADED Scenario``

    - Testing TMC-MCCS to verification of the TelescopeHealthState transition
    - in the Telescope Monitoring and Control TMC system based on the health state changes of the SDP Controller.
    - The scenario simulates a telescope setup consisting of Real MCCS, and simulated devices for the CSP and the SDP.

* ``Handling Invalid Station Id in MCCS controller`` - The TMC Low Subarray reports the exception triggered by the MCCS controller when it encounters an invalid station ID.

* ``Test Error propagation when MCCS subsystem is unavailable`` - MCCS Controller report the error when one of the subarray beam is unavailable

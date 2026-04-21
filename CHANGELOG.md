###########
Change Log
###########

All notable changes to this project will be documented in this file.
This project adheres to `Semantic Versioning <http://semver.org/>`_.

[Unreleased]
*************
Updated
-------
* Tested 16 Subarrays with different configurations, performed end to end observations and delay models for station beams ,PSS and PST beams.
* Tested 16 Subarrys for 30 min scan duration
* Tested 16 Subarrys for multi observation and multi scan scenario.
* Tested 16 Subarrays for negative observations
* Utilized CentralNode v1.2.0
* SAH-1905: Update TMC to support MCCS early scan.

[2.14.0-rc.1]
*************
Updated
-------
* Subarray node v1.4.0: Introduced new property `PreRecoveryCheckTimeDuration`,which ensures that the devices with successful command result reach final observation state and devices with failed command result reach the previous observation state. This would help in auto recovery the subarray to appropriate observation state in case of failure. If the device is stuck in transitioning observation state till time duration the subarray node won't be recovered.
* Subarray node v1.5.0: Update rules to consider `longRunningCommandResult` in addition to `ObsState=Aborted` for Abort Command.
* MCCS Leaf node v0.15.2: Fixed the issue of liveliness error not getting cleared from healthinfo.

[2.13.0]
********
* This is the full release of 2.13.0-rc.1.This release introduces improvements in logging configuration, enhanced multi-subarray execution capabilities, updated component versions, and fixes to Subarray state handling and ObsState aggregation.

[2.13.0-rc.1]
**************
Added
------
* logging level is set to 4 (``INFO`` level). To set the logging level of one or more specific component, refer to advanced cutomization options.

Updated
--------
* Utilized SubarrayNode v1.2.1

Utilised following leaf node tags with log improvements,

ska-tmc-centralnode  - 1.1.0
ska-tmc-sdpleafnode  - 0.29.0
ska-tmc-cspleafnode  - 0.43.0
ska-tmc-mccsleafnode - 0.15.0

Added
------
* Created a separate job to deploy 4 Subarrays and execute an observation on 4 subarrays parallely. This job runs only in a scheduled master pipeline daily.
* Verified that the TMC Subarry can work with 68 stations, 3 PSS beams and 2 PST beams
  and checked that the Delay Models are getting generated for all the resources .

Fixed
-----
* Fixed an issue where SubarrayNode could remain stuck in CONFIGURING
  when a Configure command failed and command_in_progress was cleared
  before aggregation was triggered.

* Fixed incorrect ObsState aggregation in scenarios where a subsystem
  command returned FAILED but no subsequent event triggered aggregation,
  preventing transition out of CONFIGURING (e.g. to FAULT).

* Added a FAULT rule so FAILED results correctly propagate to a FAULT
  ObsState when applicable.

* logging level is set to 4 (``INFO`` level). To set the logging level of one or more specific component, refer to advanced cutomization options.






[2.12.0]
************
Added
------
* Added support for forwarding the Kafka address through SDP using the receive addresses configuration
* **Improved Health Monitoring**: Introduced a new HealthInfo reporting capability on TMC nodes to provide better visibility into system health and status changes.
* **Health Change Insights**: When the health state of the TMC Subarray Node changes, the reason for the change is now available through the HealthInfo information.
* **Subsystem HealthInfo Aggregation**: The Subarray node now collects and aggregates health information from multiple subsystems, providing a clearer and more consolidated view of overall system health.
* HealthState attribute support has also been introduced on TMC Leaf Nodes.

Updated
--------
* **SubarrayNode**: Now uses ska-telmodel v1.33.0 and ska-tmc-cdm v14.8.0.
* TMC Central Node and Subarray Node: Tags updated due to base class upgrade (no functional changes).
  * CentralNode → v1.0.0
  * SubarrayNode → v1.1.0
* **TMC Component Upgrades**
  * The HealthInfo capability is introduced in the following subsystem versions:
  * TMC Subarray Node → v0.51.2
  * MCCS Subarray Leaf Node → v0.13.0
  * SDP Subarray Leaf Node → v0.27.0
  * CSP Subarray Leaf Node → v0.40.0

[2.12.0-rc.1]
**************
* TMC supports kafka topic addresses forwarding.
* TMC Central Node and Subarray Node tags updated with base class upgrade (CentralNode v1.0.0, SubarrayNode v1.1.0)

[2.11.0-rc.1]
*************
* Upgraded TMC Leaf Nodes tags with Base class updates (MCCS v0.12.2, SDP v0.26.0, CSP v0.36.0)
* Updated ska-tmc-simulator to v1.9.5.
* healthinfo attribute has been introduced on TMC Leaf Nodes (MCCS v0.13.0, SDP v0.27.0, CSP v0.40.0)

[2.10.0]
*********
* This is the full release of 2.10.0-rc.1. TMC Low now supports PSS Scans with upto 30 PSS beams.

[2.10.0-rc.1]
*************
Updated
-------
* TMC Scan command supports optional field start_time to comply with ADR-111.
* TMC Low supports upto 30 PSS beams
* Updated CentralNode to v0.29.1
* Updated CspleafNodes to v0.38.1
* Updated ska-tango-taranta to v2.18.2
* Updated TMC Low Configure schema to v6.0
* Updated RTD to reflect the changes for PSS.

Fixed
-----
* Fixed teardown issues in case of second subarray.

[2.9.0]
***********
* This is the full release of 2.9.0-rc.1. TMC Low is now compliant with ADR-63 and supports non-sidereal tracking.

[2.9.0-rc.1]
************
Updated
-------
* TMC Low Configure schema updated to include the "field" key for ADR-63 compliance.

[2.8.1]
*************
This is full version of 2.8.1-rc.1 which fixes SKB-1158.

Fixed
-----
* Improved Abort Retry mechanism to resolve SKB-1158

[2.8.0]
*************
This full version comprises of changes from 2.4.0-c.1 till 2.8.0-rc.2.

Added
------
* Introduced ResourceMonitor device in the ska-tmc-low.
    * Resource Monitor tag v0.5.0
	* Reports subarray allocations for stations through the stationsData attribute of the Resource Monitor.
	* reporting of resources stations and station beams using stations and stationBeams attributes of Resource Monitor.
* Added device configuration and FQDN under chart templates.
* Functionality of auto recovery of AssignResources and Configure command from inconsistent stage
* Added MccsReleaseInterfaceURL in values.yaml
* Full implementation of ADR-63
* Support for changing the telescope antenna layout at runtime.

Updated
--------
* Testing specific: Simulators gets deployed as separate testing service
	* Simulators tag v0.5.0
* Archiver attribute configuration includes attributes of Resource Monitor.
* Documentation includes ResourceMonitor configuration details and usage.

Removed
--------
* TMC simulators are no longer bundled with any of the TMC deliverable code.

Fixed
------
* Fixed SKB-1074
* Remove keys from input json not required by real CSP, causing command failures.

[2.8.1-rc.1]
*************
Fixed
-----
* Improved Abort Retry mechanism to resolve SKB-1158.

[2.8.0-rc.2]
*************
Fixed
-----
* Remove keys from input json not required by real CSP, causing command failures.

Added
-----
* TMC utilises Simulators as testing service

[2.8.0-rc.1]
************
Updated
--------
* TMC Low utilises Resource Monitor 0.5.0.
* TMC Low Resource Monitor supports reporting of resources stations and station beams using stations and stationBeams attributes of Resource Monitor.
* TMC Low utilises ska_tmc_simulators 1.5.1 and replaces ska_tmc_common for helper devices.

[2.3.2]
************
Updated
--------
* TMC Low full release 2.3.2

[2.7.0-rc.1]
************
Added
-----
* TMC Low now supports to antenna layout update at runtime.

[2.6.1-rc.1]
************
Fixed
------
* Fixed SKB-1074

Added
-----
* Added new RTD page to document Array Layout support.

[2.6.0-rc.1]
************
Added
-----

* Enable non sidereal object tracking for TMC low
* Updated SubarrayNode to v0.47.1
* Updated CspleafNode to v0.33.2

[2.5.0-rc.1]
************
Added
-----
* Introduced ResourceMonitor device in the ska-tmc-low.
* Added device configuration and FQDN under chart templates.
* TMC Low now supports reporting subarray allocations for stations through the stationsData attribute of the Resource Monitor.
* Updated documentation to include ResourceMonitor configuration details and usage.
* Utilised the latest ResourceMonitor release version v0.3.0 for integration and verification.


[2.4.0-rc.1]
************
Added
-----
* Functionality of auto recovery of AssignResources and Configure command from inconsistent stage
* Added MccsReleaseInterfaceURL in values.yaml
* SubarrayNode v0.45.2 integrated to support auto recovery functionality

[2.3.4]
*************
Updated
-------
* Integrated latest SubarrayNode v0.44.1
* Update TMC to support ska-low-tmc-configure/5.0 and ska-low-csp-configure/5.0
* Updated MCCS leaf node to v0.10.3

Fixed
------
* Fixed SKB-1041
* Fixed SKB-908

[2.3.3]
*************
Fixed
-----
* SKB-1056: Updated CSP subarray leaf node v0.32.2 to fix the bug.

[2.3.2-rc.2]
************
Fixed
-----
Updated Central node tag v0.24.1 to resolve SKB-860.

[2.3.2-rc.1]
************
Fixed
-----
* Updated Central node tag v0.24.0 to resolve SKB-908 and SKB-1051.

[2.3.1-rc.1]
************
Updated
--------
* Resolution of bug SKB-1013
* Updated the ska-tmc-sdpleafnodes to v0.24.2

[2.3.0-rc.1]
************
Updated
------------
* Extending the support of multiple station up to 8 station beams.
* Utilised the latest dev tag from CSP (0.32.0) and latest tag of central node (0.22.0).
* RTD improvements to reflect support for 8 station beams.

[2.3.0-dev.1]
*************
Updated
-------------
* Extending the support of multiple station up to 8 station beams.
* Utilised the latest dev tag from CSP (0.32.0) and latest tag of central node (0.22.0)


[2.2.0-rc.1]
************
Added
-----
* CommandTimeout attribute is introduced which can help to update timeout without redeployment.
* CommandTimeOutDefault property is introduced which can be used to set default value at the time of deployment.

Updated
-------
* Update to TMC Configure command to stop sending field parameter to csp subarray.
* Used EventManager in subarraynode, centralnode, cspleafnodes, mccsleafnodes.
* Changes for skb-808 on subarraynode, centralnode, cspleafnodes, mccsleafnodes.
* Updated TMC tags:
    centralnode: 0.21.1
    subarraynode: 0.41.0
    sdpleafnodes:0.24.0
    cspleafnodes: 0.31.0
    mccssleafnodes: 0.10.1
    tmccommon: 0.30.0

[2.1.0]
************
Updated
-------
* Support for the observation workflow with the subsystem configurations specified in input JSON
* Added astroDataClaim in cspleafnodes to cache the astrodata in cspleafnodes as resolution of SKB-949
* Verified the observation with scaled up TMC

[2.0.0]
************
Updated
-------
* Support for multiple station and PST beams for LOW.
* Updated tel-model to version 1.23.1
* Updated cspleafnode image to 0.28.0
* Fixed string formation of FQDNs for multiple station and PST beams.
* Utilised the latest tag of subarraynode 0.39.4
* This update enables updating subarray_count variable via global section of yaml.
* This update also includes `devices_fqdn` tag for listing fqdn of devices.
* This update also includes moving `domain` and `subarray_devices` from global section.

Fixed
-----
* This update include the fix of bug SKB-985,SKB-949,SKB-967.
* Refactored the Restart command to ensure it properly cleans up any processes still running from a command in progress.

[2.0.0-rc.5]
************
Updated
-------
 * Fixed string formation of FQDNs for multiple station and PST beams.
 * Utilised the latest tag of subarraynode 0.39.4

[2.0.0-rc.4]
************
Updated
-------
* This update enables updating subarray_count variable via global section of yaml.
* This update also includes `devices_fqdn` tag for listing fqdn of devices.
* This update also includes moving `domain` and `subarray_devices` from global section.


[2.0.0-rc.3]
************
Fixed
-----
* This update include the fix of bug SKB-985.
* This update include the fix of bug SKB-949.
* This update include the fix of bug SKB-967.
* Updated the subarraynode tag to v0.39.1.
* Refactored the Restart command to ensure it properly cleans up any processes still running from a command in progress.

[2.0.0-rc.2]
************
Added
-----
* This update includes documentation changes related to the delay model interface. TMC-Low has recently been enhanced to support four subarray station beams and two PST beams, and the document has been updated accordingly.
* TMC low supports new TMC AssignResources json v4.1 with SDP v1.0.
* Utilised latest version of centralnode v0.20.2.
* Hardcoding of sdpleafnode is now removed and attribute is created to make it runtime configurable.This resolves SKB-927.

[2.0.0-rc.1]
************
Added
-----
* Support for multiple station and PST beams for LOW.
* Updated tel-model to version 1.23.1
* Updated cspleafnode image to 0.28.0

[1.4.0-rc.1]
************
Added
-----
* TMC Subarray moves to FAULT after command timed out
* TMC Restart command is updated to invoke abort and restart on sub system to bring obs state to EMPTY
* TMC Subarray is updated to transition Obs State to FAULT after command failure

[1.3.1-rc.1]
************
Added
-----
* Update command not allowed logic to allow command execution in adminmode ENGINEERING and ONLINE
* Updated SubarrayNode image to 0.35.0
* Updated CentralNode image to 0.20.0
* Updated sdpleafnode image to 0.23.1

Fixed
-----
* Healthstate based rejection of commands is removed.

[1.2.1]
************
Updated
-------
* Retry on responsiveness check of subarraynode was implemented on central node and centralnode v0.19.7 was utilized to resolve SKB-860 .
* Resolved the hardcoding and utilised the tag v0.8.1 of mccssubarrayleafnode to resolve bug SKB-939.

[1.2.1-rc.2]
************
Updated
-------
* Utilised latest version of centralnode v0.19.7 to resolve SKB-860

[1.2.1-rc.1]
************
Updated
-------
Utilised latest version of ska-tmc-mccsleafnodes v0.8.1 to resolve SKB-939

[1.2.0]
************
Updated
-------
* Implemented error propagation and timeout functionality for the Abort and Restart commands.
* Logs were refactored to resolve SKB-794 by updating the ska-tmc-sdpleafnodes and ska-tmc-cspleafnodes repositories and utilizing their latest versions: ska-tmc-sdpleafnodes v0.22.3 and ska-tmc-cspleafnodes v0.25.2.

[1.2.0-rc.3]
************
Updated
-------
Utilised latest version of ska-tmc-sdpleafnodes and ska-tmc-cspleafnodes

[1.2.0-rc.2]
************
Updated
-------
* Utilised latest version of ska-tmc-mccsleafnodes

[1.2.0-rc.1]
************
Updated
-------
* Implemented error propagation and timeout functionality for the Abort and Restart commands.

[1.1.0]
*******

Updated
-------
* Utilized refactored event manager in ska-tmc-centralnode version 0.19.5
* ska-tmc-common version 0.27.5 is utilized for the same
* Deployed 4 mock Subarrays instances of CSP, SDP and MCCS
* Moved the processing from Tango event handler to call back functions
* Improved health state aggregation
* Used rule engine for aggregation process

[1.1.0-rc.3]
************
Unreleased
**********
* Refactored delay model testcases to remove multiple when then statements.

[1.1.0-rc.3]
************
Updated
-----------
* Utilized refactored event manager in ska-tmc-centralnode version 0.19.5
* ska-tmc-common version 0.27.5 is utilized for the same

[1.1.0-rc.2]
************
Updated
-----------
* Deployed 4 mock Subarrays instances of CSP, SDP and MCCS
* Moved the processing from Tango event handler to call back functions

[1.1.0-rc.1]
************
Updated
-----------
* Improved health state aggregation
* Used rule engine for aggregation process

[1.0.0]
*******
Added
---------
* Added `domain` field in values.yaml. The domain is `low-tmc`
* Added `family` and `member` field in deviceServers of each controller leafnode device in values.yaml
* Added `family` field in deviceServers of each subarray leafnode devices in value.yaml

Updated
-----------
* Updated the TRLs of TMC low devices as per ADR-9
* Updated subarraynode to support MCCS-only End, Scan, EndScan commands.

Fixed
-----------
* Fixed event receiver in centralNode to include state and healthState subscription instead of using from common tp fix device not defined issue.
* Resolved SKB-672
* Resolved SKB-732.
* Removed configure json interface(0.3) hardcoding in TMC SDP Subarray Leaf Node.
* Updated MCCS master Leaf Node ReleaseResources command to instruct MCCS Controller to release the resources from specific subarray
* Removed the transitional obsState RESOURCING check from SDP Subarray Leaf Node AssignResources command tracker
* Updated Subarraynode to Resolve SKB-837 : missing event of receive_address from sdp subarray
* Server Name of subarraynode device got changed from `SubarrayNodeLow` to `LowTmcSubarray`
* Fixed SKB-881 and SKB-798
* Fixed an issue in the case of Abort in obsState RESOURCING

[1.0.0-rc.7]
************
Fixed
---------
* Fixed SKB-881 and SKB-798
* Fixed an issue in the case of Abort in obsState RESOURCING

[1.0.0-rc.6]
************
Added
---------
* Updated subarraynode to support MCCS-only End, Scan, EndScan commands.

[1.0.0-rc.5]
************
Fixed
---------
* Updated Subarraynode to Resolve SKB-837 : missing event of receive_address from sdp subarray
* Server Name of subarraynode device got changed from `SubarrayNodeLow` to `LowTmcSubarray`

[1.0.0-rc.4]
************
Fixed
-----------
* Updated MCCS master Leaf Node ReleaseResources command to instruct MCCS Controller to release the resources from specific subarray
* Removed the transitional obsState RESOURCING check from SDP Subarray Leaf Node AssignResources command tracker

[1.0.0-rc.3]
************
Fixed
-----------
* Resolved SKB-732.
* Removed configure json interface(0.3) hardcoding in TMC SDP Subarray Leaf Node.


[1.0.0-rc.2]
************
Added
-----------
* Resolve SKB-672

[1.0.0-rc.1]
************
Added
-----------
* Added `domain` field in values.yaml. The domain is `low-tmc`
* Added `family` and `member` field in deviceServers of each controller leafnode device in values.yaml
* Added `family` field in deviceServers of each subarray leafnode devices in value.yaml

Updated
-----------
* Updated the TRLs of TMC low devices as per ADR-9
* ska_low/tm_central/central_node - low-tmc/central-node/0
* ska_low/tm_subarray_node/1 - low-tmc/subarray/01
* ska_low/tm_leaf_node/csp_master - low-tmc/leaf-node-csp/0
* ska_low/tm_leaf_node/sdp_master - low-tmc/leaf-node-sdp/0
* ska_low/tm_leaf_node/mccs_master - low-tmc/leaf-node-mccs/0
* ska_low/tm_leaf_node/csp_subarray01 - low-tmc/subarray-leaf-node-csp/01
* ska_low/tm_leaf_node/sdp_subarray01 - low-tmc/subarray-leaf-node-sdp/01
* ska_low/tm_leaf_node/mccs_subarray01 - low-tmc/subarray-leaf-node-mccs/01
* Updated CentralNode version to 0.18.0
* Updated MccsLeafNode version to 0.6.2
* Updated SdpLeafNode version to 0.21.0
* Updated CspLeafNode version to 0.24.0
* Updated SubarrayNode version to 0.30.0

Fixed
-----------
* Fixed event receiver in centralNode to include state and healthState subscription instead of using from common tp fix device not defined issue.


[0.20.3]
********
Added
-----------
* Updated the image of SubarrayNode to 0.27.6
* Updated the image of central node to 0.17.2
* Updated the image of Sdpleafnodes to 0.19.3
* Updated the image of CSPleafnodes to 0.23.2
* Updated the image of MCCSleafnode to 0.5.4
* Introduced error propagation and timeout for Scan /EndScan /End Commands
* Renamed the properties as required
* Made all the properties configurable
* Corrected data types of the properties wherever required
* Updated ska-tmc-subarraynode v0.29.0
* Implemented HealthState aggregation logic with AdminMode consideration (SP-4908)
* Added documentation updates for HealthState aggregation
* Included warning on `SetAdminMode` command usage

Fixed
-----------
* Fixed bug skb-525
* Fixed bug skb-658
* Fixed the RTD documentation and added documentation for all the properties of all the TMC nodes

Removed
-----------
* Removed SleepTime property and utilised properties livelinessCheckPeriod and eventSubscriptionCheck

[0.20.1]
********
Added
-----------
* Updated ska-tmc-mccsleafnodes v0.5.1 to fix SKB-627
* Resolved SKB-329
* The updated versions are as follows -
* CSPLeafNodes - 0.21.3
* Updated Subarray Node v0.26.1 to fix SKB-643 and SKB-618
* Harmonization of JSON Usage Across TMC LOW Integration Repository:
* Single Source of JSON Files: Replaced all instances of JSON files in the repository with a single source    from the TelModel repository, ensuring consistency and    easier maintenance.
* Test Case Updates: Modified test cases to reference JSON files from the TelModel repository, aligning all tests with the updated, harmonized JSON structure.
* Includes improved liveliness probe functionality
* The updated versions are as follows -
* Centralnode - 0.16.7
* SubarrayNode - 0.24.0
* Sdpleafnode - 0.17.1
* Cspleafnode - 0.5.0
* Mccsleafnode - 0.5.0

Fixed
-----------
* Fixed SKB-648

Removed
-----------
* Removal of Redundant JSON Files: Deleted duplicate JSON files from the Integration and TMC Integration repositories to reduce redundancy and improve clarity.

[0.20.0]
********
Added
-----------
* Integrate TMC CSPLeafNodes version 0.21.1 to support PST Beam Delay Calculation
* Update TMC Configure JSON to support Delay Calculation for PST Beams
* Dependency Update:
* CSPLN: v0.21.1

[0.19.0]
********
Added
-----------
* MCCS Chart Update: Utilized the latest MCCS chart v0.16.2 for enhanced functionality and stability.
* TMC-MCCS Pairwise Testing: Added test cases for Abort-Restart commands as part of TMC-MCCS pairwise integration testing but due to SKB-589 it is skipped.
* TMC-MCCS Scheme Update: Updated the TMC-MCCS scheme to include station-specific IDs, along with per-aperture handling.
* Dependency Updates:
* CSPLN: v0.19.4
* MCCSLN: v0.4.2

* Validation:
* This release validates the following tickets:
* SKB-319
* SKB-375

[0.18.0]
********
Added
-----------
* Integrate TMC SubarrayNode v0.23.1
* Obs State aggregation in subarray node is improved.
* Subarray node uses rule-engine rules to aggregate obs state.
* Integrate TMC SubarrayNode v0.23.1 to support PSS and PST as optional keys under TMC-CSP schema.
* To mitigate the dependency for PST observation to be based on having `pst` and `pss` keys (mandatory) under the TMC-CSP schema.
* As per the SKA Tel model, PSS and PST keys are not mandatory fields, considering every observation would not be around PST. The way TMC was supporting the PST observation considered these keys mandatory.
* This caused issues when the observation is not for PST.
* Changes in TMC SubarrayNode v0.23.1 handle this condition, considering PST and PSS as optional.
* Checks are added on TMC SubarrayNode to confirm the type of observation first and then send command input to CSP accordingly.


[0.20.3-rc.3]
*************
Added
-----------
* Updated ska-tmc-subarraynode v0.29.0
* Implemented HealthState aggregation logic with AdminMode consideration (SP-4908)
* Added documentation updates for HealthState aggregation
* Included warning on `SetAdminMode` command usage

[0.20.3-rc.2]
*************

Added
-----------
* Removed SleepTime property and utilised properties livelinessCheckPeriod and eventSubscriptionCheck
* Renamed the properties as required
* Made all the properties configurable
* Corrected data types of the properties wherever required

Fixed
-----------
* Fixed bug skb-658
* Fixed the RTD documentation and added documentation for all the properties of all the TMC nodes

[0.20.3-rc.1]
*************

Added
-----------
* Updated the image of SubarrayNode to 0.27.6
* Updated the image of central node to 0.17.2
* Updated the image of Sdpleafnodes to 0.19.3
* Updated the image of CSPleafnodes to 0.23.2
* Updated the image of MCCSleafnode to 0.5.4
* Introduced error propagation and timeout for Scan /EndScan /End Commands

Fixed
-----------
* Fixed bug skb-525

[0.20.2-rc.2]
*************
Fixed
-----------
* Fixed bug SKB-646 with latest subarray node image v0.27.6

[0.20.2-rc.1]
*************
Added
-----------
* Update CSPleafnodes chart to update ska-telmodel
* Updated the image of Sdpleafnodes to 0.17.3
* Updated the image of SubarrayNode to 0.26.4

Fixed
-----------
 * Fixed bug SKB-599 with latest sdp leaf node image v0.19.3
 * Fixed bug SKB-634, SKB-641
 * Fixed bug SKB-618

[0.18.1]
********
Added
-----------
* Updated Subarray Node v0.23.3 to fix SKB-512

[0.17.3]
********
Added
-----------
* Updated Subarray Node v0.22.3 to resolve SKB-477.

[0.17.2]
********
Added
-----------
* Updated Subarray Node v0.22.2 to resolve SKB-476.

[0.17.1]
********
Added
-----------
* Updated Central Node v0.16.3 and Subarray Node v0.21.4 related to SKB-438.

[0.17.0]
********
Added
-----------
* TMC Low release with base class version 1.0.0.
* Updated CentralNode: 0.16.2.
* Updated SubarrayNode: 0.21.2.
* Updated CSPLN: 0.18.2.
* Updated SDPLN: 0.16.1.
* Updated MCCSLN: 0.4.0.
* Updated the telmodel version to 1.18.2.

Fixed
-----------
* Fixed bug SKB-355.

[0.16.0]
********
Added
-----------
* REL-1557: Updated AssignResources and Configure schemas for verification as per SKA Tel Model v > 1.17.0.
* Verified TMC-MCCS interface with MCCS chart v0.13.0.
* Utilized OSO-TMC Low AssignResources v4.0 (supporting TMC-MCCS v3.0) and Configure schema v4.0 (PST observations).
* Updated CentralNode version 0.15.2 with SKA Tel Model v1.17.0 to support validations for AssignResources and ReleaseResources.
* Utilized Subarray Node version 0.19.1 with SKA Tel Model v1.18.1 to support validations for AssignResources, Configure, and Scan schema.

master
***********
Fixed
-----------
* Bug SKB-296 is fixed.
* Bug SKB-187 is fixed.

[0.15.1]
********
Added
-----------
* Updated CentralNode version to 0.15.0.
* Updated SubarrayNode version to 0.18.1 with MCCS scan command issue to fix SKB-395.
* Added "MccsScanInterfaceURL" property that can be configured during deployment to set MCCS Scan interface URL.

[0.15.0]
********
Added
-----------
* Integrated TMC SubarrayNode latest image with SKB-355 and bug fix for interface URL for CSP, SDP, and MCCS Scan and Configure commands.
* Utilized ska-csp-lmc-low v0.13.1 for SKB-355 bug verification via XTP-29657.
* Integrated TMC CspSubarrayLeafNode latest image v0.162 with SKB-329, SKB-328, and SKB-327 bug fix.
* Affected BDD test case - XTP-32140.
* Updated randomly failing test cases - TMC configure with mocks, TMC-SDP Abort in Configuring, TMC-CSP Abort in Resourcing.

[0.14.1]
********
Fixed
-----------
* Fixed SKB-300.


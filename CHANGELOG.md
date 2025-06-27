###########
Change Log
###########

All notable changes to this project will be documented in this file.
This project adheres to `Semantic Versioning <http://semver.org/>`_.

[1.2.1]
************
Updated
-------
* Retry on responsiveness check of subarraynode was implemented on 
central node and centralnode v0.19.7 was utilized to resolve SKB-860 .
* Resolved the hardcoding and utilised the  tag v0.8.1 of mccssubarrayleafnode 
to resolve bug SKB-939.

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


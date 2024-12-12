###########
Change Log
###########

All notable changes to this project will be documented in this file.
This project adheres to `Semantic Versioning <http://semver.org/>`_.

Added
-----
[0.20.1-rc.3]
* Fix bug SKB-634, SKB-641
* Update the image of SubarrayNode to 0.26.4

[0.20.1-rc.2]
* Fixed SKB-648
* Updated ska-tmc-mccsleafnodes v0.5.1 to fix SKB-627

[0.20.1-rc.1]
* Resolved SKB-329
* The updated versions are as follows - 
* CSPLeafNodes - 0.21.3
* Updated Subarray Node v0.26.1 to fix SKB-643 and SKB-618

[0.20.1-rc]
* Harmonization of JSON Usage Across TMC LOW Integration Repository:
* Single Source of JSON Files: Replaced all instances of JSON files in the repository with a single source from the TelModel repository, ensuring consistency and    easier maintenance.
* Removal of Redundant JSON Files: Deleted duplicate JSON files from the Integration and TMC Integration repositories to reduce redundancy and improve clarity.
* Test Case Updates: Modified test cases to reference JSON files from the TelModel repository, aligning all tests with the updated, harmonized JSON structure.
* Includes improved liveliness probe functionality
* The updated versions are as follows - 
* Centralnode - 0.16.7
* SubarrayNode - 0.24.0 
* Sdpleafnode - 0.17.1 
* Cspleafnode - 0.5.0
* Mccsleafnode - 0.5.0

[0.20.0]
* Integrate TMC CSPLeafNodes version 0.21.1 to support PST Beam Delay Calculation
* Update TMC Configure JSON to support Delay Calculation for PST Beams
* Dependency Update:
* CSPLN: v0.21.1

[0.19.0]
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
* Integrate TMC SubarrayNode v0.23.1
* Obs State aggregation in subarray node is improved.
* Subarray node uses rule-engine rules to aggregate obs state.
* Integrate TMC SubarrayNode v0.23.1 to support PSS and PST as optional keys under TMC-CSP schema.
* To mitigate the dependency for PST observation to be based on having `pst` and `pss` keys (mandatory) under the TMC-CSP schema.
* As per the SKA Tel model, PSS and PST keys are not mandatory fields, considering every observation would not be around PST. The way TMC was supporting the PST observation considered these keys mandatory.
* This caused issues when the observation is not for PST.
* Changes in TMC SubarrayNode v0.23.1 handle this condition, considering PST and PSS as optional. 
* Checks are added on TMC SubarrayNode to confirm the type of observation first and then send command input to CSP accordingly.

Fixed
-----
[0.18.1]
********
* Updated Subarray Node v0.23.3 to fix SKB-512

[0.17.3]
* Updated Subarray Node v0.22.3 to resolve SKB-477.

[0.17.2]
* Updated Subarray Node v0.22.2 to resolve SKB-476.

[0.17.1]
* Updated Central Node v0.16.3 and Subarray Node v0.21.4 related to SKB-438.

[0.17.0]
* TMC Low release with base class version 1.0.0.
* Updated CentralNode: 0.16.2.
* Updated SubarrayNode: 0.21.2.
* Updated CSPLN: 0.18.2.
* Updated SDPLN: 0.16.1.
* Updated MCCSLN: 0.4.0.
* Updated the telmodel version to 1.18.2.
* Fixed bug SKB-355.

[0.16.0]
* REL-1557: Updated AssignResources and Configure schemas for verification as per SKA Tel Model v > 1.17.0.
* Verified TMC-MCCS interface with MCCS chart v0.13.0.
* Utilized OSO-TMC Low AssignResources v4.0 (supporting TMC-MCCS v3.0) and Configure schema v4.0 (PST observations).
* Updated CentralNode version 0.15.2 with SKA Tel Model v1.17.0 to support validations for AssignResources and ReleaseResources.
* Utilized Subarray Node version 0.19.1 with SKA Tel Model v1.18.1 to support validations for AssignResources, Configure, and Scan schema.

[master]
* Bug SKB-296 is fixed.
* Bug SKB-187 is fixed.

[0.15.1]
* Updated CentralNode version to 0.15.0.
* Updated SubarrayNode version to 0.18.1 with MCCS scan command issue to fix SKB-395.
* Added "MccsScanInterfaceURL" property that can be configured during deployment to set MCCS Scan interface URL.

[0.15.0]
* Integrated TMC SubarrayNode latest image with SKB-355 and bug fix for interface URL for CSP, SDP, and MCCS Scan and Configure commands.
* Utilized ska-csp-lmc-low v0.13.1 for SKB-355 bug verification via XTP-29657.
* Integrated TMC CspSubarrayLeafNode latest image v0.162 with SKB-329, SKB-328, and SKB-327 bug fix.
* Affected BDD test case - XTP-32140.
* Updated randomly failing test cases - TMC configure with mocks, TMC-SDP Abort in Configuring, TMC-CSP Abort in Resourcing.

[0.14.1]
* Fixed SKB-300.

[Unreleased]
* Refactored delay model testcases to remove multiple when then statements. 

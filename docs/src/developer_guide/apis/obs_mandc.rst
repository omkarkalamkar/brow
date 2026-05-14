.. _obs_apis:

===========================
Observation Execution APIs
===========================

The observation execution can be done by following a sequence of APIs as follows:

* :ref:`Resource allocation <centralnode:assign_resources>`
* :ref:`Configure a scan <subarraynode:configure_low>`
* :ref:`Perform scan <subarraynode:scan_low>`
* :ref:`End a scan <subarraynode:end_scan_low>`
* :ref:`Resource de-allocation <centralnode:release_resources>`

Before performing any observation related operation it is necessary that the telescope is in ON state.

Additionally, monitoring of individual subarray can be done by reading/subscribing 
to the attributes exposed by various Subarray Node. Please refer to 
:ref:`Knowledge Base <knowledge_base>` > :ref:`Components <components>` > :ref:`Subarray Node <components_sn>`
for more details.


Delay Model
=================

The delay models are exposed by CSP Subarray Leaf Node in the respective 
subarray. A separate attribute is implemented for each of the beam for which 
delays are calculated. 

Following are the details of the attributes exposed for Subarray beams:

+-----------------------------+------------------------------------------------+
| **Attribute**               | **Description**                                |
+=============================+================================================+
| delayModelStationBeam01     | Delay model data for MCCS Station Beam 01.     |
|                             | Maps to `mccs.subarray_beams[0]`. Includes     |
|                             | logical bands, apertures, and sky coordinates. |
+-----------------------------+------------------------------------------------+
| delayModelStationBeam02     | Delay model data for MCCS Station Beam 02      |
|                             | (`mccs.subarray_beams[1]`).                    |
+-----------------------------+------------------------------------------------+
| delayModelStationBeam03     | Delay model data for MCCS Station Beam 03      |
|                             | (`mccs.subarray_beams[2]`).                    |
+-----------------------------+------------------------------------------------+
| delayModelStationBeam04     | Delay model data for MCCS Station Beam 04      |
|                             | (`mccs.subarray_beams[3]`).                    |
+-----------------------------+------------------------------------------------+
| delayModelStationBeam05     | Delay model data for MCCS Station Beam 05      |
|                             | (`mccs.subarray_beams[4]`).                    |
+-----------------------------+------------------------------------------------+
| delayModelStationBeam06     | Delay model data for MCCS Station Beam 06      |
|                             | (`mccs.subarray_beams[5]`).                    |
+-----------------------------+------------------------------------------------+
| delayModelStationBeam07     | Delay model data for MCCS Station Beam 07      |
|                             | (`mccs.subarray_beams[6]`).                    |
+-----------------------------+------------------------------------------------+
| delayModelStationBeam08     | Delay model data for MCCS Station Beam 08      |
|                             | (`mccs.subarray_beams[7]`).                    |
+-----------------------------+------------------------------------------------+


Following are the details of the attributes exposed for PST beams:

+-----------------------------+------------------------------------------------+
| **Attribute**               | **Description**                                |
+=============================+================================================+
| delayModelPSTBeam1          | Delay model data for PST Beam 1. Maps to       |
|                             | `csp.lowcbf.timing_beams.beams[0]`. Includes   |
|                             | station beam reference, weights, and sky field |
|                             | attributes.                                    |
+-----------------------------+------------------------------------------------+
| delayModelPSTBeam2          | Delay model data for PST Beam 2. Maps to       |
|                             | `csp.lowcbf.timing_beams.beams[1]`. Includes   |
|                             | station beam reference, weights, and sky field |
|                             | attributes.                                    |
+-----------------------------+------------------------------------------------+

Following are the details of the attributes exposed for PSS beams:

+-----------------------------+------------------------------------------------+
| **Attribute**               | **Description**                                |
+=============================+================================================+
| delayModelPSSBeam1          | Delay model data for PSS Beam 1. Maps to       |
|                             | `csp.lowcbf.search_beams.beams[0]`. Includes   |
|                             | station beam reference, weights                |
+-----------------------------+------------------------------------------------+
| delayModelPSSBeam2          | Delay model data for PSS Beam 2. Maps to       |
|                             | `csp.lowcbf.search_beams.beams[1]`. Includes   |
|                             | station beam reference, weights                |
+-----------------------------+------------------------------------------------+
| delayModelPSSBeamN          | Similarly, Delay model data for PSS Beam N.    |
|                             | Maps to `csp.lowcbf.search_beams.beams[N-1]`.  |
|                             | Includes station beam reference, weights.      |
|                             | **Here N can range from 1 to 30 (TMC supports  |
|                             | upto 30 pss beams currently)**                 |
+-----------------------------+------------------------------------------------+
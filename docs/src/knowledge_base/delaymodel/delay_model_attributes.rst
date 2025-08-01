.. _delay_model_attributes:

Delay Model Attributes
----------------------

The delay model attributes are a crucial part of observation execution in SKA-Low, allowing precise configuration and alignment of beams across multiple subsystems. These attributes are passed through nested JSON in the `Configure` command to the TMC, which forwards them to MCCS and CSP.

In the current implementation, the system supports **multiple station beams** and **multiple PST beams**, each with their own configuration fields.

+-----------------------------+--------------------------------------------------------------------------+
| **Attribute**               | **Description**                                                          |
+=============================+==========================================================================+
| delayModelStationBeam01     | Delay model data for MCCS Station Beam 01. Maps to                       |
|                             | `mccs.subarray_beams[0]`. Includes logical bands, apertures, and sky     |
|                             | coordinates.                                                             |
+-----------------------------+--------------------------------------------------------------------------+
| delayModelStationBeam02     | Delay model data for MCCS Station Beam 02 (`mccs.subarray_beams[1]`).    |
+-----------------------------+--------------------------------------------------------------------------+
| delayModelStationBeam03     | Delay model data for MCCS Station Beam 03 (`mccs.subarray_beams[2]`).    |
+-----------------------------+--------------------------------------------------------------------------+
| delayModelStationBeam04     | Delay model data for MCCS Station Beam 04 (`mccs.subarray_beams[3]`).    |
+-----------------------------+--------------------------------------------------------------------------+
| delayModelPSTBeam1          | Delay model data for CSP PST Beam 1. Maps to                             |
|                             | `csp.lowcbf.timing_beams.beams[0]`. Includes station beam reference,     |
|                             | weights, and sky field attributes.                                       |
+-----------------------------+--------------------------------------------------------------------------+
| delayModelPSTBeam2          | Delay model data for CSP PST Beam 2 (`csp.lowcbf.timing_beams.beams[1]`).|
+-----------------------------+--------------------------------------------------------------------------+

How These Attributes Are Used
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

These attributes are used during the **observation lifecycle**, primarily through the `Configure` API, as described below:

**1. During Configure:**

You include the station beam definitions (`delayModelStationBeamXX`) and PST beam setups (`delayModelPSTBeamX`) as part of the JSON passed in the `Configure` command. This allows updating or refining the beamforming and pointing setup after resource assignment.

Example use in `Configure`:

.. literalinclude:: examples/configure_delay_model.json
   :language: json
   :linenos:


**2. Output After Configuration:**

The output JSON (typically published on the result attributes) includes calculated or confirmed delay model settings.

Example Output (Station Beam and PST Beam):

.. literalinclude:: examples/subscription_points_output.json
   :language: json
   :linenos:

**Telmodel validation**: `SKA CSP Delay Model Schema <https://developer.skao.int/projects/ska-telmodel/en/latest/schemas/csp/low/delaymodel/ska-csp-low-delaymodel-1.1.html>`_


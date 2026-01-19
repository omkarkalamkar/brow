.. _delay_model_calculations:

Delay Model Calculations
=========================

The TMC is responsible for calculation and distribution of the delay models 
during the observations execution. TMC calculates delay models for 3 types of 
beams. These are:

* Subarray a.k.a station beams
* Pulsar Timing (PST) beams
* Pulsar search (PSS) beams

The delay model calculations are done separately for each of the subarray. As 
per TMC architecture, the CSP Subarray Leaf Node is responsible for 
calculating all types of delay models within the subarray. The delay 
calculations are performed in a separate subprocess running under the CSP 
Subarray Leaf Node. The calculation is triggrred as part of processing the 
`Configure` command. The calculation is stopped as part of processing the 
`End` command.


Subarray/ Station beams delay model
------------------------------------

This delay model is calculated for each station or substation in the subarray. 
As of now, the terms station beam and subarray beam are interchangable. 
This is because the mapping between a station beam and a subarray beam is 1:1
in current implementation of MCCS. Please refer MCCS documentation for more 
details.
The contents of the delay model are:

* Subarray id
* Configuration id
* Timestamp from which the delay model is valid
* Validity period of the delays in seconds.
* Cadence of delay model generation in seconds
* For each station and/or substation

  * Station id
  * Substation id
  * Coefficients of 5th order x ploynomial
  * Offset of y ploynomial (in nanoseconds. Currently hard coded to 0.0)


.. note:: Currently TMC supports 8 subarray beams per subarray. Please refer
   :ref:`Observation Execution APIs <obs_apis>` section for the specific 
   details of the APIs.

PST beams delay model
----------------------

This delay model is calculated for each of the PST beam assigned to a subarray.
The contents of the delay model are:

* Subarray id
* Configuration id
* Timestamp from which the delay model is valid
* Validity period of the delays in seconds.
* Cadence of delay model generation in seconds
* For each station and/or substation

  * Station id
  * Coefficients of 5th order x ploynomial
  * Offset of y ploynomial (in nanoseconds. Currently hard coded to 0.0)

.. note:: Currently TMC supports two PST beams per subarray. Please refer 
   :ref:`Observation Execution APIs <obs_apis>` section for the specific 
   details of the APIs.

.. note:: The 'field' key section with "c1 & c2" are required under timing beams -> beams for PST beams delay generation.

PSS beams delay model
----------------------

This delay model is calculated for each of the PSS beam assigned to a subarray.
The contents of the delay model are:

* Subarray id
* Configuration id
* Timestamp from which the delay model is valid
* Validity period of the delays in seconds.
* Cadence of delay model generation in seconds
* For each station and/or substation

  * Station id
  * Coefficients of 5th order x ploynomial
  * Offset of y ploynomial (in nanoseconds. Currently hard coded to 0.0)

.. note:: Currently TMC supports 30 PSS beams per subarray. Please refer 
   :ref:`Observation Execution APIs <obs_apis>` section for the specific 
   details of the APIs.

.. note:: In order to publish **PSS Delay polynomial** the **"beam"** key is required with "ra" and "dec" keys in all the PSS beams data

Delay model Format
====================

The delay model is provided in the form of JSON string.
The primary consumers of the delay models are CBF, PST and PSS devices. It is 
also expected that the delays models should be available to anyone who wants 
for monitoring or any other purpose. Thus, the delay models are exposed in the 
form of Tango attributes. These attribute publish the delay model as a json 
string. Any interested consumer can subscribe to the change events of thse
attributes.

.. jsonschema:: https://ska-telescope.gitlab.io/ska-telmodel/json_schema/ska-low-csp-delaymodel/1.1
   :lift_definitions:
   :auto_reference:

Following example shows a subarray beam delay model:

.. literalinclude:: examples/station_delay_model.json
   :language: json
   :linenos:

Following example shows a PST beam delay model:

.. literalinclude:: examples/pst_delay_model.json
   :language: json
   :linenos:


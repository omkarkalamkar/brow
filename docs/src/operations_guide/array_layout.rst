.. _`Applying Array Layout Through TMC`:

==========================================
 Apply Array Layout Through TMC
==========================================

Overview
--------
 
This document explains how TMC Low manages and applies the Array Layout configuration.
This capability allows the  TMC to manage, validate,  
and distribute layout data across all subarrays and leaf nodes.

The Array Layout handling begins during the **AssignResources** process, where it  
includes a ``telmodel`` section specifying the source and path of the layout data.  
The SubarrayNode retrieves this reference, downloads and validates the layout,  
and later passes the processed data inline to the CSP leaf nodes during the **Configure** step.  


Central Node
------------

The **Central Node** manages the default and active Array Layout configurations used across the TMC.  
It defines and maintains the reference to the array layout data that will be applied by SubarrayNodes during resource assignment and configuration.

**Command:**  
``AssignResources(payload)``

Two attributes are introduced for this purpose:

- **DefaultArrayLayoutURL**

  Specifies the default array layout source and path to be used when the system starts, or when no specific layout is provided.  
  This ensures that the Central Node always has a valid reference to a baseline layout configuration.

- **ArrayLayoutURL**

  Indicates the current array layout configuration actively in use.  
  This attribute can be updated dynamically when new resources are assigned, allowing operational flexibility without requiring a restart or redeployment.

When the **AssignResources** command is executed, the Central Node checks whether the request includes a custom array layout reference. 
If a `telmodel` section is provided in the request, the Central Node updates its **ArrayLayoutURL** with the new layout information.  
If no `telmodel` data is specified, the **DefaultArrayLayoutURL** is used instead.

Using the AssignResources command on the Central Node, with the telmodel section included in the JSON payload (as shown in the example), the Array Layout can be applied to leaf nodes.

**Example AssignResources JSON**

The example below shows ``telmodel`` section in the AssignResources payload for the Central Node:

.. code-block:: json

    {
    "interface": "https://schema.skao.int/ska-low-tmc-assignresources/4.3",
    "transaction_id": "txn-....-00001",
    "subarray_id": 1,
    "telmodel": {
        "source_uris": [
          "gitlab://gitlab.com/ska-telescope/ska-telmodel-data?main#tmdata"
        ],
        "array_layout_path": "instrument/ska1_low/layout/low-layout.json"
      },
    "mccs": {
      "interface": "https://schema.skao.int/ska-low-mccs-controller-allocate/3.0",
      "subarray_beams": [
        {
          "subarray_beam_id": 1,
          "apertures": [
            {
              "station_id": 1,
              "aperture_id": "AP001.01"
              
            }
            
          ],
          "number_of_channels": 8
          
        }
        
      ]
      
    },
    "csp": {
      "pss": {
        "pss_beam_ids": [
          1,
          2,
          3
        ]
      },
      "pst": {
        "pst_beam_ids": [
          1
        ]
      }
      
    },
    "sdp": {
      "interface": "https://schema.skao.int/ska-sdp-assignres/0.4",
      "resources": {
        "receptors": [
          "SKA001",
          "SKA002",
          "SKA003",
          "SKA004"
        ],
        "receive_nodes": 1
        
      },
      "execution_block": {
        "eb_id": "eb-test-20220916-00000",
        "context": {
          
        },
        "max_length": 3600.0,
        "beams": [
          {
            "beam_id": "vis0",
            "function": "visibilities"
          }
        ],
        "scan_types": [
          {
            "scan_type_id": ".default",
            "beams": {
              "vis0": {
                "channels_id": "vis_channels",
                "polarisations_id": "all"
                
              }
            }
            
          },
          {
            "scan_type_id": "target:a",
            "derive_from": ".default",
            "beams": {
              "vis0": {
                "field_id": "field_a"
              }
            }
            
          },
          {
            "scan_type_id": "calibration:b",
            "derive_from": ".default",
            "beams": {
              "vis0": {
                "field_id": "field_b"
              }
            }
            
          }
          
        ],
        "channels": [
          {
            "channels_id": "vis_channels",
            "spectral_windows": [
              {
                "spectral_window_id": "fsp_1_channels",
                "count": 4,
                "start": 0,
                "stride": 2,
                "freq_min": 350000000.0,
                "freq_max": 368000000.0,
                "link_map": [
                  [
                    0,
                    0
                  ],
                  [
                    200,
                    1
                  ],
                  [
                    744,
                    2
                  ],
                  [
                    944,
                    3
                  ]
                ]
                
              }
            ]
            
          }
        ],
        "polarisations": [
          {
            "polarisations_id": "all",
            "corr_type": [
              "XX",
              "XY",
              "YX",
              "YY"
            ]
            
          }
        ],
        "fields": [
          {
            "field_id": "field_a",
            "phase_dir": {
              "ra": [
                123.0
              ],
              "dec": [
                -60.0
              ],
              "reference_time": "...",
              "reference_frame": "ICRF3"
              
            },
            "pointing_fqdn": "..."
            
          },
          {
            "field_id": "field_b",
            "phase_dir": {
              "ra": [
                123.0
              ],
              "dec": [
                -60.0
              ],
              "reference_time": "...",
              "reference_frame": "ICRF3"
              
            },
            "pointing_fqdn": "..."
            
          }
          
        ]
        
      },
      "processing_blocks": [
        {
          "pb_id": "pb-test-20220916-00000",
          "script": {
            "kind": "realtime",
            "name": "test-receive-addresses",
            "version": "0.7.1"
            
          },
          "sbi_ids": [
            "sbi-mvp01-20210623-00000"
          ],
          "parameters": {
            
          }
          
        }
      ]
      
    }
    
  }


Subarray Node
-------------

The **SubarrayNode** manages the download, validation, and distribution of the Array Layout data.

When the **AssignResources** command is received, the SubarrayNode extracts the **Array Layout URI** provided.  
It then downloads the layout data from the specified TelModel source and stores the URI in a memorized attribute (**arrayLayoutUri**) to ensure persistence across restarts.

Once the layout is successfully downloaded and validated, it becomes available for later configuration steps.  
During the **Configure** phase, the SubarrayNode retrieves the validated Array Layout data and sends it inline to its connected leaf nodes, ensuring each element of the subarray (CSP Subarray) receives the correct layout information.

CSP Subarray Leaf Node
----------------------

The **CSP Subarray Leaf Node** also receives the validated Array Layout data inline within the **Configure**  sent from the SubarrayNode.  

Upon receiving the configuration, the CSP Subarray Leaf Node parses the layout data and uses it to perform **delay calculations**.  

If the CSP Leaf Node encounters any issues while applying the layout, it maintains the last successfully applied configuration and reports an error to the TMC.  


Persistence and Restart Behavior
--------------------------------

Both **Central Node** and **Subarray Node** persist their `ArrayLayoutdata` attributes.

- On restart, these values are automatically reloaded.
- No new **AssignResources** call is needed after restart.
- **ReleaseResources** does not clear these values; they remain until overwritten.

References
----------

For detailed design and implementation notes, refer to:  
`Spike HM-749: Implementation Details for Array Layout <https://confluence.skatelescope.org/display/SWSI/Spike+-+HM-749+%3A++Implementation+Details+for+Array+Layout>`_
Feature: Multi-subarray observation plans

  # This file stores named resource allocation plans used by `tmc_observation.feature`.
  #
  # Each plan is provided as a JSON document inside a docstring so it can be
  # retrieved and parsed by step implementations.
  #
  # A plan maps subarray id (as a string) to beam allocations:
  # - station_beams: list of {id, stations}
  # - pss_beams:     list of {id, stations}
  # - pst_beams:     list of {id, stations}

  Scenario: PlanA
    """
    {
      
        "station_beams": [
          {"id": 1, "stations": [1, 2, 3,4,5,6]},
          {"id": 2, "stations": [1, 2, 3,4,5,6]},
          {"id": 3, "stations": [1, 2, 3,4,5,6]},
          {"id": 4, "stations": [1, 2, 3,4,5,6]},
          {"id": 5, "stations": [1, 2, 3,4,5,6]},
          {"id": 6, "stations": [1, 2, 3,4,5,6]},
          {"id": 7, "stations": [1, 2, 3,4,5,6]},
          {"id": 8, "stations": [1, 2, 3,4,5,6]}
          
        ],
        "pss_beams": [{"id": 1, "stations": [3, 4]}],
        "pst_beams": [{"id": 1, "stations": [1, 2]},{"id": 2, "stations": [5, 6]}
        
        ]
      
    }
    """

  Scenario: PlanB
    """
    {
        "station_beams": [{"id": 3, "stations": [14, 15, 16]}],
        "pss_beams": [{"id": 3, "stations": [4, 5, 6]}],
        "pst_beams": []
    }
    """

  Scenario: PlanC
    """
    {
       "station_beams": [{"id": 2, "stations": [17, 18]}],
        "pss_beams": [],
        "pst_beams": [{"id": 2, "stations": [7, 8]}]
    }
    """

  Scenario: PlanD
    """
    {
        "station_beams": [{"id": 3, "stations": [17, 18]}],
        "pss_beams": [{"id": 3, "stations": [9, 10, 11, 12]}],
        "pst_beams": []
    }
    """


      Scenario: PlanA1
    """
    {
      
        "station_beams": [
          {"id": 1, "stations": [1, 2, 3,4,5,6]},
          {"id": 2, "stations": [1, 2, 3,4,5,6]},
          {"id": 3, "stations": [1, 2, 3,4,5,6]},
          {"id": 4, "stations": [1, 2, 3,4,5,6]},
          {"id": 5, "stations": [1, 2, 3,4,5,6]},
          {"id": 6, "stations": [1, 2, 3,4,5,6]},
          {"id": 7, "stations": [1, 2, 3,4,5,6]},
          {"id": 8, "stations": [1, 2, 3,4,5,6]}
          
        ],
        "pss_beams": [{"id": 2, "stations": [3, 4]}],
        "pst_beams": [{"id": 1, "stations": [1, 2]},{"id": 2, "stations": [5, 6]}
        
        ]
      
    }
    """


      Scenario: PlanA2
    """
    {
      
        "station_beams": [
          {"id": 1, "stations": [1, 2, 3,4,5,6]},
          {"id": 2, "stations": [1, 2, 3,4,5,6]},
          {"id": 3, "stations": [1, 2, 3,4,5,6]},
          {"id": 4, "stations": [1, 2, 3,4,5,6]},
          {"id": 5, "stations": [1, 2, 3,4,5,6]},
          {"id": 6, "stations": [1, 2, 3,4,5,6]},
          {"id": 7, "stations": [1, 2, 3,4,5,6]},
          {"id": 8, "stations": [1, 2, 3,4,5,6]}
          
        ],
        "pss_beams": [{"id": 3, "stations": [3, 4]}],
        "pst_beams": [{"id": 1, "stations": [1, 2]},{"id": 2, "stations": [5, 6]}
        
        ]
      
    }
    """


      Scenario: PlanA3
    """
    {
      
        "station_beams": [
          {"id": 1, "stations": [1, 2, 3,4,5,6]},
          {"id": 2, "stations": [1, 2, 3,4,5,6]},
          {"id": 3, "stations": [1, 2, 3,4,5,6]},
          {"id": 4, "stations": [1, 2, 3,4,5,6]},
          {"id": 5, "stations": [1, 2, 3,4,5,6]},
          {"id": 6, "stations": [1, 2, 3,4,5,6]},
          {"id": 7, "stations": [1, 2, 3,4,5,6]},
          {"id": 8, "stations": [1, 2, 3,4,5,6]}
          
        ],
        "pss_beams": [{"id": 4, "stations": [3, 4]}],
        "pst_beams": [{"id": 1, "stations": [1, 2]},{"id": 2, "stations": [5, 6]}
        
        ]
      
    }
    """

      Scenario: PlanA4
    """
    {
      
        "station_beams": [
          {"id": 1, "stations": [1, 2, 3,4,5,6]},
          {"id": 2, "stations": [1, 2, 3,4,5,6]},
          {"id": 3, "stations": [1, 2, 3,4,5,6]},
          {"id": 4, "stations": [1, 2, 3,4,5,6]},
          {"id": 5, "stations": [1, 2, 3,4,5,6]},
          {"id": 6, "stations": [1, 2, 3,4,5,6]},
          {"id": 7, "stations": [1, 2, 3,4,5,6]},
          {"id": 8, "stations": [1, 2, 3,4,5,6]}
          
        ],
        "pss_beams": [{"id": 5, "stations": [3, 4]}],
        "pst_beams": [{"id": 1, "stations": [1, 2]},{"id": 2, "stations": [5, 6]}
        
        ]
      
    }
    """

      Scenario: PlanA5
    """
    {
      
        "station_beams": [
          {"id": 1, "stations": [1, 2, 3,4,5,6]},
          {"id": 2, "stations": [1, 2, 3,4,5,6]},
          {"id": 3, "stations": [1, 2, 3,4,5,6]},
          {"id": 4, "stations": [1, 2, 3,4,5,6]},
          {"id": 5, "stations": [1, 2, 3,4,5,6]},
          {"id": 6, "stations": [1, 2, 3,4,5,6]},
          {"id": 7, "stations": [1, 2, 3,4,5,6]},
          {"id": 8, "stations": [1, 2, 3,4,5,6]}
          
        ],
        "pss_beams": [{"id": 6, "stations": [3, 4]}],
        "pst_beams": [{"id": 1, "stations": [1, 2]},{"id": 2, "stations": [5, 6]}
        
        ]
      
    }
    """


      Scenario: PlanA6
    """
    {
      
        "station_beams": [
          {"id": 1, "stations": [1, 2, 3,4,5,6]},
          {"id": 2, "stations": [1, 2, 3,4,5,6]},
          {"id": 3, "stations": [1, 2, 3,4,5,6]},
          {"id": 4, "stations": [1, 2, 3,4,5,6]},
          {"id": 5, "stations": [1, 2, 3,4,5,6]},
          {"id": 6, "stations": [1, 2, 3,4,5,6]},
          {"id": 7, "stations": [1, 2, 3,4,5,6]},
          {"id": 8, "stations": [1, 2, 3,4,5,6]}
          
        ],
        "pss_beams": [{"id": 7, "stations": [3, 4]}],
        "pst_beams": [{"id": 1, "stations": [1, 2]},{"id": 2, "stations": [5, 6]}
        
        ]
      
    }
    """


      Scenario: PlanA7
    """
    {
      
        "station_beams": [
          {"id": 1, "stations": [1, 2, 3,4,5,6]},
          {"id": 2, "stations": [1, 2, 3,4,5,6]},
          {"id": 3, "stations": [1, 2, 3,4,5,6]},
          {"id": 4, "stations": [1, 2, 3,4,5,6]},
          {"id": 5, "stations": [1, 2, 3,4,5,6]},
          {"id": 6, "stations": [1, 2, 3,4,5,6]},
          {"id": 7, "stations": [1, 2, 3,4,5,6]},
          {"id": 8, "stations": [1, 2, 3,4,5,6]}
          
        ],
        "pss_beams": [{"id": 8, "stations": [3, 4]}],
        "pst_beams": [{"id": 1, "stations": [1, 2]},{"id": 2, "stations": [5, 6]}
        
        ]
      
    }
    """


      Scenario: PlanA8
    """
    {
      
        "station_beams": [
          {"id": 1, "stations": [1, 2, 3,4,5,6]},
          {"id": 2, "stations": [1, 2, 3,4,5,6]},
          {"id": 3, "stations": [1, 2, 3,4,5,6]},
          {"id": 4, "stations": [1, 2, 3,4,5,6]},
          {"id": 5, "stations": [1, 2, 3,4,5,6]},
          {"id": 6, "stations": [1, 2, 3,4,5,6]},
          {"id": 7, "stations": [1, 2, 3,4,5,6]},
          {"id": 8, "stations": [1, 2, 3,4,5,6]},
          {"id": 9, "stations": [1, 2, 3,4,5,6]}
          
        ],
        "pss_beams": [{"id": 9, "stations": [3, 4]}],
        "pst_beams": [{"id": 1, "stations": [1, 2]},{"id": 2, "stations": [5, 6]}
        
        ]
      
    }
    """


      Scenario: PlanA9
    """
    {
      
        "station_beams": [
          {"id": 1, "stations": [1, 2, 3,4,5,6]},
          {"id": 2, "stations": [1, 2, 3,4,5,6]},
          {"id": 3, "stations": [1, 2, 3,4,5,6]},
          {"id": 4, "stations": [1, 2, 3,4,5,6]},
          {"id": 5, "stations": [1, 2, 3,4,5,6]},
          {"id": 6, "stations": [1, 2, 3,4,5,6]},
          {"id": 7, "stations": [1, 2, 3,4,5,6]},
          {"id": 8, "stations": [1, 2, 3,4,5,6]}.
          {"id": 10, "stations": [1, 2, 3,4,5,6]}
          
        ],
        "pss_beams": [{"id": 10, "stations": [3, 4]}],
        "pst_beams": [{"id": 1, "stations": [1, 2]},{"id": 2, "stations": [5, 6]}
        
        ]
      
    }
    """


      Scenario: PlanA10
    """
    {
      
        "station_beams": [
          {"id": 1, "stations": [1, 2, 3,4,5,6]},
          {"id": 2, "stations": [1, 2, 3,4,5,6]},
          {"id": 3, "stations": [1, 2, 3,4,5,6]},
          {"id": 4, "stations": [1, 2, 3,4,5,6]},
          {"id": 5, "stations": [1, 2, 3,4,5,6]},
          {"id": 6, "stations": [1, 2, 3,4,5,6]},
          {"id": 7, "stations": [1, 2, 3,4,5,6]},
          {"id": 8, "stations": [1, 2, 3,4,5,6]},
          {"id": 11, "stations": [1, 2, 3,4,5,6]}
          
        ],
        "pss_beams": [{"id": 11, "stations": [3, 4]}],
        "pst_beams": [{"id": 1, "stations": [1, 2]},{"id": 2, "stations": [5, 6]}
        
        ]
      
    }
    """


      Scenario: PlanA11
    """
    {
      
        "station_beams": [
          {"id": 1, "stations": [1, 2, 3,4,5,6]},
          {"id": 2, "stations": [1, 2, 3,4,5,6]},
          {"id": 3, "stations": [1, 2, 3,4,5,6]},
          {"id": 4, "stations": [1, 2, 3,4,5,6]},
          {"id": 5, "stations": [1, 2, 3,4,5,6]},
          {"id": 6, "stations": [1, 2, 3,4,5,6]},
          {"id": 7, "stations": [1, 2, 3,4,5,6]},
          {"id": 12, "stations": [1, 2, 3,4,5,6]}
          
        ],
        "pss_beams": [{"id": 12, "stations": [3, 4]}],
        "pst_beams": [{"id": 1, "stations": [1, 2]},{"id": 2, "stations": [5, 6]}
        
        ]
      
    }
    """


      Scenario: PlanA12
    """
    {
      
        "station_beams": [
          {"id": 1, "stations": [1, 2, 3,4,5,6]},
          {"id": 2, "stations": [1, 2, 3,4,5,6]},
          {"id": 3, "stations": [1, 2, 3,4,5,6]},
          {"id": 4, "stations": [1, 2, 3,4,5,6]},
          {"id": 5, "stations": [1, 2, 3,4,5,6]},
          {"id": 6, "stations": [1, 2, 3,4,5,6]},
          {"id": 7, "stations": [1, 2, 3,4,5,6]},
          {"id": 8, "stations": [1, 2, 3,4,5,6]}
          
        ],
        "pss_beams": [{"id": 13, "stations": [3, 4]}],
        "pst_beams": [{"id": 1, "stations": [1, 2]},{"id": 2, "stations": [5, 6]}
        
        ]
      
    }
    """


      Scenario: PlanA13
    """
    {
      
        "station_beams": [
          {"id": 1, "stations": [1, 2, 3,4,5,6]},
          {"id": 2, "stations": [1, 2, 3,4,5,6]},
          {"id": 3, "stations": [1, 2, 3,4,5,6]},
          {"id": 4, "stations": [1, 2, 3,4,5,6]},
          {"id": 5, "stations": [1, 2, 3,4,5,6]},
          {"id": 6, "stations": [1, 2, 3,4,5,6]},
          {"id": 7, "stations": [1, 2, 3,4,5,6]},
          {"id": 8, "stations": [1, 2, 3,4,5,6]}
          
        ],
        "pss_beams": [{"id": 14, "stations": [3, 4]}],
        "pst_beams": [{"id": 1, "stations": [1, 2]},{"id": 2, "stations": [5, 6]}
        
        ]
      
    }
    """


      Scenario: PlanA14
    """
    {
      
        "station_beams": [
          {"id": 1, "stations": [1, 2, 3,4,5,6]},
          {"id": 2, "stations": [1, 2, 3,4,5,6]},
          {"id": 3, "stations": [1, 2, 3,4,5,6]},
          {"id": 4, "stations": [1, 2, 3,4,5,6]},
          {"id": 5, "stations": [1, 2, 3,4,5,6]},
          {"id": 6, "stations": [1, 2, 3,4,5,6]},
          {"id": 7, "stations": [1, 2, 3,4,5,6]},
          {"id": 8, "stations": [1, 2, 3,4,5,6]}
          
        ],
        "pss_beams": [{"id": 15, "stations": [3, 4]}],
        "pst_beams": [{"id": 1, "stations": [1, 2]},{"id": 2, "stations": [5, 6]}
        
        ]
      
    }
    """


      Scenario: PlanA15
    """
    {
      
        "station_beams": [
          {"id": 1, "stations": [1, 2, 3,4,5,6]},
          {"id": 2, "stations": [1, 2, 3,4,5,6]},
          {"id": 3, "stations": [1, 2, 3,4,5,6]},
          {"id": 4, "stations": [1, 2, 3,4,5,6]},
          {"id": 5, "stations": [1, 2, 3,4,5,6]},
          {"id": 6, "stations": [1, 2, 3,4,5,6]},
          {"id": 7, "stations": [1, 2, 3,4,5,6]},
          {"id": 8, "stations": [1, 2, 3,4,5,6]}
          
        ],
        "pss_beams": [{"id": 16, "stations": [3, 4]}],
        "pst_beams": [{"id": 1, "stations": [1, 2]},{"id": 2, "stations": [5, 6]}
        
        ]
      
    }
    """


      Scenario: PlanA16
    """
    {
      
        "station_beams": [
          {"id": 1, "stations": [1, 2, 3,4,5,6]},
          {"id": 2, "stations": [1, 2, 3,4,5,6]},
          {"id": 3, "stations": [1, 2, 3,4,5,6]},
          {"id": 4, "stations": [1, 2, 3,4,5,6]},
          {"id": 5, "stations": [1, 2, 3,4,5,6]},
          {"id": 6, "stations": [1, 2, 3,4,5,6]},
          {"id": 7, "stations": [1, 2, 3,4,5,6]},
          {"id": 8, "stations": [1, 2, 3,4,5,6]}
          
        ],
        "pss_beams": [{"id": 17, "stations": [3, 4]}],
        "pst_beams": [{"id": 1, "stations": [1, 2]},{"id": 2, "stations": [5, 6]}
        
        ]
      
    }
    """

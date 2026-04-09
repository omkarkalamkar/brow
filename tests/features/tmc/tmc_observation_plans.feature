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

  # This scenario checks if TMC is able to process 8 subarry beams,
  #  1 PSS beam and 2 PST beams
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
  #This scenarion checks TMC SN is able to process only PSS observations
  Scenario: PlanB
    """
    {
        "station_beams": [{"id": 1, "stations": [14, 15, 16]}],
        "pss_beams": [{"id": 3, "stations": [14, 15, 16]}],
        "pst_beams": []
    }
    """
  #This scenario checks TMC SN is able to process only PST observations
  Scenario: PlanC
    """
    {
       "station_beams": [{"id": 1, "stations": [17, 18]}],
        "pss_beams": [],
        "pst_beams": [{"id": 2, "stations": [7, 8]}]
    }


    """

    #This scenario checks if TMC is able to process 4 subarry beams,
    #1 PSS beam and 2 PST beams
      Scenario: PlanD
    """
    {
      
        "station_beams": [
          {"id": 1, "stations": [1, 2, 3,4,5,6]},
          {"id": 2, "stations": [1, 2, 3,4,5,6]},
          {"id": 3, "stations": [1, 2, 3,4,5,6]},
          {"id": 4, "stations": [1, 2, 3,4,5,6]}
          
          
        ],
        "pss_beams": [{"id": 25, "stations": [3, 4]}],
        "pst_beams": [{"id": 1, "stations": [1, 2]},{"id": 2, "stations": [5, 6]}
        
        ]
      
    }
    """

    

    #This scenario checks if TMC is able to process 4 subarry beams,
    #2 PSS beam and 2 PST beams
      Scenario: PlanE
    """
    {
      
        "station_beams": [
          {"id": 1, "stations": [1, 2, 3,4,5,6]},
          {"id": 2, "stations": [1, 2, 3,4,5,6]},
          {"id": 3, "stations": [1, 2, 3,4,5,6]},
          {"id": 4, "stations": [1, 2, 3,4,5,6]}
          
          
        ],
        "pss_beams": [{"id": 5, "stations": [3, 4]}],
        "pst_beams": [{"id": 1, "stations": [1, 2]},{"id": 2, "stations": [5, 6]}
        
        ]
      
    }
    """

    #This scenario checks if TMC is able to process 8 subarry beams,
    #1 PSS beam and 2 PST beams
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

    #This scenario checks if TMC is able to process 8 subarry beams,
    #1 PSS beam and 2 PST beams and PSS and PST beams do not share stations
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
    #This scenario checks if TMC is able to process 8 subarry beams,
    #1 PSS beam and 2 PST beams and PSS and PST beams do not share stations
    


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
    #This scenario checks if TMC is able to process 8 subarry beams,
    #1 PSS beam and 2 PST beams and PSS and PST beams do not share stations
    #Also staion beams do no share staions with PSS and PST beams
    #Note - This is not working currently 
    

      Scenario: PlanA4
    """
    {
      
        "station_beams": [
          {"id": 1, "stations": [11, 12, 13,14,15,16]},
          {"id": 2, "stations": [11, 12, 13,14,15,16]},
          {"id": 3, "stations": [11, 12, 13,14,15,16]},
          {"id": 4, "stations": [11, 12, 13,14,15,16]},
          {"id": 5, "stations": [11, 12, 13,14,15,16]},
          {"id": 6, "stations": [11, 12, 13,14,15,16]},
          {"id": 7, "stations": [11, 12, 13,14,15,16]},
          {"id": 8, "stations": [11, 12, 13,14,15,16]}
          
        ],
        "pss_beams": [{"id": 5, "stations": [3, 4]}],
        "pst_beams": [{"id": 1, "stations": [1, 2]},{"id": 2, "stations": [5, 6]}
        
        ]
      
    }
    """

    #This scenario checks if TMC is able to process 5 subarry beams,
    #1 PSS beam and 2 PST beams and PSS and PST beams do not share stations
   
    

      Scenario: PlanA5
    """
    {
      
        "station_beams": [
          {"id": 1, "stations": [1, 2, 3,4,5,6]},
          {"id": 2, "stations": [1, 2, 3,4,5,6]},
          {"id": 3, "stations": [1, 2, 3,4,5,6]},
          {"id": 4, "stations": [1, 2, 3,4,5,6]},
          {"id": 5, "stations": [1, 2, 3,4,5,6]}
          
          
        ],
        "pss_beams": [{"id": 6, "stations": [3, 4]}],
        "pst_beams": [{"id": 1, "stations": [1, 2]},{"id": 2, "stations": [5, 6]}
        
        ]
      
    }
    """
    #This scenario checks if TMC is able to process 8 subarry beams,
    #3 PSS beam and 2 PST beams and PSS and PST beams do not share stations
   

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
        "pss_beams": [{"id": 7, "stations": [3, 4]} , {"id": 21, "stations": [3, 4]} , {"id": 22, "stations": [13, 14]}],
        "pst_beams": [{"id": 1, "stations": [1, 2]},{"id": 2, "stations": [5, 6]}
        
        ]
      
    }
    """

    #This scenario checks if TMC is able to process 8 subarry beams,
    #3 PSS beam and 2 PST beams and PSS and PST beams  share all stations
   


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
        "pss_beams": [{"id": 20, "stations": [3, 4]} , {"id": 21, "stations": [3, 4]} , {"id": 22, "stations": [3, 4]}],
        "pst_beams": [{"id": 1, "stations": [3, 4]},{"id": 2, "stations": [3, 4]}
        
        ]
      
    }
    """
    #This scenario checks if TMC is able to process 8 subarry beams,
    #1 PSS beam and 2 PST beams and all beams operate from 1 single station
    

      Scenario: PlanA8
    """
    {
      
        "station_beams": [
          {"id": 1, "stations": [1]},
          {"id": 2, "stations": [1]},
          {"id": 3, "stations": [1]},
          {"id": 4, "stations": [1]},
          {"id": 5, "stations": [1]},
          {"id": 6, "stations": [1]},
          {"id": 7, "stations": [1]},
          {"id": 8, "stations": [1]}
         
          
        ],
        "pss_beams": [{"id": 9, "stations": [1]}],
        "pst_beams": [{"id": 1, "stations": [1]},{"id": 2, "stations": [1]}
        
        ]
      
    }
    """
    #This scenario checks if TMC is able to process 3 subarry beams,
    #1 PSS beam and 1 PST beams and PSS and PST beams do not share  stations
   

      Scenario: PlanA9
    """
    {
      
        "station_beams": [
          {"id": 1, "stations": [1, 2, 3,4,5,6]},
          {"id": 2, "stations": [1, 2, 3,4,5,6]},
          {"id": 3, "stations": [1, 2, 3,4,5,6]}
        
          
          
        ],
        "pss_beams": [{"id": 10, "stations": [4]}],
        "pst_beams": [{"id": 1, "stations": [1, 2]},{"id": 2, "stations": [5, 6]}
        
        ]
      
    }
    """
    #This scenario checks if TMC is able to process 4 subarry beams,
    #1 PSS beam and 1 PST beams and PSS and PST beams  share all stations
   

      Scenario: PlanA10
    """
    {
      
        "station_beams": [
          {"id": 1, "stations": [1, 2, 3,4,5,6]},
          {"id": 2, "stations": [1, 2, 3,4,5,6]},
          {"id": 3, "stations": [1, 2, 3,4,5,6]},
          {"id": 4, "stations": [1, 2, 3,4,5,6]}
         
          
          
        ],
        "pss_beams": [{"id": 11, "stations": [3, 1]}],
        "pst_beams": [{"id": 1, "stations": [1, 2]},{"id": 2, "stations": [5, 6]}
        
        ]
      
    }
    """


  #This scenario checks if TMC is able to process 8 subarry beams,
  #1 PSS beam and 2 PST beams
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
          {"id": 8, "stations": [1, 2, 3,4,5,6]}
          
        ],
        "pss_beams": [{"id": 12, "stations": [4]}],
        "pst_beams": [{"id": 1, "stations": [1, 2]},{"id": 2, "stations": [5, 6]}
        
        ]
      
    }
    """


  #This scenario checks if TMC is able to process 8 subarry beams,
  #1 PSS beam and 2 PST beams
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
        "pss_beams": [{"id": 13, "stations": [6]}],
        "pst_beams": [{"id": 1, "stations": [1, 2]},{"id": 2, "stations": [5, 6]}
        
        ]
      
    }
    """


  #This scenario checks if TMC is able to process 8 subarry beams,
  #1 PSS beam and 2 PST beams
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


  #This scenario checks if TMC is able to process 8 subarry beams,
  #1 PSS beam and 2 PST beams
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
        "pss_beams": [{"id": 15, "stations": [3]}],
        "pst_beams": [{"id": 1, "stations": [1, 2]},{"id": 2, "stations": [5, 6]}
        
        ]
      
    }
    """


  #This scenario checks if TMC is able to process 8 subarry beams,
  #1 PSS beam and 2 PST beams
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
        "pss_beams": [{"id": 16, "stations": [1,3, 4]}],
        "pst_beams": [{"id": 1, "stations": [1, 2]},{"id": 2, "stations": [5, 6]}
        
        ]
      
    }
    """


  #This scenario checks if TMC is able to process 8 subarry beams,
  #1 PSS beam and 2 PST beams with multiple stations combined
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
        "pss_beams": [{"id": 17, "stations": [3, 4,5,6]}],
        "pst_beams": [{"id": 1, "stations": [1, 2]},{"id": 2, "stations": [5, 6]}
        
        ]
      
    }
    """

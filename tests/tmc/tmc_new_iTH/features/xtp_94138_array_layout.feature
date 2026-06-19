
@XTP-94138 @XTP-94137 @TEAM_HIMALAYA
Scenario: Array layout functionality in TMC Low
  Given the telescope is in ON state
  When I invoke AssignResources on the TMC central node with below array layout:
    | source_uris | gitlab://gitlab.com/ska-telescope/ska-telmodel-data?main#tmdata |
    | array_layout_path | instrument/ska1_low/layout/low-layout.json |
  Then TMC central node "arraylayouturl" attribute is updated with layout data
  And invoking Configure command on TMC starts delay calculation on TMC CSPSLN
  And TMC is able to memorize the array layout link on restart
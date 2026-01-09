@XTP-93405 @XTP-93734 @XTP-28348 @TEAM_HIMALAYA
Scenario Outline: Configure using ADR-63 field key with different reference frames in TMC Low
    Given a Subarray with resources assigned
    When I Configure the subarray using the MCCS field key with reference_frame <reference_frame> and target <target_name>
    Then the Subarray is configured successfully
    And the MCCS Subarray commandCallInfo contains the correct field configuration for target <target_name>

    Examples:
      | reference_frame | target_name       |
      | icrs            | Centaurus A       |
      | altaz           | Zenith Drift      |
      | galactic        | Galactic Centre   |
      | special         | Sun               |
      | special         | Venus             |
      | special         | Mars              |
      | tle             | ISS (ZARYA)       |
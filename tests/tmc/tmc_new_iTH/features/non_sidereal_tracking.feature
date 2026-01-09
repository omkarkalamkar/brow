@XTP-93405 @XTP-93734 @XTP-28348 @TEAM_HIMALAYA
Scenario Outline: Configure using ADR-63 field key with different reference frames in TMC Low
    Given a Subarray with resources assigned
    When I Configure the subarray using the MCCS field key with reference_frame <reference_frame> and target <target_name>
    Then the Subarray is configured successfully
    And the MCCS Subarray commandCallInfo contains the correct field configuration for target <target_name>

    Examples:
      | reference_frame | target_name       | description                          |
      | icrs            | Centaurus A       | Sidereal source (RA/Dec)             |
      | altaz           | Zenith Drift      | Topocentric drift scan               |
      | galactic        | Galactic Centre   | Galactic coordinates                 |
      | special         | Sun               | Solar system body (non-sidereal)     |
      | special         | Venus             | Solar system body (non-sidereal)     |
      | special         | Mars              | Solar system body (non-sidereal)     |
      | tle             | ISS (ZARYA)       | Satellite tracking via TLE           |
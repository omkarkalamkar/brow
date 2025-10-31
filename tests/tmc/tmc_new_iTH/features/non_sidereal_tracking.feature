
XTP-93405 @XTP-28348 @Team_HIMALAYA
Scenario: Non sidereal tracking in TMC
		Given a Subarray with resources assigned
		When I Configure it for tracking a non-sidereal object from <non_sidereal_objects>
		Then the Subarray is configured successfully
		Examples:
            |non_sidereal_objects               |
            |Sun,Venus,Mars,Saturn,Pluto        |
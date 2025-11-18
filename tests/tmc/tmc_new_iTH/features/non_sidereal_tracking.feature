@XTP-93405 @XTP-93734 @XTP-28348 @TEAM_HIMALAYA
Scenario Outline: Non sidereal tracking in TMC Low
	Given a Subarray with resources assigned
	When I Configure it for tracking a non-sidereal object from <non_sidereal_objects>
	Then the Subarray is configured successfully
	And the MCCS Subarray commandCallInfo json has record of <non_sidereal_objects>
	Examples:
		|non_sidereal_objects	|
		|Sun					|
		|Venus					|
		|Mars					|

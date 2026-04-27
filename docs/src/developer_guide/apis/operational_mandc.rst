.. _ops_apis:

=======================================
Operational Monitoring and Control APIs
=======================================

Control Commands
-----------------

TMC provides APIs in the form of Tango device commands for controlling the telescope as follows:

* :py:mod:`TelescopeOn <ska_tmc_centralnode.commands.telescope_on_command>`
* :py:mod:`TelescopeOff <ska_tmc_centralnode.commands.telescope_off_command>`
* :py:mod:`Standby <ska_tmc_centralnode.commands.telescope_standby_command>`


Monitoring of the telescope level activities can be done by reading/subscribing to 
the following Tango attributes exposed by Tango attributes exposed by :ref:`Central Node <components_cn>`:

* telescopeState
* telescopeHealthState
* telescopeAvailability
* transformedInternalModel

Additionally, monitoring of individual TMC component can be done by reading/subscribing 
to the attributes exposed by various TMC components. Please refer to 
:ref:`Knowledge Base <knowledge_base>` > :ref:`Components <components>` 
for more details.
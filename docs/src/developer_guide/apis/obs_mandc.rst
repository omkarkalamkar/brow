.. _obs_apis:

Observation Execution APIs
**************************

The observation execution can be done by following a sequence of APIs as follows:

* `Resource allocation <https://developer.skao.int/projects/ska-tmc-centralnode/en/latest/api/ska_tmc_centralnode.commands.html#ska-tmc-centralnode-commands-assign-resources-command-module>`_
* `Configure a scan <https://developer.skao.int/projects/ska-tmc-subarraynode/en/latest/api/ska_tmc_subarraynode.commands.html#module-ska_tmc_subarraynode.commands.configure_command>`_
* `Perform scan <https://developer.skao.int/projects/ska-tmc-subarraynode/en/latest/api/ska_tmc_subarraynode.commands.html#module-ska_tmc_subarraynode.commands.scan_command>`_
* `End a scan <https://developer.skao.int/projects/ska-tmc-subarraynode/en/latest/api/ska_tmc_subarraynode.commands.html#module-ska_tmc_subarraynode.commands.end_command>`_
* `Resource de-allocation <https://developer.skao.int/projects/ska-tmc-centralnode/en/latest/api/ska_tmc_centralnode.commands.html#ska-tmc-centralnode-commands-release-resources-command-module>`_

Before performing any observation related operation it is necessary that the telescope is in ON state.
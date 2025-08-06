.. _deployment:

==================
Deployment
==================

Standard deployment
====================

The TMC Low is packaged as a `helm chart <https://helm.sh/>`_ and can be 
deployed uing helm commands. The default deployment configuration is 
assumed to be the SKA production environment. In the current version,
TMC supports `one` subarray operation. Following list shows default number 
of instances deployed for each of the TMC component.

#. Central Node - 1
#. Subarray Node - 1
#. CSP Master Leaf Node - 1
#. CSP Subarray Leaf Node - 1
#. SDP Master Leaf Node - 1
#. SDP Subarray Leaf Node - 1
#. MCCS Master Leaf Node - 1
#. MCCS Subarray Leaf Node - 1

.. warning:: The number of instances of Central Node, MCCS Master Leaf Node, 
    SDP Master, Leaf Node and CSP Master Leaf Node should always be one even 
    though it is technically possible to deploy multiple instances.

To deploy the TMC use following command on the terminal:

.. code-block:: python

    helm install my-tmc-release https://artefact.skao.int/repository/helm-internal/ska-tmc-low --namespace ska-tmc-low

It is possible to customize the deployment as per need. To do so, the 
`values.yaml` file in TMC chart needs to be modified. The same can be done by 
using `--set` option in the command line while using the `helm install` 
command.

Basic Customization options
===========================

Number of subarrays 
--------------------

The number of subarrays can be deployed according to the need. A variable 
named **subarray_count** need to be set to the desired value. This option 
affects the number of instances of following components.

#. Subarray Node
#. CSP Subarray Leaf Node
#. SDP Subarray Leaf Node 
#. MCCS Subarray Leaf Node 

.. note:: The value of **subarray_count** is controlled under global section of
    `values.yaml`.


Tango host
----------

This option allows to specify the desired Tango facility. The variable 
**tango_host** is used to specify the tango facility. By default, the value 
of this variable is set to `databaseds-tango-base-test:10000`.

Command timeout
---------------

This option sets the timeout value till which the TMC components wait for
completion of commands invoked on lower level Tango devices. This timeout 
should be set for each TMC component. To set the desired timeout value, 
navigate to **deviceServers -> <component name>** in `values.yaml` file. 
Locate **CommandTimeOut** variable and set an integer value equivalant in 
seconds.

.. warning::
    When setting the command timeout values, it is essential to set bigger
    timeout values Central Node and Subarray Node than any Leaf Node. This is 
    because the as per TMC architecture, Central Node and Subarray Node are
    higher level in the hierarchy and Leaf Nodes are at lower level. The 
    commands flow from Central Node, Subarray Node, to Leaf Nodes and then to the 
    subsystems. The higher level nodes need to factor in the command timeout 
    set on lower level components.  


Advanced Customization options
===============================

Following are the advance options. These options are mainly useful for developers 
and AIV engineers for testing purpose. Customizing these parameters should be 
done carefully.


#. **file** : User can provide custom device server configuration file to 
nodes. Defaults are: 
`configuration files <https://gitlab.com/ska-telescope/ska-tmc/ska-tmc-low-integration/-/blob/main/charts/ska-tmc-low/data/>`_.

#. **enabled** : User can opt to disable any node by setting this value to False.Default is True for all nodes.

#. Variables under **global** section

    #. **domain** : This value is present under global. It is the domain name of TMC TANGO device. The value is set to "low-tmc".
    #. **subarray_count** : This value is present under global. It is the count of subarray. Value is set to 1.

#. Variables under **devices_fqdn** section

    #. **tmc_subarray_prefix** : This value is present under global, User can use this to change the FQDN prefix of SubarrayNode.
    #. **csp_subarray_ln_prefix** : This value is present under global, User can use this to change the FQDN prefix of CspSubarrayLeafNode.
    #. **sdp_subarray_ln_prefix** : This value is present under global, User can use this to change the FQDN prefix of SdpSubarrayLeafNode.
    #. **csp_master_ln** : This value is present under global, User can use this to change the FQDN of CspMasterLeafNode.
    #. **sdp_master_ln** : This value is present under global, User can use this to change the FQDN of SdpMasterLeafNode.
    #. **csp_subarray_prefix** : This value is present under global, User can use this to change the FQDN prefix of CSP Subarray.
    #. **sdp_subarray_prefix** : This value is present under global, User can use this to change the FQDN prefix of SDP Subarray.
    #. **csp_master** : This value is present under global, User can use this to change the FQDN of CSP Master.
    #. **sdp_master** : This value is present under global, User can use this to change the FQDN of SDP Master.
    #. **mccs_master** : This value is present under global, User can use this to change the FQDN of MCCS Master.
    #. **mccs_master_ln** : This value is present under global, User can use this to change the FQDN of MCCS Master Leaf Node.
    #. **mccs_subarray_prefix** : This value is present under global, User can use this to change the FQDN prefix of MCCS Subarray.
    #. **mccs_subarray_ln_prefix** : This value is present under global, User can use this to change the FQDN prefix of MCCS Subarray Leaf Node.

Component specific configuration
---------------------------------

This section specifies the configuration options for individual TMC component. 
Navigate to **deviceServers.<component>** section in values.yaml file. 

Central Node
^^^^^^^^^^^^^

    #. **SkuidService** :  This refers to the value for SKUID service. Currently defaults to "ska-ser-skuid-test-svc.ska-tmc-centralnode.svc.techops.internal.skao.int:9870".
    #. **LivelinessCheckPeriod** :  This refers to the Period (in seconds) for the liveliness probe to monitor each device in a loop. Currently defaults to 0.5 seconds.
    #. **EventSubscriptionCheckPeriod** :  This refers to the Period (in seconds) for the event subscriber to check the device subscriptions in a loop. Currently defaults to 0.5 seconds.
    #. **CommandTimeOut** :  This refers to the Timeout (in seconds) for the command execution. Currently defaults to 80 seconds.
    #. **AssignResourcesInterface** :  This refers to the interface value of AssignResources schema. Currently defaults to "https://schema.skao.int/ska-low-tmc-assignresources/4.0".
    #. **ReleaseResourcesInterface** :  This refers to the interface value of ReleaseResources schema. Currently defaults to "https://schema.skao.int/ska-low-tmc-releaseresources/3.0".
    #. **family** :  This refers to the family name of CentralNode TANGO device. Currently defaults to "central-node".
    #. **member** :  This refers to the member of CentralNode TANGO device. Currently defaults to "0".

Subarray Node
^^^^^^^^^^^^^^

    #. **CspAssignResourcesInterfaceURL** : Interface version for CSP assign resources command. Currently defaults to "https://schema.skao.int/ska-low-csp-assignresources/3.0"
    #. **CspScanInterfaceURL** : Interface version for CSP scan command. Currently defaults to "https://schema.skao.int/ska-low-csp-scan/2.0"
    #. **SdpScanInterfaceURL** : Interface version for SDP scan command. Currently defaults to "https://schema.skao.int/ska-sdp-scan/0.4"
    #. **MccsConfigureInterfaceURL** : Interface version for MCCS configure command. Currently defaults to "https://schema.skao.int/ska-low-mccs-configure/1.0"
    #. **MccsScanInterfaceURL** : Interface version for MCCS scan command. Currently defaults to "https://schema.skao.int/ska-low-mccs-scan/3.0"
    #. **JonesURI** : URI for Jones Matrix. Currently defaults to "tango://jones.skao.int/low/stn-beam/1".
    #. **LivelinessCheckPeriod** :  This refers to the Period (in seconds) for the liveliness probe to monitor each device in a loop. Currently defaults to 0.5 seconds.
    #. **EventSubscriptionCheckPeriod** :  This refers to the Period (in seconds) for the event subscriber to check the device subscriptions in a loop. Currently defaults to 0.5 seconds.
    #. **CommandTimeOut** :  This refers to the timeout (in seconds) for the command execution. Currently defaults to 70 seconds.
    #. **AbortCommandTimeOut** :  This refers to the timeout for the Subarray ABORTED obsState transition. Once the AbortCommandTimeOut exceeds, SubarrayNode transitions to obsState FAULT. Currently defaults to 40 seconds.
    #. **family** :  This refers to the family name of SubarrayNode TANGO device. Currently defaults to "subarray".

SDP Subarray Leaf Node
^^^^^^^^^^^^^^^^^^^^^^^^

    #. **LivelinessCheckPeriod** :  This refers to the Period (in seconds) for the liveliness probe to monitor each device in a loop. Currently defaults to 0.5 seconds.
    #. **EventSubscriptionCheckPeriod** :  This refers to the Period (in seconds) for the event subscriber to check the device subscriptions in a loop. Currently defaults to 0.5 seconds.
    #. **CommandTimeOut** :  This refers to the timeout (in seconds) for the command execution. Currently defaults to 50 seconds.
    #. **AdapterTimeOut** :  This refers to the timeout (in seconds) for the adapter creation. This property is for internal use. Currently defaults to 2 seconds.
    #. **family** :  This refers to the family name of SDP Subarray Leaf Node TANGO device. Currently defaults to "subarray-leaf-node-sdp".

SDP Master Leaf Node
^^^^^^^^^^^^^^^^^^^^^^^^

    #. **LivelinessCheckPeriod** :  This refers to the Period (in seconds) for the liveliness probe to monitor each device in a loop. Currently defaults to 0.5 seconds.
    #. **EventSubscriptionCheckPeriod** :  This refers to the Period (in seconds) for the event subscriber to check the device subscriptions in a loop. Currently defaults to 0.5 seconds.
    #. **AdapterTimeOut** :  This refers to the timeout (in seconds) for the adapter creation. This property is for internal use. Currently defaults to 2 seconds.
    #. **family** :  This refers to the family name of SDP Master Leaf Node TANGO device. Currently defaults to "leaf-node-sdp".
    #. **member** :  This refers to the member of SDP Master Leaf Node TANGO device. Currently defaults to "0".

CSP Master Leaf Node
^^^^^^^^^^^^^^^^^^^^^^^^

    #. **LivelinessCheckPeriod** :  This refers to the Period (in seconds) for the liveliness probe to monitor each device in a loop. Currently defaults to 0.5 seconds.
    #. **EventSubscriptionCheckPeriod** :  This refers to the Period (in seconds) for the event subscriber to check the device subscriptions in a loop. Currently defaults to 0.5 seconds.
    #. **AdapterTimeOut** :  This refers to the timeout (in seconds) for the adapter creation. This property is for internal use. Currently defaults to 2 seconds.
    #. **family** :  This refers to the family name of CSP Master Leaf Node TANGO device. Currently defaults to "leaf-node-csp".
    #. **member** :  This refers to the member of CSP Master Leaf Node TANGO device. Currently defaults to "0".

CSP Subarray Leaf Node
^^^^^^^^^^^^^^^^^^^^^^^^

    #. **DelayCadence** :  This refers to the time difference (in seconds) between each publication of delay values to the `delayModel` attribute on the `CspSubarrayLeafNode`. Currently defaults to 300 seconds.
    #. **DelayValidityPeriod** : This represents the duration (in seconds) for which delay values remain valid after being published. Currently defaults to 600 seconds.
    #. **DelayModelTimeInAdvance** : This indicates the time in seconds by which delay values need to be available in advance. Currently defaults to 600 seconds.
    #. **PSTDelayCadence** :  This refers to the time difference (in seconds) between each publication of delay values for the PST beam. Currently defaults to 300 seconds.
    #. **PSTDelayValidityPeriod** : This represents the duration (in seconds) for which delay values remain valid after being published. Currently defaults to 600 seconds.
    #. **PSTDelayModelTimeInAdvance** : This indicates the time in seconds by which delay values need to be available in advance. Currently defaults to 600 seconds.
    #. **LivelinessCheckPeriod** :  This refers to the Period (in seconds) for the liveliness probe to monitor each device in a loop. Currently defaults to 0.5 seconds.
    #. **EventSubscriptionCheckPeriod** :  This refers to the Period (in seconds) for the event subscriber to check the device subscriptions in a loop. Currently defaults to 0.5 seconds.
    #. **CommandTimeOut** :  This refers to the timeout (in seconds) for the command execution. Currently defaults to 50 seconds.
    #. **AdapterTimeOut** :  This refers to the timeout (in seconds) for the adapter creation. This property is for internal use. Currently defaults to 2 seconds.
    #. **family** :  This refers to the family name of CSP Subarray Leaf Node TANGO device. Currently defaults to "subarray-leaf-node-csp".

MCCS Master Leaf Node
^^^^^^^^^^^^^^^^^^^^^^^^

    #. **LivelinessCheckPeriod** :  This refers to the Period (in seconds) for the liveliness probe to monitor each device in a loop. Currently defaults to 0.5 seconds.
    #. **EventSubscriptionCheckPeriod** :  This refers to the Period (in seconds) for the event subscriber to check the device subscriptions in a loop. Currently defaults to 0.5 seconds.
    #. **CommandTimeOut** :  This refers to the timeout (in seconds) for the command execution. Currently defaults to 50 seconds.
    #. **AdapterTimeOut** :  This refers to the timeout (in seconds) for the adapter creation. This property is for internal use. Currently defaults to 2 seconds.
    #. **family** :  This refers to the family name of MCCS Master Leaf Node TANGO device. Currently defaults to "leaf-node-mccs".
    #. **member** :  This refers to the member of MCCS Master Leaf Node TANGO device. Currently defaults to "0".

MCCS Master Leaf Node
^^^^^^^^^^^^^^^^^^^^^^^^

    #. **LivelinessCheckPeriod** :  This refers to the Period (in seconds) for the liveliness probe to monitor each device in a loop. Currently defaults to 0.5 seconds.
    #. **EventSubscriptionCheckPeriod** :  This refers to the Period (in seconds) for the event subscriber to check the device subscriptions in a loop. Currently defaults to 0.5 seconds.
    #. **CommandTimeOut** :  This refers to the timeout (in seconds) for the command execution. Currently defaults to 50 seconds.
    #. **AdapterTimeOut** :  This refers to the timeout (in seconds) for the adapter creation. This property is for internal use. Currently defaults to 2 seconds.
    #. **family** :  This refers to the family name of MCCS Subarray Leaf Node TANGO device. Currently defaults to "subarray-leaf-node-mccs".
TMC Low Deployment
==================

TMC Low deployment comes with following components:

1. **Central Node** 

2. **Subarray Node**

3. **Csp Master Leaf Node**

4. **Csp Subarray Leaf Node**

5. **Sdp Master Leaf Node**

6. **Sdp Subarray Leaf Node**

7. **MCCS Master Leaf Node**

8. **MCCS Subarray Leaf Node**


Configurable options
--------------------

* a. **instances** : User can provide the array of device server deployment instances required for node.

    Default for nodes are:

    #. **Central Node** : ["01"] 

    #. **Csp Master Leaf Node** : ["01"] 

    #. **Sdp Master Leaf Node** : ["01"]

    #. **MCCS Master Leaf Node** : ["01"]

* b. **subarray_count** : User can set this subarray count according to number device server deployment instances required for node..

    Default Value is 2.
    
    #. **Subarray Node** 

    #. **Csp Subarray Leaf Node** 

    #. **Sdp Subarray Leaf Node** 

    #. **MCCS Subarray Leaf Node** 

* c. **file** : User can provide custom device server configuration file to  nodes.Default is  `configuration files <https://gitlab.com/ska-telescope/ska-tmc/ska-tmc-low-integration/-/blob/main/charts/ska-tmc-low/data/>`_

* d. **enabled** : User can opt to disable any node by setting this value to False.Default is True for all nodes.

* e. Variables under **global** section

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

* f. Variables under **deviceServers.centralnode** section

    #. **SkuidService** :  This refers to the value for SKUID service. Currently defaults to "ska-ser-skuid-test-svc.ska-tmc-centralnode.svc.techops.internal.skao.int:9870".

    #. **LivelinessCheckPeriod** :  This refers to the Period (in seconds) for the liveliness probe to monitor each device in a loop. Currently defaults to 0.5 seconds.

    #. **EventSubscriptionCheckPeriod** :  This refers to the Period (in seconds) for the event subscriber to check the device subscriptions in a loop. Currently defaults to 0.5 seconds.
    
    #. **CommandTimeOut** :  This refers to the Timeout (in seconds) for the command execution. Currently defaults to 80 seconds.

    #. **AssignResourcesInterface** :  This refers to the interface value of AsignResources schema. Currently defaults to "https://schema.skao.int/ska-low-tmc-assignresources/4.0".

    #. **ReleaseResourcesInterface** :  This refers to the interface value of ReleaseResources schema. Currently defaults to "https://schema.skao.int/ska-low-tmc-releaseresources/3.0".

* g. Variables under **deviceServers.subarraynode** section

    #. **CspAssignResourcesInterfaceURL** : Interface version for CSP assign resources command. Currently defaults to "https://schema.skao.int/ska-low-csp-assignresources/3.0"
    
    #. **CspScanInterfaceURL** : Interface version for CSP scan command. Currently defaults to "https://schema.skao.int/ska-low-csp-scan/2.0"
    
    #. **SdpScanInterfaceURL** : Interface version for SDP scan command. Currently defaults to "https://schema.skao.int/ska-sdp-scan/0.4"
    
    #. **MccsConfigureInterfaceURL** : Interface version for MCCS configure command. Currently defaults to "https://schema.skao.int/ska-low-mccs-configure/1.0"
    
    #. **MccsScanInterfaceURL** : Interface version for MCCS scan command. Currently defaults to "https://schema.skao.int/ska-low-mccs-scan/3.0"
    
    #. **JonesURI** : IURI for Jones Matrix. Currently defaults to "tango://jones.skao.int/low/stn-beam/1".
    
    #. **LivelinessCheckPeriod** :  This refers to the Period (in seconds) for the liveliness probe to monitor each device in a loop. Currently defaults to 0.5 seconds.

    #. **EventSubscriptionCheckPeriod** :  This refers to the Period (in seconds) for the event subscriber to check the device subscriptions in a loop. Currently defaults to 0.5 seconds.
    
    #. **CommandTimeOut** :  This refers to the timeout (in seconds) for the command execution. Currently defaults to 70 seconds.
    
    #. **AbortCommandTimeOut** :  This refers to the timeout for the Subarray ABORTED obsState transition. Once the AbortCommandTimeOut exceeds, SubarrayNode transitions to obsState FAULT. Currently defaults to 40 seconds.

* h. Variables under **deviceServers.sdpsubarrayleafnode** section

    #. **LivelinessCheckPeriod** :  This refers to the Period (in seconds) for the liveliness probe to monitor each device in a loop. Currently defaults to 0.5 seconds.

    #. **EventSubscriptionCheckPeriod** :  This refers to the Period (in seconds) for the event subscriber to check the device subscriptions in a loop. Currently defaults to 0.5 seconds.
    
    #. **CommandTimeOut** :  This refers to the timeout (in seconds) for the command execution. Currently defaults to 50 seconds.

    #. **AdapterTimeOut** :  This refers to the timeout (in seconds) for the adapter creation. This property is for internal use. Currently defaults to 2 seconds.

* i. Variables under  **deviceServers.sdpmasterleafnode** section

    #. **LivelinessCheckPeriod** :  This refers to the Period (in seconds) for the liveliness probe to monitor each device in a loop. Currently defaults to 0.5 seconds.

    #. **EventSubscriptionCheckPeriod** :  This refers to the Period (in seconds) for the event subscriber to check the device subscriptions in a loop. Currently defaults to 0.5 seconds.

    #. **AdapterTimeOut** :  This refers to the timeout (in seconds) for the adapter creation. This property is for internal use. Currently defaults to 2 seconds.

* j. Variables under **deviceServers.cspmasterleafnode** section

    #. **LivelinessCheckPeriod** :  This refers to the Period (in seconds) for the liveliness probe to monitor each device in a loop. Currently defaults to 0.5 seconds.

    #. **EventSubscriptionCheckPeriod** :  This refers to the Period (in seconds) for the event subscriber to check the device subscriptions in a loop. Currently defaults to 0.5 seconds.

    #. **AdapterTimeOut** :  This refers to the timeout (in seconds) for the adapter creation. This property is for internal use. Currently defaults to 2 seconds.

* k. Variables under **deviceServers.cspsubarrayleafnode** section

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

* l. Variables under **deviceServers.mccsmasterleafnode** section

    #. **LivelinessCheckPeriod** :  This refers to the Period (in seconds) for the liveliness probe to monitor each device in a loop. Currently defaults to 0.5 seconds.

    #. **EventSubscriptionCheckPeriod** :  This refers to the Period (in seconds) for the event subscriber to check the device subscriptions in a loop. Currently defaults to 0.5 seconds.
    
    #. **CommandTimeOut** :  This refers to the timeout (in seconds) for the command execution. Currently defaults to 50 seconds.

    #. **AdapterTimeOut** :  This refers to the timeout (in seconds) for the adapter creation. This property is for internal use. Currently defaults to 2 seconds.

* h. Variables under **deviceServers.mccssubarrayleafnode** section

    #. **LivelinessCheckPeriod** :  This refers to the Period (in seconds) for the liveliness probe to monitor each device in a loop. Currently defaults to 0.5 seconds.

    #. **EventSubscriptionCheckPeriod** :  This refers to the Period (in seconds) for the event subscriber to check the device subscriptions in a loop. Currently defaults to 0.5 seconds.
    
    #. **CommandTimeOut** :  This refers to the timeout (in seconds) for the command execution. Currently defaults to 50 seconds.

    #. **AdapterTimeOut** :  This refers to the timeout (in seconds) for the adapter creation. This property is for internal use. Currently defaults to 2 seconds.


TMC Low Sub-system FQDN's
-------------------------
Below are the FQDN's of the TMC Low components. For updated FQDN's kindly refer values.yaml in the TMC Low charts.

+------------------------------------------+------------------------------------------------------------------------+ 
| TMC Low component                        |            FQDN                                                        | 
+==========================================+========================================================================+ 
| Central Node                             |  low-tmc/central-node/0                                       |
+------------------------------------------+------------------------------------------------------------------------+
| Subarray Node                            |  low-tmc/subarray/{id}                                         |
+------------------------------------------+------------------------------------------------------------------------+
| CSP Subarray Leaf Node                   |  low-tmc/subarray-leaf-node-csp/{id}                                 |
+------------------------------------------+------------------------------------------------------------------------+
| SDP Subarray Leaf Node                   |  low-tmc/subarray-leaf-node-sdp/{id}                                 |
+------------------------------------------+------------------------------------------------------------------------+
| MCCS Subarray Leaf Node                  +  low-tmc/subarray-leaf-node-mccs/{id}                                |    
+------------------------------------------+------------------------------------------------------------------------+
| MCCS Master Leaf Node                    +  low-tmc/leaf-node-mccs/0                                      |
+------------------------------------------+------------------------------------------------------------------------+
| SDP Master Leaf Node                     +  low-tmc/leaf-node-sdp/0                                       |
+------------------------------------------+------------------------------------------------------------------------+
| CSP Master Leaf Node                     +  low-tmc/leaf-node-csp/0                                       |
+------------------------------------------+------------------------------------------------------------------------+


**NOTE** : {id} is the identifier for the deployed subarray.
           For instance, if two subarrays are deployed

            Subarray 1 will be:
           
                Subarray Node : low-tmc/subarray/01
           
                CSP Subarray Leaf Node: low-tmc/subarray-leaf-node-csp/01 
           
                SDP Subarray Leaf Node: low-tmc/subarray-leaf-node-sdp/01

                MCCS Subarray Leaf Node: low-tmc/subarray-leaf-node-mccs/01
         
            For Subarray 2:

                Subarray Node : low-tmc/subarray/02
         
                CSP Subarray Leaf Node: low-tmc/subarray-leaf-node-csp/02
         
                SDP Subarray Leaf Node: low-tmc/subarray-leaf-node-sdp/02
         
                MCCS Subarray Leaf Node: low-tmc/subarray-leaf-node-mccs/02






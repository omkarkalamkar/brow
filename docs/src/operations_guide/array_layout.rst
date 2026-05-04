.. _`Applying Array Layout Through TMC`:

==========================================
Applying Array Layout Through TMC
==========================================

Overview
--------

This page provides instructions for applying an **Array Layout** configuration through the TMC for **SKA-Low**.

TMC allows operators to specify which Array Layout should be used for observations by providing its reference in the **AssignResources** command.

When the Array Layout is applied successfully, TMC distributes it automatically to all relevant subsystems during configuration.  

How to Apply Array Layout
-------------------------

There are two ways to apply an Array Layout in TMC:

1. **Set a Telescope-level Default Layout**  

   Define a default layout once at telescope level.  
   This layout applies automatically to all subarrays unless a specific layout is later provided.  
   You can set this using the **DefaultArrayLayoutURL** attribute on CentralNode.

   The attribute **arrayLayoutFileProvided** (Boolean) on CentralNode indicates whether the default
   array layout file is provided or not. An alarm event can be generated when the default layout
   file url is not defined.

.. note::
   As per SKB-1282 resolution, the default value of the properties **DefaultArrayLayoutSourceURIs** and
   **DefaultArrayLayoutPath** on CentralNode are set to empty strings. Therefore attribute **DefaultArrayLayoutURL**
   on CentralNode must be set once after the deployment is done, then the value will get applied to all
   the observations executed after.

2. **Set a Subarray-specific Layout**  

   Provide a custom layout for a particular subarray using the ``telmodel`` section in the **AssignResources** JSON payload.  
   This overrides the default layout only for that subarray.  
   You can confirm that the **ArrayLayoutURL** attribute reflects the correct layout reference.

.. note::

   The ``telmodel`` section is **optional**.  
   If it is not included in the AssignResources JSON, the system will use the **default Array Layout** already configured.

AssignResources Example
-----------------------

The Array Layout URL can be provided in the ``telmodel`` block of the **AssignResources** command JSON.  

This feature is supported from schema version  
``"https://schema.skao.int/ska-low-tmc-assignresources/4.3"`` onwards.  

Only this section is new — the rest of the AssignResources JSON remains unchanged.

**Example:**

.. code-block:: none

   {
     "interface": "https://schema.skao.int/ska-low-tmc-assignresources/4.3",
     "transaction_id": "txn-00000-assign-low-4.3",
     "subarray_id": 1,
     "telmodel": {
       "source_uris": [
         "gitlab://gitlab.com/ska-telescope/ska-telmodel-data?main#tmdata"
       ],
       "array_layout_path": "instrument/ska1_low/layout/low-layout.json"
     },
     ...
   }

Explanation of the ``telmodel`` Section
---------------------------------------

The ``telmodel`` section provides the reference to the Array Layout data stored in the TelModel repository.

- **source_uris**  
  Specifies the source location of the TelModel data repository.  
  This can be a URI pointing to the repository containing the telescope configuration data.  
  In the example above, it points to the official SKA TelModel data repository.

  Example:  
  ``"gitlab://gitlab.com/ska-telescope/ska-telmodel-data?main#tmdata"``  
  → Fetches layout data from the **main** branch of the ``ska-telmodel-data`` repository, under the ``tmdata`` directory.

- **array_layout_path**  
  Specifies the path within the TelModel data where the layout JSON file is located.  

  Example:  
  ``"instrument/ska1_low/layout/low-layout.json"``  
  → Refers to the layout file defining the **SKA-Low** array configuration.

Behavior Scenarios
------------------

This section explains how TMC behaves under different layout assignment conditions.

1. **Default layout only**  

   - If a default layout is set (via `DefaultArrayLayoutURL`), it applies automatically to all subarrays.  
   - No ``telmodel`` section is required in the AssignResources payload.

2. **Custom layout for a subarray**  

   - If a ``telmodel`` section is provided, that subarray will use the specified layout.  
   - Other subarrays continue using the default layout.

3. **Multiple AssignResources calls**  

   - When AssignResources is issued multiple times:

     * If the latest JSON includes a ``telmodel`` section, that layout replaces the previous one.
     * If the latest JSON does **not** include a ``telmodel`` section, the last successfully applied layout remains active.

4. **Optional use of telmodel section**  

   - The ``telmodel`` block is **not mandatory**.  
   - If omitted, the default or previously applied layout continues to be used.

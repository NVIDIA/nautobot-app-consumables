# Overview

**Consumables** are user-defined assets that fall below the threshold of devices that need to be tracked individually, items such as network cables, transceivers, etc.
Once consumables are defined, they are assigned to a storage location and are available to be checked out and assigned to a device.

## Consumable Type vs. Consumable vs. Consumable Pool

Consumables are made up of three models, which together allow you to create categories of consumables (Consumable Type), specific consumable products (Consumable), and physical consumable assets available to be used in datacenters (Consumable Pool).

### Consumable Type

{%
    include-markdown "../models/consumabletype.md"
    heading-offset=2
%}

### Consumable

{%
    include-markdown "../models/consumable.md"
    heading-offset=2
%}

### Consumable Pool

{%
    include-markdown "../models/consumablepool.md"
    heading-offset=2
%}

## Consumable Detail Inheritance

When creating a Consumable Type, a detailed JSON schema is created for that type. 

When creating a Consumable, it is associated with a Consumable Type, and the JSON schema is used to construct the form with options for the product.

Updating the schema of a Consumable Type will not change any existing Consumables based on that type.

Consumable Pools can be moved between locations, but doing so will cause all checked out consumables to be checked back in.

## Checking Out Consumables

Consumable Pools are assigned to locations, and define the number of those consumables available in that location.
Once consumables are put into use, e.g. hosts and switches are cabled up, the consumables in use need to be checked out.
Checked Out Consumables track the quantity in use by each device, and decrease the number available in the pool, for proper inventory tracking.

## Filtering

The Consumables app extends the filter set for Locations to allow filtering based on the presence of Consumable Pools at a given location.
In the UI, the filter is available under the Advanced tab when filtering.
Choose **Has Consumable Pools** for the field, **is null** for the lookup type, and then choose either **Yes** or **No** to filter for locations that to or do not have Consumable Pools assigned to them.

The filter can also be used by attaching a query parameter to the request URL for the location list.
The parameter for filtering by available project consumables is `nautobot_consumables_has_pools`, set the parameter value to either `True` or `False`.

```
http://nautobot.server/dcim/locations/?nautobot_consumables_has_pools=True
```

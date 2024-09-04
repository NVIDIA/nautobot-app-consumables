# Consumables Tracking for Nautobot

## Overview

An app for [Nautobot](https://github.com/nautobot/nautobot).
This Nautobot app enables you to define arbitrary types of consumables used in your environment, create pools of available consumables, and check them out as in use on a device.
It provides:

- **Consumable Type**
  - The broad categories of consumable assets, and can be created with a JSON schema for specific details of the asset.
  - By default, types for `Cable` and `Transceiver` are added when the app is installed, along with a `Generic` type that has an empty schema.
- **Consumable**
  - A Consumable defines an actual product based on a Consumable Type.
  - The Consumable Type schema is presented as a form for the options to be set on the Consumable.
- **Consumable Pool**
  - These are the physical assets for a Consumable which available in a location.
  - Pools define the number of assets available for use.
- **Checked Out Consumable**
  - Assets in Consumable Pools may be checked out and assigned as in use on a Device.

## License

Consumables Tracking for Nautobot is released under the Apache 2.0 license.

This project will download and install additional third-party open source software projects.
Review the license terms of these open source projects before use.

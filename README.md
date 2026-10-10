[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg?style=for-the-badge)](https://github.com/hacs/integration)
[![Validate](https://github.com/zackwag/home-assistant-eero/actions/workflows/validate.yaml/badge.svg)](https://github.com/zackwag/home-assistant-eero/actions/workflows/validate.yaml)
[![Lint](https://github.com/zackwag/home-assistant-eero/actions/workflows/lint.yaml/badge.svg)](https://github.com/zackwag/home-assistant-eero/actions/workflows/lint.yaml)

# Eero Home Assistant Integration

Custom component to allow control of eero mesh networks in [Home Assistant](https://home-assistant.io), built on the [eero-api](https://github.com/fulviofreitas/eero-api) Python library.

All communication with the eero cloud goes through eero-api, and the integration aims to follow it closely: features the library doesn't support aren't implemented here.

> **Note:** This project started as a fork of [schmittx/home-assistant-eero](https://github.com/schmittx/home-assistant-eero). Since 2.0.0 it has been rebuilt on eero-api and is maintained independently.

## Requirements

- Home Assistant 2026.7.0 or newer

## Install

1. Use [HACS](https://hacs.xyz) and add this repository as a [custom repository](https://hacs.xyz/docs/faq/custom_repositories), or download and manually move to the `custom_components` folder.
2. Restart Home Assistant.
3. Go to **Settings > Devices & Services > Add Integration** and search for `eero`.
4. Follow the prompts to authenticate and configure.

## Features

- **Multiple networks** — manage all eero networks on your account
- **Network controls** — guest network, eero Plus features, eero Labs features
- **Profiles** — pause access, blocked apps (eero Plus)
- **Clients** — pause access, device tracker entities, connection sensors
- **Eero devices** — status light and nightlight control (light entities with brightness), firmware updates
- **Activity sensors** — ad blocks, threat blocks, data usage, content inspections (eero Plus)
- **Backup networks** — status and control (eero Plus)
- **Image entities** — QR codes for main and guest networks
- **Include all** — option to automatically include all resources of a given type

## Options

Networks, resources, and activity metrics can be configured via integration options. Client inclusion can be toggled between include (whitelist) or exclude (blacklist) mode. If **Advanced Mode** is enabled for the current user, additional options are available (polling interval, timeout, response logging).

## Notes

- This integration does not support login via Amazon account. A workaround is to create a new eero account without Amazon login and add that account as a network admin. See this [post](https://github.com/schmittx/home-assistant-eero/issues/77#issuecomment-1960875926) for instructions.

## Credit

- [fulviofreitas/eero-api](https://github.com/fulviofreitas/eero-api) — eero cloud API library this integration is built on
- [schmittx/home-assistant-eero](https://github.com/schmittx/home-assistant-eero) — Original integration
- [@343max's eero-client](https://github.com/343max/eero-client) — API auth and refresh methods
- [@jrlucier's eero_tracker](https://github.com/jrlucier/eero_tracker) — Initial Home Assistant concept

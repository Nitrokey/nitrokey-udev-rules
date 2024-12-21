# Changelog

## Unreleased

- Remove symlink rule for the Nitrokey Storage.  Users are advised to use
  label- or UUID-based mounting or setup a a custom rule for their device
  instead.

## [v1.0.0][] (2024-01-29)

[v1.0.0]: https://github.com/Nitrokey/nitrokey-udev-rules/releases/tag/v1.0.0

- Import [`41-nitrokey.rules`][] from libnitrokey.
- Add rules for the Nitrokey Passkey:
  - Nitrokey Passkey (20a0:42f3)
  - Nitrokey Passkey Bootloader (20a0:42f4)

[`41-nitrokey.rules`]: https://github.com/Nitrokey/libnitrokey/blob/834937476cf3aa551ed5ab6e766e9dc522d35c36/data/41-nitrokey.rules

# Nitrokey udev Rules

This repository contains udev rules for Nitrokey devices.
Previously, these rules were maintained as a part of [libnitrokey][].

[libnitrokey]: https://github.com/Nitrokey/libnitrokey

## Usage and Requirements

The [`41-nitrokey.rules`][] file contains udev rules for these devices:
- Nitrokey 3
- Nitrokey HSM
- Nitrokey FIDO U2F
- Nitrokey FIDO2
- Nitrokey Passkey
- Nitrokey Pro
- Nitrokey Storage
- Nitrokey Start
- Nitrokey U2F

[`41-nitrokey.rules`]: ./41-nitrokey.rules

It requires udev 188 or later.
For older udev versions, use the [`41-nitrokey_old.rules`][] from libnitrokey.

[`41-nitrokey_old.rules`]: https://github.com/Nitrokey/libnitrokey/blob/master/data/41-nitrokey_old.rules

The rules use the `uaccess` tag which is a systemd mechanism.

To install the rules file, place it in `/etc/udev/rules.d`.
The file prefix should be lower than 73 because the rules must be applied before udev’s `73-seat-late.rules`.

## Troubleshooting

### Check device permissions

`uaccess` grants permissions to all local users via an ACL.
Use `getfacl` to check that the permissions are set correctly, for example:

```
$ getfacl /dev/hidraw0
getfacl: Removing leading '/' from absolute path names
# file: dev/hidraw0
# owner: root
# group: root
user::rw-
user:robin:rw-
group::---
mask::rw-
other::---
```

Here, the line `user:robin:rw-` indicates that the user `robin` has access to the device.

### Grant access to remote users

`uaccess` only grants access to local users.
Remote users, for example via SSH, will not have access to the devices with these rules.
If you want to allow remote users to use a device, you have to modify the rules and set the `MODE` or `OWNER` variables.
See [udev(7)][] for more information.

[udev(7)]: https://www.freedesktop.org/software/systemd/man/latest/udev.html

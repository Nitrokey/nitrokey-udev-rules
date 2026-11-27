# Nitrokey udev Rules

This repository contains udev rules for Nitrokey devices.
Previously, these rules were maintained as a part of [libnitrokey][].
Documentation for users is available on [docs.nitrokey.com][].

[libnitrokey]: https://github.com/Nitrokey/libnitrokey
[docs.nitrokey.com]: https://docs.nitrokey.com/software/nitropy/linux/udev

## Usage and Requirements

This repository provides two udev rules files using different mechanisms:
- [`41-nitrokey.rules`][] uses the `uaccess` mechanism to automatically grant permissions to all users that are logged in locally.
  It should be used on most modern systems and requires systemd (>= 188) or eudev and elogind.
- [`41-nitrokey-plugdev.rules`][] grants permissions to all users in the `plugdev` group.
  It can be used on systems without systemd or elogind or for remote access.

[`41-nitrokey.rules`]: ./41-nitrokey.rules
[`41-nitrokey-plugdev.rules`]: ./41-nitrokey-plugdev.rules

The files contain udev rules for these devices:
- Nitrokey 3
- Nitrokey HSM
- Nitrokey FIDO U2F
- Nitrokey FIDO2
- Nitrokey Passkey
- Nitrokey Pro
- Nitrokey Storage
- Nitrokey Start
- Nitrokey U2F

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
If you want to allow remote users to use a device, you can use the `plugdev` rules or manually modify the provided rules.
See [udev(7)][] for more information.

[udev(7)]: https://www.freedesktop.org/software/systemd/man/latest/udev.html

import argparse
import dataclasses
import textwrap
import tomllib
import typing
from enum import Enum


class Mode(Enum):
    UACCESS = "uaccess"
    PLUGDEV = "plugdev"

    def __str__(self) -> str:
        return self.value

    def header(self) -> str:
        if self == Mode.UACCESS:
            header = """\
                # Here rules in new style should be provided. Matching devices should be tagged with 'uaccess'.
                # File prefix number should be lower than 73, to be correctly processed by the Udev.
                # Recommended udev version: >= 188.
            """
        elif self == Mode.PLUGDEV:
            header = """\
                # Here rules in old style should be provided. Matching devices should be added to 'plugdev' group,
                # and with mode set to "0660".
                # File prefix number should be lower than 73, to be correctly processed by the Udev.
                # Recommended udev version: < 188.
            """
        else:
            typing.assert_never(self)
        return textwrap.dedent(header)

    @staticmethod
    def from_str(s: str) -> "Mode":
        for mode in Mode:
            if mode.value == s:
                return mode
        raise ValueError(f"Unsupported mode: {s}")


@dataclasses.dataclass(frozen=True)
class Device:
    name: str
    vid: int
    pid: int
    hid: bool = False
    gnupg: bool = False
    all: bool = False

    def generate(self, mode: Mode) -> str:
        s = f"# {self.name}\n"
        attr_vid_pid = [
            ("ATTR{idVendor}", "==", f"{self.vid:04x}"),
            ("ATTR{idProduct}", "==", f"{self.pid:04x}"),
        ]
        attrs_vid_pid = [
            ("ATTRS{idVendor}", "==", f"{self.vid:04x}"),
            ("ATTRS{idProduct}", "==", f"{self.pid:04x}"),
        ]
        if mode == Mode.UACCESS:
            action = [("TAG", "+=", "uaccess")]
        elif mode == Mode.PLUGDEV:
            action = [("MODE", "=", "0660"), ("GROUP", "=", "plugdev")]
        else:
            typing.assert_never(mode)
        if self.hid:
            s += generate_rule(
                [("KERNEL", "==", "hidraw*"), ("SUBSYSTEM", "==", "hidraw")]
                + attrs_vid_pid
                + action
            )
            s += generate_rule([("SUBSYSTEMS", "==", "usb")] + attrs_vid_pid + action)
        if self.gnupg:
            s += generate_rule(
                attr_vid_pid
                + [
                    ("ENV{ID_SMARTCARD_READER}", "=", "1"),
                    ("ENV{ID_SMARTCARD_READER_DRIVER}", "=", "gnupg"),
                ]
                + action
            )
        if self.all:
            s += generate_rule(attrs_vid_pid + action)
        return s

    @classmethod
    def from_dict(cls, data: dict[str, typing.Any]) -> "Device":
        return cls(**data)


def generate_rule(matches: typing.Sequence[tuple[str, str, str]]) -> str:
    rules = [f'{key}{op}"{value}"' for (key, op, value) in matches]
    return ", ".join(rules) + "\n"


def generate_u2f(devices: list[Device], mode: Mode) -> str:
    output = 'ACTION!="add|change", GOTO="u2f_end"\n'
    output += "\n"
    for device in devices:
        output += device.generate(mode)
    output += "\n"
    output += 'LABEL="u2f_end"\n'
    return output


def generate_ccid(devices: list[Device], mode: Mode) -> str:
    output = ""
    output += 'SUBSYSTEM!="usb", GOTO="gnupg_rules_end"\n'
    output += 'ACTION!="add", GOTO="gnupg_rules_end"\n'
    output += "\n"
    for device in devices:
        output += device.generate(mode)
    output += "\n"
    output += 'LABEL="gnupg_rules_end"\n'
    return output


def generate(
    version: str, u2f_devices: list[Device], ccid_devices: list[Device], mode: Mode
) -> str:
    header = f"""\
        # Copyright (c) Nitrokey GmbH
        # SPDX-License-Identifier: CC0-1.0
        # nitrokey-udev-rules {version} ({mode})
    """

    sections = []
    if u2f_devices:
        sections.append(generate_u2f(u2f_devices, mode))
    if ccid_devices:
        sections.append(generate_ccid(ccid_devices, mode))

    output = textwrap.dedent(header)
    output += "\n"
    output += mode.header()
    output += "\n"
    output += "\n\n".join(sections)
    return output


def run(version: str, input: str, output: str, mode: Mode) -> None:
    with open(input, "rb") as f:
        data = tomllib.load(f)

    u2f_devices = []
    if "u2f" in data:
        assert isinstance(data["u2f"], list)
        for device in data["u2f"]:
            assert isinstance(device, dict)
            u2f_devices.append(Device.from_dict(device))

    ccid_devices = []
    if "ccid" in data:
        assert isinstance(data["ccid"], list)
        for device in data["ccid"]:
            assert isinstance(device, dict)
            ccid_devices.append(Device.from_dict(device))

    rules = generate(version, u2f_devices, ccid_devices, mode)
    with open(output, "w") as f:
        f.write(rules)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("version")
    parser.add_argument("input")
    parser.add_argument("output")
    parser.add_argument("--mode", required=True, type=Mode.from_str)

    args = parser.parse_args()
    run(args.version, args.input, args.output, mode=args.mode)

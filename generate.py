import argparse
import dataclasses
import textwrap
import tomllib
import typing


@dataclasses.dataclass(frozen=True)
class Device:
    name: str
    vid: int
    pid: int
    hidraw: bool = False
    gnupg: bool = False
    all: bool = False

    def generate(self) -> str:
        s = f"# {self.name}\n"
        attr_vid_pid = [
            ("ATTR{idVendor}", "==", f"{self.vid:04x}"),
            ("ATTR{idProduct}", "==", f"{self.pid:04x}"),
        ]
        attrs_vid_pid = [
            ("ATTRS{idVendor}", "==", f"{self.vid:04x}"),
            ("ATTRS{idProduct}", "==", f"{self.pid:04x}"),
        ]
        uaccess = [("TAG", "+=", "uaccess")]
        if self.hidraw:
            s += generate_rule(
                [("KERNEL", "==", "hidraw*"), ("SUBSYSTEM", "==", "hidraw")]
                + attrs_vid_pid
                + uaccess
            )
        if self.gnupg:
            s += generate_rule(
                attr_vid_pid
                + [
                    ("ENV{ID_SMARTCARD_READER}", "=", "1"),
                    ("ENV{ID_SMARTCARD_READER_DRIVER}", "=", "gnupg"),
                ]
                + uaccess
            )
        if self.all:
            s += generate_rule(attrs_vid_pid + uaccess)
        return s

    @classmethod
    def from_dict(cls, data: dict[str, typing.Any]) -> "Device":
        return cls(**data)


def generate_rule(matches: typing.Sequence[tuple[str, str, str]]) -> str:
    rules = [f'{key}{op}"{value}"' for (key, op, value) in matches]
    return ", ".join(rules) + "\n"


def generate_u2f(devices: list[Device]) -> str:
    output = 'ACTION!="add|change", GOTO="u2f_end"\n'
    output += "\n"
    for device in devices:
        output += device.generate()
    output += "\n"
    output += 'LABEL="u2f_end"\n'
    return output


def generate_ccid(devices: list[Device]) -> str:
    output = ""
    output += 'SUBSYSTEM!="usb", GOTO="gnupg_rules_end"\n'
    output += 'ACTION!="add", GOTO="gnupg_rules_end"\n'
    output += "\n"
    for device in devices:
        output += device.generate()
    output += "\n"
    output += 'LABEL="gnupg_rules_end"\n'
    return output


def generate(u2f_devices: list[Device], ccid_devices: list[Device]) -> str:
    header = """\
        # Copyright (c) Nitrokey GmbH
        # SPDX-License-Identifier: CC0-1.0

        # Here rules in new style should be provided. Matching devices should be tagged with 'uaccess'.
        # File prefix number should be lower than 73, to be correctly processed by the Udev.
        # Recommended udev version: >= 188.

    """

    sections = []
    if u2f_devices:
        sections.append(generate_u2f(u2f_devices))
    if ccid_devices:
        sections.append(generate_ccid(ccid_devices))

    output = textwrap.dedent(header)
    output += "\n\n".join(sections)
    # TODO: can we remove this?
    output += textwrap.dedent("""

        # Nitrokey Storage dev Entry
        KERNEL=="sd?1", ATTRS{idVendor}=="20a0", ATTRS{idProduct}=="4109", SYMLINK+="nitrospace"
    """)
    return output


def run(input: str, output: str) -> None:
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

    rules = generate(u2f_devices, ccid_devices)
    with open(output, "w") as f:
        f.write(rules)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input")
    parser.add_argument("output")

    args = parser.parse_args()
    run(args.input, args.output)

from __future__ import annotations

import importlib
import sys
from dataclasses import dataclass


@dataclass(frozen=True)
class Command:
    name: str
    module: str
    description: str
    section: str
    show_in_help: bool = True


COMMANDS = (
    Command(
        name="patch",
        module="patch",
        description="Patch supported Reflexive wrapper executables.",
        section="tool",
    ),
    Command(
        name="unwrap",
        module="unwrap",
        description="Statically unwrap Reflexive wrapper payloads.",
        section="tool",
    ),
    Command(
        name="keygen",
        module="keygen",
        description="Generate or decode Reflexive registration material.",
        section="tool",
    ),
    Command(
        name="unpack-mpress",
        module="unpack_mpress",
        description="Dump and rebuild MPRESS-packed PE files.",
        section="advanced",
    ),
    Command(
        name="extract",
        module="extract_rutracker_installer",
        description="Extract Reflexive outer installers.",
        section="tool",
    ),
    Command(
        name="extract-repack",
        module="extract_installer",
        description="Extract Reflexive smart installers from archive repacks.",
        section="tool",
    ),
    Command(
        name="download",
        module="download",
        description="Download a single RuTracker installer from the mirror.",
        section="tool",
    ),
    Command(
        name="unwrapper-sweep",
        module="unwrapper_sweep",
        description="Run the full static unwrapper sweep.",
        section="internal",
        show_in_help=False,
    ),
    Command(
        name="installer-snapshot",
        module="installer_snapshot",
        description="Snapshot source installers with SHA-256 hashes.",
        section="internal",
        show_in_help=False,
    ),
    Command(
        name="native-registration-scan",
        module="native_registration_scan",
        description="Scan binaries for native registration signals.",
        section="internal",
        show_in_help=False,
    ),
    Command(
        name="integrated-wrappers",
        module="integrated_wrappers",
        description="Report likely Reflexive wrappers fused into the main EXE.",
        section="internal",
        show_in_help=False,
    ),
    Command(
        name="key-inventory",
        module="key_inventory",
        description="Extract embedded Reflexive RSA key material from branded DLLs.",
        section="internal",
        show_in_help=False,
    ),
    Command(
        name="recovered-list",
        module="recovered_list",
        description="Generate a recovered list.txt from a key inventory report.",
        section="internal",
        show_in_help=False,
    ),
    Command(
        name="compare-unwrapped",
        module="compare_unwrapped",
        description="Compare unwrapped corpora across sources.",
        section="internal",
        show_in_help=False,
    ),
)

COMMAND_INDEX = {command.name: command for command in COMMANDS}


def format_help() -> str:
    visible_commands = [command for command in COMMANDS if command.show_in_help]
    tools = [command for command in visible_commands if command.section == "tool"]
    advanced = [command for command in visible_commands if command.section == "advanced"]
    width = max(len(c.name) for c in COMMANDS)

    lines = [
        "Usage: reflexive <command> [args...]",
        "",
        "Tools:",
    ]
    for command in tools:
        lines.append(f"  {command.name.ljust(width)}  {command.description}")

    if advanced:
        lines.append("")
        lines.append("Advanced:")
        for command in advanced:
            lines.append(f"  {command.name.ljust(width)}  {command.description}")

    lines.extend(
        [
            "",
            "Internal analysis/report commands remain callable but are omitted from main help.",
            "Run `reflexive <command> --help` for command-specific options.",
        ]
    )
    return "\n".join(lines)


def dispatch(command_name: str, argv: list[str]) -> int:
    command = COMMAND_INDEX.get(command_name)
    if command is None:
        print(f"error: unknown command: {command_name}", file=sys.stderr)
        print(format_help(), file=sys.stderr)
        return 2

    module = importlib.import_module(f".{command.module}", package=__package__)
    if not hasattr(module, "main"):
        print(f"error: command module has no main(): {command.module}", file=sys.stderr)
        return 1

    previous_argv = sys.argv
    sys.argv = [f"reflexive {command.name}", *argv]
    try:
        try:
            result = module.main()
        except SystemExit as exc:
            code = exc.code
            if code is None:
                return 0
            if isinstance(code, int):
                return code
            print(code, file=sys.stderr)
            return 1
    finally:
        sys.argv = previous_argv

    if result is None:
        return 0
    return int(result)


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)

    if not args or args[0] in {"-h", "--help"}:
        print(format_help())
        return 0

    if args[0] == "help":
        if len(args) == 1:
            print(format_help())
            return 0
        return dispatch(args[1], ["--help"])

    return dispatch(args[0], args[1:])

from __future__ import annotations

import importlib
import sys
from dataclasses import dataclass


@dataclass(frozen=True)
class Command:
    name: str
    module: str
    description: str


COMMANDS = (
    Command(
        name="patch",
        module="patch",
        description="Patch supported Reflexive wrapper executables.",
    ),
    Command(
        name="unwrap",
        module="unwrap",
        description="Statically unwrap Reflexive wrapper payloads.",
    ),
    Command(
        name="keygen",
        module="keygen",
        description="Generate or decode Reflexive registration material.",
    ),
    Command(
        name="unpack-mpress",
        module="unpack_mpress",
        description="Dump and rebuild MPRESS-packed PE files.",
    ),
    Command(
        name="extract-installer",
        module="extract_installer",
        description="Extract Reflexive smart installers.",
    ),
    Command(
        name="extract-rutracker-installer",
        module="extract_rutracker_installer",
        description="Extract the rutracker Reflexive installer corpus.",
    ),
    Command(
        name="wrapper-versions",
        module="wrapper_versions",
        description="Scan wrapper binaries and summarize version families.",
    ),
    Command(
        name="wrapper-inventory",
        module="wrapper_inventory",
        description="Build a wrapper inventory for an extracted corpus.",
    ),
    Command(
        name="unwrapper-sweep",
        module="unwrapper_sweep",
        description="Run the full static unwrapper sweep.",
    ),
    Command(
        name="unwrapper-report",
        module="unwrapper_report",
        description="Render the unwrapper coverage report.",
    ),
    Command(
        name="game-list",
        module="game_list",
        description="Generate a game list from an extracted corpus.",
    ),
    Command(
        name="native-registration-scan",
        module="native_registration_scan",
        description="Scan binaries for native registration signals.",
    ),
    Command(
        name="key-inventory",
        module="key_inventory",
        description="Extract embedded Reflexive RSA key material from branded DLLs.",
    ),
    Command(
        name="recovered-list",
        module="recovered_list",
        description="Generate a recovered list.txt from a key inventory report.",
    ),
    Command(
        name="compare-unwrapped",
        module="compare_unwrapped",
        description="Compare unwrapped corpora across sources.",
    ),
    Command(
        name="rutracker-game-list",
        module="rutracker_game_list",
        description="Generate the rutracker installer-derived game list.",
    ),
    Command(
        name="rutracker-probe-report",
        module="rutracker_probe_report",
        description="Build the rutracker probe report.",
    ),
    Command(
        name="rutracker-publisher-attribution",
        module="rutracker_publisher_attribution",
        description="Build the rutracker publisher attribution report.",
    ),
    Command(
        name="rutracker-engine-report",
        module="rutracker_engine_report",
        description="Build the rutracker game engine report.",
    ),
)

COMMAND_INDEX = {
    command.name: command
    for command in COMMANDS
}

def format_help() -> str:
    lines = [
        "Usage: reflexive <command> [args...]",
        "",
        "Commands:",
    ]
    width = max(len(command.name) for command in COMMANDS)
    for command in COMMANDS:
        lines.append(f"  {command.name.ljust(width)}  {command.description}")
    lines.extend(
        [
            "",
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

from __future__ import annotations

import importlib
import sys
from dataclasses import dataclass


@dataclass(frozen=True)
class Command:
    name: str
    module: str
    description: str
    aliases: tuple[str, ...] = ()


COMMANDS = (
    Command(
        name="patch-exe",
        module="patch_reflexive_exe",
        description="Patch supported Reflexive wrapper executables.",
        aliases=("patch-reflexive-exe",),
    ),
    Command(
        name="unwrap-wrapper",
        module="unwrap_reflexive_wrapper",
        description="Statically unwrap Reflexive wrapper payloads.",
        aliases=("unwrap-reflexive-wrapper",),
    ),
    Command(
        name="listkg",
        module="reflexive_listkg",
        description="Generate or decode Reflexive registration material.",
        aliases=("reflexive-listkg",),
    ),
    Command(
        name="unpack-mpress",
        module="unpack_mpress",
        description="Dump and rebuild MPRESS-packed PE files.",
        aliases=("unpack-mpress-pe",),
    ),
    Command(
        name="extract-installer",
        module="extract_reflexive_smart_installer",
        description="Extract Reflexive smart installers.",
        aliases=("extract-reflexive-smart-installer",),
    ),
    Command(
        name="extract-rutracker-installer",
        module="extract_rutracker_reflexive_installer",
        description="Extract the rutracker Reflexive installer corpus.",
        aliases=("extract-rutracker-reflexive-installer",),
    ),
    Command(
        name="wrapper-versions",
        module="generate_reflexive_wrapper_versions",
        description="Scan wrapper binaries and summarize version families.",
        aliases=("generate-reflexive-wrapper-versions",),
    ),
    Command(
        name="wrapper-inventory",
        module="generate_reflexive_wrapper_inventory",
        description="Build a wrapper inventory for an extracted corpus.",
        aliases=("generate-reflexive-wrapper-inventory",),
    ),
    Command(
        name="unwrapper-sweep",
        module="generate_reflexive_unwrapper_sweep",
        description="Run the full static unwrapper sweep.",
        aliases=("generate-reflexive-unwrapper-sweep",),
    ),
    Command(
        name="unwrapper-report",
        module="generate_reflexive_unwrapper_report",
        description="Render the unwrapper coverage report.",
        aliases=("generate-reflexive-unwrapper-report",),
    ),
    Command(
        name="game-list",
        module="generate_game_list",
        description="Generate a game list from an extracted corpus.",
        aliases=("generate-game-list",),
    ),
    Command(
        name="native-registration-scan",
        module="generate_native_registration_scan",
        description="Scan binaries for native registration signals.",
        aliases=("generate-native-registration-scan",),
    ),
    Command(
        name="compare-unwrapped",
        module="compare_unwrapped_corpus_versions",
        description="Compare unwrapped corpora across sources.",
        aliases=("compare-unwrapped-corpus-versions",),
    ),
    Command(
        name="rutracker-game-list",
        module="generate_rutracker_game_list",
        description="Generate the rutracker installer-derived game list.",
        aliases=("generate-rutracker-game-list",),
    ),
    Command(
        name="rutracker-probe-report",
        module="generate_rutracker_probe_report",
        description="Build the rutracker probe report.",
        aliases=("generate-rutracker-probe-report",),
    ),
    Command(
        name="rutracker-publisher-attribution",
        module="generate_rutracker_publisher_attribution",
        description="Build the rutracker publisher attribution report.",
        aliases=("generate-rutracker-publisher-attribution",),
    ),
    Command(
        name="rutracker-engine-report",
        module="generate_rutracker_engine_report",
        description="Build the rutracker game engine report.",
        aliases=("generate-rutracker-engine-report",),
    ),
)

COMMAND_INDEX = {
    alias: command
    for command in COMMANDS
    for alias in (command.name, *command.aliases)
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

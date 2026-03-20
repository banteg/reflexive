from reflexive.cli import COMMAND_INDEX, format_help


def test_help_uses_renamed_primary_commands() -> None:
    help_text = format_help()

    assert "  patch " in help_text
    assert "  unwrap " in help_text
    assert "  keygen " in help_text
    assert "  extract " in help_text
    assert "  extract-repack " in help_text
    assert "  download " in help_text
    assert "  unpack-mpress " in help_text
    assert "  installer-snapshot " not in help_text
    assert "  integrated-wrappers " not in help_text
    assert "  key-inventory " not in help_text
    assert "Internal analysis/report commands remain callable" in help_text
    assert "patch-exe" not in help_text
    assert "unwrap-wrapper" not in help_text
    assert "listkg" not in help_text


def test_only_canonical_command_names_are_registered() -> None:
    assert COMMAND_INDEX["patch"].name == "patch"
    assert COMMAND_INDEX["unwrap"].name == "unwrap"
    assert COMMAND_INDEX["keygen"].name == "keygen"
    assert COMMAND_INDEX["download"].name == "download"
    assert COMMAND_INDEX["installer-snapshot"].name == "installer-snapshot"
    assert COMMAND_INDEX["integrated-wrappers"].name == "integrated-wrappers"
    assert COMMAND_INDEX["key-inventory"].name == "key-inventory"
    assert "wrapper-versions" not in COMMAND_INDEX
    assert "wrapper-inventory" not in COMMAND_INDEX
    assert "unwrapper-report" not in COMMAND_INDEX
    assert "game-list" not in COMMAND_INDEX
    assert "rutracker-game-list" not in COMMAND_INDEX
    assert "rutracker-probe-report" not in COMMAND_INDEX
    assert "rutracker-publisher-attribution" not in COMMAND_INDEX
    assert "rutracker-engine-report" not in COMMAND_INDEX
    assert "patch-exe" not in COMMAND_INDEX
    assert "unwrap-wrapper" not in COMMAND_INDEX
    assert "listkg" not in COMMAND_INDEX

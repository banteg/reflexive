from reflexive.cli import COMMAND_INDEX, format_help


def test_help_uses_renamed_primary_commands() -> None:
    help_text = format_help()

    assert "  patch " in help_text
    assert "  unwrap " in help_text
    assert "  keygen " in help_text
    assert "  integrated-wrappers " in help_text
    assert "patch-exe" not in help_text
    assert "unwrap-wrapper" not in help_text
    assert "listkg" not in help_text


def test_only_canonical_command_names_are_registered() -> None:
    assert COMMAND_INDEX["patch"].name == "patch"
    assert COMMAND_INDEX["unwrap"].name == "unwrap"
    assert COMMAND_INDEX["keygen"].name == "keygen"
    assert COMMAND_INDEX["integrated-wrappers"].name == "integrated-wrappers"
    assert "patch-exe" not in COMMAND_INDEX
    assert "unwrap-wrapper" not in COMMAND_INDEX
    assert "listkg" not in COMMAND_INDEX

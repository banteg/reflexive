from reflexive.cli import COMMAND_INDEX, format_help


def test_help_uses_renamed_primary_commands() -> None:
    help_text = format_help()

    assert "  patch " in help_text
    assert "  unwrap " in help_text
    assert "  keygen " in help_text
    assert "patch-exe" not in help_text
    assert "unwrap-wrapper" not in help_text
    assert "listkg" not in help_text


def test_old_command_names_remain_supported_as_aliases() -> None:
    assert COMMAND_INDEX["patch"].name == "patch"
    assert COMMAND_INDEX["patch-exe"].name == "patch"
    assert COMMAND_INDEX["unwrap"].name == "unwrap"
    assert COMMAND_INDEX["unwrap-wrapper"].name == "unwrap"
    assert COMMAND_INDEX["keygen"].name == "keygen"
    assert COMMAND_INDEX["listkg"].name == "keygen"

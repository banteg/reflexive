# Keygen fallback

[reflexive_listkg.py](/Users/banteg/dev/banteg/reflexive/src/reflexive/reflexive_listkg.py) is a pure-Python fallback for the unpacked `listkg` v3.22 `E`-type Reflexive keygen.

It reproduces the key path recovered from [listkg.unpacked.exe](/Users/banteg/dev/banteg/reflexive/artifacts/rutracker/_Crack/listkg_1421_by_russiankid/listkg.unpacked.exe):

- normalize typed product codes by stripping ` ,.'" - /`
- require an `E`-type prefix
- ignore the second character and the final two characters
- base32-decode the remaining payload with the Reflexive alphabet `ABCDEFGHIJKLMNOPQRSTUVWXYZ345679`
- recover the game id and registration groups from the decoded decimal string
- build the registration code with the same CRC32-based formatting used by the keygen
- generate the unlock code with the per-game modulus/exponent data from the checked-in recovered [list.txt](/Users/banteg/dev/banteg/reflexive/docs/generated/rutracker/list.txt)

## Historical Context

The local Ru.Board dump at [artifacts/ruboard](/Users/banteg/dev/banteg/reflexive/artifacts/ruboard) matches the recovered binary well:

- `listkg` belongs to the post-2007 per-game key era, not the older universal-keygen era
- the shared list format is exactly the structure the binary consumes:
  - `Game Name|GameID|RSA modulus N|private exponent D|`
- the later keygen builds added bulk `.reg` generation for all known games, which corresponds to
  the large-button behavior seen in the unpacked UI and supported by `--all`

This matters because the script is not just emulating one GUI sample. It is implementing the
community-maintained per-game keygen model described in the historical threads.

The repository now keeps two distinct list files:

- the historical crack artifact at [artifacts/rutracker/_Crack/listkg_1421_by_russiankid/list.txt](/Users/banteg/dev/banteg/reflexive/artifacts/rutracker/_Crack/listkg_1421_by_russiankid/list.txt)
- the recovered RuTracker default at [docs/generated/rutracker/list.txt](/Users/banteg/dev/banteg/reflexive/docs/generated/rutracker/list.txt)

`uv run reflexive keygen ...` now defaults to the recovered list so missing, mismatched, and corrected rows work out of the box for the RuTracker corpus.

Examples:

```bash
uv run reflexive keygen EACFPXKUCGKWHJGEEKTYAA
```

```bash
uv run reflexive keygen EACFPXKUCGKWHJGEEKTYAA --all --reg-out /tmp/reflexive.reg
```

Synthetic test code generation:

```bash
uv run reflexive keygen --synthesize --game-id 66 --groups 1,2,3,4,5
```

Synthetic `B`-revision product code generation:

```bash
uv run reflexive keygen --synthesize --game-id 53 --groups 1,2,3,4,5 --revision B
```

That synthetic mode is useful for sanity-checking the parser and generator path because the original binary ignores the second character and the final two characters of the typed `E`-type code.

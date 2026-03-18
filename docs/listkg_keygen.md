# listkg keygen fallback

[scripts/reflexive_listkg.py](/Users/banteg/dev/banteg/reflexive/scripts/reflexive_listkg.py) is a pure-Python fallback for the unpacked `listkg` v3.22 `E`-type Reflexive keygen.

It reproduces the key path recovered from [listkg.unpacked.exe](/Users/banteg/dev/banteg/reflexive/artifacts/rutracker/_Crack/listkg_1421_by_russiankid/listkg.unpacked.exe):

- normalize typed product codes by stripping ` ,.'" - /`
- require an `E`-type prefix
- ignore the second character and the final two characters
- base32-decode the remaining payload with the Reflexive alphabet `ABCDEFGHIJKLMNOPQRSTUVWXYZ345679`
- recover the game id and registration groups from the decoded decimal string
- build the registration code with the same CRC32-based formatting used by the keygen
- generate the unlock code with the per-game modulus/exponent data from [list.txt](/Users/banteg/dev/banteg/reflexive/artifacts/rutracker/_Crack/listkg_1421_by_russiankid/list.txt)

Examples:

```bash
uv run scripts/reflexive_listkg.py EACFPXKUCGKWHJGEEKTYAA
```

```bash
uv run scripts/reflexive_listkg.py EACFPXKUCGKWHJGEEKTYAA --all --reg-out /tmp/reflexive.reg
```

Synthetic test code generation:

```bash
uv run scripts/reflexive_listkg.py --synthesize --game-id 66 --groups 1,2,3,4,5
```

That synthetic mode is useful for sanity-checking the parser and generator path because the original binary ignores the second character and the final two characters of the typed `E`-type code.

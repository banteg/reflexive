# Ru.Board

## Source Record

- Source id: `ruboard`
- Repo-local path: `artifacts/ruboard`
- Source type: historical forum dump
- Status: analyzed
- Files:
  - `artifacts/ruboard/reflexive2005.html`
  - `artifacts/ruboard/reflexive2008.html`

## Scope

This source is not an installer corpus. It is a local HTML dump of long-running Reflexive threads on
Ru.Board, used here as historical context for the wrapper, unwrapper, and keygen work.

The dump is useful because it preserves:

- the evolution of community tools around Reflexive wrappers
- the shift from simple `RWG` unwrapping to per-game key generation
- the meaning of the `listkg_*_by_russiankid` tool family and its list format
- later archival discussion tying specific patchers and keygens to wrapper-version ranges

## Historical Findings

The local dump supports the following working timeline.

### 2005: RWG-first unwrapping

- `RWG` files were understood as the original game executables wrapped by a small Reflexive loader.
- Early community tooling focused on decrypting `RWG -> EXE`, often removing the only meaningful
  registration barrier for a large fraction of games.
- This matches the current project result that many wrapper roots become playable once the outer
  Reflexive layer is removed.

### 2006: protection split and wrapper evolution

- Ru.Board discussion describes a newer protection family with `Application.dat`, `Arcade.dat`, and
  `ReflexiveArcade.dll`.
- The historical threads treat older and newer product-code families as distinct, with the first
  letter of the code used for routing.
- That lines up with our current wrapper-family split and with the original-installer vs archive
  repack differences.

### 2007: per-game RSA key era

- The forum timeline describes the December 2007 shift away from a truly universal keygen.
- The new model was per-game: the game-side DLL carried a game id plus a public RSA modulus, and
  the community-derived key lists added the corresponding private exponent.
- The thread format matches the recovered `listkg` data exactly:
  - `Game Name|GameID|RSA modulus N|private exponent D|`

This is the key historical explanation for why `listkg` is list-driven and why later Reflexive
support cannot be reduced to one fixed unlock algorithm without per-game material.

### 2008-2010: listkg growth and Mac branch

- The later dump references the `listkg` line format, bulk `.reg` generation, and ongoing list
  growth into the thousands of games.
- It also describes Mac support via `GameCenterSolution.dylib`, which is the historical equivalent
  of extracting key material from the Windows `ReflexiveArcade.dll` family.
- Later versions moved beyond the small-AID assumptions of early builds, which explains the
  long-lived `listkg_10xx` through `listkg_16xx` series present in the patch corpus.

## Project Implications

- The current unwrapper direction is historically sound: for many games, removing the wrapper is the
  right solution and no keygen is needed afterward.
- The remaining `dll_only_with_application_dat` and integrated-wrapper roots are historically the
  cases where a keygen or shim path still matters.
- The recovered `listkg` binary and [src/reflexive/keygen.py](/Users/banteg/dev/banteg/reflexive/src/reflexive/keygen.py) fit the documented post-2007 per-game RSA model, not the earlier universal-keygen model.
- The `list.txt` files should be treated as a community-maintained `(name, game id, modulus, private
  exponent)` database, not just a UI game list.
- Historical discussion of wrapper-version ranges such as `167-184` is consistent with the
  launcher-build observations already recorded in `docs/generated/archive/wrapper_versions.md`.

## Current Use In This Repo

This source should be used for:

- historical attribution and timeline notes
- validating the interpretation of `RWG`, wrapper `.exe`, and `.dll` roles
- explaining why `listkg` needs per-game key material
- guiding future work on unsupported wrapper families and any Mac-oriented follow-up

This source should not be used for:

- exact provenance claims for individual installers
- assuming every forum-era tool is preserved or bit-identical to the local copies
- replacing direct binary analysis when an implementation detail can be recovered locally

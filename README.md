# reflexive

Game preservation toolkit for [Reflexive Arcade](https://en.wikipedia.org/wiki/Reflexive_Entertainment) titles — a casual games publisher and download portal active from the early 2000s through ~2010. Reflexive wrapped third-party games in a registration shell before distributing them. The service is long defunct, but the wrapped executables survive in archived collections.

This project provides tools to make those games playable again:

- Recovered RSA key material for ~1400 titles
- A static unwrapper that extracts bare game executables from Reflexive wrappers
- An exe patcher that bypasses the registration shell in-place
- A keygen that generates valid registration and unlock codes

## Installation

```
uv add reflexive
```

Or install from source:

```
git clone https://github.com/banteg/reflexive
cd reflexive
uv sync
```

## Usage

### Generate registration codes

Given a product code (printed on the game's purchase confirmation or embedded in the wrapper), generate the registration and unlock codes:

```
reflexive keygen EACFPXKUCGKWHJGEEKTYAA
```

Generate keys for every known game at once and export a `.reg` file:

```
reflexive keygen EACFPXKUCGKWHJGEEKTYAA --all --reg-out keys.reg
```

### Unwrap a game executable

Strip the Reflexive wrapper to recover the original game exe. This is the cleanest approach — the output is the bare game with no wrapper code left:

```
reflexive unwrap --extracted-root path/to/extracted/corpus "Game Name"
```

### Patch a wrapper exe

Patch a Reflexive wrapper executable in-place to bypass registration. Use this when unwrapping isn't possible (e.g. integrated wrappers):

```
reflexive patch path/to/game.exe
```

## Coverage

From the two analyzed corpora (Archive.org repack and RuTracker anthology):

- ~1650 games successfully unwrapped out of ~1700 wrapper roots
- ~1400 RSA key rows recovered from shipped DLLs via modulus factoring
- 0 remaining execution errors in the unwrapper sweep

## Technical notes

- [Embedded key reconstruction](docs/notes/embedded_key_reconstruction.md) — how branded RSA keys are recovered from shipped DLLs
- [Keygen internals](docs/notes/listkg_keygen.md) — how the registration and unlock code generation works
- [Generated reports](docs/generated/index.md) — machine-generated analysis of the wrapped game corpora
- [Provenance](docs/provenance/index.md) — source records and historical context

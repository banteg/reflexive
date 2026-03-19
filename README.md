# reflexive

Game preservation toolkit for [Reflexive Arcade](https://en.wikipedia.org/wiki/Reflexive_Entertainment) titles — a casual games publisher and download portal active from the early 2000s through ~2010. Reflexive wrapped third-party games in a registration shell before distributing them. The service is long defunct, but the wrapped executables survive in archived collections.

This project provides tools to make those games playable again:

- Recovered RSA key material for ~1400 titles
- A static unwrapper that extracts bare game executables from Reflexive wrappers
- An exe patcher that bypasses the registration shell in-place
- A keygen that generates valid registration and unlock codes

## Installation

Install as a tool:

```
uv tool install git+https://github.com/banteg/reflexive
```

Or clone and run directly:

```
git clone https://github.com/banteg/reflexive
cd reflexive
uv run reflexive --help
```

## Usage

### Generate registration codes

In the Reflexive launcher, click "Already Paid", then choose "I'm not connected to the internet", copy the product code, then run:

```
reflexive keygen EAYO-6RIG-MYJ1-1
```

Then paste the unlock code and press "Submit"

Generate keys for every known game at once and export a `.reg` file.
Knowing a single product is sufficient to derive unlock codes for the entire collection.

```
reflexive keygen EAYO-6RIG-MYJ1-1 --all --reg-out keys.reg
```

### Unwrap a game executable

Strip the Reflexive wrapper to recover the original game exe. This is the cleanest approach — the output is the bare game with no wrapper code left:

```
reflexive unwrap --extracted-root path/to/extracted/corpus "Game Name"
```

Note that several games integrate Reflexive libraries right into the game and this method will not work for them.

### Patch a wrapper exe

Patch a Reflexive wrapper executable in-place to bypass registration. Use this when unwrapping isn't possible:

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

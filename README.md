# reflexive

Game preservation toolkit for [Reflexive Arcade](https://en.wikipedia.org/wiki/Reflexive_Entertainment) titles. Reflexive Entertainment was a prominent casual-games publisher and download portal in the 2000s, distributing both its own releases and a large catalog of third-party Windows games through a branded installer and registration stack. That service is long defunct, but the wrapped executables and setup installers survive in archived collections.

This project provides tools to make those games playable again:

- Recovered RSA key material for 1,653 RuTracker titles
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

### Extract installers

Download a single RuTracker installer from the mirror:

```
reflexive download "Air Strike 2"
```

For the full RuTracker corpus, prefer the torrent instead of mirror-downloading hundreds of individual installers.

Extract a single installer into an installed game tree:

```
reflexive extract AlienShooterSetup.exe
```

Extract and unwrap in one step:

```
reflexive extract AlienShooterSetup.exe --unwrap
```

Extract the entire corpus:

```
reflexive extract --all path/to/installers
reflexive extract --all path/to/installers --unwrap
```

Resume an interrupted batch run without redoing completed work:

```
reflexive extract --all path/to/installers --unwrap --keep-extracted --skip-existing
```

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

Note that some games integrate the Reflexive binding layer right into the main game exe, so this method will not work for them.

### Patch a wrapper exe

Patch a Reflexive wrapper executable in-place to bypass registration. Use this when unwrapping isn't possible:

```
reflexive patch path/to/game.exe
```

## Coverage

From the RuTracker corpus, which is the main source this project targets:

- `1661 / 1697` wrapper roots statically unwrapped
- `1653` branded key rows recovered and available to `keygen`
- `36` unwrap roots still unsupported
- `12` likely integrated main-exe wrappers identified
- `0` execution errors in the unwrapper sweep

## Technical notes

- [Embedded key reconstruction](docs/notes/embedded_key_reconstruction.md) — how branded RSA keys are recovered from shipped DLLs
- [Keygen internals](docs/notes/listkg_keygen.md) — how the registration and unlock code generation works
- [Integrated wrappers report](docs/generated/rutracker/integrated_wrappers.md) — titles where the Reflexive binding layer appears to be fused into the main exe
- [Generated reports](docs/generated/index.md) — machine-generated analysis of the wrapped game corpora
- [Provenance](docs/provenance/index.md) — source records and historical context

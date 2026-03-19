# Integrated Reflexive Wrappers

Generated from `artifacts/extracted/rutracker`.

## Methodology

- Structural filter: Select effective unwrap roots where the unwrapper has no safe strategy, the primary wrapper binary is the top-level EXE, there is no Reflexive helper EXE, no launcher .exe.BAK, no encrypted child payload, and no RAW_002 wrapper config.
- Binding filter: Treat the top-level EXE as an integrated Reflexive wrapper when it carries either a direct Reflexive binding reference (ReflexiveArcade.dll plus one or more radll_* export-name strings) or the stronger dynamic-loader pattern that also references LoadLibrary* and GetProcAddress.
- Interpretation: These roots are not peelable classic wrappers; the game executable itself appears to host the Reflexive binding layer.

## Summary

- Effective unwrap roots scanned: 638
- Structural candidates: 12
- Likely integrated wrappers: 12
- Uncertain candidates: 0
- Layout counts:
  - `dll_only_with_application_dat`: 6
  - `other`: 6
- Binding modes:
  - `dynamic_loader`: 12

## Likely Integrated Roots

| Root | Layout | Main EXE | Binding | App ID | Rev | radll_* |
| --- | --- | --- | --- | ---: | --- | ---: |
| `Alien Sky` | `other` | `AlienSky.exe` | `dynamic_loader` | 90 | `A` | 17 |
| `Around 3 D` | `dll_only_with_application_dat` | `around.exe` | `dynamic_loader` | 115 | `B` | 25 |
| `Atomaders` | `other` | `Atomaders.exe` | `dynamic_loader` | 60 | `A` | 17 |
| `Ball Game` | `dll_only_with_application_dat` | `BallGame.exe` | `dynamic_loader` | 45 | `B` | 17 |
| `Bugatron` | `other` | `Bug3D.exe` | `dynamic_loader` | 51 | `B` | 17 |
| `Colony` | `other` | `Colony.exe` | `dynamic_loader` | 26 | `A` | 17 |
| `Crazy Computers` | `dll_only_with_application_dat` | `CrazyComputers.exe` | `dynamic_loader` | 59 | `B` | 17 |
| `Digger` | `dll_only_with_application_dat` | `digger.exe` | `dynamic_loader` | 22 | `A` | 17 |
| `Docker` | `other` | `docker.exe` | `dynamic_loader` | 27 | `B` | 17 |
| `FCF` | `dll_only_with_application_dat` | `FiveCardFrenzy.exe` | `dynamic_loader` | 40 | `A` | 17 |
| `Flip Words` | `other` | `FlipWords.exe` | `dynamic_loader` | 91 | `B` | 17 |
| `GDI Test App` | `dll_only_with_application_dat` | `GDITestApp.exe` | `dynamic_loader` | 6 | `A` | 18 |

# Reflexive Key Inventory (RuTracker)

- Extracted root: `artifacts/extracted/rutracker`
- Support DLLs scanned: 1697
- App ids recovered: 1653
- Public keys recovered: 1653
- Private exponents available: 1653
- Factored private exponents: 1653
- Public modulus matches in `list.txt`: 1152
- Exact `list.txt` matches: 1151
- Records with extraction errors: 45
- Records missing from `list.txt`: 232
- Records mismatching `list.txt`: 270

## Key Revisions

| Revision | Count |
| --- | ---: |
| A | 1172 |
| B | 481 |

## Private Exponent Sources

| Source | Count |
| --- | ---: |
| historical_list | 1150 |
| msieve | 503 |

## Factoring Backends

| Backend | Count |
| --- | ---: |
| msieve | 1653 |

## Historical Verification

- Historical rows re-factored: 1151
- Matches: 1150
- Mismatches: 1

| Game | App ID | Historical D | Factored D |
| --- | ---: | --- | --- |
| Fiber Twig | 130 | 237F9D49165AED0BB70F46ED61D7C57D3FDA71 | 12A629B7CC94CC5EEEFAD43C72570C981F9D41 |

## Exact Matches

| Game | App ID | Revision | Modulus | D | Source |
| --- | ---: | --- | --- | --- | --- |
| Crimsonland | 9 | B | 312E4B27EC6596D3CF0CE73EAB3E8007E21F21 | 172F3AB0DC695BBC0815E2EED5C6CBEE1CC541 | historical_list |
| Collapse | 10 | A | 369CC183478E9CA26F63A38FA47E1BA26DB413 | D39E9A3E1B0A83EAEB7DE646921B839A5F001 | historical_list |
| Mahjong | 11 | B | 3137AE48A675E7F229742C2D0C0AA910449BB3 | 2CA50D7AE9445AB9D7C3BE318E97A11B3285C1 | historical_list |
| Glinx | 12 | A | 33E271BAF3EAA5F0D6506D8A705E62E73CC03F | 135262F4325DD20A4C6026CA0C69AB876D8341 | historical_list |
| Text Twist | 13 | B | 30172E99B5E4CD71CA6AA8062EF8E1BD85DFBF | 35ECC8C473C26CDCFC1DAEE123EE1FCB53101 | historical_list |
| Feed The Snake | 17 | B | 2D348C06E5D82C36886DEAA6AE8784B4773E97 | 16D9C10E9B90B288BE5741A669F7F16DE115C1 | historical_list |
| Blox World | 18 | A | 2FC1659F20B50D02417A027F27DEAB814FF3CF | AEF9EF5F1E7843320083FD8025447A80B1401 | historical_list |
| Gold Sprinter | 20 | A | 389BF2592129901F87C159591B145DA1FE7A25 | 3203DE904F1378C9D2CB7BEC2CBB9205491195 | historical_list |
| Digger | 22 | A | 343A575F59F3051ADB598A127744A17167F2C5 | 22AB57B484113E2245CFD6577D90B4D1578B5 | historical_list |
| Grump | 23 | B | 2FB76B14C5075A0B67D13AC112BF77E3B019F7 | 2CEED9C53B2C8B1C865FB60257ED6CD5ED57E1 | historical_list |
| Speed | 24 | A | 375CDF58433905685AC967F30547A30B30E417 | 18BDC07249586A3A4091AA156ADFDF71C55381 | historical_list |
| Recharge | 25 | A | 36C7F843AC537C1AF0BBFD2C58D243A88A1933 | 2E9720249E195AC1A6D3FE244F9A510AE36981 | historical_list |
| Colony | 26 | A | 3389EFDBEB2B7F538C81ACC1149AF299F85685 | 1C8448096118123D824B13C461DE56E0A09AC1 | historical_list |
| Docker | 27 | B | 341617FA454E1597DEC54EC42EC2186B001499 | 2C6C5780ED911E5B8BE8D87FE94EB5FB12FFFD | historical_list |
| Triptych | 28 | A | 32D173B63AC63931E654FC2049E9F7A5CC6453 | EC22781BFD5FB9C534D2CCA22F2FE1B6CE7F9 | historical_list |
| Ricochet | 29 | B | 29648D0C66450BA31B6E9F919F8853C5BF3C37 | 106976E780B145B0F14D6C36B14B84DB3BC9E1 | historical_list |
| Swarm | 30 | A | 2A078B258FFA1AAA5DDF363E7009257ECB4721 | 56EBA2E9DC08F27CC3EBBB47F98DBD78CD6CD | historical_list |
| FCF | 40 | A | 31052FCC573EB4ECF22555B6AC019478B52C59 | 126367B2B7678666FBC94A40E025C9008AEE81 | historical_list |
| LSP | 41 | B | 2F07A51004377BEA6E12BC751CF2C20986C671 | 1B0814DAF8E17F4B06C3BF407EF46840FEC8C5 | historical_list |
| Aqua Bubble | 42 | A | 2FC6093525522CA292D699B59FF9B0EBE7D049 | 21A8D74DF1A8AF3830516D30F53574873F8BFD | historical_list |

## Extraction Failures

| DLL | Errors |
| --- | --- |
| `artifacts/extracted/rutracker/Fiber Twig/ReflexiveArcade/ReflexiveArcade.dll` | historical private exponent failed RSA verification; using factored replacement |
| `artifacts/extracted/rutracker/Bejeweled 2/ReflexiveArcade/ReflexiveArcade.dll` | missing unittest_GetBrandedApplicationID export; missing Decryption Key Data string |
| `artifacts/extracted/rutracker/Alpha Ball/bin/ReflexiveArcade/ReflexiveArcade.dll` | missing unittest_GetBrandedApplicationID export; missing Decryption Key Data string |
| `artifacts/extracted/rutracker/Blowfish/jre14202redist/bin/ReflexiveArcade/ReflexiveArcade.dll` | missing unittest_GetBrandedApplicationID export; missing Decryption Key Data string |
| `artifacts/extracted/rutracker/Bounce Out Blitz/ReflexiveArcade/ReflexiveArcade.dll` | missing unittest_GetBrandedApplicationID export; missing Decryption Key Data string |
| `artifacts/extracted/rutracker/Bursting Bubbles/ReflexiveArcade/ReflexiveArcade.dll` | missing unittest_GetBrandedApplicationID export; missing Decryption Key Data string |
| `artifacts/extracted/rutracker/Chuzzle/ReflexiveArcade/ReflexiveArcade.dll` | missing unittest_GetBrandedApplicationID export; missing Decryption Key Data string |
| `artifacts/extracted/rutracker/Collapse Crunch/ReflexiveArcade/ReflexiveArcade.dll` | missing unittest_GetBrandedApplicationID export; missing Decryption Key Data string |
| `artifacts/extracted/rutracker/Crazy Coins/ReflexiveArcade/ReflexiveArcade.dll` | missing unittest_GetBrandedApplicationID export; missing Decryption Key Data string |
| `artifacts/extracted/rutracker/Crystal Path/ReflexiveArcade/ReflexiveArcade.dll` | missing unittest_GetBrandedApplicationID export; missing Decryption Key Data string |
| `artifacts/extracted/rutracker/Cubis Gold/ReflexiveArcade/ReflexiveArcade.dll` | missing unittest_GetBrandedApplicationID export; missing Decryption Key Data string |
| `artifacts/extracted/rutracker/Freak Out Gold/ReflexiveArcade/ReflexiveArcade.dll` | missing unittest_GetBrandedApplicationID export; missing Decryption Key Data string |
| `artifacts/extracted/rutracker/Gearz/ReflexiveArcade/ReflexiveArcade.dll` | missing unittest_GetBrandedApplicationID export; missing Decryption Key Data string |
| `artifacts/extracted/rutracker/Iggle Pop/ReflexiveArcade/ReflexiveArcade.dll` | missing unittest_GetBrandedApplicationID export; missing Decryption Key Data string |
| `artifacts/extracted/rutracker/Incredible Ink/ReflexiveArcade/ReflexiveArcade.dll` | missing unittest_GetBrandedApplicationID export; missing Decryption Key Data string |
| `artifacts/extracted/rutracker/Insaniquarium Deluxe/ReflexiveArcade/ReflexiveArcade.dll` | missing unittest_GetBrandedApplicationID export; missing Decryption Key Data string |
| `artifacts/extracted/rutracker/Marble Match/ReflexiveArcade/ReflexiveArcade.dll` | missing unittest_GetBrandedApplicationID export; missing Decryption Key Data string |
| `artifacts/extracted/rutracker/Mini Golf Gold/ReflexiveArcade/ReflexiveArcade.dll` | missing unittest_GetBrandedApplicationID export; missing Decryption Key Data string |
| `artifacts/extracted/rutracker/Nook And Cranny/ReflexiveArcade/ReflexiveArcade.dll` | missing unittest_GetBrandedApplicationID export; missing Decryption Key Data string |
| `artifacts/extracted/rutracker/Puzzle Inlay/ReflexiveArcade/ReflexiveArcade.dll` | missing unittest_GetBrandedApplicationID export; missing Decryption Key Data string |
| `artifacts/extracted/rutracker/Regal Solitaire/ReflexiveArcade/ReflexiveArcade.dll` | missing unittest_GetBrandedApplicationID export; missing Decryption Key Data string |
| `artifacts/extracted/rutracker/Super 5 Line Slots/ReflexiveArcade/ReflexiveArcade.dll` | missing unittest_GetBrandedApplicationID export; missing Decryption Key Data string |
| `artifacts/extracted/rutracker/Super Black Jack/ReflexiveArcade/ReflexiveArcade.dll` | missing unittest_GetBrandedApplicationID export; missing Decryption Key Data string |
| `artifacts/extracted/rutracker/Super Collapse/ReflexiveArcade/ReflexiveArcade.dll` | missing unittest_GetBrandedApplicationID export; missing Decryption Key Data string |
| `artifacts/extracted/rutracker/Super Collapse 2/ReflexiveArcade/ReflexiveArcade.dll` | missing unittest_GetBrandedApplicationID export; missing Decryption Key Data string |
| `artifacts/extracted/rutracker/Super Gem Drop/ReflexiveArcade/ReflexiveArcade.dll` | missing unittest_GetBrandedApplicationID export; missing Decryption Key Data string |
| `artifacts/extracted/rutracker/Super Glinx/ReflexiveArcade/ReflexiveArcade.dll` | missing unittest_GetBrandedApplicationID export; missing Decryption Key Data string |
| `artifacts/extracted/rutracker/Super Mahjong/ReflexiveArcade/ReflexiveArcade.dll` | missing unittest_GetBrandedApplicationID export; missing Decryption Key Data string |
| `artifacts/extracted/rutracker/Super Nisqually/ReflexiveArcade/ReflexiveArcade.dll` | missing unittest_GetBrandedApplicationID export; missing Decryption Key Data string |
| `artifacts/extracted/rutracker/Super Pile Up/ReflexiveArcade/ReflexiveArcade.dll` | missing unittest_GetBrandedApplicationID export; missing Decryption Key Data string |
| `artifacts/extracted/rutracker/Super Popn Drop/ReflexiveArcade/ReflexiveArcade.dll` | missing unittest_GetBrandedApplicationID export; missing Decryption Key Data string |
| `artifacts/extracted/rutracker/Super Solitaire/ReflexiveArcade/ReflexiveArcade.dll` | missing unittest_GetBrandedApplicationID export; missing Decryption Key Data string |
| `artifacts/extracted/rutracker/Super Solitaire 2/ReflexiveArcade/ReflexiveArcade.dll` | missing unittest_GetBrandedApplicationID export; missing Decryption Key Data string |
| `artifacts/extracted/rutracker/Super Solitaire 3/ReflexiveArcade/ReflexiveArcade.dll` | missing unittest_GetBrandedApplicationID export; missing Decryption Key Data string |
| `artifacts/extracted/rutracker/Super Text Twist/ReflexiveArcade/ReflexiveArcade.dll` | missing unittest_GetBrandedApplicationID export; missing Decryption Key Data string |
| `artifacts/extracted/rutracker/Super What Word/ReflexiveArcade/ReflexiveArcade.dll` | missing unittest_GetBrandedApplicationID export; missing Decryption Key Data string |
| `artifacts/extracted/rutracker/Tapa Jam/ReflexiveArcade/ReflexiveArcade.dll` | missing unittest_GetBrandedApplicationID export; missing Decryption Key Data string |
| `artifacts/extracted/rutracker/Top 10 Solitaire/ReflexiveArcade/ReflexiveArcade.dll` | missing unittest_GetBrandedApplicationID export; missing Decryption Key Data string |
| `artifacts/extracted/rutracker/Tower Blaster/ReflexiveArcade/ReflexiveArcade.dll` | missing unittest_GetBrandedApplicationID export; missing Decryption Key Data string |
| `artifacts/extracted/rutracker/Trickor Treat Smash/ReflexiveArcade/ReflexiveArcade.dll` | missing unittest_GetBrandedApplicationID export; missing Decryption Key Data string |

## list.txt Mismatches

| Game | App ID | Modulus Match | D Match | DLL |
| --- | ---: | --- | --- | --- |
| Fiber Twig | 130 | True | False | `artifacts/extracted/rutracker/Fiber Twig/ReflexiveArcade/ReflexiveArcade.dll` |
| Space Taxi 2 | 201 | False | False | `artifacts/extracted/rutracker/Space Taxi 2/ReflexiveArcade/ReflexiveArcade.dll` |
| Snow Ball | 205 | False | False | `artifacts/extracted/rutracker/Snow Ball/ReflexiveArcade/ReflexiveArcade.dll` |
| Spin Win | 207 | False | False | `artifacts/extracted/rutracker/Spin Win/ReflexiveArcade/ReflexiveArcade.dll` |
| Brave Piglet | 211 | False | False | `artifacts/extracted/rutracker/Brave Piglet/ReflexiveArcade/ReflexiveArcade.dll` |
| Global Defense Network | 213 | False | False | `artifacts/extracted/rutracker/Global Defense Network/ReflexiveArcade/ReflexiveArcade.dll` |
| Dr Blobs Organism | 217 | False | False | `artifacts/extracted/rutracker/Dr Blobs Organism/ReflexiveArcade/ReflexiveArcade.dll` |
| Weave Words | 219 | False | False | `artifacts/extracted/rutracker/Weave Words/ReflexiveArcade/ReflexiveArcade.dll` |
| Rival Ball Tournament | 223 | False | False | `artifacts/extracted/rutracker/Rival Ball Tournament/ReflexiveArcade/ReflexiveArcade.dll` |
| River Raider II | 233 | False | False | `artifacts/extracted/rutracker/River Raider II/ReflexiveArcade/ReflexiveArcade.dll` |
| Big Kahuna Words | 239 | False | False | `artifacts/extracted/rutracker/Big Kahuna Words/ReflexiveArcade/ReflexiveArcade.dll` |
| Machine Hell | 243 | False | False | `artifacts/extracted/rutracker/Machine Hell/ReflexiveArcade/ReflexiveArcade.dll` |
| Barnyard Invasion | 245 | False | False | `artifacts/extracted/rutracker/Barnyard Invasion/ReflexiveArcade/ReflexiveArcade.dll` |
| Super Bounce Out | 247 | False | False | `artifacts/extracted/rutracker/Super Bounce Out/ReflexiveArcade/ReflexiveArcade.dll` |
| Jets N Guns | 249 | False | False | `artifacts/extracted/rutracker/Jets N Guns/ReflexiveArcade/ReflexiveArcade.dll` |
| Funny Faces | 251 | False | False | `artifacts/extracted/rutracker/Funny Faces/ReflexiveArcade/ReflexiveArcade.dll` |
| Warblade | 253 | False | False | `artifacts/extracted/rutracker/Warblade/ReflexiveArcade/ReflexiveArcade.dll` |
| Mortimer and the Enchanted Castle | 255 | False | False | `artifacts/extracted/rutracker/Mortimer and the Enchanted Castle/ReflexiveArcade/ReflexiveArcade.dll` |
| ABC Island | 257 | False | False | `artifacts/extracted/rutracker/ABC Island/ReflexiveArcade/ReflexiveArcade.dll` |
| Zzed | 259 | False | False | `artifacts/extracted/rutracker/Zzed/ReflexiveArcade/ReflexiveArcade.dll` |
| Zero Count | 261 | False | False | `artifacts/extracted/rutracker/Zero Count/ReflexiveArcade/ReflexiveArcade.dll` |
| 5 Spots II | 263 | False | False | `artifacts/extracted/rutracker/5 Spots II/ReflexiveArcade/ReflexiveArcade.dll` |
| Add Em Up | 265 | False | False | `artifacts/extracted/rutracker/Add Em Up/ReflexiveArcade/ReflexiveArcade.dll` |
| Fresco Wizard | 267 | False | False | `artifacts/extracted/rutracker/Fresco Wizard/ReflexiveArcade/ReflexiveArcade.dll` |
| Wonderland Secret Worlds | 271 | False | False | `artifacts/extracted/rutracker/Wonderland Secret Worlds/ReflexiveArcade/ReflexiveArcade.dll` |
| Coffee Tycoon | 273 | False | False | `artifacts/extracted/rutracker/Coffee Tycoon/ReflexiveArcade/ReflexiveArcade.dll` |
| Charm Tale | 275 | False | False | `artifacts/extracted/rutracker/Charm Tale/ReflexiveArcade/ReflexiveArcade.dll` |
| Super Cubes | 277 | False | False | `artifacts/extracted/rutracker/Super Cubes/ReflexiveArcade/ReflexiveArcade.dll` |
| Pizza Frenzy | 279 | False | False | `artifacts/extracted/rutracker/Pizza Frenzy/ReflexiveArcade/ReflexiveArcade.dll` |
| Action Memory | 281 | False | False | `artifacts/extracted/rutracker/Action Memory/ReflexiveArcade/ReflexiveArcade.dll` |
| Glow Worm | 285 | False | False | `artifacts/extracted/rutracker/Glow Worm/ReflexiveArcade/ReflexiveArcade.dll` |
| Wild West Wendy | 291 | False | False | `artifacts/extracted/rutracker/Wild West Wendy/ReflexiveArcade/ReflexiveArcade.dll` |
| Tennis Titans | 295 | False | False | `artifacts/extracted/rutracker/Tennis Titans/ReflexiveArcade/ReflexiveArcade.dll` |
| Arkout 3 D | 297 | False | False | `artifacts/extracted/rutracker/Arkout 3 D/ReflexiveArcade/ReflexiveArcade.dll` |
| Gamehouse Word Collection | 299 | False | False | `artifacts/extracted/rutracker/Gamehouse Word Collection/ReflexiveArcade/ReflexiveArcade.dll` |
| Amazon Quest | 305 | False | False | `artifacts/extracted/rutracker/Amazon Quest/ReflexiveArcade/ReflexiveArcade.dll` |
| Kick Shot Pool | 307 | False | False | `artifacts/extracted/rutracker/Kick Shot Pool/ReflexiveArcade/ReflexiveArcade.dll` |
| Fruit Lockers | 309 | False | False | `artifacts/extracted/rutracker/Fruit Lockers/ReflexiveArcade/ReflexiveArcade.dll` |
| Fairy Words | 311 | False | False | `artifacts/extracted/rutracker/Fairy Words/ReflexiveArcade/ReflexiveArcade.dll` |
| Slyder Adventures | 313 | False | False | `artifacts/extracted/rutracker/Slyder Adventures/ReflexiveArcade/ReflexiveArcade.dll` |

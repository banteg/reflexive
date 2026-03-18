# Native Registration Signal Scan

Executed against `artifacts/unwrapped/rutracker` using primary output executables from `docs/generated/rutracker/unwrapper_sweep.json`.

This is a heuristic scan for strings that suggest a game may still implement its own
registration, trial, or upsell logic even after Reflexive wrapper removal.

## Summary

- Source: `rutracker` (RuTracker)
- Successful unwrapped roots considered: 1661
- Roots with suspicious native-registration signals: 547
- Missing output executables while scanning: 1
- Suspicious roots by severity:
  - `high`: 59
  - `medium`: 68
  - `low`: 420
- Signal hits by tag:
  - `code_fields`: 57
  - `demo_or_presentation`: 116
  - `registration_state`: 252
  - `serial_or_key`: 118
  - `trial_or_upsell`: 224

## Suspicious Roots

| Root | Severity | Score | Strategy | Output Executable | Signal Tags | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| `Mind Your Marbles` | `high` | `34` | `static` | `Mind Your Marbles.exe` | `code_fields`, `serial_or_key`, `registration_state`, `trial_or_upsell`, `demo_or_presentation` | `After placing your order, you receive a registration code via e-mail or postal mail, which fully unlocks your copy of`<br>`Enter Registration Code`<br>`,This copy of 3D Morris is still unregistered`<br>`How many licenses would you like to order? You need one for each computer that you want to run the full version on.` |
| `Mind Your Marbles Xmas` | `high` | `34` | `static` | `Mind Your Marbles.exe` | `code_fields`, `serial_or_key`, `registration_state`, `trial_or_upsell`, `demo_or_presentation` | `After placing your order, you receive a registration code via e-mail or postal mail, which fully unlocks your copy of`<br>`Enter Registration Code`<br>`,This copy of 3D Morris is still unregistered`<br>`How many licenses would you like to order? You need one for each computer that you want to run the full version on.` |
| `Word Blitz` | `high` | `30` | `direct` | `WordBlitz.exe` | `code_fields`, `serial_or_key`, `registration_state`, `trial_or_upsell` | `You have entered wrong serial number or registration code for 3 times!`<br>`Serial number`<br>`This executable file was created by an UNREGISTERED copy of SWFKit!`<br>`&Buy Now` |
| `Jig Words` | `high` | `27` | `static` | `JigWords.exe` | `code_fields`, `serial_or_key`, `trial_or_upsell`, `demo_or_presentation` | `VAL=ENTER REGISTRATION CODE...`<br>`VAL=Enter your registration key exactly as it was given to you\nwhen you purchased the full version`<br>`Full Version`<br>`VAL=Your photo pack has been successfully submitted to the HipSoft servers.\n\nYou can give out the following web address to download a demo version\nof the game that will allow your photo pack to...` |
| `Ricochet Lost Worlds` | `high` | `27` | `static` | `Ricochet.exe` | `code_fields`, `serial_or_key`, `trial_or_upsell`, `demo_or_presentation` | `Registration Code`<br>`Enter Registration Code`<br>`This feature is only available in the full version of Ricochet Lost Worlds.`<br>`As in "Zax DEMO Version 1.0 Build 345"` |
| `Ricochet Lost Worlds Coke` | `high` | `27` | `static` | `Ricochet.exe` | `code_fields`, `serial_or_key`, `trial_or_upsell`, `demo_or_presentation` | `Registration Code`<br>`Enter Registration Code`<br>`This feature is only available in the full version of Ricochet Lost Worlds.`<br>`As in "Zax DEMO Version 1.0 Build 345"` |
| `Void War` | `high` | `27` | `direct` | `Launch Void War.exe` | `code_fields`, `serial_or_key`, `trial_or_upsell`, `demo_or_presentation` | `Enter registration code:`<br>`Enter registration code:`<br>`Purchase the full version for access to more battlefields,`<br>`This battlefield is not available in the demo version.` |
| `Real Ball` | `high` | `26` | `static` | `realball.exe` | `code_fields`, `registration_state`, `trial_or_upsell`, `demo_or_presentation` | `Your registration code is valid.`<br>`REGISTER NOW`<br>`in the full version of Real Ball`<br>`Demo Version` |
| `Bombard Deluxe` | `high` | `25` | `static` | `Bombard.exe` | `code_fields`, `serial_or_key`, `registration_state` | `You have entered wrong serial number or registration code for 3 times!`<br>`Serial number`<br>`This executable file was created by an UNREGISTERED copy of SWFKit!` |
| `Cafe Mahjongg` | `high` | `25` | `static` | `cafe mahjongg.exe` | `code_fields`, `serial_or_key`, `registration_state` | `You have entered wrong serial number or registration code for 3 times!`<br>`Serial number`<br>`This executable file was created by an UNREGISTERED copy of SWFKit!` |
| `Happy Hour` | `high` | `25` | `static` | `Happy Hour 1.0.1.exe` | `code_fields`, `serial_or_key`, `registration_state` | `You have entered wrong serial number or registration code for 3 times!`<br>`Serial number`<br>`This executable file was created by an UNREGISTERED copy of SWFKit!` |
| `Hawaiian Explorer Pearl Harbor` | `high` | `25` | `static` | `Hawaiian Explorer Pearl Harbor.exe` | `code_fields`, `serial_or_key`, `registration_state` | `You have entered wrong serial number or registration code for 3 times!`<br>`Serial number`<br>`This executable file was created by an UNREGISTERED copy of SWFKit!` |
| `Hawaiian Explorer The Lost Island` | `high` | `25` | `static` | `LostIsland.exe` | `code_fields`, `serial_or_key`, `registration_state` | `You have entered wrong serial number or registration code for 3 times!`<br>`Serial number`<br>`This executable file was created by an UNREGISTERED copy of SWFKit!` |
| `Hidden Expedition Devils Triangle` | `high` | `25` | `static` | `Hidden Expedition - Devils Triangle.exe` | `code_fields`, `serial_or_key`, `registration_state` | `You have entered wrong serial number or registration code for 3 times!`<br>`Serial number`<br>`This executable file was created by an UNREGISTERED copy of SWFKit!` |
| `House Of Wonders The Kitty Kat Wedding` | `high` | `25` | `static` | `HouseOfWonders.exe` | `code_fields`, `serial_or_key`, `registration_state` | `You have entered wrong serial number or registration code for 3 times!`<br>`Serial number`<br>`This executable file was created by an UNREGISTERED copy of SWFKit!` |
| `Mahjong Mania Deluxe` | `high` | `25` | `static` | `Mahjong.exe` | `code_fields`, `serial_or_key`, `registration_state` | `You have entered wrong serial number or registration code for 3 times!`<br>`Serial number`<br>`This executable file was created by an UNREGISTERED copy of SWFKit!` |
| `Mystery Case Files Dire Grove` | `high` | `25` | `static` | `MCF6Standard.exe` | `code_fields`, `serial_or_key`, `registration_state` | `You have entered wrong serial number or registration code for 3 times!`<br>`Serial number`<br>`This executable file was created by an UNREGISTERED copy of SWFKit!` |
| `Totem Treasure` | `high` | `25` | `static` | `PokieMagic_TotemTreasure_BFG.exe` | `code_fields`, `serial_or_key`, `registration_state` | `Please enter registration code (copy and paste):`<br>`Please enter registration code (copy and paste):`<br>`. If you have not registered, please register now. Play the pokies at home!` |
| `Bud Redhead` | `high` | `24` | `static` | `BudRedhead.exe` | `serial_or_key`, `registration_state`, `trial_or_upsell`, `demo_or_presentation` | `key (serial number) which will unlock the full version.`<br>`Unregistered!`<br>`key (serial number) which will unlock the full version.`<br>`This is the end of the DEMO version!` |
| `Electric` | `high` | `24` | `direct` | `Electric.exe` | `serial_or_key`, `registration_state`, `trial_or_upsell`, `demo_or_presentation` | `Serial Number:`<br>`G!Not registered congratulations HS`<br>`Registering high scores is possible in the full version of Electric. To register your current high score, and to access all the other features, please upgrade to the full version by clicking BUY NOW.`<br>`30,You are now playing the demo version of Electric` |
| `Buildalot` | `high` | `23` | `static` | `Buildalot.exe` | `code_fields`, `serial_or_key`, `trial_or_upsell` | `VAL=ENTER REGISTRATION CODE...`<br>`VAL=ENTER YOUR REGISTRATION KEY EXACTLY AS IT WAS GIVEN\nTO YOU WHEN YOU PURCHASED THE FULL VERSION`<br>`Full Version` |
| `Digby's Donuts` | `high` | `23` | `static` | `DigbysDonuts.exe` | `code_fields`, `serial_or_key`, `trial_or_upsell` | `VAL=ENTER REGISTRATION CODE...`<br>`VAL=ENTER YOUR REGISTRATION KEY EXACTLY AS IT WAS GIVEN TO\nYOU WHEN YOU PURCHASED THE FULL VERSION.`<br>`Full Version` |
| `Flip Words 2` | `high` | `23` | `static` | `FlipWords2.exe` | `code_fields`, `serial_or_key`, `trial_or_upsell` | `VAL=ENTER REGISTRATION CODE...`<br>`VAL=ENTER YOUR REGISTRATION KEY EXACTLY AS IT WAS GIVEN TO YOU\nWHEN YOU PURCHASED THE FULL VERSION`<br>`Full Version` |
| `Gem Shop` | `high` | `23` | `static` | `GemShop.exe` | `code_fields`, `serial_or_key`, `trial_or_upsell` | `VAL=ENTER REGISTRATION CODE...`<br>`VAL=Enter your registration key exactly as it was given to you\nwhen you purchased the full version`<br>`Full Version` |
| `Gift Shop` | `high` | `23` | `static` | `GiftShop.exe` | `code_fields`, `serial_or_key`, `trial_or_upsell` | `VAL=ENTER REGISTRATION CODE...`<br>`VAL=Enter your registration key exactly as it was given to you\nwhen you purchased the full version`<br>`Full Version` |
| `Ocean Express` | `high` | `23` | `static` | `OceanExpress.exe` | `code_fields`, `serial_or_key`, `trial_or_upsell` | `VAL=ENTER REGISTRATION CODE...`<br>`VAL=ENTER YOUR REGISTRATION KEY EXACTLY AS IT WAS GIVEN TO YOU\nWHEN YOU PURCHASED THE FULL VERSION`<br>`Full Version` |
| `Bamboozle` | `high` | `22` | `direct` | `bamboozle.exe` | `code_fields`, `registration_state`, `trial_or_upsell` | `Get Registration Code`<br>`Your playtime has expired. If you have enjoyed Bamboozle please Register to play the over 150 puzzles from adventurous locations like 'Under the Ocean' and 'Pyramids Of Egypt.' Registering is insta...`<br>`Buy Now` |
| `Gemsweeper` | `high` | `22` | `static` | `Gemsweeper.exe` | `code_fields`, `registration_state`, `trial_or_upsell` | `The code you entered seems to be an order ID, not a registration code for this game. The registration code is delivered to you in a separate e-mail, which does not contain any order ID like the one...`<br>`unregistered class`<br>`and will therefore not unlock the full version. Please visit` |
| `Ricochet` | `high` | `22` | `static` | `Ricochet.exe` | `code_fields`, `serial_or_key`, `demo_or_presentation` | `Registration Code`<br>`Enter Registration Code`<br>`As in "Zax DEMO Version 1.0 Build 345"` |
| `Rival Ball Tournament` | `high` | `22` | `static` | `RB Tournament.exe` | `code_fields`, `registration_state`, `trial_or_upsell` | `Invalid registration code.`<br>`You have one or more unregistered products.`<br>`You must register RBT Full Version before you can start the game.` |
| `Smash Frenzy` | `high` | `22` | `static` | `SmashFrenzy.exe` | `code_fields`, `registration_state`, `trial_or_upsell` | `Enter you registration code below, please`<br>`UNREGISTERED VERSION`<br>`Unregistred trial version` |
| `Super Cubes` | `high` | `22` | `static` | `SuperCubes.exe` | `code_fields`, `registration_state`, `trial_or_upsell` | `Wrong registration code. Please, check registration information.`<br>`Unregistered version`<br>`5Three easy steps to order Full Version of Super Cubes` |
| `Avernum 5` | `high` | `19` | `static` | `Avernum 5.exe` | `code_fields`, `trial_or_upsell`, `demo_or_presentation` | `When you register Avernum 5, give the registration code (the number above). You will be given a key (a 4 or 5 digit number). Type the number in the text area below to register this copy.`<br>`This is the demo version of the game, which only contains the first section (out of nine). The full version of Avernum 5 is much, much bigger.`<br>`This is the demo version of the game, which only contains the first section (out of nine). The full version of Avernum 5 is much, much bigger.` |
| `Avernum 6` | `high` | `19` | `static` | `Avernum 6.exe` | `code_fields`, `trial_or_upsell`, `demo_or_presentation` | `Registration code: %d`<br>`This is the demo version of the game, which only contains ten percent of the game. The full version of Avernum 6 is much, much bigger.`<br>`This is the demo version of the game, which only contains ten percent of the game. The full version of Avernum 6 is much, much bigger.` |
| `Avernum IV` | `high` | `19` | `static` | `Avernum 4.exe` | `code_fields`, `trial_or_upsell`, `demo_or_presentation` | `When you register Avernum 4, give the registration code (the number above). You will be given a key (a 4 or 5 digit number). Type the number in the text area below to register this copy.`<br>`This is the demo version of the game, which only contains the first fifth or so of the world of Avernum. The full version of Avernum 4 is much, much bigger.`<br>`This is the demo version of the game, which only contains the first fifth or so of the world of Avernum. The full version of Avernum 4 is much, much bigger.` |
| `Passage 3` | `high` | `19` | `static` | `Extra.exe` | `code_fields`, `trial_or_upsell`, `demo_or_presentation` | `UNABLE TO CHECK REGISTRATION CODE!`<br>`ORDER THE FULL VERSION TODAY AND YOU WILL GET...`<br>`DEMO VERSION` |
| `Jungle Heart` | `high` | `18` | `static` | `JungleHeart.exe` | `code_fields`, `serial_or_key` | `XUY 2 REGISTRATION CODE`<br>`JUNGLE HEART: ENTER REGISTRATION CODE` |
| `RIP` | `high` | `18` | `static` | `RIP.exe` | `code_fields`, `serial_or_key` | `RIP: ENTER REGISTRATION CODE`<br>`RIP: ENTER REGISTRATION CODE` |
| `RIP Strike Back` | `high` | `18` | `static` | `RIP.exe` | `code_fields`, `serial_or_key` | `RIP: ENTER REGISTRATION CODE`<br>`RIP: ENTER REGISTRATION CODE` |
| `Astariel` | `medium` | `17` | `static` | `Astariel.exe` | `serial_or_key`, `trial_or_upsell`, `demo_or_presentation` | `Main::Read_Registry_Serial:: Creating a new serial number`<br>`FULL VERSION`<br>`THIS IS A BETA DEMO VERSION OF ASTARIEL` |
| `Hamsterball` | `medium` | `17` | `static` | `Hamsterball.exe` | `serial_or_key`, `trial_or_upsell`, `demo_or_presentation` | `SERIAL NUMBER:`<br>`DID YOU KNOW THAT IF YOU BUY HAMSTERBALL, YOU CAN CONTINUE YOUR TOURNAMENT LATER? YOU CAN BUY NOW, AND PICK UP WHERE YOU LEFT OFF NEXT TIME YOU PLAY! (PRESS CANCEL IF YOU DON'T WANT TO BUY NOW)`<br>`You have reached the end of the demo version of Hamsterball! But, if you buy now, you can continue, right here, right now! Or, click cancel to return to the main menu.` |
| `XAvenger` | `medium` | `17` | `static` | `X-Avenger.exe` | `serial_or_key`, `trial_or_upsell`, `demo_or_presentation` | `Registration Key`<br>`Buy Now`<br>`These Weapons are not available in the Demo version of the game.` |
| `Brickquest` | `medium` | `16` | `static` | `brickquest.exe` | `registration_state`, `trial_or_upsell`, `demo_or_presentation` | `Register now !`<br>`Buy now !`<br>`Not available in demo version` |
| `Delivery King` | `medium` | `16` | `static` | `Delivery King.exe` | `registration_state`, `trial_or_upsell`, `demo_or_presentation` | `CUnregistered version`<br>`ABUY NOW AND GET:`<br>`This is a DEMO version of the game` |
| `Dragons Abode` | `medium` | `16` | `static` | `DA.exe` | `registration_state`, `trial_or_upsell`, `demo_or_presentation` | `UNREGISTERED demo version`<br>`Trial version (timeleft: %s)`<br>`UNREGISTERED demo version` |
| `Gamino` | `medium` | `16` | `static` | `Gamino.exe` | `registration_state`, `trial_or_upsell`, `demo_or_presentation` | `Register now !`<br>`Buy now !`<br>`Welcome to Gamino demo version !` |
| `Pipeline` | `medium` | `16` | `static` | `Pipeline.exe` | `registration_state`, `trial_or_upsell`, `demo_or_presentation` | `System event has not registered a callback function.`<br>`Demo Buy Now`<br>`Text Demo Version` |
| `The Cursed Wheel` | `medium` | `16` | `static` | `tcw.exe` | `registration_state`, `trial_or_upsell`, `demo_or_presentation` | `Cannot remove compression scheme %s; not registered`<br>`The Cursed Wheel - Demo Version - Buy Full Version at www.FunManGames.com`<br>`The Cursed Wheel - Demo Version - Buy Full Version at www.FunManGames.com` |
| `War Chess` | `medium` | `16` | `static` | `WarChess.exe` | `registration_state`, `trial_or_upsell`, `demo_or_presentation` | `Unregistered version. The * features available only to registered users.`<br>`#;Your demo time has expired. Please buy full version. The game is over for now.`<br>`This feature is disabled in demo version.` |
| `Astral Masters` | `medium` | `15` | `static` | `masters.exe` | `serial_or_key`, `registration_state` | `Please enter a valid registration key!`<br>`unregistered` |
| `Break Quest` | `high` | `15` | `static` | `BreakQuest.exe` | `code_fields`, `trial_or_upsell` | `;Type your registration code below to complete the process.`<br>`Full Version data download` |
| `Cactus Bruce` | `high` | `15` | `static` | `Reflexive.exe` | `code_fields`, `trial_or_upsell` | `Please check and re-enter your Serial/Registration codes.`<br>`Full Version` |
| `Druids Battle Of Magic` | `high` | `15` | `static` | `TheDruids.exe` | `code_fields`, `trial_or_upsell` | `6Please, enter your License Name and Registration Code.`<br>`&Buy Now` |
| `Fantastic Farm` | `medium` | `15` | `static` | `Fantastic Farm.exe` | `serial_or_key`, `registration_state` | `Enter Registration Key`<br>`Unregistered error message` |
| `Insaniquarium Deluxe` | `high` | `15` | `static` | `InsaniquariumDeluxe.exe` | `code_fields`, `trial_or_upsell` | `CLICK HERE TO GET REGISTRATION CODE`<br>`Your trial version of Insaniquarium has expired!` |
| `Mr Jones Graveyard Shift` | `medium` | `15` | `static` | `Mr. Jones' Graveyard Shift.exe` | `serial_or_key`, `registration_state` | `Serial Number`<br>`Internal RPC error. Invalid RPC index, function not registered.` |
| `Zuma` | `high` | `15` | `static` | `Zuma.exe` | `code_fields`, `trial_or_upsell` | `CLICK HERE TO GET REGISTRATION CODE`<br>`Your trial version of Zuma has expired!` |
| `Zuma Deluxe` | `high` | `15` | `static` | `Zuma.exe` | `code_fields`, `trial_or_upsell` | `CLICK HERE TO GET REGISTRATION CODE`<br>`Your trial version of Zuma has expired!` |
| `Animal Empire` | `medium` | `13` | `static` | `AnimalEmpire.exe` | `serial_or_key`, `trial_or_upsell` | `After you buy the full version, you will receive a registration key.`<br>`After you buy the full version, you will receive a registration key.` |
| `Brain Booster` | `medium` | `13` | `static` | `brainbooster.exe` | `serial_or_key`, `trial_or_upsell` | `Serial Number:`<br>`buy now` |
| `Dungeon Scroll Gold Edition` | `medium` | `13` | `static` | `game.exe` | `serial_or_key`, `trial_or_upsell` | `Unlock key:`<br>`the full version.` |
| `Fiber Twig` | `medium` | `13` | `static` | `FiberTwig.exe` | `serial_or_key`, `trial_or_upsell` | `This registration key is not valid!`<br>`This is a trial version. You can use it for 14 days or run 14 times (whichever expires first). Registering the game removes all limitation and opens access to all levels. For details see` |
| `Jet Jumper` | `medium` | `13` | `static` | `JJ-Game.exe` | `serial_or_key`, `trial_or_upsell` | `No Processor Serial Number`<br>`ReflexiveArcade Full Version` |
| `Jump Jump Jelly Reactor` | `medium` | `13` | `static` | `JJJR.exe` | `serial_or_key`, `trial_or_upsell` | `Processor Serial Number. The processor supports the 96-bit processor identification number feature and the feature is enabled.`<br>`Buy Now!` |
| `Magic Inlay` | `medium` | `13` | `static` | `MagicInlay.exe` | `serial_or_key`, `trial_or_upsell` | `Enter Registration Key`<br>`This is a trial version. You can use it for 14 days or run 14 times (whichever expires first). Registering the game removes all limitation and opens access to all levels. For details see` |
| `Magic Match` | `medium` | `13` | `static` | `MagicMatch.exe` | `serial_or_key`, `trial_or_upsell` | `Registration Key (serial number):`<br>`Buy Now!` |
| `Mahjong The Endless Journey` | `medium` | `13` | `static` | `MahjongTEJ.exe` | `serial_or_key`, `trial_or_upsell` | `Thank you for purchasing Mahjong, to unlock this full version please enter your serial number. This would have been sent to you after purchase.`<br>`This trial version has now expired, thank you for using our software, if you would like to purchase the full version of this game, which has no time limitations, press the 'buy now' button below.` |
| `Merv Griffins Crosswords` | `medium` | `13` | `static` | `MervGriffinCrosswords.exe` | `serial_or_key`, `trial_or_upsell` | `Serial Number:`<br>`main menu buy and other buttons[#pWhichButton: [#comment: "Which Button:", #default: "Buy Now", #format: #string, #range: ["Buy Now", "Other Games"]]]` |
| `Meteor` | `medium` | `13` | `static` | `Meteor.exe` | `serial_or_key`, `trial_or_upsell` | `After you buy the full version, you will receive a registration key.`<br>`After you buy the full version, you will receive a registration key.` |
| `Puzzle Myth` | `medium` | `13` | `direct` | `PuzzleMyth.exe` | `serial_or_key`, `trial_or_upsell` | `Enter registration key`<br>`This is a trial version. You can use it for 14 days or run 14 times (whichever expires first). Registering the game removes all limitation and opens access to all levels. For details see` |
| `Spellunker` | `medium` | `13` | `static` | `Spellunker.exe` | `serial_or_key`, `trial_or_upsell` | `To protect your purchase, we encrypt any serial number transmissions and/or product downloads. If you download a product, it will remain encrypted on your machine until after the purchase is comple...`<br>`-TRIAL PERIOD EXPIRED- BUY NOW! to continue` |
| `Truffle Tray` | `medium` | `13` | `direct` | `Truffle Tray.exe` | `serial_or_key`, `trial_or_upsell` | `Serial Number:`<br>`Reflexive full version` |
| `Ballhalla` | `medium` | `12` | `static` | `Ballhalla.exe` | `registration_state`, `trial_or_upsell` | `Screen of sprite %s not found! Sprites should be unregistered before the screen is removed.`<br>`Buy Now` |
| `Bejeweled Twist` | `medium` | `12` | `static` | `BejeweledTwist.exe` | `registration_state`, `trial_or_upsell` | `@^FBCD77^Register now for:`<br>`^00FF00^Full Version^FFFFFF^ to` |
| `Bookworm Adventures Astounding Planet` | `medium` | `12` | `static` | `BookwormAdventuresAP.exe` | `registration_state`, `trial_or_upsell` | `Linked call made on unregistered object. Call RegisterObject first.`<br>`By defeating the Hydra, you have reached the end of your free trial. To unlock the game and adventure further, you must buy the full version.` |
| `Bookworm Adventures Deluxe` | `medium` | `12` | `static` | `BookwormAdventures.exe` | `registration_state`, `trial_or_upsell` | `Linked call made on unregistered object. Call RegisterObject first.`<br>`By defeating the Hydra, you have reached the end of your free trial. To unlock the game and adventure further, you must buy the full version.` |
| `Bookworm Adventures Fractured Fairytales` | `medium` | `12` | `static` | `BookwormAdventuresFF.exe` | `registration_state`, `trial_or_upsell` | `Linked call made on unregistered object. Call RegisterObject first.`<br>`By defeating the Hydra, you have reached the end of your free trial. To unlock the game and adventure further, you must buy the full version.` |
| `Bookworm Deluxe` | `medium` | `12` | `static` | `BookWorm.exe` | `registration_state`, `trial_or_upsell` | `UNREGISTERED VERSION`<br>`Your trial version of` |
| `Brixquest` | `medium` | `12` | `static` | `BrixQuest.exe` | `registration_state`, `trial_or_upsell` | `Not Registered`<br>`Buy Now` |
| `Da Vincis Secret` | `medium` | `12` | `static` | `DaVincisSecret.exe` | `registration_state`, `trial_or_upsell` | `Cannot remove compression scheme %s; not registered`<br>`this is a trial version.` |
| `Deep Voyage` | `medium` | `12` | `static` | `dv.exe` | `serial_or_key`, `demo_or_presentation` | `Serial Number`<br>`Demo Version` |
| `Evil Invasion` | `medium` | `12` | `static` | `EvilInvasion.exe` | `registration_state`, `trial_or_upsell` | `Evil Invasion (unregistered)`<br>`Buy Now ($19.95)!` |
| `Fishing Trip` | `medium` | `12` | `static` | `fishingtrip.exe` | `registration_state`, `trial_or_upsell` | `Fishing Trip Registration Information`<br>`This is trial version. You can use it for 7 day or run 7 times (whichever expires fist).` |
| `Kick Shot Pool` | `medium` | `12` | `static` | `Pool.exe` | `registration_state`, `trial_or_upsell` | `Register Now`<br>`Get Full Version` |
| `Pahelika Secret Legends` | `medium` | `12` | `static` | `PahelikaRelease.exe` | `registration_state`, `trial_or_upsell` | `binfo.base && "You cannot derive from an unregistered type"`<br>`Buy Now` |
| `Rainbow Drops Buster` | `medium` | `12` | `static` | `RainbowDropsBuster.exe` | `registration_state`, `trial_or_upsell` | `Rainbow Drops Buster [Unregistered version] // Press Alt+Enter to switch to fullscreen`<br>`TRIAL VERSION - %d MINUTES REMAINING` |
| `Rocket Mania Deluxe` | `medium` | `12` | `static` | `RocketMania.exe` | `registration_state`, `trial_or_upsell` | `UNREGISTERED VERSION`<br>`Trial Version: You have %d minutes of free play left` |
| `Shopping Blocks` | `medium` | `12` | `static` | `ShoppingBlocks.exe` | `registration_state`, `trial_or_upsell` | `Cannot remove compression scheme %s; not registered`<br>`this is a trial version.` |
| `Super 5 Line Slots` | `medium` | `12` | `static` | `Slots.exe` | `registration_state`, `trial_or_upsell` | `Super %s Unregistered Version`<br>`Buy Now!` |
| `Super Black Jack` | `medium` | `12` | `static` | `Blackjack.exe` | `registration_state`, `trial_or_upsell` | `Super %s Unregistered Version`<br>`Buy Now!` |
| `Super Bounce Out` | `medium` | `12` | `static` | `BounceOut.exe` | `registration_state`, `trial_or_upsell` | `Super %s Unregistered Version`<br>`Buy Now!` |
| `Super Collapse` | `medium` | `12` | `static` | `Collapse.exe` | `registration_state`, `trial_or_upsell` | `Super %s Unregistered Version`<br>`Buy Now!` |
| `Super Gem Drop` | `medium` | `12` | `static` | `GemDrop.exe` | `registration_state`, `trial_or_upsell` | `Super %s Unregistered Version`<br>`Buy Now!` |
| `Super Glinx` | `medium` | `12` | `static` | `Glinx.exe` | `registration_state`, `trial_or_upsell` | `Super %s Unregistered Version`<br>`Buy Now!` |
| `Super Jigsaw Puppies` | `medium` | `12` | `static` | `JigsawPuppies.exe` | `registration_state`, `trial_or_upsell` | `Super %s Unregistered Version`<br>`&Buy Now` |
| `Super Mahjong` | `medium` | `12` | `static` | `mahjong.exe` | `registration_state`, `trial_or_upsell` | `Super %s Unregistered Version`<br>`Buy Now!` |
| `Super Nisqually` | `medium` | `12` | `static` | `Nisqually.exe` | `registration_state`, `trial_or_upsell` | `Super %s Unregistered Version`<br>`Buy Now!` |
| `Super Pile Up` | `medium` | `12` | `static` | `PileUp.exe` | `registration_state`, `trial_or_upsell` | `Super %s Unregistered Version`<br>`Buy Now!` |
| `Super Popn Drop` | `medium` | `12` | `static` | `PopNDrop.exe` | `registration_state`, `trial_or_upsell` | `Super %s Unregistered Version`<br>`Buy Now!` |
| `Super Solitaire` | `medium` | `12` | `static` | `Solitaire.exe` | `registration_state`, `trial_or_upsell` | `Super %s Unregistered Version`<br>`Buy Now!` |
| `Super Solitaire 2` | `medium` | `12` | `static` | `ghsol2.exe` | `registration_state`, `trial_or_upsell` | `Super %s Unregistered Version`<br>`Buy Now!` |
| `Super Text Twist` | `medium` | `12` | `static` | `TextTwist.exe` | `registration_state`, `trial_or_upsell` | `Super %s Unregistered Version`<br>`Buy Now!` |
| `Super What Word` | `medium` | `12` | `static` | `WHATword.exe` | `registration_state`, `trial_or_upsell` | `Super %s Unregistered Version`<br>`Buy Now!` |
| `Tapa Jam` | `medium` | `12` | `static` | `TapaJam.exe` | `registration_state`, `trial_or_upsell` | `Super %s Unregistered Version`<br>`Buy Now!` |
| `The Pini Society` | `medium` | `12` | `static` | `ThePiniSociety.exe` | `registration_state`, `trial_or_upsell` | `Interface was not registered`<br>`PURCHASE THE FULL VERSION TO CONTINUE THE EXPEDITION` |
| `Universal Boxing Manager` | `medium` | `12` | `static` | `game.exe` | `serial_or_key`, `demo_or_presentation` | `Enter serial`<br>`Playing the Limited Demo Version.` |
| `War On Folvos` | `medium` | `12` | `static` | `Game.exe` | `registration_state`, `trial_or_upsell` | `sidCaptionUnregistered`<br>`Buy Now.url` |
| `Buzzword` | `medium` | `11` | `static` | `Buzzword.exe` | `registration_state`, `demo_or_presentation` | `unregistered`<br>`shareware` |
| `Dark Archon` | `medium` | `11` | `static` | `Dark Archon.exe` | `registration_state`, `demo_or_presentation` | `The object could only load partially. This can happen if some components are not registered properly, such as embedded tracks and tools. This can also happen if some content is missing. For example...`<br>`Shareware Time Expired!` |
| `Gravity Gems` | `medium` | `11` | `static` | `Gravity Gems.exe` | `registration_state`, `demo_or_presentation` | `Register now!`<br>`demo version` |
| `Guardian` | `medium` | `11` | `static` | `Guardian.exe` | `registration_state`, `demo_or_presentation` | `System event has not registered a callback function.`<br>`Text Your demo version...` |
| `Incadia` | `medium` | `11` | `static` | `Incadia.exe` | `registration_state`, `demo_or_presentation` | `Device not registered`<br>`Demo Version %d.%02d` |
| `Magic Gem` | `medium` | `11` | `static` | `magicgem.exe` | `registration_state`, `demo_or_presentation` | `The device or device instance is not registered with DirectInput. This value is equal to the REGDB_E_CLASSNOTREG standard COM return value.`<br>`This is a demo version!` |
| `Adventure Ball` | `high` | `10` | `static` | `AdventureBall.exe` | `code_fields` | `Registration Code:` |
| `Aqua Pearls` | `high` | `10` | `static` | `pearls.exe` | `code_fields` | `2. Enter the registration code` |
| `Best Gift` | `high` | `10` | `static` | `BestGift.exe` | `code_fields` | `2. Enter the registration code` |
| `Captain BubbleBeards Treasure` | `high` | `10` | `static` | `BubbleBeard.exe` | `code_fields` | `Registration Code:` |
| `DDD Pool` | `high` | `10` | `static` | `DDDPool.exe` | `code_fields` | `INVALID ACTIVATION CODE!` |
| `Fairway Solitaire` | `high` | `10` | `static` | `FairwaySolitaire.exe` | `code_fields` | `' has an invalid unlock code!` |
| `Gish` | `high` | `10` | `static` | `gish.exe` | `code_fields` | `Registration Code Line 1` |
| `Holiday Gift` | `high` | `10` | `static` | `HollydayGift.exe` | `code_fields` | `2. Enter the registration code` |
| `Last Galaxy Hero` | `high` | `10` | `static` | `LastGalaxyHero.exe` | `code_fields` | `2. Enter the registration code` |
| `Swap & Fall 2` | `high` | `10` | `static` | `swapfall2.exe` | `code_fields` | `2. Enter the registration code` |
| `Tanks Evolution` | `high` | `10` | `static` | `TanksEvo.exe` | `code_fields` | `1. Recive the registration code online` |
| `Treasure Of Persia` | `high` | `10` | `static` | `persia.exe` | `code_fields` | `2. Enter the registration code` |
| `Turtle Odyssey` | `high` | `10` | `static` | `Game.exe` | `code_fields` | `2. Enter the registration code` |
| `Valentines Gift` | `high` | `10` | `static` | `ValentinesGift.exe` | `code_fields` | `2. Enter the registration code` |
| `Airport Mania` | `low` | `9` | `static` | `AirportMania.exe` | `trial_or_upsell`, `demo_or_presentation` | `Full Version`<br>`Demo Version` |
| `Alien Abduction` | `low` | `9` | `static` | `AlienAbduction.exe` | `trial_or_upsell`, `demo_or_presentation` | `full version %s`<br>`demo version %s` |
| `Arklight` | `low` | `9` | `static` | `ArkLight.exe` | `trial_or_upsell`, `demo_or_presentation` | `Buy Now`<br>`www.5Star-Shareware.com` |
| `Babylonia` | `low` | `9` | `static` | `Babylonia.exe` | `trial_or_upsell`, `demo_or_presentation` | `Buy the full version for unlimited gameplay`<br>`Demo version of Jewel Match expired` |
| `Blast Miner` | `low` | `9` | `static` | `blastminer.exe` | `trial_or_upsell`, `demo_or_presentation` | `Buy Now`<br>`Demo Version 1.4` |
| `BrixFormer` | `low` | `9` | `static` | `BrixFormer.exe` | `trial_or_upsell`, `demo_or_presentation` | `in full version only`<br>`in DEMO version` |
| `Brixout XP` | `low` | `9` | `static` | `BrixoutXP.exe` | `trial_or_upsell`, `demo_or_presentation` | `Full version of the game includes:`<br>`--- Initialized demo version` |
| `Bugix Adventures` | `low` | `9` | `static` | `Bugix.exe` | `trial_or_upsell`, `demo_or_presentation` | `FULL VERSION OF THE GAME INCLUDES:`<br>`--- Initialized demo version` |
| `Bullet Candy` | `low` | `9` | `static` | `BulletCandyV2.exe` | `trial_or_upsell`, `demo_or_presentation` | `Buy Now`<br>`Bullet Candy Un-Registered Demo Version` |
| `Chicken Invaders 3` | `low` | `9` | `static` | `CI3.exe` | `trial_or_upsell`, `demo_or_presentation` | `Order the full version today`<br>`a short and feature-limited demo version?` |
| `Chicken Invaders 3 Christmas Edition` | `low` | `9` | `static` | `CI3Xmas.exe` | `trial_or_upsell`, `demo_or_presentation` | `Order the full version today`<br>`a short and feature-limited demo version?` |
| `Chocolate Castle` | `low` | `9` | `static` | `choc.exe` | `trial_or_upsell`, `demo_or_presentation` | `Castle? You'll love the full version! Order today`<br>`This is the demo version of Chocolate Castle which` |
| `Circulate` | `low` | `9` | `static` | `Circulate.exe` | `trial_or_upsell`, `demo_or_presentation` | `Buy Now`<br>`www.5Star-Shareware.com` |
| `Crimsonland` | `low` | `9` | `static` | `crimsonland.exe` | `trial_or_upsell`, `demo_or_presentation` | `please upgrade to the full version of Crimsonland. The process is very easy`<br>`You've completed all Quest mode levels available in the Demo version.` |
| `Cubology` | `low` | `9` | `static` | `Cubology.exe` | `trial_or_upsell`, `demo_or_presentation` | `Buy Now`<br>`www.5Star-Shareware.com` |
| `Darkside` | `low` | `9` | `static` | `DarkSide.exe` | `trial_or_upsell`, `demo_or_presentation` | `Buy Now`<br>`www.5Star-Shareware.com` |
| `DemonStar Classic` | `low` | `9` | `static` | `ds.exe` | `trial_or_upsell`, `demo_or_presentation` | `ORDER FULL VERSION`<br>`Shareware Version 3.2a` |
| `Desperate Space` | `low` | `9` | `static` | `Desperate.exe` | `trial_or_upsell`, `demo_or_presentation` | `Did you know that the full version of Desperate Space is way better than the demo? The later levels of this game are a lot more fun than the ones you are currently playing, but can only be experien...`<br>`The Demo version of Desperate Space is limited to just 5 levels and 30 minutes of play time. Get the full version today and you will receive:` |
| `Filler` | `low` | `9` | `static` | `filler_release_full.exe` | `trial_or_upsell`, `demo_or_presentation` | `Please buy full version.`<br>`This is demo version of the game.` |
| `Gem Mine` | `low` | `9` | `static` | `GemMine.exe` | `trial_or_upsell`, `demo_or_presentation` | `FULL VERSION OF THE GAME INCLUDES:`<br>`--- Initialized demo version` |
| `Hamster Blocks` | `low` | `9` | `static` | `Hamsters.exe` | `trial_or_upsell`, `demo_or_presentation` | `FULL VERSION OF THE GAME INCLUDES:`<br>`--- Initialized demo version` |
| `Jewel Match 2` | `low` | `9` | `static` | `JewelMatch2.exe` | `trial_or_upsell`, `demo_or_presentation` | `Buy the full version for unlimited gameplay`<br>`Demo version of Jewel Match expired` |
| `Jewel Match Winter Wonderland` | `low` | `9` | `static` | `JewelMatch_WinterWonderland.exe` | `trial_or_upsell`, `demo_or_presentation` | `Buy the full version for unlimited gameplay`<br>`Demo version of Jewel Match expired` |
| `Jezzonix` | `low` | `9` | `static` | `Jezzonix.exe` | `trial_or_upsell`, `demo_or_presentation` | `TO PLAY FULL VERSION OF THIS`<br>`JEZZONIX IS SHAREWARE!` |
| `Laser Dolphin` | `low` | `9` | `static` | `laserdolphin.exe` | `trial_or_upsell`, `demo_or_presentation` | `Experience the full version of Laser Dolphin for only $19.95`<br>`Welcome to the demo version of Laser Dolphin` |
| `Loco` | `low` | `9` | `static` | `Loco.exe` | `trial_or_upsell`, `demo_or_presentation` | `register the full version today!`<br>`You have reached|the end of the demo version!` |
| `Mighty Rodent` | `low` | `9` | `static` | `MightyRodent.exe` | `trial_or_upsell`, `demo_or_presentation` | `GET FULL VERSION`<br>`The Demo version of Mighty Rodent is limited to just 7 levels and 30 minutes of play time. Get the full version today and you will receive:` |
| `Mirror Mixup` | `low` | `9` | `static` | `MirrorMixup.exe` | `trial_or_upsell`, `demo_or_presentation` | `Buy Now`<br>`www.5Star-Shareware.com` |
| `Neon Wars` | `low` | `9` | `static` | `neonwars.exe` | `trial_or_upsell`, `demo_or_presentation` | `BUY NOW!`<br>`Demo Zone: 1 Minute Time Limit in Shareware Version` |
| `Piggly Christmas Edition` | `low` | `9` | `static` | `PigglyXmas.exe` | `trial_or_upsell`, `demo_or_presentation` | `Order now!`<br>`You have reached the end of the DEMO version. Please order the full game to continue your adventures!` |
| `Plummit` | `low` | `9` | `static` | `Plummit.exe` | `trial_or_upsell`, `demo_or_presentation` | `BUY THE FULL VERSION AND`<br>`DEMO VERSION` |
| `Professor Fizzwizzle` | `low` | `9` | `static` | `Professor.exe` | `trial_or_upsell`, `demo_or_presentation` | `This level is only available in the full version. Would you like to get the full version now?`<br>`Congratulations! You've found the Frost Gun and reached the end of this demo version of `Professor Fizzwizzle"!` |
| `PyraCubes` | `low` | `9` | `static` | `PyraCubes.exe` | `trial_or_upsell`, `demo_or_presentation` | `Buy Now`<br>`www.5Star-Shareware.com` |
| `Real Jigsaw Puzzle` | `low` | `9` | `static` | `rjpuzzle.exe` | `trial_or_upsell`, `demo_or_presentation` | `Get full version`<br>`Hints Used: Application must be re-launched.<You need to solve all puzzles in this room to open this doornHope you enjoy playing Real Jigsaw Puzzle. However, Campaign is not available in the demo v...` |
| `Scavenger` | `low` | `9` | `static` | `Scavenger.exe` | `trial_or_upsell`, `demo_or_presentation` | `Buy Now`<br>`www.5Star-Shareware.com` |
| `Sheeplings` | `low` | `9` | `static` | `Sheeplings.exe` | `trial_or_upsell`, `demo_or_presentation` | `Buy Now`<br>`Demo version` |
| `Simplz Zoo` | `low` | `9` | `static` | `SZ.exe` | `trial_or_upsell`, `demo_or_presentation` | `Full Version`<br>`Demo Version` |
| `Snow Ball` | `low` | `9` | `static` | `SnowBall.exe` | `trial_or_upsell`, `demo_or_presentation` | `FULL VERSION INCLUDES:`<br>`--- Initialized demo version` |
| `Sunny Ball` | `low` | `9` | `static` | `Sunny Ball.exe` | `trial_or_upsell`, `demo_or_presentation` | `Full version cannot load non-full version boards..`<br>`Demo version cannot load non-demo boards!` |
| `System Mania` | `low` | `9` | `static` | `SystemMania.exe` | `trial_or_upsell`, `demo_or_presentation` | `Buy Now`<br>`www.5Star-Shareware.com` |
| `Traffic Jam Extreme` | `low` | `9` | `static` | `tjx.exe` | `trial_or_upsell`, `demo_or_presentation` | `PLEASE GET THE FULL VERSION FOR MORE`<br>`YOU HAVE COMPLETED THE DEMO VERSION.` |
| `Virtual Families` | `low` | `9` | `static` | `Virtual Families.exe` | `trial_or_upsell`, `demo_or_presentation` | `Most store items are only available in the full version of Virtual Families.`<br>`Version 1.00.05, %s, DEMO VERSION` |
| `Virtual Villagers` | `low` | `9` | `static` | `VirtualVillagers.exe` | `trial_or_upsell`, `demo_or_presentation` | `Only available in the full version!`<br>`Version 1.0%i DEMO VERSION` |
| `Virtual Villagers 2` | `low` | `9` | `static` | `Virtual Villagers - The Lost Children.exe` | `trial_or_upsell`, `demo_or_presentation` | `Only available in the full version!`<br>`Version .%i DEMO VERSION` |
| `Virtual Villagers 4 The Treeof Life` | `low` | `9` | `static` | `Virtual Villagers - The Tree of Life.exe` | `trial_or_upsell`, `demo_or_presentation` | `You can purchase the full version from the main menu.`<br>`Version 1.00.01, %s, DEMO VERSION` |
| `Virtual Villagers The Secret City` | `low` | `9` | `static` | `Virtual Villagers - The Secret City.exe` | `trial_or_upsell`, `demo_or_presentation` | `You can purchase the full version from the main menu.`<br>`Version 1.00.04, %s, DEMO VERSION` |
| `Wonderland` | `low` | `9` | `direct` | `Wonderland.exe` | `trial_or_upsell`, `demo_or_presentation` | `by ordering the full version.`<br>`free demo version of Wonderland.` |
| `Wonderland Adventures` | `low` | `9` | `static` | `Wonderland.exe` | `trial_or_upsell`, `demo_or_presentation` | `Get Full Version`<br>`You have reached the end of the demo version.` |
| `Zen Puzzle Garden` | `low` | `9` | `static` | `zen.exe` | `trial_or_upsell`, `demo_or_presentation` | `gardens? You'll love the full version!`<br>`This is the demo version of Zen Puzzle` |
| `80 Days` | `low` | `8` | `static` | `80days.exe` | `serial_or_key` | `Serial Number:` |
| `Ancient Hearts And Spades` | `low` | `8` | `static` | `AncientHandS.exe` | `serial_or_key` | `Serial Number:` |
| `Ancient Spider Solitaire` | `low` | `8` | `static` | `Spider.exe` | `serial_or_key` | `Serial Number:` |
| `Babysitting Mania` | `low` | `8` | `static` | `BabySittingMania.exe` | `serial_or_key` | `Serial Number:` |
| `Book Bind` | `low` | `8` | `static` | `Book Bind.exe` | `serial_or_key` | `Serial Number:` |
| `Boonka` | `low` | `8` | `static` | `Boonka.exe` | `serial_or_key` | `You have entered an invalid name or serial number-- please try again!` |
| `Bursting Bubbles` | `low` | `8` | `static` | `Bursting Bubbles.exe` | `serial_or_key` | `Serial Number:` |
| `Buzzy Bumble` | `low` | `8` | `static` | `BuzzyBumble.exe` | `serial_or_key` | `To obtain your unlock key, please visit the LithTech website at http://www.lithtech.com. The website contains instructions on how to register your demo.` |
| `Cave Days` | `low` | `8` | `static` | `cavedays.exe` | `serial_or_key` | `Serial Number:` |
| `Chuzzle` | `low` | `8` | `static` | `Chuzzle.exe` | `serial_or_key` | `To unlock Chuzzle, you must buy a serial number and enter it below.` |
| `Chuzzle Deluxe` | `low` | `8` | `static` | `Chuzzle.exe` | `serial_or_key` | `To unlock Chuzzle, you must buy a serial number and enter it below.` |
| `Double Play Nanny Mania 2 and Babysitting Mania` | `low` | `8` | `static` | `ManiaCombo.exe` | `serial_or_key` | `Serial Number:` |
| `Double Play The Hidden Object Show 1 and 2` | `low` | `8` | `static` | `THOSCombo.exe` | `serial_or_key` | `Serial Number:` |
| `Drop` | `low` | `8` | `static` | `Drop.exe` | `serial_or_key` | `Serial Number:` |
| `Drop 2 GT` | `low` | `8` | `static` | `Drop ExtremeSW.exe` | `serial_or_key` | `Serial Number:` |
| `Egg vs. Chicken` | `low` | `8` | `static` | `Egg vs Chicken.exe` | `serial_or_key` | `Serial Number:` |
| `Fireworks Extravaganza` | `low` | `8` | `static` | `fireworks.exe` | `serial_or_key` | `Serial Number:` |
| `Gutterball 2` | `low` | `8` | `static` | `Gutterball2.exe` | `serial_or_key` | `Serial Number:` |
| `Hap Hazard` | `low` | `8` | `static` | `HapHazard.exe` | `serial_or_key` | `You have entered an invalid name or serial number-- please try again!` |
| `Hidden Expedition Amazon` | `low` | `8` | `static` | `Hidden Expedition Amazon.exe` | `serial_or_key` | `Serial Number:` |
| `Hidden Expedition Everest` | `low` | `8` | `static` | `Hidden Expedition Everest.exe` | `serial_or_key` | `Serial Number:` |
| `Hidden Expedition Titanic` | `low` | `8` | `static` | `HidExpTitanic.exe` | `serial_or_key` | `Serial Number:` |
| `Hidden Relics` | `low` | `8` | `static` | `Hidden Relics.exe` | `serial_or_key` | `Serial Number:` |
| `High Seas The Family Fortune` | `low` | `8` | `static` | `highseas.exe` | `serial_or_key` | `serial number =` |
| `Ice Cream Craze Tycoon Takeover` | `low` | `8` | `static` | `icecream.exe` | `serial_or_key` | `Serial Number:` |
| `Inspector Parker` | `low` | `8` | `static` | `Parker.exe` | `serial_or_key` | `Serial Number:` |
| `Kakuro Epic` | `low` | `8` | `static` | `Kakuro Epic.exe` | `serial_or_key` | `Enter Registration Key` |
| `Mah Jong Adventures` | `low` | `8` | `static` | `MahJongAdventures.exe` | `serial_or_key` | `Serial Number:` |
| `Mahjong Epic` | `low` | `8` | `static` | `Mahjong Epic.exe` | `serial_or_key` | `Enter Registration Key` |
| `Mahjong Towers 2` | `low` | `8` | `direct` | `Mahjong Towers II.exe` | `serial_or_key` | `Serial Number:` |
| `Mevoand The Grooveriders` | `low` | `8` | `static` | `Mevo.exe` | `serial_or_key` | `To obtain your unlock key, please visit the LithTech website at http://www.lithtech.com. The website contains instructions on how to register your demo.` |
| `Moleculous` | `low` | `8` | `static` | `Moleculous.exe` | `serial_or_key` | `Serial Number:` |
| `Mortimer and the Enchanted Castle` | `low` | `8` | `static` | `castle.exe` | `serial_or_key` | `Serial Number:` |
| `My Life Story` | `low` | `8` | `static` | `MyLifeStory.exe` | `serial_or_key` | `Serial Number:` |
| `Mystery Case Files Madame Fate` | `low` | `8` | `static` | `Madame Fate.exe` | `serial_or_key` | `Serial Number:` |
| `Mystery Case Files Ravenhearst` | `low` | `8` | `static` | `Ravenhearst.exe` | `serial_or_key` | `Serial Number:` |
| `Ouba The Great Journey` | `low` | `8` | `static` | `Ouba.exe` | `serial_or_key` | `Serial Number:` |
| `Paradise Pet Salon` | `low` | `8` | `static` | `PetSalon.exe` | `serial_or_key` | `Serial Number:` |
| `Pirates Plunder` | `low` | `8` | `static` | `PiratesPlunder_Oberon_358.exe` | `serial_or_key` | `Invalid serial number` |
| `Puppy Luv` | `low` | `8` | `static` | `Puppy Luv.exe` | `serial_or_key` | `Serial Number:` |
| `Q Beez 2` | `low` | `8` | `static` | `QBeez2.exe` | `serial_or_key` | `Serial Number:` |
| `Santas Super Friends` | `low` | `8` | `static` | `Santas Super Friends.exe` | `serial_or_key` | `Serial Number:` |
| `Slickball` | `low` | `8` | `static` | `slickball.exe` | `serial_or_key` | `Serial Number:` |
| `Slot Words` | `low` | `8` | `static` | `slotwords.exe` | `serial_or_key` | `Serial Number:` |
| `Solitaire Epic` | `low` | `8` | `static` | `Solitaire Epic.exe` | `serial_or_key` | `Enter Registration Key` |
| `Sudoku Epic` | `low` | `8` | `static` | `Sudoku Epic.exe` | `serial_or_key` | `Enter Registration Key` |
| `Talesof Monkey Island Chapter 1` | `low` | `8` | `static` | `MonkeyIsland101.exe` | `serial_or_key` | `-s, --serial Specify a serial number for the stream. If encoding` |
| `Talesof Monkey Island Chapter 2` | `low` | `8` | `static` | `MonkeyIsland102.exe` | `serial_or_key` | `-s, --serial Specify a serial number for the stream. If encoding` |
| `Talesof Monkey Island Chapter 3` | `low` | `8` | `static` | `MonkeyIsland103.exe` | `serial_or_key` | `-s, --serial Specify a serial number for the stream. If encoding` |
| `Talesof Monkey Island Chapter 4` | `low` | `8` | `static` | `MonkeyIsland104.exe` | `serial_or_key` | `-s, --serial Specify a serial number for the stream. If encoding` |
| `Talesof Monkey Island Chapter 5` | `low` | `8` | `static` | `MonkeyIsland105.exe` | `serial_or_key` | `-s, --serial Specify a serial number for the stream. If encoding` |
| `Tennis Titans` | `low` | `8` | `static` | `Tennis Titans.exe` | `serial_or_key` | `Serial Number:` |
| `The Hidden Object Show` | `low` | `8` | `static` | `THOS.exe` | `serial_or_key` | `Serial Number:` |
| `The Hidden Object Show Season 2` | `low` | `8` | `static` | `Hidden Object Show 2.exe` | `serial_or_key` | `Serial Number:` |
| `Theseusandthe Minotaur` | `low` | `8` | `static` | `Theseus.exe` | `serial_or_key` | `Enter Registration Key` |
| `Tic A Tac Royale` | `low` | `8` | `static` | `TicATac_Royale.exe` | `serial_or_key` | `Serial Number:` |
| `Top 10 Solitaire` | `low` | `8` | `static` | `Top Ten Solitaire.exe` | `serial_or_key` | `Serial Number:` |
| `Varmintz` | `low` | `8` | `static` | `Varmintz.exe` | `serial_or_key` | `Serial Number:` |
| `Varmintz Deluxe` | `low` | `8` | `static` | `Varmintz.exe` | `serial_or_key` | `Serial Number:` |
| `Wallaceand Gromits Grand Adventures Episode 1` | `low` | `8` | `static` | `WallaceGromit101.exe` | `serial_or_key` | `-s, --serial Specify a serial number for the stream. If encoding` |
| `Wallaceand Gromits Grand Adventures Episode 2` | `low` | `8` | `static` | `WallaceGromit102.exe` | `serial_or_key` | `-s, --serial Specify a serial number for the stream. If encoding` |
| `Wallaceand Gromits Grand Adventures Episode 3` | `low` | `8` | `static` | `WallaceGromit103.exe` | `serial_or_key` | `-s, --serial Specify a serial number for the stream. If encoding` |
| `Wallaceand Gromits Grand Adventures Episode 4` | `low` | `8` | `static` | `WallaceGromit104.exe` | `serial_or_key` | `-s, --serial Specify a serial number for the stream. If encoding` |
| `Word Search Deluxe` | `low` | `8` | `static` | `Word Search Deluxe.exe` | `serial_or_key` | `Serial Number:` |
| `Word Wizard` | `low` | `8` | `static` | `Word Wizard.exe` | `serial_or_key` | `Serial Number:` |
| `Zam BeeZee` | `low` | `8` | `static` | `Zam BeeZee.exe` | `serial_or_key` | `Serial Number:` |
| `Zoo Vet` | `low` | `8` | `static` | `zoovet.exe` | `serial_or_key` | `Serial Number:` |
| `7 Lands` | `low` | `7` | `static` | `7Lands.exe` | `registration_state` | `Version: Not Registered` |
| `7 Wonders` | `low` | `7` | `static` | `Wonders.exe` | `registration_state` | `The object could only load partially. This can happen if some components, such as embedded tracks and tools, are not registered properly. It can also happen if some content is missing; for example,...` |
| `7 Wonders II` | `low` | `7` | `static` | `7 Wonders II.exe` | `registration_state` | `Resource type "%s" not registered` |
| `After The End` | `low` | `7` | `static` | `AfterTheEnd.exe` | `registration_state` | `Don't register now.` |
| `Agatha Christie Peril At End House` | `low` | `7` | `static` | `endhouse.exe` | `registration_state` | `BonusRoundFactory::NewBonusRound - bonus round class '%s' not registered` |
| `Age of Castles` | `low` | `7` | `static` | `Age-of-Castles.exe` | `registration_state` | `Event '%s' not registered` |
| `Alien Stars` | `low` | `7` | `static` | `AlienStars.exe` | `registration_state` | `Unregistered` |
| `Amazing Adventures Around The World` | `low` | `7` | `static` | `AmazingAdventures2.exe` | `registration_state` | `Device not registered` |
| `Amazing Adventures Special Edition Bundle` | `low` | `7` | `static` | `AmazingAdventuresBundle.exe` | `registration_state` | `Device not registered` |
| `Amazing Adventures The Lost Tomb` | `low` | `7` | `static` | `AmazingAdventures.exe` | `registration_state` | `Device not registered` |
| `Ashley Jones` | `low` | `7` | `static` | `HrtEgypt.exe` | `registration_state` | `Not Registered` |
| `Astro Avenger 2` | `low` | `7` | `static` | `AstroAvenger2.exe` | `registration_state` | `Failed to create AI by name: "%s" -- unregistered class name (for the entity "%s").` |
| `AstroAvenger` | `low` | `7` | `static` | `AstroAvenger.exe` | `registration_state` | `Failed to create AI by name: "%s" -- unregistered class name (for the entity "%s").` |
| `Astrobatics` | `low` | `7` | `static` | `Astrobatics.exe` | `registration_state` | `The device or device instance is not registered with DirectInput. This value is equal to the REGDB_E_CLASSNOTREG standard COM return value.` |
| `Azteca` | `low` | `7` | `static` | `Azteca.exe` | `registration_state` | `unregistered extension code %ld` |
| `Band Of Bugs` | `low` | `7` | `static` | `BoB.exe` | `registration_state` | `WARNING: Window class already unregistered.` |
| `Beetle Bug 2` | `low` | `7` | `static` | `bj2.exe` | `registration_state` | `unregistered extension code %ld` |
| `Beetle Bug 3` | `low` | `7` | `static` | `bj3.exe` | `registration_state` | `unregistered extension code %ld` |
| `Bejeweled 2` | `low` | `7` | `static` | `WinBej2.exe` | `registration_state` | `registration information below.` |
| `Bejeweled 2 Deluxe` | `low` | `7` | `static` | `WinBej2.exe` | `registration_state` | `registration information below.` |
| `Bengal Gameof Gods` | `low` | `7` | `static` | `Bengal.exe` | `registration_state` | `unregistered extension code %ld` |
| `Blokus World Tour` | `low` | `7` | `static` | `Blokus.exe` | `registration_state` | `The object could only load partially. This can happen if some components are not registered properly, such as embedded tracks and tools. This can also happen if some content is missing. For example...` |
| `Brave Piglet` | `low` | `7` | `static` | `BravePiglet.exe` | `registration_state` | `REGISTER NOW!` |
| `Bricktopia` | `low` | `7` | `static` | `Bricktopia.exe` | `registration_state` | `CreateDevice failed -- The device or device instance is not registered with DirectInput.` |
| `Bubble Shooter Premium Edition` | `low` | `7` | `static` | `Bubblez.exe` | `registration_state` | `Control class with id:%s: not registered` |
| `Build It Miami Beach Resort` | `low` | `7` | `static` | `Buildit.exe` | `registration_state` | `T-object type is not registered:` |
| `Burger Rush` | `low` | `7` | `static` | `BurgerRush.exe` | `registration_state` | `Trying to load unregistered resource!` |
| `Call Of Atlantis` | `low` | `7` | `static` | `Call of Atlantis.exe` | `registration_state` | `crep && "you are trying to use an unregistered type"` |
| `Charlottes Web Word Rescue` | `low` | `7` | `static` | `CharlottesWeb.exe` | `registration_state` | `Resource type "%s" not registered` |
| `Charma` | `low` | `7` | `static` | `Charma.exe` | `registration_state` | `unregistered void cast` |
| `Chicken Attack Deluxe` | `low` | `7` | `static` | `ChickenAttack.exe` | `registration_state` | `unregistered extension code %ld` |
| `Chicken Invaders 2` | `low` | `7` | `static` | `ChickenInvaders2.exe` | `registration_state` | `The object could only load partially. This can happen if some components, such as embedded tracks and tools, are not registered properly.` |
| `Chicken Rush Deluxe` | `low` | `7` | `static` | `ChickenRush.exe` | `registration_state` | `unregistered extension code %ld` |
| `Chicken Village` | `low` | `7` | `static` | `chicken.exe` | `registration_state` | `- Warrning, Param (%s='%s')for node not registered in class` |
| `Clash N Slash` | `low` | `7` | `static` | `Clash N Slash.exe` | `registration_state` | `[DIERR_DEVICENOTREG] The device or device instance is not registered with DirectInput. This value is equal to the REGDB_E_CLASSNOTREG standard COM return value.` |
| `Clash N Slash Worlds Away` | `low` | `7` | `static` | `Clash N Slash Worlds Away.exe` | `registration_state` | `[DIERR_DEVICENOTREG] The device or device instance is not registered with DirectInput. This value is equal to the REGDB_E_CLASSNOTREG standard COM return value.` |
| `Clayside` | `low` | `7` | `static` | `Clayside.exe` | `registration_state` | `Screen.Main.unregistered` |
| `Click O Pack` | `low` | `7` | `static` | `Click-O-Pack.exe` | `registration_state` | `DefAnimator class with id:%s: not registered` |
| `CLUE Classic` | `low` | `7` | `static` | `CLUE Classic.exe` | `registration_state` | `QMetaObject::invokeMethod: Unable to handle unregistered datatype '%s'` |
| `Cradle Of Persia` | `low` | `7` | `static` | `CradleOfPersia.exe` | `registration_state` | `not registered!` |
| `Cradle Of Rome` | `low` | `7` | `static` | `CradleOfRome.exe` | `registration_state` | `not registered!` |
| `Crusaders Of Space 2` | `low` | `7` | `static` | `Cos2.exe` | `registration_state` | `not registered` |
| `Curseofthe Pharaoh The Questfor Nefertiti` | `low` | `7` | `static` | `Pharaoh.exe` | `registration_state` | `dispatchMessageObject: Message was not registered and no more object IDs are available for messages` |
| `Daycare Nightmare` | `low` | `7` | `static` | `DaycareNightmare.exe` | `registration_state` | `FGResLoader.getImage >>> requested image not registered:` |
| `Daycare Nightmare Mini Monsters` | `low` | `7` | `static` | `DaycareNightmare2.exe` | `registration_state` | `FGResLoader.getImage >>> requested image not registered:` |
| `Deadtime Stories` | `low` | `7` | `static` | `DeadtimeStories.exe` | `registration_state` | `Unregistered error message` |
| `Death On The Nile` | `low` | `7` | `static` | `DeathOnTheNile.exe` | `registration_state` | `BonusRoundFactory::NewBonusRound - bonus round class '%s' not registered` |
| `Department 42 The Mysteryofthe Nine` | `low` | `7` | `static` | `casual.exe` | `registration_state` | `The device or device instance is not registered with Microsoft` |
| `Diamond Drop` | `low` | `7` | `static` | `DiamondDrop.exe` | `registration_state` | `unregistered extension code %ld` |
| `Diamond Drop 2` | `low` | `7` | `static` | `Game.exe` | `registration_state` | `unregistered extension code %ld` |
| `Diner Dash Flo On The Go` | `low` | `7` | `static` | `Diner Dash - Flo On The Go.exe` | `registration_state` | `The device or device instance is not registered with DirectInput. This value is equal to the REGDB_E_CLASSNOTREG standard COM return value.` |
| `Discovery A Seek And Find Adventure` | `low` | `7` | `static` | `Discovery.exe` | `registration_state` | `ERROR: '%s' was not registered as a command alias because it is already a game variable.` |
| `Dr Lynch Grave Secrets` | `low` | `7` | `static` | `gravesecrets.exe` | `registration_state` | `WidgetFactory::NewWidget - cannot create widget '%s' of unregistered class '%s'` |
| `Dream Day First Home` | `low` | `7` | `static` | `DreamDayFirstHome.exe` | `registration_state` | `This file was created with the ECW JPEG 2000 SDK build %s copyright 1998-2005 by ER Mapper. This GeoJP2 header was translated from the following ER Mapper style registration information:` |
| `Dream Day Honeymoon` | `low` | `7` | `static` | `DreamDayHoneymoon.exe` | `registration_state` | `This file was created with the ECW JPEG 2000 SDK build %s copyright 1998-2005 by ER Mapper. This GeoJP2 header was translated from the following ER Mapper style registration information:` |
| `Dream Day Wedding 2` | `low` | `7` | `static` | `Dream Day Wedding - Married in Manhattan.exe` | `registration_state` | `This file was created with the ECW JPEG 2000 SDK build %s copyright 1998-2005 by ER Mapper. This GeoJP2 header was translated from the following ER Mapper style registration information:` |
| `Eets/Bin` | `low` | `7` | `static` | `Eets.exe` | `registration_state` | `The object could only load partially. This can happen if some components are not registered properly, such as embedded tracks and tools. This can also happen if some content is missing. For example...` |
| `El Dorado Quest` | `low` | `7` | `static` | `ElDoradoQuest.exe` | `registration_state` | `Not Registered` |
| `Electra` | `low` | `7` | `static` | `Electra.exe` | `registration_state` | `Register NOW!` |
| `Elf Bowling Hawaiian Vacation` | `low` | `7` | `static` | `ElfBowling.exe` | `registration_state` | `Resource type "%s" not registered` |
| `Elf Bowling The Last Insult` | `low` | `7` | `static` | `ElfBowling.exe` | `registration_state` | `Resource type "%s" not registered` |
| `Elias The Mighty` | `low` | `7` | `static` | `game.exe` | `registration_state` | `unregistered void cast` |
| `Elven Mists` | `low` | `7` | `static` | `Game.exe` | `registration_state` | `unregistered extension code %ld` |
| `Elven Mists 2` | `low` | `7` | `static` | `Game.exe` | `registration_state` | `unregistered extension code %ld` |
| `Emerald Tale` | `low` | `7` | `static` | `Emerald Tale.exe` | `registration_state` | `Screen.Main.unregistered` |
| `Empressofthe Deep` | `low` | `7` | `static` | `Empress of the Deep 632.exe` | `registration_state` | `dispatchMessageObject: Message was not registered and no more object IDs are available for messages` |
| `Enchanted Gardens` | `low` | `7` | `static` | `EnchantedGardens.exe` | `registration_state` | `BlockCipherFactory::create() - Error! Cipher-name %s is not registered!` |
| `Escape From Lost Island` | `low` | `7` | `static` | `EscapeFromLostIsland.exe` | `registration_state` | `unregistered extension code %ld` |
| `Escape Rosecliff Island` | `low` | `7` | `static` | `EscapeRosecliffIsland.exe` | `registration_state` | `Device not registered` |
| `Fairy Jewels` | `low` | `7` | `static` | `FairyJewels.exe` | `registration_state` | `unregistered extension code %ld` |
| `Fairy Jewels 2` | `low` | `7` | `static` | `Game.exe` | `registration_state` | `unregistered extension code %ld` |
| `Fashion Solitaire` | `low` | `7` | `static` | `Fashion.exe` | `registration_state` | `$pref::FakeUnregistered` |
| `Feelers` | `low` | `7` | `static` | `Feelers.exe` | `registration_state` | `Feelers - UNREGISTERED` |
| `Fishdom Frosty Splash` | `low` | `7` | `static` | `Fishdom.exe` | `registration_state` | `crep && "you are trying to use an unregistered type"` |
| `Fishdom H 20 Hidden Odyssey` | `low` | `7` | `static` | `Fishdom H2O.exe` | `registration_state` | `crep && "you are trying to use an unregistered type"` |
| `Fishdom Spooky Splash` | `low` | `7` | `static` | `Fishdom.exe` | `registration_state` | `crep && "you are trying to use an unregistered type"` |
| `Fishdom Updated` | `low` | `7` | `static` | `Fishdom.exe` | `registration_state` | `crep && "you are trying to use an unregistered type"` |
| `Flux Family Secrets The Ripple Effect` | `low` | `7` | `static` | `Flux Family Secrets.exe` | `registration_state` | `dispatchMessageObject: Message was not registered and no more object IDs are available for messages` |
| `Freak Out Gold` | `low` | `7` | `static` | `FreakOutGold.exe` | `registration_state` | `REGISTER NOW` |
| `Froggy's Adventures` | `low` | `7` | `static` | `froggy.exe` | `registration_state` | `Unregistered Version.` |
| `Funkiball Adventure` | `low` | `7` | `static` | `funkiball.exe` | `registration_state` | `The object could only load partially. This can happen if some components are not registered properly, such as embedded tracks and tools. This can also happen if some content is missing. For example...` |
| `Gazillionaire III` | `low` | `7` | `static` | `GAZ3.exe` | `registration_state` | `The Soothsayer's Union lodged a complaint today with the Minister of Predictions, claiming that unregistered Soothsayers were handing out erroneous readings.` |
| `Gem Slider Deluxe` | `low` | `7` | `static` | `gs.exe` | `registration_state` | `unregistered` |
| `GHOST Chronicles Phantom Renaissance Faire` | `low` | `7` | `static` | `GHOST Chronicles.exe` | `registration_state` | `dispatchMessageObject: Message was not registered and no more object IDs are available for messages` |
| `GHOST Hunters The Haunting Of Majesty Manor` | `low` | `7` | `static` | `GHOST Hunters.exe` | `registration_state` | `BlockCipherFactory::create() - Error! Cipher-name %s is not registered!` |
| `Gold Sprinter` | `low` | `7` | `direct` | `GoldSprinter.exe` | `registration_state` | `IDB_UNREGISTERED` |
| `Golden Sub` | `low` | `7` | `static` | `Submarine.exe` | `registration_state` | `unregistered extension code %ld` |
| `Granny In Paradise` | `low` | `7` | `static` | `granny_download.exe` | `registration_state` | `not registered` |
| `Green Valley Funonthe Farm` | `low` | `7` | `static` | `Game.exe` | `registration_state` | `unregistered extension code %ld` |
| `Haunted Hotel 2` | `low` | `7` | `static` | `HauntedHotel2.exe` | `registration_state` | `print("%s : Bad module name or Module not Registered.");` |
| `Heavy Weapon` | `low` | `7` | `static` | `Heavy Weapon Deluxe.exe` | `registration_state` | `NOTE: This will open a browser window. When you have registered, enter your registration information below.` |
| `Heroesof Hellas 2 Olympia` | `low` | `7` | `static` | `hoh2.exe` | `registration_state` | `node with id %1% not registered in factory` |
| `Hyperballoid Around The World` | `low` | `7` | `static` | `Hyperballoid.exe` | `registration_state` | `- Unregistered command: %s` |
| `Hyperballoid Complete` | `low` | `7` | `static` | `game.exe` | `registration_state` | `- Unregistered command: %s` |
| `Hyperballoid Golden Pack` | `low` | `7` | `static` | `Hyperballoid.exe` | `registration_state` | `- Unregistered command: %s` |
| `Inca Ball` | `low` | `7` | `static` | `IncaBall.exe` | `registration_state` | `Failed to create AI by name: "%s" -- unregistered class name (for the entity "%s").` |
| `Insider Tales The Stolen Venus` | `low` | `7` | `static` | `StolenVenus.exe` | `registration_state` | `unregistered extension code %ld` |
| `Insider Tales Vanishedin Rome` | `low` | `7` | `static` | `VanishedInRome.exe` | `registration_state` | `unregistered extension code %ld` |
| `IQ Identity Quest` | `low` | `7` | `static` | `I.Q. Identity Quest.exe` | `registration_state` | `BlockCipherFactory::create() - Error! Cipher-name %s is not registered!` |
| `Jackpot Matchup` | `low` | `7` | `static` | `Jackpot_Match-Up.exe` | `registration_state` | `$pref::FakeUnregistered` |
| `Jane Angel Templar Mystery` | `low` | `7` | `static` | `Jane Angel - Templar Mystery.exe` | `registration_state` | `unregistered class` |
| `Jewel Of Atlantis` | `low` | `7` | `static` | `Jewel of Atlantis.exe` | `registration_state` | `[DIERR_DEVICENOTREG] The device or device instance is not registered with DirectInput. This value is equal to the REGDB_E_CLASSNOTREG standard COM return value.` |
| `Jewelix` | `low` | `7` | `static` | `Jewelix.exe` | `registration_state` | `Control class with id:%s: not registered` |
| `Joan Jadeandthe Gatesof Xibalba` | `low` | `7` | `static` | `JoanJade.exe` | `registration_state` | `unregistered class` |
| `Jurassic Realm` | `low` | `7` | `static` | `Jurassic Realm.exe` | `registration_state` | `[DIERR_DEVICENOTREG] The device or device instance is not registered with DirectInput. This value is equal to the REGDB_E_CLASSNOTREG standard COM return value.` |
| `King Kong Skull Island Adventure` | `low` | `7` | `static` | `Kong.exe` | `registration_state` | `CreateDevice failed -- The device or device instance is not registered with DirectInput.` |
| `Law And Order The Vengeful Heart` | `low` | `7` | `static` | `game.exe` | `registration_state` | `The object could only load partially. This can happen if some components are not registered properly, such as embedded tracks and tools. This can also happen if some content is missing. For example...` |
| `LexiCastle` | `low` | `7` | `static` | `LexiCastle32.exe` | `registration_state` | `Device not registered` |
| `Lottso Deluxe` | `low` | `7` | `static` | `Lottso2.exe` | `registration_state` | `lots.unregistered.max.games` |
| `Luck Charm Deluxe` | `low` | `7` | `static` | `LuckCharmDeluxe.exe` | `registration_state` | `Event '%s' not registered` |
| `Luxor Quest For The Afterlife` | `low` | `7` | `static` | `LUXOR - Quest for the Afterlife.exe` | `registration_state` | `ERROR: '%s' was not registered as a command alias because it is already a game variable.` |
| `Mad Magic` | `low` | `7` | `static` | `mad magic.exe` | `registration_state` | `Attempt to unregister not registered window class.` |
| `Magic Shop` | `low` | `7` | `static` | `game.exe` | `registration_state` | `Module with ID: %d was not registered` |
| `Mah Jomino` | `low` | `7` | `static` | `mahjomino.exe` | `registration_state` | `Font "%1" is not registered.` |
| `Mahjongg Dimensions Deluxe` | `low` | `7` | `static` | `Mahjongg Dimensions Deluxe.exe` | `registration_state` | `Callback %1 is not registered.` |
| `Mishap An Accidental Haunting` | `low` | `7` | `static` | `Mishap.exe` | `registration_state` | `dispatchMessageObject: Message was not registered and no more object IDs are available for messages` |
| `My Farm` | `low` | `7` | `static` | `My Farm.exe` | `registration_state` | `The object could only load partially. This can happen if some components are not registered properly, such as embedded tracks and tools. This can also happen if some content is missing. For example...` |
| `Mysteries Of Horus` | `low` | `7` | `static` | `MysteriesOfHorus.exe` | `registration_state` | `unregistered void cast` |
| `Mysterious City Cairo` | `low` | `7` | `static` | `Cairo.exe` | `registration_state` | `Warning: trying to unregister not registered sound driver.` |
| `Mysterious City Vegas` | `low` | `7` | `static` | `Vegas.exe` | `registration_state` | `Warning: trying to unregister not registered sound driver.` |
| `Mystery Masterpiece The Moonstone` | `low` | `7` | `static` | `Moonstone.exe` | `registration_state` | `key %s is not registered with code %s(` |
| `Mystery PI Lostin Los Angeles` | `low` | `7` | `static` | `MysteryPILosAngeles.exe` | `registration_state` | `Device not registered` |
| `Mystery PI The Lottery Ticket` | `low` | `7` | `static` | `MysteryPI.exe` | `registration_state` | `Device not registered` |
| `Mystery PI The New York Fortune` | `low` | `7` | `static` | `MysteryPINewYork.exe` | `registration_state` | `Device not registered` |
| `Mystery PI The Vegas Heist` | `low` | `7` | `static` | `MysteryPIVegas.exe` | `registration_state` | `Device not registered` |
| `Mystery Solitaire Secret Island` | `low` | `7` | `static` | `MysterySolitaire.exe` | `registration_state` | `Device not registered` |
| `Nat Geo Eco Rescue Rivers` | `low` | `7` | `static` | `EcoRescue.exe` | `registration_state` | `Try to get id by type name("%s") of not registered stored object` |
| `Ocean Diver` | `low` | `7` | `static` | `OceanDiver.exe` | `registration_state` | `Device not registered` |
| `Pacific Heroes` | `low` | `7` | `static` | `pacific.exe` | `registration_state` | `The object could only load partially. This can happen if some components are not registered properly, such as embedded tracks and tools. This can also happen if some content is missing. For example...` |
| `Party Planner` | `low` | `7` | `static` | `PartyPlanner.exe` | `registration_state` | `DIERR_DEVICENOTREG : The device or device instance is not registered with DirectInput. This value is equal to the REGDB_E_CLASSNOTREG standard COM return value.` |
| `Pirate Poppers` | `low` | `7` | `static` | `piratepoppers.exe` | `registration_state` | `The device or device instance is not registered with DirectInput. This value is equal to the REGDB_E_CLASSNOTREG standard COM return value.` |
| `Plant Tycoon` | `low` | `7` | `static` | `Plant Tycoon.exe` | `registration_state` | `Unregistered` |
| `Pocahontas Princessofthe Powhatan` | `low` | `7` | `static` | `Pocahontas.exe` | `registration_state` | `dispatchMessageObject: Message was not registered and no more object IDs are available for messages` |
| `Poker Superstars II` | `low` | `7` | `static` | `PokerSuperstars2.exe` | `registration_state` | `The object could only load partially. This can happen if some components are not registered properly, such as embedded tracks and tools. This can also happen if some content is missing. For example...` |
| `Poker Superstars III` | `low` | `7` | `static` | `Poker3.exe` | `registration_state` | `The object could only load partially. This can happen if some components are not registered properly, such as embedded tracks and tools. This can also happen if some content is missing. For example...` |
| `Poker Superstars Invitational` | `low` | `7` | `static` | `poker.exe` | `registration_state` | `The object could only load partially. This can happen if some components are not registered properly, such as embedded tracks and tools. This can also happen if some content is missing. For example...` |
| `Pulsarius` | `low` | `7` | `static` | `Pulsarius.exe` | `registration_state` | `The object could only load partially. This can happen if some components are not registered properly, such as embedded tracks and tools. This can also happen if some content is missing. For example...` |
| `Puzzle Blast` | `low` | `7` | `static` | `PuzzleBlast.exe` | `registration_state` | `Not registered` |
| `Rasputins Curse` | `low` | `7` | `static` | `Rasputin.exe` | `registration_state` | `dispatchMessageObject: Message was not registered and no more object IDs are available for messages` |
| `Reaxxion` | `low` | `7` | `static` | `Reaxxion.exe` | `registration_state` | `Resource type "%s" not registered` |
| `Restoring Rhonda` | `low` | `7` | `static` | `Restoring Rhonda.exe` | `registration_state` | `dispatchMessageObject: Message was not registered and no more object IDs are available for messages` |
| `Rhianna Fordandthe Da Vinci Letter` | `low` | `7` | `static` | `RhiannaFord.exe` | `registration_state` | `WidgetFactory::NewWidget - cannot create widget '%s' of unregistered class '%s'` |
| `Roboball` | `low` | `7` | `static` | `roboball.exe` | `registration_state` | `The object could only load partially. This can happen if some components are not registered properly, such as embedded tracks and tools. This can also happen if some content is missing. For example...` |
| `Rocket Bowl` | `low` | `7` | `static` | `RocketBowl.exe` | `registration_state` | `$pref::FakeUnregistered` |
| `Royal Envoy` | `low` | `7` | `static` | `Royal Envoy.exe` | `registration_state` | `The object could only load partially. This can happen if some components are not registered properly, such as embedded tracks and tools. This can also happen if some content is missing. For example...` |
| `Runic` | `low` | `7` | `static` | `Runic.exe` | `registration_state` | `The object could only load partially. This can happen if some components are not registered properly, such as embedded tracks and tools. This can also happen if some content is missing. For example...` |
| `Sallys Quick Clips` | `low` | `7` | `static` | `SallysQuickClips.exe` | `registration_state` | `DIERR_DEVICENOTREG : The device or device instance is not registered with DirectInput. This value is equal to the REGDB_E_CLASSNOTREG standard COM return value.` |
| `Sallys Salon` | `low` | `7` | `static` | `SallysSalon.exe` | `registration_state` | `DIERR_DEVICENOTREG : The device or device instance is not registered with DirectInput. This value is equal to the REGDB_E_CLASSNOTREG standard COM return value.` |
| `Sallys Spa` | `low` | `7` | `static` | `SallysSpa.exe` | `registration_state` | `DIERR_DEVICENOTREG : The device or device instance is not registered with DirectInput. This value is equal to the REGDB_E_CLASSNOTREG standard COM return value.` |
| `SandScript` | `low` | `7` | `static` | `sandscript.exe` | `registration_state` | `The device or device instance is not registered with DirectInput. This value is equal to the REGDB_E_CLASSNOTREG standard COM return value.` |
| `Shutter Island` | `low` | `7` | `static` | `Shutter Island.exe` | `registration_state` | `The object could only load partially. This can happen if some components are not registered properly, such as embedded tracks and tools. This can also happen if some content is missing. For example...` |
| `Slingo Mystery Whos Gold` | `low` | `7` | `static` | `SlingoMystery.exe` | `registration_state` | `The object could only load partially. This can happen if some components are not registered properly, such as embedded tracks and tools. This can also happen if some content is missing. For example...` |
| `Slingo Quest` | `low` | `7` | `static` | `SlingoQuest.exe` | `registration_state` | `The object could only load partially. This can happen if some components are not registered properly, such as embedded tracks and tools. This can also happen if some content is missing. For example...` |
| `Slingo Quest Hawaii` | `low` | `7` | `static` | `SlingoQuest2.exe` | `registration_state` | `The object could only load partially. This can happen if some components are not registered properly, such as embedded tracks and tools. This can also happen if some content is missing. For example...` |
| `Slingo Supreme` | `low` | `7` | `static` | `SlingoSupreme.exe` | `registration_state` | `The object could only load partially. This can happen if some components are not registered properly, such as embedded tracks and tools. This can also happen if some content is missing. For example...` |
| `Snapshot Adventures` | `low` | `7` | `static` | `Snap.exe` | `registration_state` | `$pref::FakeUnregistered` |
| `Spirit Of Wandering The Legend` | `low` | `7` | `static` | `SpiritOfWandering.exe` | `registration_state` | `unregistered void cast` |
| `Spooky Spirits/bin` | `low` | `7` | `static` | `Spooky Spirits.exe` | `registration_state` | `unregistered void cast` |
| `Star Defender 3` | `low` | `7` | `static` | `StarDefender3.exe` | `registration_state` | `not registered!` |
| `Star Defender 4` | `low` | `7` | `static` | `StarDefender4.exe` | `registration_state` | `not registered!` |
| `Steam Brigade` | `low` | `7` | `static` | `SteamBrigade.exe` | `registration_state` | `ForwardUnregistered` |
| `Super Granny 3` | `low` | `7` | `static` | `SuperGranny3.exe` | `registration_state` | `not registered` |
| `Super Granny Winter Wonderland` | `low` | `7` | `static` | `SuperGrannyWinterWonderland.exe` | `registration_state` | `not registered` |
| `Super Slyder` | `low` | `7` | `static` | `SuperSlyder_release.exe` | `registration_state` | `not registered` |
| `Sushi To Go Express` | `low` | `7` | `static` | `Sushi To Go Express.exe` | `registration_state` | `dispatchMessageObject: Message was not registered and no more object IDs are available for messages` |
| `Sweetopia` | `low` | `7` | `static` | `Sweetopia.exe` | `registration_state` | `The device or device instance is not registered with DirectInput. This value is equal to the REGDB_E_CLASSNOTREG standard COM return value.` |
| `The 80s Game` | `low` | `7` | `static` | `T8G_Release.exe` | `registration_state` | `The object could only load partially. This can happen if some components are not registered properly, such as embedded tracks and tools. This can also happen if some content is missing. For example...` |
| `The Mystery Of The Crystal Portal` | `low` | `7` | `static` | `MysteryOfTheCrystalPortal.exe` | `registration_state` | `unregistered class` |
| `The Poppit Show` | `low` | `7` | `static` | `Poppit3.exe` | `registration_state` | `pop.unregisteredgames.max` |
| `Thomas And The Magical Words` | `low` | `7` | `static` | `thomaswords.exe` | `registration_state` | `DIERR_DEVICENOTREG : The device or device instance is not registered with DirectInput. This value is equal to the REGDB_E_CLASSNOTREG standard COM return value.` |
| `Tower Blaster` | `low` | `7` | `static` | `TowerBlaster.exe` | `registration_state` | `Event '%s' not registered` |
| `Tradewinds 2` | `low` | `7` | `static` | `tw2_vista.exe` | `registration_state` | `not registered` |
| `Tradewinds Caravans` | `low` | `7` | `static` | `TradewindsCaravans.exe` | `registration_state` | `not registered!` |
| `Tradewinds Legends` | `low` | `7` | `static` | `tw3_0123.exe` | `registration_state` | `not registered` |
| `Trijinx` | `low` | `7` | `static` | `TriJinx.exe` | `registration_state` | `The device or device instance is not registered with DirectInput. This value is equal to the REGDB_E_CLASSNOTREG standard COM return value.` |
| `Westward` | `low` | `7` | `static` | `WestwardVistaFinal.exe` | `registration_state` | `not registered` |
| `Womens Murder Club Death In Scarlet` | `low` | `7` | `static` | `WMC.exe` | `registration_state` | `WidgetFactory::NewWidget - cannot create widget '%s' of unregistered class '%s'` |
| `World Voyage` | `low` | `7` | `static` | `WorldVoyage.exe` | `registration_state` | `Failed to create AI by name: "%s" -- unregistered class name (for the entity "%s"). (%s)` |
| `Yard Sale Junkie` | `low` | `7` | `static` | `Yard Sale Junkie.exe` | `registration_state` | `dispatchMessageObject: Message was not registered and no more object IDs are available for messages` |
| `Yummy Drink Factory` | `low` | `7` | `static` | `Yummy Drink Factory.exe` | `registration_state` | `dispatchMessageObject: Message was not registered and no more object IDs are available for messages` |
| `Zodiac Tower` | `low` | `7` | `static` | `Zodiac Tower.exe` | `registration_state` | `[DIERR_DEVICENOTREG] The device or device instance is not registered with DirectInput. This value is equal to the REGDB_E_CLASSNOTREG standard COM return value.` |
| `Zombie Bowl O Rama` | `low` | `7` | `static` | `Zombie Bowl-O-Rama.exe` | `registration_state` | `Resource type "%s" not registered` |
| `10 Talismans` | `low` | `5` | `static` | `10talismans.exe` | `trial_or_upsell` | `Trial version` |
| `Action Memory` | `low` | `5` | `static` | `ActionMemory.exe` | `trial_or_upsell` | `Close the game and follow the instructions on how to register the full version.` |
| `Air Assault` | `low` | `5` | `static` | `game.exe` | `trial_or_upsell` | `CDemo is over, please buy full version to play more levels.` |
| `Air Strike II Gulf Thunder` | `low` | `5` | `static` | `AirStrike3D II - Gulf.exe` | `trial_or_upsell` | `To continue playing, please upgrade to the full version.` |
| `Alice Greenfingers 2` | `low` | `5` | `static` | `AliceGreenfingers2.exe` | `trial_or_upsell` | `FULL version` |
| `Alpha Ball/bin` | `low` | `5` | `static` | `AlphaBall.exe` | `trial_or_upsell` | `Order Full Version To Get:` |
| `Angkor` | `low` | `5` | `static` | `AngkorRelease.exe` | `trial_or_upsell` | `You have completed the demo! To discover the rest of the amulet pieces and continue your journey through the lands of Angkor, buy the full version!` |
| `Atlantis Quest` | `low` | `5` | `static` | `Atlantis.exe` | `trial_or_upsell` | `1Buy the full version to enjoy unlimited gameplay.` |
| `Ballistik` | `low` | `5` | `static` | `Ballistik.exe` | `trial_or_upsell` | `Order Full Version To Get:` |
| `Barrel Mania` | `low` | `5` | `static` | `bmania.exe` | `trial_or_upsell` | `CBUY NOW!` |
| `Beesly's Buzzwords` | `low` | `5` | `static` | `Buzzwords.exe` | `trial_or_upsell` | `(Evaluation version)` |
| `Betty's Beer Bar` | `low` | `5` | `static` | `bbb.exe` | `trial_or_upsell` | `This application appears to be become corrupted and must be reinstalled. If you have already purchased this application then you will still have the full version after the reinstallation.` |
| `Blowfish/jre14202redist/bin` | `low` | `5` | `static` | `javaw.exe` | `trial_or_upsell` | `%s full version "%s"` |
| `Bobthe Builder Can Do Carnival` | `low` | `5` | `static` | `BobTheBuilder Carnival.exe` | `trial_or_upsell` | `[Full Version]` |
| `Bobthe Builder Can Do Zoo` | `low` | `5` | `static` | `BobTheBuilder Zoo.exe` | `trial_or_upsell` | `[Full Version]` |
| `Break Ball 2 Gold` | `low` | `5` | `static` | `Break Ball 2 Gold.exe` | `trial_or_upsell` | `with the full version you` |
| `Bubble Odyssey` | `low` | `5` | `static` | `odyssey.exe` | `trial_or_upsell` | `Buy Now` |
| `Build A Lot 3 Passport To Europe` | `low` | `5` | `static` | `Buildalot3.exe` | `trial_or_upsell` | `Full Version` |
| `Buildalot 2 Town Of The Year` | `low` | `5` | `static` | `Buildalot2.exe` | `trial_or_upsell` | `Full Version` |
| `Buildalot 4 Power Source` | `low` | `5` | `static` | `Buildalot4.exe` | `trial_or_upsell` | `Full Version` |
| `Carl The Caveman` | `low` | `5` | `static` | `Caveman.exe` | `trial_or_upsell` | `buy now` |
| `Christmasville` | `low` | `5` | `static` | `Christmasville.exe` | `trial_or_upsell` | `Trial version` |
| `Crusaders of Space Open Range` | `low` | `5` | `static` | `Cos.exe` | `trial_or_upsell` | `Full version` |
| `Digi Pool` | `low` | `5` | `static` | `Digi Pool.exe` | `trial_or_upsell` | `YOU MUST GET THE FULL VERSION TO CONTINUE PLAY` |
| `DNA` | `low` | `5` | `static` | `D.N.A.exe` | `trial_or_upsell` | `Buy Now!` |
| `Easter Bonus` | `low` | `5` | `static` | `easterbonus.exe` | `trial_or_upsell` | `You have reached the end of the demo. Get the full version for 110 levels!` |
| `Empires And Dungeons` | `low` | `5` | `static` | `EmpiresDungeons.exe` | `trial_or_upsell` | `The golden vessel displays the amount of experience you need to gather to level up. In the full version the level cap is at 8. You can get experience mainly by slaying monsters.` |
| `Eschalon Book 1` | `low` | `5` | `static` | `Eschalon Book I.exe` | `trial_or_upsell` | `The area beyond exists only in the full version of Eschalon: Book I.` |
| `Family Feud Battleofthe Sexes` | `low` | `5` | `static` | `FamilyFeud4.exe` | `trial_or_upsell` | `Evaluation Copy` |
| `Family Feud Dream Home` | `low` | `5` | `static` | `FamilyFeud3.exe` | `trial_or_upsell` | `Evaluation Copy` |
| `FastCrawl` | `low` | `5` | `static` | `FastCrawl.exe` | `trial_or_upsell` | `Get Full Version` |
| `Fatman` | `low` | `5` | `direct` | `fatman.exe` | `trial_or_upsell` | `Buy now` |
| `Fish Tycoon` | `low` | `5` | `static` | `FishTycoon.exe` | `trial_or_upsell` | `This shop item is only available in the full version.||||` |
| `Five Card Deluxe` | `low` | `5` | `static` | `FiveCardDeluxe.exe` | `trial_or_upsell` | `Full Version` |
| `Funny Creatures` | `low` | `5` | `static` | `FunnyCreatures.exe` | `trial_or_upsell` | `This level is available only in the full version!` |
| `G2 Geeks Unleashed` | `low` | `5` | `static` | `GeeksPC.exe` | `trial_or_upsell` | `BUY NOW` |
| `Geom` | `low` | `5` | `static` | `framework.exe` | `trial_or_upsell` | `Buy the Full Version now and Get :-` |
| `Hangman Wild West 2` | `low` | `5` | `direct` | `Hangman.exe` | `trial_or_upsell` | `Trial Version` |
| `Hidden Wonders Of The Depths` | `low` | `5` | `static` | `HWD.exe` | `trial_or_upsell` | `Buy Now.url` |
| `Holiday Bonus` | `low` | `5` | `static` | `HolidayBonus.exe` | `trial_or_upsell` | `Sorry, the demo time-limit has expired. For more fun, levels and unlockable pictures please get the full version.` |
| `Invadazoid` | `low` | `5` | `static` | `Invadazoid.exe` | `trial_or_upsell` | `Click here to get the Full Version` |
| `Jewel Quest Mysteries` | `low` | `5` | `static` | `EmeraldTear.exe` | `trial_or_upsell` | `Evaluation Copy` |
| `Jojos Fashion Show` | `low` | `5` | `static` | `JojosFashionShow.exe` | `trial_or_upsell` | `N[Full Version]` |
| `Jojos Fashion Show 2` | `low` | `5` | `static` | `JojosFashionShow2.exe` | `trial_or_upsell` | `[Full Version]` |
| `Kitten Sanctuary` | `low` | `5` | `static` | `KittenSanctuary.exe` | `trial_or_upsell` | `Buy Now` |
| `Legend of Aladdin` | `low` | `5` | `static` | `LegendOfAladdin.exe` | `trial_or_upsell` | `YOU ARE PLAYING THE FULL VERSION` |
| `Machine Hell` | `low` | `5` | `static` | `MachineHell.exe` | `trial_or_upsell` | `in full version only.` |
| `Magic Academy` | `low` | `5` | `static` | `academy.exe` | `trial_or_upsell` | `Trial version` |
| `Magic Ball 2 New Worlds` | `low` | `5` | `static` | `MagicBall2.exe` | `trial_or_upsell` | `Full version` |
| `Magic Stones` | `low` | `5` | `static` | `Magic Stones.exe` | `trial_or_upsell` | `Sorry, but the trial version limits your druid to level 3. You can still play the game until the 90 minutes trial expires, but you won't be able to gain further levels.` |
| `Mah Jong Quest 3` | `low` | `5` | `static` | `MahjongQuest3.exe` | `trial_or_upsell` | `Evaluation Copy` |
| `Miss Management` | `low` | `5` | `static` | `Miss Management.exe` | `trial_or_upsell` | `R[Full Version]` |
| `Musikapa` | `low` | `5` | `static` | `game.exe` | `trial_or_upsell` | `c:\Projects\Musikapa\Musikapa\Full Version\3DArkanoid.pdb` |
| `My Kingdomforthe Princess` | `low` | `5` | `static` | `mykingdomfortheprincess.exe` | `trial_or_upsell` | `Trial version` |
| `Mysteryville` | `low` | `5` | `static` | `Mysteryville.exe` | `trial_or_upsell` | `Trial version` |
| `Mysteryville 2` | `low` | `5` | `static` | `Mysteryville2.exe` | `trial_or_upsell` | `Trial version` |
| `Out Of Your Mind` | `low` | `5` | `static` | `Out Of Your Mind.exe` | `trial_or_upsell` | `M[Full Version]` |
| `Paradoxion` | `low` | `5` | `static` | `Paradoxion.exe` | `trial_or_upsell` | `Buy Now!` |
| `Peggle Deluxe` | `low` | `5` | `static` | `Peggle.exe` | `trial_or_upsell` | `Trial Version` |
| `Peggle Nights` | `low` | `5` | `static` | `PeggleNights.exe` | `trial_or_upsell` | `The rest of Adventure mode is locked in this free trial version. You can still continue playing ^00FF00^Quick Play^oldclr^, ^00FF00^Duel^oldclr^ or the newly unlocked ^00FF00^Challenge^oldclr^ mode.` |
| `Pirates of Treasure Island` | `low` | `5` | `static` | `Pirates of Treasure Island.exe` | `trial_or_upsell` | `You may only use the re-scramble function one time in this trial version. The full version offers unlimited usage of this function!` |
| `Pirateville` | `low` | `5` | `static` | `Pirateville.exe` | `trial_or_upsell` | `Trial version` |
| `PJ Pride Pet Detective` | `low` | `5` | `static` | `PJPride.exe` | `trial_or_upsell` | `Evaluation Copy` |
| `Platypus` | `low` | `5` | `static` | `platypus.exe` | `trial_or_upsell` | `BUY FULL VERSION` |
| `PopATronic` | `low` | `5` | `static` | `Popatronic.exe` | `trial_or_upsell` | `Buy Now!` |
| `Puzzle Express` | `low` | `5` | `static` | `PuzzleExpress.exe` | `trial_or_upsell` | `Full Version` |
| `Puzzle Inlay` | `low` | `5` | `static` | `PuzzleInlay.exe` | `trial_or_upsell` | `This is a trial version. You can run it 14 times. Registering the game removes all limitation and opens access to over 50 new levels. For details see` |
| `Reaktor` | `low` | `5` | `static` | `Reaktor.exe` | `trial_or_upsell` | `NOW YOU CAN BUY FULL VERSION OF REAKTOR` |
| `Rotate Mania Deluxe` | `low` | `5` | `static` | `rmaniadeluxe.exe` | `trial_or_upsell` | `#-#1In full version:` |
| `Sky Bubbles Deluxe` | `low` | `5` | `static` | `SkyBubbles.exe` | `trial_or_upsell` | `BUY NOW` |
| `Smash Frenzy 2` | `low` | `5` | `static` | `SF2.exe` | `trial_or_upsell` | `Full version` |
| `Space Strike` | `low` | `5` | `static` | `game.exe` | `trial_or_upsell` | `To continue playing, please upgrade to the full version.` |
| `Spandex Force` | `low` | `5` | `static` | `Spandex Force.exe` | `trial_or_upsell` | `|the full version of the game. Click on the Buy Now button` |
| `Sportball` | `low` | `5` | `static` | `Sportball.exe` | `trial_or_upsell` | `Full Version` |
| `Starscape` | `low` | `5` | `static` | `Starscape.exe` | `trial_or_upsell` | `Buy Now (22)` |
| `StoneLoops Of Jurassica` | `low` | `5` | `static` | `StoneLoops.exe` | `trial_or_upsell` | `only in the full version!` |
| `Supercow` | `low` | `5` | `static` | `supercow.exe` | `trial_or_upsell` | `Trial version` |
| `Tasty Planet` | `low` | `5` | `static` | `tastyplanet.exe` | `trial_or_upsell` | `Get the Full Version` |
| `The Magicians Handbook Cursed Valley` | `low` | `5` | `static` | `The Magicians Handbook Cursed Valley.exe` | `trial_or_upsell` | `Would you like to read the full version of the story or the quick version?` |
| `Tiks Texas Hold Em` | `low` | `5` | `static` | `HoldEm.exe` | `trial_or_upsell` | `You are out of chips. Would you like to rebuy now?` |
| `Top Chef` | `low` | `5` | `static` | `TopChef.exe` | `trial_or_upsell` | `[Full Version]` |
| `Treasure Fall` | `low` | `5` | `static` | `tf.exe` | `trial_or_upsell` | `REMOVE THIS DELAY; BUY THE FULL VERSION TODAY` |
| `Treasure Island` | `low` | `5` | `static` | `treasureisland.exe` | `trial_or_upsell` | `Trial version` |
| `Tropico Jong` | `low` | `5` | `static` | `TropicoJong.exe` | `trial_or_upsell` | `FULL version` |
| `Wonderland Secret Worlds` | `low` | `5` | `static` | `Wonderland.exe` | `trial_or_upsell` | `GET THE FULL VERSION` |
| `Wonderlines` | `low` | `5` | `static` | `wonderlines.exe` | `trial_or_upsell` | `Trial version` |
| `Xmas Bonus` | `low` | `5` | `static` | `xmasbonus.exe` | `trial_or_upsell` | `You have reached the end of the demo. Please buy the full version to get 100 levels!` |
| `5 Spots II` | `low` | `4` | `static` | `5spots2.exe` | `demo_or_presentation` | `Thanks for playing the demo version of 5spots2. We hope you enjoyed it!` |
| `Action Ball` | `low` | `4` | `static` | `actionball.exe` | `demo_or_presentation` | `DEMO VERSION` |
| `Action Ball Deluxe` | `low` | `4` | `static` | `actionball.exe` | `demo_or_presentation` | `DEMO VERSION` |
| `Alien Shooter` | `low` | `4` | `static` | `AlienShooter.exe` | `demo_or_presentation` | `Presentation version. Not for sale!` |
| `Amazon Quest` | `low` | `4` | `static` | `AQuest.exe` | `demo_or_presentation` | `--- Initialized demo version` |
| `Amulet Of Tricolor` | `low` | `4` | `static` | `Game.exe` | `demo_or_presentation` | `Not for sale` |
| `AquaPOP` | `low` | `4` | `static` | `AquaPop.exe` | `demo_or_presentation` | `--- Initialized demo version` |
| `Carls Classics` | `low` | `4` | `static` | `cc.exe` | `demo_or_presentation` | `Shareware` |
| `Chaks Temple` | `low` | `4` | `static` | `ChakTemple.exe` | `demo_or_presentation` | `Presentation version. Not for sale!` |
| `City Magnate` | `low` | `4` | `static` | `CityMagnate.exe` | `demo_or_presentation` | `This is a DEMO version of the game.` |
| `Fish Tales` | `low` | `4` | `static` | `FishTales.exe` | `demo_or_presentation` | `--- Initialized demo version` |
| `Froggy Castle 2` | `low` | `4` | `static` | `FC2.exe` | `demo_or_presentation` | `@Demo Version %d.%d` |
| `Gumboy Crazy Adventures` | `low` | `4` | `static` | `GumboyCrazyAdventures.exe` | `demo_or_presentation` | `DEMO VERSION` |
| `Hd O Adventure Frankenstein` | `low` | `4` | `static` | `Frankenstein.without_hot_links.exe` | `demo_or_presentation` | `Launch the demo version` |
| `Hd O Adventure Hollywood` | `low` | `4` | `static` | `Hollywood.exe` | `demo_or_presentation` | `Launch the demo version` |
| `Hd O Adventure Secretsofthe Vatican` | `low` | `4` | `static` | `Vatican.without_hot_links.exe` | `demo_or_presentation` | `Launch the demo version` |
| `Hd O Adventure The Time Machine` | `low` | `4` | `static` | `TimeMachine.exe` | `demo_or_presentation` | `Launch the demo version` |
| `Jam XM` | `low` | `4` | `static` | `jamxm.exe` | `demo_or_presentation` | `ATTENTION! This is a DEMO version !` |
| `Jaspers Journeys` | `low` | `4` | `static` | `jasper.exe` | `demo_or_presentation` | `This is the demo version of Jasper which contains the` |
| `Jets N Guns` | `low` | `4` | `static` | `JnG.exe` | `demo_or_presentation` | `NOT FOR SALE` |
| `Many Years Ago` | `low` | `4` | `static` | `ManyYearsAgo.exe` | `demo_or_presentation` | `DEMO VERSION` |
| `Naval Strike` | `low` | `4` | `static` | `NavalStrike.exe` | `demo_or_presentation` | `--- Initialized demo version` |
| `Psychoballs` | `low` | `4` | `static` | `PsychoBalls.exe` | `demo_or_presentation` | `gfx/shareware.jpg` |
| `Redisruption` | `low` | `4` | `static` | `game.exe` | `demo_or_presentation` | `Redisruption problem (Shareware)` |
| `Restaurant Empire` | `low` | `4` | `static` | `re.exe` | `demo_or_presentation` | `Sale Type: Not for sale nor for lease` |
| `Rock Frenzy` | `low` | `4` | `static` | `rf.exe` | `demo_or_presentation` | `This is a DEMO version of` |
| `Sarah Maribuandthe Lost World` | `low` | `4` | `static` | `Sarah Maribu and The Lost World.exe` | `demo_or_presentation` | `@DEMO VERSION` |
| `The Dark Legions` | `low` | `4` | `static` | `TheDarkLegions.exe` | `demo_or_presentation` | `SHAREWARE_WWW` |
| `The Great Mahjong` | `low` | `4` | `static` | `Mahjong.exe` | `demo_or_presentation` | `Not available in demo version!` |
| `Theseus Return of the Hero` | `low` | `4` | `static` | `Theseus.exe` | `demo_or_presentation` | `Presentation version. Not for sale!` |
| `Wik Fable Of Souls` | `low` | `4` | `static` | `Wik.exe` | `demo_or_presentation` | `As in "Zax DEMO Version 1.0 Build 345"` |
| `Wonderland Adventures Mysteriesof Fire Island` | `low` | `4` | `static` | `Wonderland.exe` | `demo_or_presentation` | `Thank you for playing the demo version of` |
| `Xeno Assault II` | `low` | `4` | `static` | `Xeno.exe` | `demo_or_presentation` | `Demo Version` |
| `Zero Count` | `low` | `4` | `static` | `Zero Count.exe` | `demo_or_presentation` | `SHAREWARE TIMER:` |
| `Zombie Shooter` | `low` | `4` | `static` | `ZombieShooter.exe` | `demo_or_presentation` | `Presentation version. Not for sale!` |

## Missing Outputs

- `Gekko Mahjong/Data/System`

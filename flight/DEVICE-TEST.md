# Flight · softwareverifikation og fysisk enhedstest

Status 2026-11-09: Flight 0.2.0 er fysisk afprøvet som en afgrænset smoke-test.
Pluginfilerne er byteidentiske med `38bcb8d98b99d19814131d24a7dfd252df50ebe9`;
SDK'et er fra `f326564`. Den installerede ejer-godkendte core rapporterer build
`2911e2dd17e578dc` på Waveshare 7B / ESP32-P4 revision 1.3.

Ejeren bekræfter kort/fly, flyvalg, zoom og Flight/kort efter fysisk RESET.
Tre USB-genindlæsninger med billeder samt stop/oprydning og automatisk
sessionudløb er kontrolleret. Wi-Fi forblev tilsluttet ved kontrolpunkterne.
Efter den efterfølgende læsende browser-chipaflæsning bekræfter ejeren igen
Flight, og USB bekræfter samme build og tilsluttet Wi-Fi.

Kontrolleret Wi-Fi-udfald/genforbindelse er udskudt efter ejerens ønske.
Strømudfald under cache, individuel visuel kvittering for et bestemt logo og
langtidstest er ikke attesteret. Andre skærmmodeller er ikke fysisk afprøvet.
Katalogets udgivelsesstatus er ikke en påstand om disse manglende testresultater.

- 17 offentlige Lua-tests: liste, dataalder, enheder, valg, kortdata, ICAO,
  manglende mediestøtte, rate-limit og annullering.
- SDK/pakke-tests og browserens simulerede USB-kontrakt kontrollerer, at en
  ældre core afvises før parring/upload. Pakken har fortsat kun fire tekstfiler.
- Private tests udfører den rigtige Lua-loader, skærmbibliotek og bounded
  billeddecoder med syntetiske billeder på 800×480 og 1024×600. Cache-/kø-/
  fejlsvar testes med kunstige platformadaptere. Ingen privat kilde medfølger her.

Gamle Counter-tests gælder ikke Flight; ovenstående Flight-resultater og begrænsninger er testgrundlaget.

## Fysisk forløb — kræver konkret ejeraccept

1. Bekræft hardware/revision og den præcise private core-build. Bevar NVS,
   Wi-Fi, partitioner og rollback. Pluginudvikleren skal ikke have core-kilden.
2. Installér den godkendte udviklings-core én gang. Kontrollér boot, Wi-Fi,
   minimal core-startside og `httpFlight=true` og `flightMedia=1`. En core uden mediestøtte afvises.
3. Kør `hn.py check/pack`, vælg kun `flight`, og par fysisk med en frisk kode.
   Brug `--config` til valideret placering/radius; ingen andre plugins indlæses.
4. Bekræft et skrivbart cachelager uden formatering. Se rigtige kortfliser,
   synlig OpenStreetMap-kildeangivelse, zoom og flyvalg ved berøring. Kontrollér
   kendt ICAO-logo samt tekstfallback ved ukendt fly. Se live kaldesignaler, højde, fart og afstand. Sammenhold med datakilden.
   Kontrollér Opdater, Forrige/Næste og skift mellem m/km/t og ft/kn/NM.
5. Skift til cores indstillinger og tilbage: ingen polling mens skjult og ingen
   gammel callback til frigivet UI. Stop/genindlæs flere gange; core/Wi-Fi fortsætter.
6. Afbryd netværket kontrolleret, se fejl/dataalder, og genopret forbindelsen.
   Test tomt/ugyldigt/stort/429-svar i host-fixtures, ikke ved at misbruge tjenesten.
7. Lad USB-sessionen udløbe; kontrollér frigivne widgets/Lua og ingen fortsatte jobs.
8. Registrér præcis plugin-commit/pakkehash, core-version/API/capabilities,
   boardrevision og faktisk resultat. Del ikke private core-dumps, kode eller tokens.

Udgivelsen følger `dev` → `test` → `main` med ovenstående afgrænsede testgrundlag
og de dokumenterede udskydelser. En metadataændring attesterer ikke nye fysiske
prøver. Se også [fælles procedure](../_sdk/DEVICE-TEST.md).

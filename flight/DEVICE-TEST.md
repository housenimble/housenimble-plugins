# Flight · softwareverifikation og fysisk enhedstest

Status 2026-11-09: 0.2.0 med kort/logoer er softwaretestet; fysisk test mangler.

- 17 offentlige Lua-tests: liste, dataalder, enheder, valg, kortdata, ICAO,
  manglende mediestøtte, rate-limit og annullering.
- SDK/pakke-tests og browserens simulerede USB-kontrakt kontrollerer, at en
  ældre core afvises før parring/upload. Pakken har fortsat kun fire tekstfiler.
- Private tests udfører den rigtige Lua-loader, skærmbibliotek og bounded
  billeddecoder med syntetiske billeder på 800×480 og 1024×600. Cache-/kø-/
  fejlsvar testes med kunstige platformadaptere. Ingen privat kilde medfølger her.

**Fysisk TLS, SD/SPIFFS, hukommelse over tid, touch, offline/reconnect og genstart
på denne nye core er ikke attesteret.** Gamle Counter-tests gælder ikke Flight.

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

Ingen markering som Udgivet eller produktion før det faktiske testforløb og
`dev` → `test` → `main` er gennemført. Se også [fælles procedure](../_sdk/DEVICE-TEST.md).

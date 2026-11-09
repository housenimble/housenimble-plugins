# Flight · fly i nærheden

En selvstændig Lua-side, der henter fly i nærheden direkte fra
[adsb.fi](https://adsb.fi/) gennem cores afgrænsede HTTPS-binding.
Ingen Home API, database, login eller andre plugins er nødvendige.

**Status 2026-11-09: version 0.2.0 med kort og logoer til software- og enhedstest.**
Kræver en ejerinstalleret udviklings-core med `httpFlight=true` og `flightMedia=1`.
Den nye medieudvidelse er endnu ikke fysisk testet eller udgivet til produktion.

## Visning og betjening

- Liste over fly med kaldesignal, afstand, højde, fart og retning.
- Registrering, type og position for det valgte fly. Forrige/Næste bevarer valget
  efter opdatering, når samme fly stadig findes.
- Filtrering efter placering/radius, friske positioner og eventuelt fly på jorden.
- Sortering efter afstand, metrisk/luftfarts-enheder, manuel og automatisk opdatering.
- Dataalder, fejl og rate-limit vises. Gamle data bevares tydeligt ved udfald;
  gamle positioner mærkes GAMMEL/OLD. Ukendte tal bliver ikke til nul.
- Op til 80 modtagne fly; ved afgrænset svar vises en begrænsningsmarkering.
  Det er ikke en garanti for alle eller de globalt nærmeste fly ved store områder.
- Dansk/engelsk og synlig kildeangivelse.

Kortet viser flyenes positioner/retning, søgeområde og valgt fly. Tryk på et fly
for at vælge det; +/− ændrer zoom. Listen kan rulles, mens de fire betjeningsknapper
bliver stående. Flyselskabslogo udledes af et identificerbart ICAO-kaldesignal;
ukendte eller manglende logoer erstattes af tekst, aldrig et opdigtet logo.
Ruteopslag er ikke medtaget. Data afhænger af modtagere og tjenestens dækning.

Core henter kun de synlige OpenStreetMap-fliser. En skrivbar SD-cache eller en
allerede monterbar SPIFFS-partition er nødvendig til kortfliser; core formaterer
ikke lager. Uden cache vises flyene på en tydeligt markeret radarbaggrund.
Kort/logoer har egne grænser uden for Lua-RAM; cachefejl og manglende logoer
stopper ikke flylisten. Cache beholdes mindst syv dage og har højst 32 pladser.

## Konfiguration

Skemaet indeholder GLOBAL, sprog, breddegrad, længdegrad, radius (1–450 km),
opdatering (10–300 sekunder), antal fly (1–80) og visning af fly på jorden.
Standardplaceringen er **Københavns centrum**, ikke ejerens hjem. Land/område
bestemmes af koordinater; der kræves ingen intern geokodning eller database.

Gem eksempelvis denne **ikke-hemmelige** fil uden for Git som `flight-config.json`:

```json
{"latitude":55.6761,"longitude":12.5683,"radius_km":30,"language":"da"}
```

Hent/installer først en ejerautoriseret udviklings-core med capabilities `httpFlight=true` og `flightMedia=1`.
Testklienten kontrollerer dette før fysisk parring og afviser en ældre core:

```sh
python3 -m pip install -r _tools/requirements.txt
python3 _tools/hn.py test flight --port <USB-port> --isolated --duration 840 --config /sti/flight-config.json
```

Omitér `--config` for schemaets standarder. Core validerer alle værdier igen.
Dette kræver ingen genbygning af core pr. ændring eller installation af andre plugins.
Der er endnu ingen generel indstillingseditor på skærmen til Lua-pluginers felter;
konfigurationen leveres ved USB-test. Wi-Fi og generelle indstillinger ejes af core.

## Afgrænset netværk

Manifestet anmoder om de tre præcise origins `https://opendata.adsb.fi`,
`https://tile.openstreetmap.org` og `https://raw.githubusercontent.com`. Core giver kun dette
plugin en anonym **GET**-adgang til `/api/v3/lat/LAT/lon/LON/dist/NM` med validerede
koordinater/radius. Kilometer omregnes til NM. Ingen redirects, frie LAN-mål,
credentials, cookies eller andre origins i Lua-HTTP-bindingen.
Kort og logoer går gennem `ctx.ui.flight_map`, hvor core bygger de faste billed-URL’er.
Lua kan ikke hente vilkårlige billeder eller se billedbytes/filstier. Lua kan ikke tilføje headers eller token.

Netværksarbejdet kører uden for UI/Lua. Rå svardata, JSON, jobkø og leveret resultat
har separate budgetter. Core leverer kun godkendte scalarfelter for op til 80 fly.
Nye requests begrænses også i hosten, så genindlæsning ikke omgår tjenestens pause.
Callbacks annulleres ved skjul/fjernelse og må ikke ramme en ny plugininstans.
Se [HOST-CONTRACT.md](HOST-CONTRACT.md) og [enhedstest](DEVICE-TEST.md).

## Lokal test og pakning

```sh
python3 -m pip install -r flight/tests/requirements.txt
python3 -m unittest discover -s flight/tests -v
python3 _tools/hn.py check flight
python3 _tools/hn.py pack flight --out /tmp/flight.hnplugin
```

De offentlige tests kræver ingen privat core, fysisk enhed eller netværkskonto.
De udfører den faktiske Lua-kode med syntetiske svar. Privat core har derudover
testet samme offentlige Lua-pakke gennem sin reelle loader, JSON/config-binding
og LVGL på to skærmstørrelser. Kort/logo-tests bruger syntetiske billeder og flydata; de attesterer ikke fysisk
ESP32-TLS, SD/SPIFFS eller berøring på den nye firmware. Dette er ikke en fysisk test af ESP32-netværk.

## Data og vilkår

Kilde: [adsb.fi API](https://github.com/adsbfi/opendata). v3-positionsendpointet
anbefales til nye integrationer og tillader radius op til 250 NM.
API'et er til personlig, ikke-kommerciel brug; kommerciel anvendelse kræver en
særskilt aftale/egnet datakilde. Bevar kildeangivelsen i UI. Pluginets nye Lua-kode
er MIT; det ændrer ikke dataleverandørens vilkår. Ingen privat C++ er kopieret hertil.


## Test fra en hjemmeside

Den offentlige `_sdk/web-usb.js` implementerer samme parrede USB-protokol som
Python-klienten. Hjemmesiden kan hente en fast, verificeret pluginversion og
indlæse Flight direkte via Web Serial. USB-kode og sessionstoken sendes kun til
enheden, aldrig til webserveren. Core-firmware leveres ikke af SDK'et.
En kompatibel ejerinstalleret udviklings-core kræves; den eksisterende native
firmware afvises før parring/upload. Dette er stadig en midlertidig udviklingstest.

Browsertransportens kontrakttest kan køres med Node 20+:

```sh
node _tests/web/usb.mjs
```

Kort: [OpenStreetMap](https://www.openstreetmap.org/copyright), med synlig
kildeangivelse og [tilepolitik](https://operations.osmfoundation.org/policies/tiles/).
Logoer hentes fra [airline-logos](https://github.com/sexym0nk3y/airline-logos)
ved en fast revision. Billederne medfølger ikke pluginpakken; varemærker og
billedrettigheder tilhører deres respektive ejere og dækkes ikke af pluginets MIT-licens.

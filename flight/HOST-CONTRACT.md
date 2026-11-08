# Flight · host-kontrakt, API 1-udvidelse

Flight bruger de eksisterende UI-primitiver og lifecycle samt følgende afgrænsede
HTTP-del-API. Capability annonceres som `hello.capabilities.httpFlight=true`.
En ældre core må ikke accepteres, blot fordi den tilbyder `coreApi=1`.

```lua
local id = ctx.http.request({
  method="GET",
  url="https://opendata.adsb.fi/api/v3/lat/55.67610/lon/12.56830/dist/16.199",
  tag="<instans>:<sekvens>", timeout_ms=8000, max_response_bytes=32768
})
ctx.http.cancel(id)
```

Kun anmodet og host-godkendt Flight-grant eksponerer `ctx.http`. Ukendte felter,
credentials og andre metoder afvises. Request returnerer et positivt id eller nil
ved afvist grant/rate-limit/fuld kø. Callback er altid asynkron og kommer kun på
UI-tråden med `name="http"`, `id`, uændret `tag`, `status`, `now_ms`, eventuel
`error`, `retry_after_ms` og et begrænset dekodet `json`-objekt. Eventets `json.ac`
indeholder kun scalarfelterne `hex`, `flight`, `r`, `t`, `lat`, `lon`, `alt_baro`,
`gs`, `track`, `seen_pos`; højst 80 rækker, med `json.truncated` ved begrænsning.
Tjenestens root `now` kan medfølge; det er ikke hostens monotone tidsbasis.

Host laver TLS-validering og håndhæver præcist origin/path, koordinater, radius,
requestsinterval, ingen redirects/credentials og separate rå-/JSON-/Lua-budgetter.
Der følges ingen links fra datakilden. Fejl svarer med faste, ufølsomme fejltyper.
Lange numeriske Retry-After-pauser bevares også efter stop/genindlæsning.

`name="tick", now_ms=<monotone millisekunder>` leveres til synligt plugin.
Skjul/stop annullerer job og timers uden at frigive en payload, mens en worker
stadig bruger den. Gamle svar må ikke leveres til en ny plugininstans.
Pluginet har højst ét request i gang og validerer id/tag, data og alder igen.

Host validerer schema-defaults og valgfri USB `begin.config` mod det afgrænsede
Flight-feltsæt. Ingen credentials, andre indstillinger eller ukendte felter tillades.
Konfiguration kopieres til `ctx.config`, ikke en global database.

Denne binding er **ikke** en fri HTTP/OAuth- eller Sonos-tjeneste. Spotify-pluginets
krav til OAuth og player-skrivninger er fortsat ikke understøttet af denne Flight-grant.

## Kort og logoer · flightMedia 1

Version 0.2 kræver desuden heltals-capability `hello.capabilities.flightMedia=1`.
Begge SDK-klienter afviser manglende/forkert version før parring og upload.
Den tidligere Flight-grant med kun adsb.fi kan stadig anvendes af ældre listepakker.

```lua
ctx.ui.flight_map({
  id="aircraft-map", latitude=55.6761, longitude=12.5683, radius_km=30,
  selected="abc123", airline_icao="SAS", language="da", age_seconds=0,
  points={{hex="abc123", callsign="SAS123", lat=55.68, lon=12.57, heading=90, seen=2}}
})
```

Funktionen returnerer en boolsk værdi og opretter/opdaterer ét kort (én widget).
Kun Flight med manifestets tre præcise origins i ovenstående rækkefølge får denne
funktion. Ingen URL, filsti, rå billeder eller credentials accepteres. Op til 80
positioner, radius 1–450 km, centrum ±85°/±180°, dataalder op til syv dage,
hex-id på seks små hextegn og valgfri ICAO-kode med tre store bogstaver.
`heading` er valgfri; `seen` er 0–60 sekunder. Tekstkaldesignal er højst 16 ASCII-tegn.
Tryk på et fly leverer eventnavnet `select:<hex>`; zoom håndteres af core.

Core begrænser PNG-input til 96 KiB pr. 256×256-kortflise og 64 KiB pr. logo
(højst 512×512). PNG-integritet og udpakket størrelse kontrolleres. Der er højst
otte synlige fliser, fire logoer i RAM og én aktiv mediejob. USB-statusfeltet
`mediaBytes` viser de tilbageholdte billedbytes særskilt fra `memoryBytes` for Lua.
Core reserverer persistent cache før en flisehentning, holder cache mindst syv
dage, undlader prefetch og følger ikke redirects. Ingen lagerformatering.
Ved stop frigives billeder; ved skjul annulleres jobs. Gamle resultater kasseres.

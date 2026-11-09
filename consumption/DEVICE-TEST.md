# Test: Forbrugsfordeling 0.1.0

Status: softwaretestet kandidat; ingen fysisk Consumption-test eller udgivelse.
Ejeren har valgt eksisterende Home API. Den tidligere Flight-test attesterer
ikke denne nye tjeneste eller renderer.

Lokale tests med kunstige data:

```sh
python3 -m pip install -r spotify/tests/requirements.txt
python3 -m unittest discover -s _tests -v
python3 -m unittest discover -s consumption/tests -v
python3 _tools/hn.py check consumption
python3 _tools/hn.py pack consumption --out /tmp/consumption.hnplugin
node _tests/web/usb.mjs
```

Lua-testene kører den faktiske main.lua med en kunstig host. De dækker data,
andele, nettotaler, manglende/negative priser, 20 kategorier, tom/ugyldig data,
perioder, fejl, skjulte sider, genindlæsning og sene svar. USB-klienterne afviser
ældre core før parring/upload. Private core-tests og kompilering foregår separat;
core-kilde, firmware og private logs lægges aldrig i dette repo.

Før udgivelse skal en præcis plugin-SHA og kompatibel core-SHA prøves på den
fysiske skærm efter ejerens særskilte accept. Bevar app-backup, Wi-Fi, NVS og
partitioner. Brug fysisk USB-parring og en lokal runtime-konfiguration med
korrekt api_origin; læg ikke den rigtige adresse eller målinger i Git.

Kontrollér dag/måned/år mod Home API, alle periodeknapper, rullende kategoriliste,
tomme perioder, manglende pris, fejl/tidligere data, stop/genindlæsning og fysisk
reset. Kontrollér også, at hjemmesiden skjuler kandidaten med en ældre bygger,
gemmer årsagen for admin og bevarer Home API-adressen ved gem/genåbn.
Registrér kun redigerede resultater og præcise versioner. Kontrolleret
netværksudfald, langtidstest og strømudfald er særskilte prøver; softwaretests
må ikke beskrives som beståede fysiske prøver.

# Test: Forbrugsfordeling 0.1.0

Status: afgrænset fysisk smoke-test bestået; udgivelse klargjort, ikke publiceret.
Ejeren har valgt eksisterende Home API. Se det redigerede
[testresultat](tests/device-result.json).

Præcis plugin-SHA `f43a07dab006277fd670321129a5041591dd15ae`, pakke-SHA-256
`5c532aa91633177277b73068059abbcf52cd5a7e4a8fd3589b74318523f9b851`, på
Waveshare 7B / ESP32-P4 rev1.3 med separat ejerprovisioneret core, der annoncerer
consumptionData=1/pieChart=1/settingsSchema=1. Ejeren bekræfter diagram,
kategorier, kWh, alle syv periode-/opdateringsknapper og rulning. Efter fysisk
RESET/RST kom diagram og data normalt tilbage.

Fysisk parring og to USB-indlæsninger består. Ved begge stop var Lua-RAM,
billed-RAM og widgets nul, Wi-Fi forblev tilsluttet, og den indbyggede
Forbrugsfordeling er startet igen. Den midlertidige USB-prøve skrev ingen
firmware. Testen attesterer kun den præcise pakke og dette afgrænsede forløb.
Netværks-/API-udfald, strømudfald, langtid og særskilt visuel kontrol af ukendt
pris/negative korrektioner er ikke fysisk prøvet. Softwareprøverne nedenfor
attesterer ikke disse fysiske scenarier. Ingen målinger, adresser, tokens,
private firmwarefiler eller rå logs medtages i resultatet.

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

Ved senere kandidater skal en præcis plugin-SHA og kompatibel core prøves på
den fysiske skærm efter ejerens særskilte accept. Den eksisterende smoke-test
godkender ikke automatisk en ny test-branch eller release. Bevar app-backup, Wi-Fi, NVS og
partitioner. Brug fysisk USB-parring og en lokal runtime-konfiguration med
korrekt api_origin; læg ikke den rigtige adresse eller målinger i Git.

Kontrollér dag/måned/år mod Home API, alle periodeknapper, rullende kategoriliste,
tomme perioder, manglende pris, fejl/tidligere data, stop/genindlæsning og fysisk
reset. Kontrollér også, at hjemmesiden skjuler kandidaten med en ældre bygger,
gemmer årsagen for admin og bevarer Home API-adressen ved gem/genåbn.
Registrér kun redigerede resultater og præcise versioner. Kontrolleret
netværksudfald, langtidstest og strømudfald er særskilte prøver; softwaretests
må ikke beskrives som beståede fysiske prøver.

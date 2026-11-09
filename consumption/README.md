# Forbrugsfordeling

Lua-kandidat, version 0.1.0. Viser dit Home API's faktiske forbrug fordelt på
kategorier med cirkeldiagram, kWh, andele og pris. Vælg dag, måned eller år,
gå til forrige/næste periode, eller vend tilbage til den aktuelle periode.
Diagrammets liste kan rulles, så alle kategorier kan læses.

**Ikke udgivet endnu.** Kataloget markerer kandidaten som `testable`, ikke
`installable`. Eksisterende Flight-core understøtter ikke den nye datatjeneste
eller cirkeldiagram. Der kræves særskilt godkendt core med `consumptionData=1`,
`pieChart=1` og en afsluttende fysisk test før udgivelse.

Ejeren har valgt sit eksisterende Home API som første datakilde. Angiv selv
serverens lokale adresse i `api_origin`, eksempelvis `http://192.168.1.10:8111`.
Ingen bestemt serveradresse er indbygget. Kun en eksplicit RFC1918 IPv4-adresse
og valgfri port accepteres; ingen sti, brugernavn, adgangskode eller DNS-navn.
Skærmen skal kunne nå serveren på det betroede lokale netværk. Denne adapter
bruger ukrypteret HTTP uden login; HTTPS/autentificerede adaptere er fremtidigt
arbejde. Pluginet kræver ingen andre plugins og ingen separat databaseadgang.

Serveren skal understøtte GET `/api/consumption?from=YYYY-MM-DD&to=YYYY-MM-DD`
med eksklusiv slutdato og returnere en JSON-liste:

```json
[{"date":"2026-11-09","type":"Varmepumpe","kwh":2.5,"price":7.0}]
```

Eksemplet er kunstigt. `price` er beløbet for målingen, ikke pris pr. kWh.
Manglende pris vises som `--`; valutaen vælges i opsætningen uden omregning.
Negative korrektioner medregnes i nettototalen og vises i status; diagrammets
andele beregnes af positivt forbrug. Tomme perioder giver en tomtilstand.
Ved fejl bevares tidligere data for samme periode med en tydelig fejltekst.
Core anvender sin egen dato/tidszone og afviser fremtidige perioder. Der er
plads til 32 kategorier; overskridelse afvises frem for skjult frasortering.

[Konfiguration](config.schema.json) · [offentlig host-kontrakt](HOST-CONTRACT.md)
· [test og manglende fysisk verifikation](DEVICE-TEST.md).

Land kan vælges som GLOBAL, DK, SE eller DE. Det er et opsætningsvalg, ikke en
påstand om færdig integration med alle lokale energiselskaber.

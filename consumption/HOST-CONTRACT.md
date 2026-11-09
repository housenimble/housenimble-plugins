# Consumption data service · version 1 (candidate)

This public interface is implemented alongside a separately provisioned private
host. It does not grant access on existing Flight-only firmware. A scoped
physical smoke test has passed for the exact package in DEVICE-TEST.md.
The feature catalog is prepared for release; promotion and production approval
remain separate. This does not attest a later test-branch commit.

The owner selected their existing Home API. A new installation supplies its own
`api_origin`, an explicit `http://` RFC1918 IPv4 address and optional port. There
is no built-in server address, DNS lookup, redirect, credential or cloud relay.
Only anonymous GET `/api/consumption?from=YYYY-MM-DD&to=YYYY-MM-DD` is allowed;
the end date is exclusive. This LAN adapter requires a trusted local network.
It is not a general HTTP grant. Authenticated/HTTPS adapters are future work.

Manifest permission `network: ["home-api:consumption"]` is a **named service
grant**, not a URL or origin. Only `housenimble.consumption` can request it.
Older validators/loaders reject it. USB requires `consumptionData: 1` and
`pieChart: 1` before pairing or upload; API/protocol 1 alone is insufficient.

`ctx.consumption.request({period="day"|"month"|"year", date="current"|ISO-date,
shift=-1|0|1, tag="…"})` returns a positive request id or nil. Core uses its own
clock/timezone, normalizes calendar periods, prevents future periods and admits
one bounded request at a time. No URL, headers, SQL, token or arbitrary dates
are passed to a general HTTP function. `cancel(id)` cancels the logical request;
stop/hide/replacement invalidate late results.

Event `name="consumption"` contains matching `id`, `tag`, `status`, `now_ms` and
either a fixed error label or `json={period,from,to,is_current,groups}`. Each of
at most 32 groups has `name`, finite `kwh`, and an optional finite `price`.
Prices are sums, not rates. A missing price on any source row leaves that
group's price unknown. Negative corrections contribute to the net total but
not to positive consumption shares. No category is silently dropped.

Provider rows are `{date,type,kwh,price?}`. Core checks calendar dates, UTF-8,
field sizes, finite numeric values, bounded row/category counts, response size,
deadline and completion before delivering an aggregate. Invalid/oversized data
fails closed. HTTP error/redirect bodies never reach Lua.

`ctx.ui.pie_chart({id,empty_text,slices={{label,value,detail},…}})` updates one
bounded chart with a scrollable legend. At most 32 slices; nonnegative finite
values; bounded UTF-8 text. All-zero input shows `empty_text`. Rendering and
cleanup belong to core. It is not a framebuffer or native-code interface.

Day/month/year navigation, refresh, totals and stale/error presentation belong
to the Lua plugin. Currency is a display unit matching the provider; no currency
conversion or invented price is performed.

# Ask your Mac about flights from Bali to Bangkok

You're planning a trip and either Bangkok airport works. From a chat connected to
CMDOP, ask a Mac with Fli installed:

> Use Fli on my Mac to check nonstop flights from Bali to either Bangkok airport
> on December 10, 2026, for one adult. Show the cheapest options in USD and their
> local departure times.

In a recorded CMDOP MCP call for that date, the search returned Thai Airways
TG432 departing at 16:10 and TG440 at 19:00, both arriving at Suvarnabhumi
(BKK). Each was quoted at US$341 during that search. Choose a future travel date
for your own run to get current fares.

## Where the answer comes from

CMDOP sends the request to the selected machine. A small client there calls
Fli's local MCP tool. Fli queries Google Flights and the result comes back to
the caller. Fli is an unofficial interface. The example searches fares and
leaves booking to the traveler.

Use the same workflow from [Python](../examples/python/google-flights.py) or
[TypeScript](../examples/typescript/google-flights.ts). To prepare Fli, run the
example, or save a successful search to your Desktop, follow the
[Google Flights recipe](../docs/examples/google-flights.md).

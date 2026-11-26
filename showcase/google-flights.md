# Ask your Mac about flights from Bali to Bangkok

You're planning a trip and either Bangkok airport works. From a chat connected to
CMDOP, ask a Mac with Fli installed:

> Use Fli on my Mac to check nonstop flights from Bali to either Bangkok airport
> on December 10, 2026, for one adult. Show the cheapest options in USD and their
> local departure times.

On November 26 at 19:02 Bali time, a manual search through CMDOP returned
Thai Airways TG432 for US$309 and TG440 for US$340. Both were nonstop flights
to Suvarnabhumi (BKK). Choose a future travel date to check current fares.

## Leave the result on your Desktop

Add one sentence to the request: “Save the results as Bangkok flights.md on
my Desktop.” In the recorded run, CMDOP created the file on the Mac and read
it back to verify that its contents matched the search.

With a US$320 threshold, a local alert helper submitted one macOS notification
for TG432. Replaying the same result kept the Mac quiet. The notification
request was verified during a manual run. A visible banner and an hourly
trigger from a cloud chat still need a recorded demonstration.

## Where the answer comes from

CMDOP sends the request to the selected machine. A small client there calls
Fli's local MCP tool. Fli queries Google Flights and the result comes back to
the caller. Fli is an unofficial interface. The example searches fares and
leaves booking to the traveler.

Use the same workflow from [Python](../examples/python/google-flights.py) or
[TypeScript](../examples/typescript/google-flights.ts). To prepare Fli, run the
example, or save a successful search to your Desktop, follow the
[Google Flights recipe](../docs/examples/google-flights.md).

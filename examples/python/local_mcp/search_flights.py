"""Find one-way nonstop flights from Bali to Bangkok using the local Fli server."""
import asyncio
import json
import math
import shutil
import sys
from datetime import date, datetime, timezone

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


def summarize(payload, departure_date):
    if not isinstance(payload, dict) or payload.get("success") is not True:
        raise ValueError("Fli could not complete the search")
    options = payload.get("flights")
    if not isinstance(options, list):
        raise ValueError("Missing flight list")
    fares = {}
    for option in options:
        legs = option["legs"]
        if len(legs) != 1 or option["currency"] != "USD":
            raise ValueError("Unexpected route or currency")
        leg = legs[0]
        if datetime.fromisoformat(leg["departure_time"]).date() != departure_date:
            raise ValueError("Unexpected departure date")
        price = option["price"]
        if type(price) not in (int, float) or not math.isfinite(price) or price < 0:
            raise ValueError("Invalid fare")
        number = f'{leg["airline_code"]}{leg["flight_number"]}'
        key = (number, leg["departure_time"], leg["arrival_airport"])
        if key not in fares or price < fares[key]["price"]:
            fares[key] = dict(flight=number, airline=leg["airline"], departure=key[1],
                              arrival_airport=key[2], price=price, currency="USD",
                              booking_url=option.get("booking_url"))
    return {"searched_at": datetime.now(timezone.utc).isoformat(), "date": departure_date.isoformat(),
            "flights": sorted(fares.values(), key=lambda row: row["price"])[:3]}


async def main():
    departure_date = date.fromisoformat(sys.argv[1])
    if departure_date < date.today():
        raise ValueError("Choose today or a future departure date")
    executable = shutil.which("fli-mcp")
    if not executable:
        raise RuntimeError("Install flights[mcp] in the target environment")
    server = StdioServerParameters(command=executable, args=[])
    async with asyncio.timeout(35), stdio_client(server) as streams:
        async with ClientSession(*streams) as client:
            await client.initialize()
            result = await client.call_tool("search_flights", {
                "origin": "DPS", "destination": "BKK,DMK", "departure_date": str(departure_date),
                "passengers": 1, "max_stops": "NON_STOP", "currency": "USD", "sort_by": "CHEAPEST",
            })
            if result.is_error:
                raise RuntimeError("Fli tool call failed")
            print(json.dumps(summarize(result.structured_content, departure_date)))


if __name__ == "__main__":
    asyncio.run(main())

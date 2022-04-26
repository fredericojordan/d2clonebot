import os

import requests
from discord.ext import commands

BASE_URL = "https://diablo2.io/dclone_api.php"


class RegionFilter:
    REGION_AMERICAS = 1
    REGION_EUROPE = 2
    REGION_ASIA = 3


class LadderFilter:
    LADDER = 1
    NON_LADDER = 2


class HardcoreFilter:
    HARDCORE = 1
    SOFTCORE = 2


class SortDirection:
    ASCENDING = "a"
    DESCENDING = "d"


class SortKey:
    PROGRESS = "p"
    REGION = "r"
    LADDER = "l"
    HARDCORE = "h"
    TIMESTAMP = "t"


def get_diablo_tracker(
    region=None, ladder=None, hardcore=None, sort_key=None, sort_direction=None
):
    params = {
        "region": region,
        "ladder": ladder,
        "hc": hardcore,
        "sk": sort_key,
        "sd": sort_direction,
    }
    filtered_params = {k: v for k, v in params.items() if v is not None}
    return requests.get(BASE_URL, params=filtered_params)


bot = commands.Bot(command_prefix="!")


@bot.command()
async def uberdiablo(ctx):
    response = get_diablo_tracker(
        ladder=LadderFilter.NON_LADDER,
        hardcore=HardcoreFilter.SOFTCORE,
        sort_key=SortKey.REGION,
    )
    progresses = [p["progress"] for p in response.json()]
    await ctx.send(
        f"Diablo Clone Progress Tracker!\nAmericas: {progresses[0]}/6, Europe: {progresses[1]}/6, Asia: {progresses[2]}/6\nData courtesy of  diablo2.io"
    )


bot.run(os.environ.get("TOKEN"))

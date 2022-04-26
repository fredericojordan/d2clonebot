import os

import discord
import requests
from discord.ext import tasks

BASE_URL = "https://diablo2.io/dclone_api.php"
DISCORD_CHANNEL_ID = int(os.environ.get("DISCORD_CHANNEL_ID", 0))


class Regions:
    AMERICAS = 1
    EUROPE = 2
    ASIA = 3
    TEXT = {1: "Americas", 2: "Europe", 3: "Asia"}


class Ladder:
    LADDER = 1
    NON_LADDER = 2
    TEXT = {1: "Ladder", 2: "Non-ladder"}


class Hardcore:
    HARDCORE = 1
    SOFTCORE = 2
    TEXT = {1: "Hardcore", 2: "Softcore"}


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
    headers = {"User-Agent": "d2clone"}
    response = requests.get(BASE_URL, params=filtered_params, headers=headers)
    return response.json() if response.status_code == 200 else None


class DCloneTracker:
    def __init__(self):
        self.progress = {
            (Regions.AMERICAS, Ladder.LADDER, Hardcore.HARDCORE): None,
            (Regions.AMERICAS, Ladder.LADDER, Hardcore.SOFTCORE): None,
            (Regions.AMERICAS, Ladder.NON_LADDER, Hardcore.HARDCORE): None,
            (Regions.AMERICAS, Ladder.NON_LADDER, Hardcore.SOFTCORE): None,
            (Regions.EUROPE, Ladder.LADDER, Hardcore.HARDCORE): None,
            (Regions.EUROPE, Ladder.LADDER, Hardcore.SOFTCORE): None,
            (Regions.EUROPE, Ladder.NON_LADDER, Hardcore.HARDCORE): None,
            (Regions.EUROPE, Ladder.NON_LADDER, Hardcore.SOFTCORE): None,
            (Regions.ASIA, Ladder.LADDER, Hardcore.HARDCORE): None,
            (Regions.ASIA, Ladder.LADDER, Hardcore.SOFTCORE): None,
            (Regions.ASIA, Ladder.NON_LADDER, Hardcore.HARDCORE): None,
            (Regions.ASIA, Ladder.NON_LADDER, Hardcore.SOFTCORE): None,
        }

    def update(self):
        progress_json = get_diablo_tracker()
        updated_statuses = []

        if not progress_json:
            return None
        else:
            for entry in progress_json:
                key = (int(entry["region"]), int(entry["ladder"]), int(entry["hc"]))
                if not self.progress[key] == int(entry["progress"]):
                    if self.progress[key]:
                        updated_statuses.append(key)
                    self.progress[key] = int(entry["progress"])

        return updated_statuses

    def text(self):
        text = ""
        for key, value in self.progress.items():
            text += f"**[{value}/6]** {Regions.TEXT[key[0]]} {Ladder.TEXT[key[1]]} {Hardcore.TEXT[key[2]]}\n"
        text += "> Data courtesy of diablo2.io"
        return text


class DiscordClient(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dclone_tracker = DCloneTracker()

    async def on_ready(self):
        self.report_status_update.start()

    async def on_message(self, message):
        if message.author == self.user:
            return

        if message.content.startswith("!uberdiablo"):
            self.dclone_tracker.update()
            await message.channel.send(self.dclone_tracker.text())

    @tasks.loop(seconds=60)
    async def report_status_update(self):
        updated_statuses = self.dclone_tracker.update()

        if not updated_statuses or not DISCORD_CHANNEL_ID:
            return

        message = ""
        for key in updated_statuses:
            progress = self.dclone_tracker.progress[key]
            message += f"**[{progress}/6]** {Regions.TEXT[key[0]]} {Ladder.TEXT[key[1]]} {Hardcore.TEXT[key[2]]} DClone updated\n"

        message += "> Data courtesy of diablo2.io"
        channel = self.get_channel(DISCORD_CHANNEL_ID)
        await channel.send(message)

    @report_status_update.before_loop
    async def setup(self):
        await self.wait_until_ready()


if __name__ == "__main__":
    token = os.environ.get("DISCORD_TOKEN")

    if token:
        client = DiscordClient(intents=discord.Intents.default())
        client.run(token)
    else:
        print("Please set the DISCORD_TOKEN environment variable!")
        exit(1)

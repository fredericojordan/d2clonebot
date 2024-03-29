import os
from typing import Optional

import discord
import requests
from discord.ext import tasks
from dotenv import load_dotenv

load_dotenv()

API_BASE_URL = os.environ.get("API_BASE_URL", "https://diablo2.io/dclone_api.php")
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
    headers = {"User-Agent": "d2clone-discord"}
    response = requests.get(API_BASE_URL, params=filtered_params, headers=headers)
    return response.json() if response.status_code == 200 else None


def filter_realm(key, region, ladder, hardcore):
    return (
        (not region or key[0] == region)
        and (not ladder or key[1] == ladder)
        and (not hardcore or key[2] == hardcore)
    )


def parse_args(args):
    if not args:
        return None, None, None

    region = None
    ladder = None
    hardcore = None

    if any("am" in arg for arg in args):
        region = Regions.AMERICAS
    if any("eu" in arg for arg in args):
        region = Regions.EUROPE
    if any("asi" in arg for arg in args):
        region = Regions.ASIA

    if any("non" in arg for arg in args):
        ladder = Ladder.NON_LADDER
    if any("ladder" in arg for arg in args) and not any("non" in arg for arg in args):
        ladder = Ladder.LADDER

    if any("hard" in arg for arg in args):
        hardcore = Hardcore.HARDCORE
    if any("soft" in arg for arg in args):
        hardcore = Hardcore.SOFTCORE

    return region, ladder, hardcore


class D2Clone(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        self.command_tree = discord.app_commands.CommandTree(self)
        self.dclone_status = {
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

    async def on_ready(self):
        self.report_status_update.start()

    async def setup_hook(self):
        await self.command_tree.sync()

    @tasks.loop(seconds=60)
    async def report_status_update(self):
        updated_statuses = self.update_dclone_status()

        if not updated_statuses or not DISCORD_CHANNEL_ID:
            return

        message = ""
        for key in updated_statuses:
            progress = self.dclone_status[key]
            message += f"**[{progress}/6]** {Regions.TEXT[key[0]]} {Ladder.TEXT[key[1]]} {Hardcore.TEXT[key[2]]} DClone updated\n"

        message += "> Data courtesy of diablo2.io"
        channel = self.get_channel(DISCORD_CHANNEL_ID)
        await channel.send(message)

    @report_status_update.before_loop
    async def setup(self):
        await self.wait_until_ready()

    def update_dclone_status(self):
        progress_json = get_diablo_tracker()
        updated_statuses = []

        if not progress_json:
            return None
        else:
            for entry in progress_json:
                key = (int(entry["region"]), int(entry["ladder"]), int(entry["hc"]))
                if not self.dclone_status[key] == int(entry["progress"]):
                    if self.dclone_status[key]:
                        updated_statuses.append(key)
                    self.dclone_status[key] = int(entry["progress"])

        return updated_statuses

    def status_text(self, region=None, ladder=None, hardcore=None):
        text = ""
        for key, value in self.dclone_status.items():
            if filter_realm(key, region, ladder, hardcore):
                text += f"**[{value}/6]** {Regions.TEXT[key[0]]} {Ladder.TEXT[key[1]]} {Hardcore.TEXT[key[2]]}\n"
        text += "> Data courtesy of diablo2.io"
        return text


if __name__ == "__main__":
    token = os.environ.get("DISCORD_TOKEN")

    if token:
        client = D2Clone(intents=discord.Intents.default())

        @client.command_tree.command()
        @discord.app_commands.describe(realm_filters="Realm keyword filters (e.g 'non-ladder softcore americas')")
        async def uberdiablo(
            interaction: discord.Interaction, realm_filters: Optional[str] = ""
        ):
            """Report Diablo Clone status"""
            client.update_dclone_status()
            region, ladder, hardcore = parse_args(realm_filters.split())
            text_message = client.status_text(
                region=region, ladder=ladder, hardcore=hardcore
            )
            await interaction.response.send_message(text_message)

        client.run(token)
    else:
        print("Please set the DISCORD_TOKEN environment variable!")
        exit(1)

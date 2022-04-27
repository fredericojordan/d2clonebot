# Diablo II: Resurrected - Diablo Clone Tracker Discord Bot

[![powered-by-diablo2.io](https://img.shields.io/badge/powered%20by-diablo2.io-green)](https://diablo2.io/)

This is a bot that scrapes the [Diablo Clone Tracker](https://diablo2.io/dclonetracker.php) API and offers some functionalities on Discord:

1. `!uberdiablo` command for Diablo Clone tracker verification.
2. Proactive reports when the tracker progresses.

## Quickstart

Click [this link](https://discord.com/api/oauth2/authorize?client_id=968258121803915264&permissions=3072&scope=bot) to add D2 Clone bot to your server!

## Running the bot

You may also download the code, alter it in any fashion and run the bot on your own computer.

1. Create a [Discord Application](https://discord.com/developers/applications), enable a bot account and create its authentication token.
2. Set your token as the `DISCORD_TOKEN` environment variable by running `export DISCORD_TOKEN=YOUR_TOKEN_HERE`.
   1. Optionally set the `DISCORD_CHANNEL_ID` to match the ID of the channel you wish to receive proactive status updates.
3. Download and run the bot by executing the following:
   ```shell
   git clone https://github.com/fredericojordan/d2clonebot.git
   cd d2clonebot
   python d2clone.py
   ```
4. Generate an invite link and add the bot to your Discord server.

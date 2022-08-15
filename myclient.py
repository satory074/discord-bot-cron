import platform
import sys
from typing import Optional

from discord import Client, TextChannel, utils

from botutility import BotUtility
from cronfunction import CronFunction


class MyClient(BotUtility, Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.cf: CronFunction

    async def on_ready(self):
        """Awakening of the Unbobo"""

        self.cf = CronFunction(self.guilds[0])

        channel: Optional[TextChannel] = utils.find(
            lambda c: c.name == "開発室", self.guilds[0].text_channels
        )

        if not channel:
            return

        # Post
        await channel.send(platform.uname())

        # Process
        func: str = sys.argv[1]
        await channel.send(f"Start cron: {func}")
        await eval(f"self.cf.{func}(channel)")

        exit()

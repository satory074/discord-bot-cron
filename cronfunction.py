import json
import os
import sys

sys.path.append(os.getcwd())

import copy
from datetime import timedelta
from typing import Any, Optional, Union

import requests
from discord import Guild, Member, Message, TextChannel

from botutility import BotUtility
from mydropbox import MyDropbox


class CronFunction(BotUtility, MyDropbox):
    def __init__(self, guild: Guild, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.guild: Guild = guild

    async def extract_attachments(self, channel: TextChannel) -> None:
        """ メッセージログファイルからattachmentを抽出して書き出す """

        PATH: str = f'{os.environ["HOME"]}/Dropbox/discord/log'
        OUTPUTFILE: str = "_attachments.json"
        OUTPUTPATH: str = f"{PATH}/{OUTPUTFILE}"

        # Initialize log file
        with open(OUTPUTPATH, mode="w") as f:
            pass

        output: dict = {}
        acount: int = 0  # attachment counter
        for file_ in os.listdir(PATH):
            acount = 0
            if os.path.splitext(file_)[1] == ".json" and file_ != OUTPUTFILE:
                # load channel message log
                with open(f"{PATH}/{file_}") as f:
                    df: dict = json.load(f)

                # add attachment
                for (dfk, dfv) in df.items():
                    acount += len(df[dfk]["attachments"])
                    for (_, av) in df[dfk]["attachments"].items():
                        dfv_ = copy.copy(dfv)
                        dfv_["attachments"] = av
                        output[av["id"]] = dfv_

                # number of attachments
                await channel.send((file_, acount))  # type: ignore

        # output
        with open(OUTPUTPATH, mode="w") as f:
            json.dump(output, f, ensure_ascii=False)

    async def output_log(self, channel: TextChannel) -> None:
        """ メッセージログをチャンネルごとに書き出す """

        for ch in self.guild.text_channels:
            await channel.send(ch.name)

            # Open log file
            dlog: dict[Union[int, str], Any] = {}

            # Create dict of discord.message
            async for message in ch.history(oldest_first=True):
                # attachment
                d_a: dict = {}
                if message.attachments:
                    for i, attachment in enumerate(message.attachments):
                        d_a[i] = {
                            "id": attachment.id,
                            "size": attachment.size,
                            "height": attachment.height,
                            "width": attachment.width,
                            "filename": attachment.filename,
                            "url": attachment.url,
                        }

                # discor.message
                d: dict[str, Any] = {
                    "author": {
                        "name": message.author.name,  # type: ignore
                        "discriminator": message.author.discriminator,  # type: ignore
                        "avatar": str(message.author.avatar),  # type: ignore
                        "bot": message.author.bot,  # type: ignore
                        "display_name": message.author.display_name,
                        "mention": message.author.mention,
                    },
                    "content": message.content,
                    "channel": {
                        "name": message.channel.name,  # type: ignore
                        "id": message.channel.id,
                        "category_id": message.channel.category_id  # type: ignore
                        if message.channel.category  # type: ignore
                        else "",
                        "category_name": message.channel.category.name  # type: ignore
                        if message.channel.category  # type: ignore
                        else "",
                    },
                    "attachments": d_a,
                    "created_at": (message.created_at + timedelta(hours=9)).strftime(
                        "%Y/%m/%d %H:%M:%S"
                    ),
                }

                # add
                dlog[message.id]: dict[str, Any] = d  # type: ignore

            # output
            filepath: str = f'{os.environ["HOME"]}/Dropbox/discord/log/{ch.name}.json'
            with open(filepath, mode="w") as f:
                json.dump(dlog, f, ensure_ascii=False)

    async def tenki(self, channel: TextChannel) -> None:
        """わーい！おひさまてんてーん！"""

        tenkilist: dict[str, str] = {
            "01": "☀",
            "02": "☀",
            "03": "⛅",
            "04": "☁",
            "09": "🌧",
            "10": "☔",
            "11": "🌩",
            "13": "❄",
            "50": "🌫",
            "other": "💩",
        }

        for user in self.guild.members:
            member: Optional[Member] = self.guild.get_member(user.id)
            if member is None:
                continue

            nick: str = member.display_name

            # Escape
            if user.bot:
                continue

            if not nick[-1] in tenkilist.values():
                continue

            try:
                await member.edit(nick=member.display_name)
            except Exception as e:
                print(e.args)
                continue

            # Get tenki
            pf: Optional[dict[str, dict[str, str]]] = self.get_profile()

            city: str = pf[user.name]["locate"]  # type: ignore
            key: str = self.get_environvar("KEY_OPENWEATHER")
            url: str = f"http://api.openweathermap.org/data/2.5/forecast?units=metric&q={city}&APPID={key}"
            data: dict = json.loads(requests.get(url).text)

            # Forecast icons
            ficon: list[str] = [
                tenkilist[li["weather"][0]["icon"][:-1]] for li in data["list"]
            ]

            # Change nick
            nick_ = ""
            for i, _ in enumerate(nick):
                if nick[i] in tenkilist.values():
                    nick_ += ficon.pop(0)
                else:
                    nick_ += nick[i]

            await member.edit(nick=nick_)
            await channel.send(f"{nick_}: {city}")

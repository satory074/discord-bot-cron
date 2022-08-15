import json
import os
import re
from typing import Any, Optional, Union

import pykakasi
from discord import Message, TextChannel, Webhook, utils


class BotUtility:
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.EMOJI_PATTERN: str = r"<:[0-9|a-z|_]+:[0-9]+>"  # Regex custom emoji

        kks = pykakasi.kakasi()
        kks.setMode("H", "a")
        kks.setMode("K", "a")
        kks.setMode("J", "a")
        self.kksconv = kks.getConverter()

    def get_environvar(self, key: str) -> str:
        """Return environments"""

        if key in os.environ:  # Heroku
            return os.environ[key]
        else:  # Local
            path: str = f'{os.environ["HOME"]}/Dropbox/discord/data/vars.json'
            with open(path) as f:
                vars: dict[str, str] = json.load(f)

            if key in vars:
                return vars[key]
            else:  # Error
                exit(f"Environment variable not found: {path}, {key}")

    def disassemble_content(self, content: str) -> list[str]:
        """文字列を絵文字を考慮しつつリストにする"""

        EMOJI_PATTERN: str = r"<:[0-9|a-z|_]+:[0-9]+>|."  # カスタム絵文字の正規表現 | 任意の文字
        return [e.group() for e in re.finditer(EMOJI_PATTERN, content)]

    def limitnchar(self, s: str, nchar: int = 1950) -> str:
        """文字数を制限する"""

        if len(s) > nchar:
            return s[:nchar] + "\n<--- 2000文字以上の文章は捨てた --->"
        else:
            return s

    async def post_subreply(self, message: Message, reply: str) -> None:
        """ デバッグ用チャンネルに投稿する """

        channel: TextChannel = utils.find(
            lambda c: c.name == "うんち", message.guild.text_channels  # type: ignore
        )

        data: dict[str, Any] = {"channel": channel, "reply": reply}
        await self.webhook(**data)

    async def webhook(
        self,
        channel: TextChannel,
        reply: str,
        avatar_url: Optional[str] = None,
        username: Optional[str] = None,
    ) -> None:
        """Post webhook message"""

        # Create webhook data
        data: dict[str, Union[str, TextChannel]] = {
            "content": reply,
        }

        if avatar_url:
            data["avatar_url"] = avatar_url

        if username:
            data["username"] = username

        # Get webhook
        webhooks: list[Webhook] = await channel.webhooks()

        # webhookを1つ拝借
        for w in webhooks:
            if w.token:  # 使えるwebhookがある場合
                webhook: Webhook = w
                break
        else:  # 使えるwebhookがない場合は作成
            webhook: Webhook = await channel.create_webhook(name="unbobo-webhook")

        await webhook.send(**data)

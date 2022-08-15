from discord import Intents

from botutility import BotUtility
from myclient import MyClient

unbobot: MyClient = MyClient(intents=Intents.all())
botutil: BotUtility = BotUtility()

unbobot.run(botutil.get_environvar("TOKEN"))

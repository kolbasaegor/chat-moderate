from botforge import Bot
from config import SETTINGS as S

bot = Bot(S['bot']['token'], config=S)

bot.loop()

import os
import logging	
import aiogram
from urllib.parse import urljoin
from aiogram.utils.executor import start_webhook
from Core.bot import bot, dp, BOT_TOKEN
import Core.handlers

async def on_startup(dp):
	await bot.set_webhook(WEBHOOK_URL)
	logging.warning("Start")

async def on_shutdown(dp):
	logging.warning("Shutdown")

WEBHOOK_HOST = os.environ["WEBHOOK_HOST"]
WEBHOOK_PATH = "/webhook/{}".format(BOT_TOKEN)
WEBHOOK_URL = urljoin(WEBHOOK_HOST, WEBHOOK_PATH)

WEBAPP_HOST = "0.0.0.0"
WEBAPP_PORT = os.environ["PORT"]

if __name__ == '__main__':
	start_webhook(
		dispatcher=dp,
		webhook_path=WEBHOOK_PATH,
		on_startup=on_startup,
		on_shutdown=on_shutdown,
		skip_updates=False,
		host=WEBAPP_HOST,
		port=WEBAPP_PORT
	)
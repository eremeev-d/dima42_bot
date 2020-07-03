from aiogram import types
from Core.bot import bot, dp

@dp.message_handler()
async def default_handler(message: types.Message):
	answer = "Мне не удалось распознать твою команду, напиши /help чтобы получить список доступных команд"
	await bot.send_message(message.chat.id, answer)
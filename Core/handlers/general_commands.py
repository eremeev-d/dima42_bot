from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from Core.bot import bot, dp

@dp.message_handler(commands = ['start'])
async def start_handler(message: types.Message):
	answer = "Привет, меня зовут StyleArtBot. Я - бот для стилизации изображений, отправь /help, чтобы получить список команд"
	await bot.send_message(message.chat.id, answer)

@dp.message_handler(commands = ['help'])
async def help_hadler(message: types.Message):
	answer = (
		"Доступные команды:\n"
		"/help - список доступных команд\n"
		"/cancel - отменить текущее действие\n"
		"/style - перенести на картинку один из доступных стилей (работает 5-10 секунд)\n"
		"/custom - перенести на картинку стиль с другой картинки (работает около 30 секунд)\n"
	)
	await bot.send_message(message.chat.id, answer)

@dp.message_handler(state='*', commands='cancel')
@dp.message_handler(Text(equals = 'cancel', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
	current_state = await state.get_state()
	if not current_state is None:
		await state.finish()
	await message.reply('Отменено', reply_markup=types.ReplyKeyboardRemove())
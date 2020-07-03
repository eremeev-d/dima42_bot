from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
import shutil
import os
from Core.bot import dp
from ML_models.CycleGAN import CycleGAN

style_names = [
	"Van Gogh",
	"Cezanne",
	"Monet",
	"Ukiyoe"
]

class StateGAN(StatesGroup):
	waiting_for_picture = State()
	waiting_for_style = State()

@dp.message_handler(commands = ['style'], state = "*")
async def style_transfer_start(message: types.Message, state: FSMContext):	
	await StateGAN.waiting_for_picture.set()
	await message.answer("Отправь картинку для переноса стиля", reply=False)

@dp.message_handler(state = StateGAN.waiting_for_picture, content_types = types.ContentTypes.PHOTO)
async def style_transfer_get_photo(message: types.Message, state: FSMContext):
	try:
		os.makedirs("img/{}".format(message.chat.id))
	except FileExistsError:
		pass
	await message.photo[-1].download("img/{}/photo.jpg".format(message.chat.id))
	keyboard = types.ReplyKeyboardMarkup(resize_keyboard = True)
	for name in style_names:
		keyboard.add(name)
	await message.answer("Выбери стиль:", reply_markup = keyboard)
	await StateGAN.waiting_for_style.set()

@dp.message_handler(state = StateGAN.waiting_for_style, content_types = types.ContentTypes.TEXT)
async def style_transfer_final(message: types.Message, state: FSMContext):
	# Get data
	if not message.text.title() in style_names:
		await message.reply("Я не могу использовать этот стиль :( Выбери из имеющихся")
		return
	style = message.text.title()
	# Answer 
	await message.reply("Картинка в обработке!", reply_markup = types.ReplyKeyboardRemove(), reply = False)
	#Process
	model = CycleGAN()
	photo_path = model.process("img/{}".format(message.chat.id), style)
	#Reply
	with open(photo_path, "rb") as photo:
		await message.reply_photo(photo, reply_markup = types.ReplyKeyboardRemove(), reply = False)
	# Clear everything
	current_state = await state.get_state()
	if not current_state is None:
		await state.finish()
	shutil.rmtree("img/{}".format(message.chat.id))

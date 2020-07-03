from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
import os
from Core.bot import dp
from Core.img_funcs import load_img, save_img
from ML_models.ModelNST import ModelNST

class StateNST(StatesGroup):
	waiting_for_content = State()
	waiting_for_style = State()

@dp.message_handler(commands = ['custom'], state = "*")
async def nst_start(message: types.Message, state: FSMContext):
	await StateNST.waiting_for_content.set()
	await message.answer("Отправь картинку, на которую надо перенести стиль", reply=False)

@dp.message_handler(state = StateNST.waiting_for_content, content_types = types.ContentTypes.PHOTO)
async def nst_get_content(message: types.Message, state: FSMContext):
	await message.photo[-1].download("img\\content_{}.jpg".format(message.chat.id))
	await StateNST.waiting_for_style.set()
	await message.answer("Отправь картинку стиля", reply=False)

@dp.message_handler(state = StateNST.waiting_for_style, content_types = types.ContentTypes.PHOTO)
async def nst_get_style(message: types.Message, state: FSMContext):
	# Get photo
	await message.photo[-1].download("img\\style_{}.jpg".format(message.chat.id))
	await message.reply("Отлично! Твоё фото в обработке :)", reply=False)
	# Transformataion part
	content = load_img("img\\content_{}.jpg".format(message.chat.id))
	style = load_img("img\\style_{}.jpg".format(message.chat.id))
	model = ModelNST(content, style)
	processed_img = model.run_nst()
	save_img(processed_img, "img\\processed_{}.jpg".format(message.chat.id))
	# Finish and send 
	with open("img\\processed_{}.jpg".format(message.chat.id), "rb") as photo:
		await message.reply_photo(photo, reply=False)
	# Finish States
	del model
	current_state = await state.get_state()
	if not current_state is None:
		await state.finish()
	os.remove("img\\content_{}.jpg".format(message.chat.id))
	os.remove("img\\style_{}.jpg".format(message.chat.id))
	os.remove("img\\processed_{}.jpg".format(message.chat.id))
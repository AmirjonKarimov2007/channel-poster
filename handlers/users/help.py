from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandHelp
from filters.users import IsGroup
from loader import dp

@dp.message_handler(IsGroup())
async def falsereturn(message: types.Message):
    pass

@dp.message_handler(CommandHelp())
async def bot_help(message: types.Message):
    text = ("Buyruqlar: ",
            "/start - Botni ishga tushirish",
            "/help - Yordam")
    
    await message.answer("\n".join(text))
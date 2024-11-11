from functools import update_wrapper

from aiogram import types
from data.config import ADMINS
from loader import db,dp,bot
from aiogram.types import InlineKeyboardMarkup,InlineKeyboardButton
from filters.admins import IsSuperAdmin
from aiogram.types import CallbackQuery,Message
from keyboards.inline.main_menu_super_admin import main_menu_for_super_admin
from keyboards.inline.nomzodlar_btn import pin_posts_keyboard
@dp.callback_query_handler(IsSuperAdmin(),text='post_edit')
async def edit_post_handler(call: CallbackQuery):
    await call.answer(cache_time=1)
    markup = await pin_posts_keyboard()

    if call.message.caption:
        await call.message.delete()
        await call.message.answer(text="<b>📌Bu yerda siz qo'shgan  postlaringizni pin qilishingiz.</b>",
                                  reply_markup=markup)
    else:
        await call.message.edit_text("📌<b>Bu yerda siz qo'shgan  postlaringizni pin qilishingiz.</b>",
                                     reply_markup=markup)
async def check_post(post_id):
    pin_post = await db.select_post(pin=True)
    post = await db.select_post(id=int(post_id))
    check = post[0]['pin']
    if pin_post:
        if check == True:
            return True, ''
        else:
            return False, pin_post[0]['id']
    else:
        return 'nopin',''

@dp.callback_query_handler(IsSuperAdmin(),text_contains = 'post_pin:')
async def pinposthandler(call: CallbackQuery):
    await call.answer(cache_time=1)
    data = call.data.rsplit(":")
    post_id = data[1]
    check = await check_post(post_id)
    holat = check[0]
    pin_post_id = check[1]
    if holat==True:
        await call.message.edit_text('❗️Post Avvaldan Pin Qilingan edi.',reply_markup=main_menu_for_super_admin)
    elif holat=='nopin':
        pinned_post = await db.update_post_checkbox(pin=True,id=int(post_id))
        await call.message.edit_text('✅Post pin qilindi.',reply_markup=main_menu_for_super_admin)
    else:
        first_post_update = await db.update_post_checkbox(pin=False,id=int(pin_post_id))
        pinned_post = await db.update_post_checkbox(pin=True,id=int(post_id))
        await call.message.edit_text('✅Post pin qilindi.',reply_markup=main_menu_for_super_admin)


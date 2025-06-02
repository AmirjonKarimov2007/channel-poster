from datetime import datetime

from aiogram import types
from data.config import ADMINS
from keyboards.inline.nomzodlar_btn import posts_keyboard
from loader import db,dp,bot
from aiogram.types import InlineKeyboardMarkup,InlineKeyboardButton
from filters.admins import IsSuperAdmin
from keyboards.inline.main_menu_super_admin import main_menu_for_super_admin, back_to_main_menu, main_menu_for_admin
from aiogram.types import Message,CallbackQuery
import aiogram.utils.exceptions
from states.send_chanell import SuperAdminStateCreatePost,SuperAdminStateCreateNomzod
from aiogram.dispatcher import FSMContext



@dp.callback_query_handler(IsSuperAdmin(),text='create_new_post',state='*')
async def createpost(call: CallbackQuery,state: FSMContext):
    await call.answer(cache_time=1)
    await state.finish()
    markup = back_to_main_menu
    await call.message.edit_text(f"<b>📛Yaxshi,endi post sarlavhasini yuboring.</b>",reply_markup=markup)
    await SuperAdminStateCreatePost.SUPER_ADMIN_STATE_GET_POST_MESSAGE_ID.set()
from html import escape
from aiogram.types import ParseMode
from .ovozlar import default_channel
@dp.message_handler(IsSuperAdmin(),content_types=types.ContentTypes.TEXT,state=SuperAdminStateCreatePost.SUPER_ADMIN_STATE_GET_POST_MESSAGE_ID)
async def get_to_channel_id(message: types.Message,state:FSMContext):
    try:
        sarlavha = message.text
        if sarlavha:
            try:
                post_message_id = await bot.send_message(chat_id=default_channel,text=sarlavha)
                created_date = datetime.now()
                await db.add_post(
                    title=str(sarlavha),
                    channel=default_channel,
                    message_id=int(post_message_id.message_id),
                    created_date=created_date
                )

                await message.answer(text=f"✅Post {default_channel} kanaliga muvaffaqiyatli yuborildi.",
                                       reply_markup=main_menu_for_super_admin)
                await state.finish()
            except Exception as e:
                await message.answer(text=f"❌Post qo'shilmadi:{e}",reply_markup=main_menu_for_super_admin)
                await state.finish()
    except Exception as e:
        for admin in ADMINS:
            await bot.send_message(admin,f"Xatolik yuz berdi.{e}")
        await state.finish()



@dp.callback_query_handler(IsSuperAdmin(), text_contains='post_delete:', state="*")
async def delete_post_handler(call: CallbackQuery):
    post_id = call.data.split(":")[1]

    try:
        # Postni va unga bog'liq yozuvlarni o'chirish
        result = await db.delete_post_with_nomzodlar_and_votes(int(post_id))
        if result:
            await call.message.delete()
            await call.message.answer("✅ Post muvaffaqiyatli o'chirildi.", reply_markup=main_menu_for_super_admin)
        else:
            await call.message.answer("❌ Post o'chirilmadi", reply_markup=main_menu_for_super_admin)
    except Exception as e:
        print(e)
        await call.message.answer("❌ Post o'chirishda xatolik yuz berdi.", reply_markup=main_menu_for_super_admin)



@dp.callback_query_handler(IsSuperAdmin(),text_contains='nomzod_add:',state='*')
async def add_nomzod_to_post(call: CallbackQuery,state: FSMContext):
    await call.answer(cache_time=1)
    data = call.data.rsplit(":")
    post_id = data[1]
    await state.update_data({"post_id":post_id})
    try:
        await call.message.answer("📛Nomzod ismini yuboring.")
        await SuperAdminStateCreateNomzod.SUPER_ADMIN_STATE_GET_NOMZOD_NAME.set()
    except Exception as e:
        await call.message.answer(f"❌Xatolik yuz berdi:{e}")

@dp.message_handler(IsSuperAdmin(), state=SuperAdminStateCreateNomzod.SUPER_ADMIN_STATE_GET_NOMZOD_NAME, content_types=types.ContentTypes.TEXT)
async def add_nomzod_name(message: types.Message, state: FSMContext):
    data = await state.get_data()
    post_id = data.get('post_id')
    
    raw_text = message.text
    nomzodlar = []
    
    if raw_text:
        # Satrlarga bo'lish va bo'sh satrlarni o'tkazib yuborish
        for line in raw_text.splitlines():
            name = line.strip()
            if name:  # bo'sh bo'lmasa
                nomzodlar.append({'name': name})
        
        try:
            success = await db.add_nomzodlar_to_post(int(post_id), nomzodlar)
            if success:
                print("Nomzodlar muvaffaqiyatli qo'shildi.")
                await message.answer("✅Nomzodlar muvaffaqiyatli qo'shildi", reply_markup=main_menu_for_super_admin)
            else:
                print("Nomzodlarni qo'shishda xatolik yuz berdi.")
                await message.answer("❌Nomzodlarni qo'shishda xatolik yuz berdi.")
        except Exception as e:
            print(e)
            await message.answer("❌Nomzod qo'shilmadi. Iltimos, xabar matni to'g'ri ekanligiga ishonch hosil qiling.")
    else:
        await message.answer("❌ Iltimos, kamida bitta nomzod nomini kiriting.")
    await state.finish()

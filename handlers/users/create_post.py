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
from html import escape
from aiogram.types import ParseMode
from .ovozlar import default_channel


@dp.callback_query_handler(IsSuperAdmin(),text='create_new_post',state='*')
async def createpost(call: CallbackQuery,state: FSMContext):
    await call.answer(cache_time=1)
    await state.finish()
    markup = back_to_main_menu
    await call.message.edit_text(f"<b>📛Yaxshi,endi post sarlavhasini yuboring.</b>",reply_markup=markup)
    await SuperAdminStateCreatePost.SUPER_ADMIN_STATE_GET_POST_MESSAGE_ID.set()

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


@dp.callback_query_handler(IsSuperAdmin(), text_contains='nomzod_add:', state='*')
async def add_nomzod_to_post(call: CallbackQuery, state: FSMContext):
    try:
        await call.answer(cache_time=1)
        
        if not call.data or ':' not in call.data:
            await call.message.answer("❌ Noto'g'ri so'rov ma'lumoti. Iltimos, qayta urinib ko'ring.")
            await state.finish()
            return
            
        data = call.data.rsplit(":")
        if len(data) < 2:
            await call.message.answer("❌ Post ID topilmadi.")
            await state.finish()
            return
            
        post_id = data[1]
        
        if not post_id.isdigit():
            await call.message.answer("❌ Noto'g'ri post ID formati. Raqam bo'lishi kerak.")
            await state.finish()
            return
            
        await state.update_data({"post_id": post_id})
        
        
            
        instructions = (
            "📛 Nomzodlarning ismlarini quyidagi ko'rinishda yuboring:\n\n"
            "Ali Valiyev\n"
            "Guli Nurmatova\n"
            "Shoxruh Bekchanov\n\n"
            "* Har bir yangi qatordagi ism alohida nomzod sifatida saqlanadi\n"
            "* Maksimal 100 ta nomzod qo'shish mumkin\n"
            "* Ismlar 3-100 belgidan iborat bo'lishi kerak"
        )
        
        await call.message.answer(instructions)
        await SuperAdminStateCreateNomzod.SUPER_ADMIN_STATE_GET_NOMZOD_NAME.set()
        
    except Exception as e:
        await call.message.answer("❌ Kutilmagan xatolik yuz berdi. Iltimos, qayta urinib ko'ring.")
        print(e)
        await state.finish()

@dp.message_handler(
    IsSuperAdmin(), 
    state=SuperAdminStateCreateNomzod.SUPER_ADMIN_STATE_GET_NOMZOD_NAME,
    content_types=types.ContentTypes.TEXT
)
async def add_nomzod_name(message: types.Message, state: FSMContext):
    try:
        data = await state.get_data()
        post_id = data.get('post_id')
        
        if not post_id:
            await message.answer("❌ Post ID topilmadi. Iltimos, jarayonni qayta boshlang.")
            await state.finish()
            return
            
        # Nomzodlar ro'yxatini olish va ularning sonini hisoblash
        current_nomzodlar = await db.select_post_nomzodlar(post_id=int(post_id))
        current_count = len(current_nomzodlar)  # Ro'yxat uzunligini olish
        
        if current_count >= 100:
            await message.answer("⚠️ Nomzodlar soni chegarasiga yetildi (maksimal 100). Yangi qo'shish uchun avval ba'zilarini o'chiring.")
            await state.finish()
            return
            
        raw_text = message.text.strip()
        nomzodlar = []
        xatolar = []
        
        if not raw_text:
            await message.answer("❌ Hech qanday ism kiritilmadi. Iltimos, nomzodlarning ismlarini ko'rsatilganidek yuboring.")
            return
            
        lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
        
        qolgan_joy = 100 - current_count
        if len(lines) > qolgan_joy:
            await message.answer(
                f"⚠️ Siz {len(lines)} ta nomzod qo'shmoqchisiz, lekin faqat {qolgan_joy} ta joy qolgan.\n"
                "Iltimos, nomzodlar sonini kamaytiring yoki bir necha marta yuboring."
            )
            return
            
        for i, name in enumerate(lines, 1):
            if not (3 <= len(name) <= 100):
                xatolar.append(
                    f"{i}-qator: '{name[:20]}...' - 3-100 belgidan iborat bo'lishi kerak"
                )
            else:
                nomzodlar.append({'name': name})
                
        if xatolar:
            xabar = (
                "❌ Quyidagi ismlar talablarga javob bermadi:\n\n" +
                "\n".join(xatolar[:5]) +
                ("\n\n...va yana" if len(xatolar) > 5 else "")
            )
            await message.answer(xabar)
            return
            
        if not nomzodlar:
            await message.answer("❌ Qo'shish uchun mos ismlar topilmadi. Barcha ismlar 3-100 belgidan iborat bo'lishi kerak.")
            await state.finish()
            return
            
        try:
            success = await db.add_nomzodlar_to_post(int(post_id), nomzodlar)
            
            if success:
                qoshilgan = len(nomzodlar)
                jami = current_count + qoshilgan
                
                javob = (
                    f"✅ Muvaffaqiyatli qo'shildi: {qoshilgan} ta nomzod.\n"
                    f"📊 Jami nomzodlar: {jami}/100\n\n"
                    f"Yana {100 - jami} ta nomzod qo'shish mumkin."
                )
                
                if jami >= 90:
                    javob += "\n\n⚠️ Diqqat! Nomzodlar soni chegarasiga yaqinlashmoqdasiz!"
                    
                await message.answer(javob, reply_markup=main_menu_for_super_admin)
            else:
                await message.answer("❌ Nomzodlarni saqlashda xatolik yuz berdi. Iltimos, qayta urinib ko'ring.")
                
        except Exception as db_error:
            await message.answer("❌ Nomzodlarni saqlashda xatolik yuz berdi. Iltimos, kamroq sonli nomzodlar bilan qayta urinib ko'ring.")
            print(f"Database error: {db_error}")
            
    except Exception as e:
        await message.answer("❌ Kutilmagan xatolik yuz berdi. Iltimos, qayta urinib ko'ring yoki texnik yordamga murojaat qiling.")
        print(f"Unexpected error: {e}")
        
    finally:
        await state.finish()
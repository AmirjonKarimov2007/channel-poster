import time
from datetime import datetime
from aiogram.utils.exceptions import BadRequest
import aiogram.utils.exceptions
from aiogram import types
from aiogram.types import Message,CallbackQuery
from data.config import ADMINS
from loader import dp, db,bot
from aiogram.types import InlineKeyboardButton,InlineKeyboardMarkup
from filters.admins import IsSuperAdmin
from keyboards.inline.nomzodlar_btn import nomzotlar_keyboard,posts_keyboard,post_keyboard
from keyboards.inline.main_menu_super_admin import main_menu_for_super_admin
from keyboards.inline.nomzodlar_btn import channel_send_keybaord

default_channel = '@Yangipostlaruzb'

@dp.callback_query_handler(IsSuperAdmin(),text='posts',state='*')
async def all_posts_handler(call: types.CallbackQuery):
    markup = await posts_keyboard()
    if call.message.caption:
        await call.message.delete()
        await call.message.answer(text="<b>Bu yerda siz qo'shgan jami postlar ro'yxati ko'rinadi.</b>",
                                     reply_markup=markup)
    else:
        await call.message.edit_text("<b>Bu yerda siz qo'shgan jami postlar ro'yxati ko'rinadi.</b>",reply_markup=markup)

@dp.callback_query_handler(text_contains='post:', state="*")
async def one_post_handler(call: types.CallbackQuery):
    await call.answer(cache_time=1)
    data = call.data.rsplit(":")
    post_id = data[1]
    post_data = await db.select_post_nomzodlar(int(post_id))
    markup = await post_keyboard(post_data,user_id=call.from_user.id)
    post = post_data[0]
    if post['message_id'] and post['channel']:
        try:
            await call.message.delete()
            await bot.copy_message(chat_id=call.from_user.id,from_chat_id=f"{post['channel']}",message_id=post['message_id'],reply_markup=markup)
        except BadRequest as e:
            if "Message to copy not found" in str(e):
                await db.delete_post_with_nomzodlar_and_votes(int(post['id']))
                await call.message.answer(text=f"<b>❌{default_channel} kanalidan Kanalidan topilmadi va postlar ro'yxatida butunlay o'chirib tashlandi.</b>",reply_markup=main_menu_for_super_admin)
    else:
        await call.message.edit_text(f"<b>{post['title']}</b>", reply_markup=markup)

import pytz

async def check_date(post_id, state="*"):
    current_date = datetime.now()
    post = await db.select_post(id=int(post_id))  # Ma'lumotni olish
    end_date = post[0]['end_date']

    if end_date:
        tashkent = pytz.timezone('Asia/Tashkent')
        current_date_time = current_date.astimezone(tashkent)
        current_date = current_date_time.strftime('%Y-%m-%d %H:%M:%S')
        end_date_time_tashkent = end_date.astimezone(tashkent)
        end_date = end_date_time_tashkent.strftime('%Y-%m-%d %H:%M:%S')
        if current_date > end_date:
            return False
        else:
            return True
    else:
        return True
@dp.callback_query_handler(text_contains='ovoz_add:', state="*")
async def add_to_nomzot_vote_channel(call: types.CallbackQuery):


    chat_id = call.message.chat.id
    message_id = call.message.message_id
    first_char = str(chat_id)[0]
    data = call.data.rsplit(":")
    nomzot_id = data[1]
    nomzot_list = await db.select_nomzot(id=int(nomzot_id))
    check_time = await check_date(int(nomzot_list[0]['posts_id']))
    telegram_id = call.from_user.id
    if check_time==True:
        if nomzot_list:
            nomzot = nomzot_list[0]
            jami_ovozlar = await db.select_all_votes(post_id=int(nomzot['posts_id']))
            user_voted = any(user['telegram_id'] == telegram_id for user in jami_ovozlar)

            if first_char == '-':
                chat_member = await bot.get_chat_member(f"@{call.message.chat.username}", call.from_user.id)
                if chat_member.status in ['member', 'administrator', 'creator']:
                    if user_voted:
                        await bot.answer_callback_query(call.id, text="Siz allaqachon ovoz berdingiz!",show_alert=True)
                    else:
                        try:
                            try:
                                    await db.add_vote(int(telegram_id), int(nomzot_id), int(nomzot['posts_id']))
                                    new_vote_count = nomzot['ovozlar'] + 1
                                    await db.update_nomzot_vote(int(new_vote_count), int(nomzot_id))
                                    post_data = await db.select_post_nomzodlar(int(nomzot['posts_id']))
                                    markup = await channel_send_keybaord(post_data)
                                    await bot.answer_callback_query(call.id, text="Ovozingiz qabul qilindi!", show_alert=True)
                                    await bot.edit_message_reply_markup(chat_id=call.message.chat.id,
                                            message_id=call.message.message_id,
                                            reply_markup=markup)

                            except:
                                await bot.send_message(chat_id=5955950834,text='botda xatolik yuz berdi.')
                        except:
                            print('ovozlar.pyning add_to_nomzot_vote funksiyasida xatolik yuz berdi. ')
                else:
                    await bot.answer_callback_query(call.id, text="❌Ovoz berish uchun kanalga obuna bo'ling.", show_alert=True)
            # admin  uchun
            else:
                if user_voted:
                    await bot.answer_callback_query(call.id, text="Siz allaqachon ovoz berdingiz!", show_alert=True)
                else:
                    try:
                        try:

                            await db.add_vote(int(telegram_id), int(nomzot_id), int(nomzot['posts_id']))
                            new_vote_count = nomzot['ovozlar'] + 1
                            await db.update_nomzot_vote(int(new_vote_count), int(nomzot_id))
                            post_data = await db.select_post_nomzodlar(int(nomzot['posts_id']))
                            markup = await post_keyboard(post_data,user_id=call.from_user.id)
                            await bot.answer_callback_query(call.id, text="Ovozingiz qabul qilindi!", show_alert=True)
                            await bot.edit_message_reply_markup(chat_id=call.message.chat.id,
                                                                message_id=call.message.message_id,
                                                                reply_markup=markup)

                        except:
                            await bot.send_message(chat_id=5955950834, text='botda xatolik yuz berdi.')
                    except:
                        print('ovozlar.pyning add_to_nomzot_vote funksiyasida xatolik yuz berdi. ')
        else:
            await call.message.answer("Nomzot topilmadi.", reply_markup=main_menu_for_super_admin)
    elif check_time==False:
        await bot.answer_callback_query(call.id, text="Ovoz berish vaqti tugagan!", show_alert=True)

@dp.callback_query_handler(IsSuperAdmin(), text_contains='select_type:', state="*")
async def select_advertisiment_type(call: CallbackQuery):
    data = call.data.rsplit(":")
    post_id = data[1]
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(InlineKeyboardButton(text='🔰Kanallarga',callback_data=f'send_channel:{data[1]}'))
    markup.insert(InlineKeyboardButton(text="👥  Foydalanuvchilarga", callback_data=f"post_send_users:{post_id}"))
    markup.add(InlineKeyboardButton(text="⬅️ Orqaga", callback_data=f"post:{post_id}"))
    if call.message.caption:
        await call.message.edit_caption("<b>Postni qayerga yubormoqchisiz?</b>",reply_markup=markup)
    else:
        await call.message.edit_text("<b>Postni qayerga yubormoqchisiz?</b>",reply_markup=markup)
@dp.callback_query_handler(IsSuperAdmin(),text_contains='send_channel:')
async def send_channels(call: types.CallbackQuery):
    data = call.data.rsplit(":")
    post_id = data[1]
    royxat = await db.select_channels()
    text = "<b>🔰 Yubormoqchi bo'lgan kanalni tanlang:</b>\n\n"
    son = 0
    for o in royxat:
        son += 1
        text += f"<b>{son}. {o[1]}\n💠 Username: {o[1]}</b>\n\n"
    channels = await db.select_all_channels()
    buttons = InlineKeyboardMarkup(row_width=2)
    for channel in channels:
        buttons.add(InlineKeyboardButton(text=f"{channel[1]}", callback_data=f"send_to_one_channel:{channel[1]}:{post_id}"))

    buttons.add(InlineKeyboardButton(text="♻️ Hamma Kanallarga", callback_data=f"send_all_channel:{post_id}"))
    buttons.add(InlineKeyboardButton(text="⬅️ Orqaga", callback_data=f"select_type:{post_id}"))

    if call.message.caption:
        await call.message.edit_caption(caption=text, reply_markup=buttons)
    else:
        await call.message.edit_text(text=text, reply_markup=buttons)



@dp.callback_query_handler(IsSuperAdmin(),text_contains = "send_to_one_channel:",state='*')
async def send_one_channel(call:CallbackQuery):
    await call.answer(cache_time=1)
    data = call.data.rsplit(":")
    channel_username= data[1]
    post_id = data[2]
    post_data = await db.select_post_nomzodlar(int(post_id))
    markup = await channel_send_keybaord(post_data)
    try:
        post = post_data[0]
        try:
            await bot.copy_message(chat_id=channel_username,from_chat_id=default_channel,message_id=int(post['message_id']),reply_markup=markup)
            await call.message.edit_text(f"<b>✅Post {channel_username} kanaliga muvaffaqiyatli yuborildi.</b>",reply_markup=main_menu_for_super_admin)
        except BadRequest as e:
            if "Message to copy not found" in str(e):
                # Handle the specific "Message to copy not found" error
                await call.message.answer(text="❌ Xabar kanaldan o'chirib tashlagan iltimos yangi post qo'shib qaytadan urining.")
    except aiogram.utils.exceptions.BadRequest as e:
       await call.message.answer("<b>Yubormoqchi bo'lgan postingiz botdan o'chirib tashlangan.Iltimos Amallarni boshidan bajaring va postni o'chirib yubormang.</b>")
    except Exception as e:
        for admin in ADMINS:
            await bot.send_message(admin, "Xatolk yuz berdi.")
        await call.message.answer(f"❌Post yuborishda hatolik yuz berdi:{e}")

@dp.callback_query_handler(IsSuperAdmin(),text_contains='send_all_channel:')
async def send_all_channel_post(call: CallbackQuery):
    await call.answer(cache_time=1)
    channels = await db.select_channels()
    data = call.data.rsplit(":")
    post_id = data[1]
    post_data = await db.select_post_nomzodlar(int(post_id))
    markup = await channel_send_keybaord(post_data)
    try:
        for channel in channels:
            try:
                await bot.copy_message(chat_id=channel['channel'], from_chat_id=default_channel,message_id=int(post_data[0]['message_id']), reply_markup=markup)
                time.sleep(0.5)
            except BadRequest as e:
                if "Message to copy not found" in str(e):
                    await call.message.answer( text="❌ Xabar kanaldan o'chirib tashlagan iltimos yangi post qo'shib qaytadan urining.")
        if call.message.caption:
            await call.message.delete()
            await call.message.answer(f"<b>✅Post Hamma kanallarga muvaffaqiyatli yuborildi.</b>",
                                         reply_markup=main_menu_for_super_admin)
        else:
            await call.message.edit_text(f"<b>✅Post Hamma kanallarga muvaffaqiyatli yuborildi.</b>",
                                         reply_markup=main_menu_for_super_admin)
    except Exception as e:
        for admin in ADMINS:
            await bot.send_message(admin, f"Xatolk yuz berdi:{e}")

@dp.callback_query_handler(IsSuperAdmin(),text_contains="post_send_users:")
async def send_all_of_the_users(call: CallbackQuery):
    await call.answer(cache_time=1)
    users = await db.stat()
    users = str(users)
    black_list = 0
    white_list = 0
    datas = datetime.now()
    data = call.data.rsplit(":")
    post_id = data[1]
    post_data = await db.select_post_nomzodlar(int(post_id))
    markup = await channel_send_keybaord(post_data)

    boshlanish_vaqti = f"{datas.hour}:{datas.minute}:{datas.second}"
    start_msg = await call.message.answer(f"📢 Post jo'natish boshlandi...\n"
                                     f"📊 Foydalanuvchilar soni: {users} ta\n"
                                     f"🕒 Kuting...\n")
    user = await db.select_all_users()

    for i in user:
        user_id = i['user_id']
        try:
            msg = await bot.copy_message(chat_id=user_id, from_chat_id=str(post_data[0]['channel']),
                                         message_id=int(post_data[0]['message_id']), reply_markup=markup)
            white_list += 1
            time.sleep(0.5)
        except Exception as e:
            print(e)
            black_list += 1
    data = datetime.now()
    tugash_vaqti = f"{data.hour}:{data.minute}:{data.second}"
    text = f'<b>✅ Post muvaffaqiyatli yuborildi!</b>\n\n'
    text += f'<b>⏰Post yuborishning boshlangan vaqt: {boshlanish_vaqti}</b>\n'
    text += f"<b>👥 Post yuborilgan foydalanuchilar soni:{white_list}</b>\n"
    text += f"<b>🚫Post yuborilmagan foydalanuvchilar soni:{black_list}</b>\n"
    text += f'<b>🏁Post yuborishning tugash vaqt: {tugash_vaqti}</b>\n'
    await bot.delete_message(chat_id=start_msg.chat.id, message_id=start_msg.message_id)
    await call.message.answer(text, reply_markup=main_menu_for_super_admin)

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from data.config import ADMINS
from loader import db

ADMINS = [int(i) for i in ADMINS]
async def nomzotlar_keyboard(nomzotlar_royxati):
    nomzotlar = InlineKeyboardMarkup(row_width=1)
    for nomzot in nomzotlar_royxati:
        nomzotlar.insert(InlineKeyboardButton(text=f"{nomzot.fullname}||{nomzot.ovozlar}",callback_data=f"nomzot_add:{nomzot.id}"))
    return nomzotlar
async def posts_keyboard():
    posts_list = await db.select_all_posts()
    posts = InlineKeyboardMarkup(row_width=1)
    for post in posts_list:
        posts.insert(InlineKeyboardButton(text=f"{post['title'].title()}",callback_data=f"post:{post['id']}"))
    posts.add(InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_to_main_menu"))

    return posts

async def pin_posts_keyboard():
    posts_list = await db.select_all_posts()

    posts = InlineKeyboardMarkup(row_width=1)
    for post in posts_list:
        check = post['pin']
        if check:
            posts.insert(
                InlineKeyboardButton(text=f"📌 {post['title'].title()}", callback_data=f"post_pin:{post['id']}"))
        else:
            posts.insert(InlineKeyboardButton(text=f"{post['title'].title()}", callback_data=f"post_pin:{post['id']}"))

    posts.add(InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_to_main_menu"))
    return posts


from aiogram import types
from datetime import datetime


async def post_keyboard(post_info, user_id):
    post = InlineKeyboardMarkup(row_width=2)

    if post_info and post_info[0].get('nomzod_id'):
        sorted_post_info = sorted(post_info, key=lambda x: x['ovozlar'], reverse=True)
        for idx, nomzod in enumerate(sorted_post_info):
            if idx == 0:
                medal = "🥇"
            elif idx == 1:
                medal = "🥈"
            elif idx == 2:
                medal = "🥉"
            else:
                medal = ""
            post.add(InlineKeyboardButton(text=f"{medal} {nomzod['fullname'].title()} || {nomzod['ovozlar']}",
                                          callback_data=f"ovoz_add:{nomzod['nomzod_id']}"))

        if user_id in ADMINS:
            post.add(InlineKeyboardButton(text="✅ Yuborish", callback_data=f"select_type:{post_info[0]['id']}"))
            post.insert(InlineKeyboardButton(text="📝 Tahrirlalsh", web_app=types.WebAppInfo(url=f"https://sorovnoma.alwaysdata.net/admin/users/post/{post_info[0]['id']}/change/")))
            post.add(InlineKeyboardButton(text="🗑 O'chirish", callback_data=f"post_delete:{post_info[0]['id']}"))
            # post.insert(InlineKeyboardButton(text="➕ Nomzod Qo'shish", callback_data=f"nomzod_add:{post_info[0]['id']}"))
            post.add(InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_to_post_menu"))
            return post
        else:
            return post

    else:
        if user_id in ADMINS:
            post.add(InlineKeyboardButton(text="✅ Yuborish", callback_data=f"select_type:{post_info[0]['id']}"))
            post.insert(InlineKeyboardButton(text="📝 Tahrirlalsh", web_app=types.WebAppInfo(url=f"https://sorovnoma.alwaysdata.net/admin/users/post/{post_info[0]['id']}/change/")))
            post.add(InlineKeyboardButton(text="🗑 O'chirish", callback_data=f"post_delete:{post_info[0]['id']}"))
            # post.insert(InlineKeyboardButton(text="➕ Nomzod Qo'shish", callback_data=f"nomzod_add:{post_info[0]['id']}"))
            post.add(InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_to_post_menu"))
            return post
        else:
            return post


async def channel_send_keybaord(post_info):
    post = InlineKeyboardMarkup(row_width=2)
    if post_info and post_info[0].get('nomzod_id'):
        sorted_post_info = sorted(post_info, key=lambda x: x['ovozlar'], reverse=True)
        for idx, nomzod in enumerate(sorted_post_info):
            if idx == 0:
                medal = "🥇"
            elif idx == 1:
                medal = "🥈"
            elif idx == 2:
                medal = "🥉"
            else:
                medal = ""
            post.add(InlineKeyboardButton(text=f"{medal} {nomzod['fullname'].title()} || {nomzod['ovozlar']}",
                                          callback_data=f"ovoz_add:{nomzod['nomzod_id']}"))
        return post
    else:
        pass


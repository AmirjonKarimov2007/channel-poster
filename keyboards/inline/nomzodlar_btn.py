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
    
    if not post_info:
        return post
        
    post_id = post_info[0]['id']
    nomzodlar_ovozlar = await db.get_votes_by_post(post_id=post_id)
    
    # Nomzodlar mavjud bo'lsa
    if post_info[0].get('nomzod_id'):
        # Ovozlar soni bo'yicha saralash (kamayish tartibida)
        sorted_post_info = sorted(
            post_info, 
            key=lambda x: len([r for r in nomzodlar_ovozlar if r['nomzod_id'] == x['nomzod_id']]), 
            reverse=True
        )
        
        for idx, nomzod in enumerate(sorted_post_info):
            nomzod_id = nomzod['nomzod_id']
            ovozlar_soni = len([r for r in nomzodlar_ovozlar if r['nomzod_id'] == nomzod_id])
            
            # Medalni aniqlash
            if idx == 0:
                medal = "🥇"
            elif idx == 1:
                medal = "🥈"
            elif idx == 2:
                medal = "🥉"
            else:
                medal = ""
                
            post.add(InlineKeyboardButton(
                text=f"{medal} {nomzod['fullname'].title()} || {ovozlar_soni}",
                callback_data=f"ovoz_add:{nomzod['nomzod_id']}"
            ))
    
    # Admin uchun tugmalar
    if user_id in ADMINS:
        post.row(
            InlineKeyboardButton(text="✅ Yuborish", callback_data=f"select_type:{post_id}"),
            InlineKeyboardButton(text="➕ Nomzod Qo'shish", callback_data=f"nomzod_add:{post_id}")
        )
        post.row(
            InlineKeyboardButton(text="🗑 O'chirish", callback_data=f"post_delete:{post_id}"),
            InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_to_post_menu")
        )
    
    return post

async def channel_send_keybaord(post_info):
    post = InlineKeyboardMarkup(row_width=2)
    
    if not post_info or not post_info[0].get('nomzod_id'):
        return post
        
    post_id = post_info[0]['id']
    nomzodlar_ovozlar = await db.get_votes_by_post(post_id=post_id)
    
    # Ovozlar soni bo'yicha saralash (kamayish tartibida)
    sorted_post_info = sorted(
        post_info, 
        key=lambda x: len([r for r in nomzodlar_ovozlar if r['nomzod_id'] == x['nomzod_id']]), 
        reverse=True
    )
    
    for idx, nomzod in enumerate(sorted_post_info):
        nomzod_id = nomzod['nomzod_id']
        ovozlar_soni = len([r for r in nomzodlar_ovozlar if r['nomzod_id'] == nomzod_id])
        
        # Medalni aniqlash
        if idx == 0:
            medal = "🥇"
        elif idx == 1:
            medal = "🥈"
        elif idx == 2:
            medal = "🥉"
        else:
            medal = ""
            
        post.add(InlineKeyboardButton(
            text=f"{medal} {nomzod['fullname'].title()} || {ovozlar_soni}",
            callback_data=f"ovoz_add:{nomzod['nomzod_id']}"
        ))
    
    return post
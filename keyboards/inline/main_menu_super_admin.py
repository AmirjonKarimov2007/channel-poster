from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

main_menu_for_super_admin = InlineKeyboardMarkup(row_width=2)

main_menu_for_super_admin.add(InlineKeyboardButton(text="➕ Kanal qo'shish", callback_data="add_channel"),
                              InlineKeyboardButton(text="➖ Kanal o'chirish", callback_data="del_channel"),
                              InlineKeyboardButton(text="➕ Admin qo'shish", callback_data="add_admin"),
                              InlineKeyboardButton(text="➖ Admin o'chirish", callback_data="del_admin"),
                              InlineKeyboardButton(text="🚩 Post tayyorlash", callback_data="create_new_post"),
                              InlineKeyboardButton(text="🔰 Postlar", callback_data="posts"),
                              InlineKeyboardButton(text="📌️ Pin Post", callback_data="post_edit"),
                              InlineKeyboardButton(text="👤 Adminlar", callback_data="admins"),
                              InlineKeyboardButton(text="📝 Adminlarga Xabar yuborish",callback_data="send_message_to_admins"),
                              InlineKeyboardButton(text="📝 Reklama Jo'natish", callback_data="send_advertisement"),
                              InlineKeyboardButton(text="📊 Statistika", callback_data="statistics"),
                              )

main_menu_for_admin = InlineKeyboardMarkup(row_width=2)

main_menu_for_admin.add(InlineKeyboardButton(text="📊 Statistika", callback_data="stat"),
                              )

back_to_main_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_to_main_menu")
        ]
    ]
)

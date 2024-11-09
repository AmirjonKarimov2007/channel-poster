import os
import django

# Django loyihasining `settings.py` fayliga yo'l ko'rsating
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_admin.telegram_bot.settings")
django.setup()

# `users` app'idan modellaringizni import qiling
from bot.django_admin.users import SendPost  # Agar `users` `django_admin` ichida joylashgan bo'lsa

# Modellarga kirish
users = SendPost.objects.all()
print(users)

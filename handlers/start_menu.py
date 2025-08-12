"""
ماژول هندلر منوی اصلی و دستور /start

این فایل مسئولیت مدیریت دستور اولیه `/start` را بر عهده دارد.
وقتی کاربر برای اولین بار ربات را استارت می‌زند یا دستور `/start` را ارسال می‌کند،
این هندلر فعال می‌شود.

تابع `start`:
- به کاربر خوشامد می‌گوید.
- بررسی می‌کند آیا کاربر ثبت‌نام کرده است یا خیر (با استفاده از gsheets.py).
- اگر ثبت‌نام نکرده باشد، او را به سمت ثبت‌نام هدایت می‌کند.
- اگر ثبت‌نام کرده باشد، منوی اصلی ربات را با دکمه‌های شیشه‌ای نمایش می‌دهد.
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils.i18n import get_text
from utils.common import build_menu
# from utils.gsheets import get_db # در پیاده‌سازی کامل استفاده خواهد شد

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """هنگام ارسال دستور /start توسط کاربر، این تابع فراخوانی می‌شود."""
    user = update.effective_user
    # زبان کاربر را از داده‌های ذخیره شده یا پیش‌فرض می‌خوانیم
    lang = context.user_data.get("lang", "fa")

    # TODO: در پیاده‌سازی کامل، وضعیت ثبت‌نام کاربر از دیتابیس (Google Sheets) چک می‌شود.
    # db = get_db()
    # is_registered = db.get_user(user.id) is not None
    is_registered = True # برای این مرحله، فرض می‌کنیم کاربر ثبت‌نام کرده است

    if not is_registered:
        await update.message.reply_text(get_text("not_registered", lang))
        # در اینجا می‌توان کاربر را به سمت دستور /register هدایت کرد.
        return

    # --- ساخت منوی اصلی ---
    welcome_message = get_text("welcome", lang)
    menu_header = get_text("main_menu_header", lang)

    buttons = [
        [
            InlineKeyboardButton(get_text("btn_resources_hub", lang), callback_data="hub_main"),
            InlineKeyboardButton(get_text("btn_scholarships", lang), callback_data="scholarships_main"),
        ],
        [
            InlineKeyboardButton(get_text("btn_isee", lang), callback_data="isee_start"),
            InlineKeyboardButton(get_text("btn_weather", lang), callback_data="weather_start"),
        ],
        [
            InlineKeyboardButton(get_text("btn_news", lang), callback_data="news_main"),
            InlineKeyboardButton(get_text("btn_profile", lang), callback_data="profile_view"),
        ],
        [
            InlineKeyboardButton(get_text("btn_roommate_finder", lang), callback_data="roommate_main"),
            InlineKeyboardButton(get_text("btn_live_chat", lang), callback_data="live_chat_start"),
        ]
    ]

    reply_markup = InlineKeyboardMarkup(buttons)

    await update.message.reply_text(
        f"{welcome_message}\n\n{menu_header}",
        reply_markup=reply_markup
    )

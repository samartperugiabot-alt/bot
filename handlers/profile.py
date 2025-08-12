"""
ماژول هندلر پروفایل کاربر (/profile) - نسخه کامل

این فایل به کاربران اجازه می‌دهد پروفایل خود را مشاهده، ویرایش و یا حذف کنند.
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils.gsheets import get_db
from utils.i18n import get_text
from utils.logger import log

# --- Handler Functions ---

async def view_profile(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """اطلاعات پروفایل کاربر را نمایش می‌دهد."""
    user_id = update.effective_user.id
    lang = context.user_data.get("lang", "fa")
    db = get_db()

    if not db:
        await update.message.reply_text(get_text("error_generic", lang))
        return

    user_data = db.get_user(user_id)
    if not user_data:
        await update.message.reply_text(get_text("not_registered", lang))
        return

    # TODO: این پیام‌ها را به i18n منتقل کن
    profile_text = (
        f"👤 *پروفایل شما*\n\n"
        f"*نام:* {user_data.get('name', 'N/A')}\n"
        f"*سن:* {user_data.get('age', 'N/A')}\n"
        f"*کشور:* {user_data.get('country', 'N/A')}\n"
        f"*رشته:* {user_data.get('field', 'N/A')}\n"
        f"*ایمیل:* {user_data.get('email', 'N/A')}"
    )

    buttons = [
        # [InlineKeyboardButton("✏️ ویرایش پروفایل", callback_data="profile_edit_start")],
        [InlineKeyboardButton("🗑️ حذف تمام اطلاعات من", callback_data="profile_delete_confirm")]
    ]
    reply_markup = InlineKeyboardMarkup(buttons)

    await update.message.reply_text(profile_text, reply_markup=reply_markup, parse_mode="Markdown")

async def confirm_delete_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """از کاربر برای حذف پروفایل تأییدیه می‌گیرد."""
    query = update.callback_query
    await query.answer()

    # TODO: این پیام‌ها را به i18n منتقل کن
    warning_text = (
        "⚠️ *اخطار جدی*\n\n"
        "آیا مطمئن هستید که می‌خواهید تمام اطلاعات خود را برای همیشه حذف کنید؟\n"
        "این عمل غیرقابل بازگشت است."
    )
    buttons = [
        [
            InlineKeyboardButton("✅ بله، حذف کن", callback_data="profile_delete_execute"),
            InlineKeyboardButton("❌ خیر، لغو", callback_data="profile_delete_cancel")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(buttons)
    await query.edit_message_text(text=warning_text, reply_markup=reply_markup, parse_mode="Markdown")

async def execute_delete_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """اطلاعات کاربر را حذف می‌کند."""
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    db = get_db()

    if db and db.delete_user(user_id):
        log.info(f"کاربر {user_id} اطلاعات خود را حذف کرد.")
        # TODO: این پیام را به i18n منتقل کن
        await query.edit_message_text("تمام اطلاعات شما با موفقیت از سیستم ما حذف شد.")
    else:
        log.error(f"خطا در حذف اطلاعات کاربر {user_id}.")
        # TODO: این پیام را به i18n منتقل کن
        await query.edit_message_text("خطایی در حذف اطلاعات شما رخ داد. لطفاً با ادمین تماس بگیرید.")

async def cancel_delete_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عملیات حذف را لغو کرده و به نمایش پروفایل بازمی‌گردد."""
    query = update.callback_query
    await query.answer()

    # برای نمایش مجدد پروفایل، باید دوباره آن را از دیتابیس بخوانیم
    user_id = update.effective_user.id
    db = get_db()
    user_data = db.get_user(user_id) if db else None

    if user_data:
        profile_text = (
            f"👤 *پروفایل شما*\n\n"
            f"*نام:* {user_data.get('name', 'N/A')}\n"
            f"*سن:* {user_data.get('age', 'N/A')}\n"
            f"*کشور:* {user_data.get('country', 'N/A')}\n"
            f"*رشته:* {user_data.get('field', 'N/A')}\n"
            f"*ایمیل:* {user_data.get('email', 'N/A')}"
        )
        buttons = [[InlineKeyboardButton("🗑️ حذف تمام اطلاعات من", callback_data="profile_delete_confirm")]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.edit_message_text(profile_text, reply_markup=reply_markup, parse_mode="Markdown")
    else:
        await query.edit_message_text("عملیات لغو شد.")

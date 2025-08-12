"""
ماژول گیت‌ها و دکوراتورهای دسترسی (Gates & Access Decorators) - نسخه کامل

این فایل شامل دکوراتورهایی است که برای کنترل دسترسی به دستورات استفاده می‌شوند.
"""
from functools import wraps
from telegram import Update
from telegram.ext import ContextTypes
from utils.gsheets import get_db
from utils.i18n import get_text
from utils.logger import log

def require_registration(func):
    """
    دکوراتوری که چک می‌کند کاربر ثبت‌نام کرده باشد.
    """
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user_id = update.effective_user.id
        db = get_db()

        # اگر دیتابیس در دسترس نباشد، برای امنیت دسترسی را محدود می‌کنیم
        if not db:
            log.error("GSheets DB در دسترس نیست. دسترسی به تابع require_registration رد شد.")
            await update.message.reply_text(get_text("error_generic", "fa"))
            return

        if not db.get_user(user_id):
            lang = context.user_data.get("lang", "fa")
            await update.message.reply_text(get_text("not_registered", lang))
            return

        return await func(update, context, *args, **kwargs)
    return wrapper

def require_admin(func):
    """
    دکوراتوری که چک می‌کند کاربر اجراکننده دستور، یک ادمین باشد.
    برای RBAC دقیق‌تر، می‌توان یک پارامتر `role` نیز به آن اضافه کرد.
    """
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user_id = update.effective_user.id
        db = get_db()

        if not db:
            log.error("GSheets DB در دسترس نیست. دسترسی به تابع require_admin رد شد.")
            await update.message.reply_text(get_text("error_generic", "fa"))
            return

        admin_ids = db.get_admins()
        if user_id not in admin_ids:
            log.warning(f"دسترسی غیرمجاز به دستور ادمین توسط کاربر {user_id}")
            # TODO: این پیام را به i18n منتقل کن
            await update.message.reply_text("شما دسترسی لازم برای اجرای این دستور را ندارید.")
            return

        log.info(f"ادمین {user_id} به دستور محافظت‌شده دسترسی پیدا کرد.")
        return await func(update, context, *args, **kwargs)
    return wrapper

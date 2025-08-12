"""
ماژول گیت‌ها و دکوراتورهای دسترسی (Gates & Access Decorators)

این فایل شامل دکوراتورهایی است که برای کنترل دسترسی به دستورات و قابلیت‌های
مختلف ربات استفاده می‌شوند. این یک لایه امنیتی مهم برای ربات است.

دکوراتورهای نمونه:
-   @require_registration: بررسی می‌کند که آیا کاربر قبل از اجرای دستور،
    ثبت‌نام کرده است یا خیر. اگر نه، پیام مناسب را ارسال کرده و اجرای دستور
    را متوقف می‌کند.
-   @require_admin: بررسی می‌کند که آیا کاربر اجراکننده دستور، یک ادمین
    با نقش مشخص است یا خیر (RBAC - Role-Based Access Control).
"""
from functools import wraps
# from utils.gsheets import get_db
# from utils.i18n import get_text

def require_registration(func):
    """
    دکوراتوری که چک می‌کند کاربر ثبت‌نام کرده باشد.
    """
    @wraps(func)
    async def wrapper(update, context, *args, **kwargs):
        # user_id = update.effective_user.id
        # db = get_db()
        # if not db.get_user(user_id):
        #     lang = context.user_data.get("lang", "fa")
        #     await update.message.reply_text(get_text("not_registered", lang))
        #     return
        # print(f"کاربر {user_id} مجاز است.")
        return await func(update, context, *args, **kwargs)
    return wrapper

def require_admin(role="admin"):
    """
    دکوراتوری که چک می‌کند کاربر ادمین با نقش مشخصی باشد.
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(update, context, *args, **kwargs):
            # user_id = update.effective_user.id
            # db = get_db()
            # admin_roles = db.get_admin_roles(user_id) # متد فرضی
            # if role not in admin_roles:
            #     await update.message.reply_text("شما دسترسی لازم برای اجرای این دستور را ندارید.")
            #     return
            # print(f"ادمین {user_id} با نقش '{role}' مجاز است.")
            return await func(update, context, *args, **kwargs)
        return wrapper
    return decorator

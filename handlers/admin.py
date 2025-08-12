"""
ماژول هندلرهای پنل ادمین

این فایل شامل دستورات و قابلیت‌هایی است که فقط برای ادمین‌های ربات قابل دسترس است.
-   مدیریت کاربران (بن/آنبن کردن)
-   ارسال پیام همگانی (Broadcast)
-   مشاهده لاگ‌ها و بازخوردها
-   مدیریت نقش‌ها (Role-Based Access Control - RBAC)

دسترسی به این دستورات باید توسط دکوراتورهای موجود در `utils/gates.py` محافظت شود.
"""

# مثال از یک دستور ادمین:
# from utils.gates import require_admin
#
# @require_admin
# async def broadcast_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     # منطق ارسال پیام همگانی
#     pass

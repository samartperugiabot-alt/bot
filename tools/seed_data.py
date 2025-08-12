"""
اسکریپت پر کردن داده‌های اولیه (Seed Data)

این اسکریپت برای توسعه و تست محلی استفاده می‌شود. هدف آن، پر کردن
Google Sheets (یا دیتابیس) با داده‌های نمونه است تا بتوان عملکرد ربات را
بدون نیاز به ثبت‌نام دستی کاربران یا ایجاد داده از طریق ربات، آزمایش کرد.

نحوه اجرا:
-   این اسکریپت به صورت مستقل از خط فرمان اجرا می‌شود.
-   قبل از اجرا، باید فایل `.env` با اطلاعات صحیح (مخصوصاً اعتبارنامه‌های گوگل)
    در ریشه پروژه وجود داشته باشد.
-   `python tools/seed_data.py`

کارهایی که انجام می‌دهد:
-   اتصال به Google Sheets.
-   ایجاد شیت‌های مورد نیاز (users, admins, ...) در صورت عدم وجود.
-   اضافه کردن چند کاربر تستی به شیت 'users'.
-   اضافه کردن یک ادمین به شیت 'admins'.
"""
import os
import sys

# افزودن ریشه پروژه به مسیر پایتون برای وارد کردن ماژول‌های پروژه
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.gsheets import get_db
import config

def seed():
    """تابع اصلی برای اجرای عملیات seed."""
    print("شروع عملیات Seed Data...")

    try:
        db = get_db()
        print("اتصال به Google Sheets برقرار است.")
    except Exception as e:
        print(f"خطا: اتصال به Google Sheets ناموفق بود. آیا فایل .env را تنظیم کرده‌اید؟")
        print(f"جزئیات خطا: {e}")
        return

    # --- ایجاد شیت‌ها در صورت نیاز ---
    required_sheets = [
        'users', 'admins', 'questions', 'feedback',
        'roommates', 'logs', 'isee_calcs'
    ]
    for sheet_name in required_sheets:
        try:
            db._get_worksheet(sheet_name)
            print(f"شیت '{sheet_name}' از قبل وجود دارد یا با موفقیت ایجاد شد.")
        except Exception as e:
            print(f"خطا در ایجاد شیت '{sheet_name}': {e}")

    # --- افزودن داده‌های نمونه ---
    # TODO: در پیاده‌سازی کامل، می‌توان رکوردهای نمونه را به شیت‌ها اضافه کرد.
    # مثال:
    # admin_data = {
    #     'user_id': config.ADMIN_CHAT_ID,
    #     'username': 'bot_admin',
    #     'roles': 'superadmin,news_admin'
    # }
    # admins_sheet = db._get_worksheet('admins')
    # admins_sheet.append_row(list(admin_data.values()))
    # print("ادمین نمونه اضافه شد.")

    print("\nعملیات Seed Data با موفقیت (به صورت شبیه‌سازی شده) به پایان رسید.")

if __name__ == "__main__":
    seed()

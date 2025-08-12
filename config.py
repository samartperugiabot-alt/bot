"""
ماژول تنظیمات (Configuration Module)

این فایل مسئولیت بارگذاری تمام تنظیمات و متغیرهای محیطی را بر عهده دارد.
به جای هاردکد کردن مقادیر در کد، تمام تنظیمات از محیط (Environment) خوانده می‌شوند.
این کار امنیت و انعطاف‌پذیری پروژه را افزایش می‌دهد.

توابع این ماژول:
- مقادیر را از `os.environ` می‌خوانند.
- برای متغیرهای الزامی، در صورت عدم وجود، خطا ایجاد می‌کنند.
- مقادیر پیش‌فرض برای متغیرهای اختیاری تعیین می‌کنند.
"""

import os
import base64
import json
from dotenv import load_dotenv

# بارگذاری متغیرهای محیطی از فایل .env برای توسعه محلی
# در محیط پروداکشن (مثل Render)، متغیرها مستقیماً در محیط تنظیم می‌شوند.
load_dotenv()

def get_env_var(var_name: str, default: str = None) -> str:
    """یک متغیر محیطی را می‌خواند. اگر الزامی باشد و وجود نداشته باشد، خطا می‌دهد."""
    value = os.environ.get(var_name)
    if value is None:
        if default is None:
            raise ValueError(f"متغیر محیطی ضروری '{var_name}' یافت نشد.")
        return default
    return value

# --- Telegram Bot Configuration ---
TELEGRAM_BOT_TOKEN = get_env_var("TELEGRAM_BOT_TOKEN")
BASE_URL = get_env_var("BASE_URL").rstrip('/')
WEBHOOK_SECRET = get_env_var("WEBHOOK_SECRET")
ADMIN_CHAT_ID = get_env_var("ADMIN_CHAT_ID")

# --- External API Keys ---
OWM_API_KEY = get_env_var("OWM_API_KEY")
EXCHANGE_RATE_API_KEY = get_env_var("EXCHANGE_RATE_API_KEY")
HUGGINGFACE_API_KEY = get_env_var("HUGGINGFACE_API_KEY", default="") # اختیاری

# --- Google Services Credentials ---
# اعتبارنامه‌های گوگل از یک متغیر base64 خوانده و دیکود می‌شوند.
# این روش برای محیط‌هایی مانند Render که فایل JSON را مستقیم پشتیبانی نمی‌کنند، مناسب است.
GOOGLE_CREDS_BASE64 = get_env_var("GOOGLE_CREDS_BASE64")
try:
    GOOGLE_CREDS_JSON = base64.b64decode(GOOGLE_CREDS_BASE64).decode('utf-8')
    GOOGLE_CREDS = json.loads(GOOGLE_CREDS_JSON)
except (json.JSONDecodeError, TypeError, ValueError) as e:
    raise ValueError(f"خطا در تجزیه GOOGLE_CREDS_BASE64: {e}")

GOOGLE_DRIVE_UPLOAD_FOLDER_ID = get_env_var("GOOGLE_DRIVE_UPLOAD_FOLDER_ID")
SHEET_ID = get_env_var("SHEET_ID")
SPREADSHEET_NAME = get_env_var("SPREADSHEET_NAME")
QUESTIONS_SHEET_NAME = get_env_var("QUESTIONS_SHEET_NAME", default="questions")

# --- Redis Configuration ---
REDIS_URL = get_env_var("REDIS_URL")

# --- Application Configuration ---
PORT = int(get_env_var("PORT", default="8000"))
LOG_LEVEL = get_env_var("LOG_LEVEL", default="INFO").upper()

# --- ISEE Calculator Constants ---
ISEE_THRESHOLD = 23000.0  # آستانه بورسیه کامل

# --- Rate Limiting ---
RATE_LIMIT_REQUESTS = 100  # تعداد درخواست
RATE_LIMIT_WINDOW = 60    # در هر 60 ثانیه

# --- Project Structure (Data URLs) ---
# آدرس پایه ریپازیتوری GitHub که فایل‌های JSON محتوایی در آن قرار دارند.
# مثال: "https://raw.githubusercontent.com/your-username/your-repo/main/data"
DATA_REPO_URL = get_env_var("DATA_REPO_URL", default="")

# --- نسخه بندی داده‌ها ---
# برای مدیریت کش: اگر نسخه در فایل JSON با این نسخه متفاوت بود، کش را رفرش کن.
DATA_VERSION = "1.0.0"

# --- URL ریپازیتوری داده‌های مرکز منابع ---
# این آدرس به پوشه data در ریپازیتوری GitHub شما اشاره می‌کند.
# مثال: "https://raw.githubusercontent.com/YourUsername/YourRepo/main/data"
# برای تست، می‌توانید از یک ریپازیتوری عمومی استفاده کنید.
DATA_REPO_URL = get_env_var("DATA_REPO_URL", "")

"""
ماژول هندلر آپلود فایل (/upload) - نسخه کامل

این فایل به کاربران اجازه می‌دهد تا فایل‌های خود را به صورت امن آپلود کنند.
"""
import os
import uuid
import datetime
from telegram import Update
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    filters,
)
from utils.gdrive import get_drive_uploader
from utils.gsheets import get_db
from utils.i18n import get_text
from utils.logger import log
from utils.gates import require_registration

# تعریف حالت مکالمه
WAITING_FILE = range(1)
TEMP_DIR = "/tmp/bot_uploads" # استفاده از /tmp برای فایل‌های موقت

@require_registration
async def start_upload(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """شروع مکالمه آپلود فایل."""
    lang = context.user_data.get("lang", "fa")
    # TODO: این پیام را به i18n منتقل کن
    await update.message.reply_text(
        "لطفاً فایلی که می‌خواهید آپلود کنید را ارسال نمایید (حداکثر ۲۰ مگابایت).\n"
        "برای لغو، دستور /cancel را ارسال کنید."
    )
    return WAITING_FILE

async def received_file(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """فایل را دریافت، دانلود، آپلود به درایو و پاک می‌کند."""
    lang = context.user_data.get("lang", "fa")
    user_id = update.effective_user.id

    # انتخاب فایل (پشتیبانی از عکس و داکیومنت)
    file_to_download = update.message.document or update.message.photo[-1]
    if not file_to_download:
        await update.message.reply_text("فرمت فایل پشتیبانی نمی‌شود. لطفاً یک سند یا عکس ارسال کنید.")
        return WAITING_FILE

    if file_to_download.file_size > 20 * 1024 * 1024: # محدودیت ۲۰ مگابایت
        await update.message.reply_text("حجم فایل بیش از حد مجاز (۲۰ مگابایت) است.")
        return WAITING_FILE

    # ایجاد پوشه موقت در صورت عدم وجود
    os.makedirs(TEMP_DIR, exist_ok=True)

    # دانلود فایل
    try:
        tg_file = await file_to_download.get_file()
        original_filename = tg_file.file_path.split('/')[-1]
        # استفاده از UUID برای جلوگیری از تداخل نام فایل
        temp_filename = f"{uuid.uuid4()}_{original_filename}"
        local_filepath = os.path.join(TEMP_DIR, temp_filename)
        await tg_file.download_to_drive(local_filepath)
        log.info(f"فایل از تلگرام در مسیر {local_filepath} دانلود شد.")
    except Exception as e:
        log.error(f"خطا در دانلود فایل از تلگرام: {e}")
        await update.message.reply_text(get_text("error_generic", lang))
        return ConversationHandler.END

    # آپلود به گوگل درایو
    drive_uploader = get_drive_uploader()
    if not drive_uploader:
        await update.message.reply_text(get_text("error_generic", lang))
        os.remove(local_filepath) # پاک کردن فایل موقت
        return ConversationHandler.END

    remote_filename = f"{user_id}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}_{original_filename}"
    file_id = drive_uploader.upload_file(local_filepath, remote_filename)

    # پاک کردن فایل موقت پس از آپلود
    os.remove(local_filepath)

    if file_id:
        # TODO: ذخیره file_id در پروفایل کاربر در Google Sheets
        # db = get_db()
        # user_data = db.get_user(user_id)
        # ... منطق اضافه کردن file_id به یک ستون ...
        # db.save_user(user_data)
        log.info(f"فایل کاربر {user_id} با شناسه {file_id} در Drive آپلود شد.")
        await update.message.reply_text("✅ فایل شما با موفقیت آپلود شد!")
    else:
        await update.message.reply_text("متأسفانه در آپلود فایل شما مشکلی پیش آمد.")

    return ConversationHandler.END

async def cancel_upload(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """مکالمه آپلود را لغو می‌کند."""
    await update.message.reply_text("عملیات آپلود لغو شد.")
    return ConversationHandler.END

upload_conv_handler = ConversationHandler(
    entry_points=[CommandHandler('upload', start_upload)],
    states={
        WAITING_FILE: [MessageHandler(filters.Document.ALL | filters.PHOTO, received_file)],
    },
    fallbacks=[CommandHandler('cancel', cancel_upload)],
    conversation_timeout=300
)

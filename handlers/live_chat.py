"""
ماژول هندلر چت زنده (/live_chat) - نسخه کامل

این فایل سیستم چت زنده بین کاربر و ادمین را پیاده‌سازی می‌کند.
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, MessageHandler, filters
from utils.gsheets import get_db
from utils.gates import require_registration, require_admin
from utils.logger import log

LIVE_CHAT_SESSIONS = 'live_chat_sessions'
LIVE_CHAT_QUEUE = 'live_chat_queue'

# ========== دستورات کاربر ==========

@require_registration
async def start_live_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """کاربر درخواست چت زنده را آغاز می‌کند."""
    user_id = update.effective_user.id

    # مقداردهی اولیه دیکشنری‌ها در صورت عدم وجود
    if LIVE_CHAT_SESSIONS not in context.bot_data:
        context.bot_data[LIVE_CHAT_SESSIONS] = {}
    if LIVE_CHAT_QUEUE not in context.bot_data:
        context.bot_data[LIVE_CHAT_QUEUE] = []

    # بررسی اینکه آیا کاربر از قبل در یک جلسه یا در صف است
    if user_id in context.bot_data[LIVE_CHAT_SESSIONS]:
        await update.message.reply_text("شما در حال حاضر در یک جلسه چت هستید.")
        return
    if user_id in context.bot_data[LIVE_CHAT_QUEUE]:
        await update.message.reply_text("شما در صف انتظار برای اتصال به ادمین هستید. لطفاً صبور باشید.")
        return

    # افزودن کاربر به صف انتظار
    context.bot_data[LIVE_CHAT_QUEUE].append(user_id)
    await update.message.reply_text("درخواست شما برای چت با ادمین ثبت شد. لطفاً منتظر بمانید...")
    log.info(f"کاربر {user_id} وارد صف چت زنده شد.")

    # اطلاع‌رسانی به ادمین‌ها
    db = get_db()
    if not db: return

    admin_ids = db.get_admins()
    user_info = f"{update.effective_user.first_name} (@{update.effective_user.username or 'N/A'})"
    message = f"کاربر جدیدی ({user_info}) در صف انتظار چت زنده است."
    buttons = [[InlineKeyboardButton("✅ اتصال به این کاربر", callback_data=f"livechat_connect:{user_id}")]]

    for admin_id in admin_ids:
        try:
            await context.bot.send_message(chat_id=admin_id, text=message, reply_markup=InlineKeyboardMarkup(buttons))
        except Exception as e:
            log.error(f"خطا در ارسال پیام به ادمین {admin_id}: {e}")

# ========== دستورات ادمین ==========

@require_admin
async def connect_to_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """یک ادمین را به یک کاربر در صف انتظار متصل می‌کند."""
    query = update.callback_query
    admin_id = update.effective_user.id

    try:
        user_id_to_connect = int(query.data.split(":")[1])
    except (IndexError, ValueError):
        await query.answer("خطا در پردازش درخواست.", show_alert=True)
        return

    # بررسی اینکه آیا کاربر هنوز در صف است
    if user_id_to_connect not in context.bot_data.get(LIVE_CHAT_QUEUE, []):
        await query.answer("این کاربر دیگر در صف انتظار نیست (شاید توسط ادمین دیگری متصل شده).", show_alert=True)
        await query.edit_message_text("این درخواست دیگر معتبر نیست.")
        return

    # حذف کاربر از صف و ایجاد جلسه
    context.bot_data[LIVE_CHAT_QUEUE].remove(user_id_to_connect)
    context.bot_data[LIVE_CHAT_SESSIONS][user_id_to_connect] = admin_id
    context.bot_data[LIVE_CHAT_SESSIONS][admin_id] = user_id_to_connect

    log.info(f"ادمین {admin_id} به کاربر {user_id_to_connect} متصل شد.")

    await query.edit_message_text(f"شما به کاربر {user_id_to_connect} متصل شدید. برای پایان چت از /end_chat استفاده کنید.")
    await context.bot.send_message(chat_id=user_id_to_connect, text="یک ادمین به شما متصل شد. می‌توانید صحبت خود را شروع کنید.\nبرای پایان چت، دستور /end_chat را ارسال کنید.")

# ========== مدیریت چت ==========

async def forward_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """پیام‌ها را بین کاربر و ادمین در یک جلسه فعال فوروارد می‌کند."""
    sender_id = update.effective_user.id
    sessions = context.bot_data.get(LIVE_CHAT_SESSIONS, {})

    if sender_id in sessions:
        recipient_id = sessions[sender_id]
        # افزودن یک پیشوند برای مشخص شدن اینکه پیام از طرف کیست
        prefix = "👤 کاربر:" if sender_id in sessions and sessions[recipient_id] == sender_id else "ادمین 👮:"

        try:
            await context.bot.send_message(chat_id=recipient_id, text=f"{prefix}\n{update.message.text}")
        except Exception as e:
            log.error(f"خطا در فوروارد کردن پیام از {sender_id} به {recipient_id}: {e}")
            await update.message.reply_text("خطایی در ارسال پیام رخ داد.")

async def end_live_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """جلسه چت زنده را خاتمه می‌دهد."""
    ender_id = update.effective_user.id
    sessions = context.bot_data.get(LIVE_CHAT_SESSIONS, {})

    if ender_id not in sessions:
        await update.message.reply_text("شما در حال حاضر در هیچ جلسه چتی نیستید.")
        return

    partner_id = sessions[ender_id]

    # حذف جلسه از هر دو طرف
    del context.bot_data[LIVE_CHAT_SESSIONS][ender_id]
    if partner_id in context.bot_data[LIVE_CHAT_SESSIONS]:
        del context.bot_data[LIVE_CHAT_SESSIONS][partner_id]

    log.info(f"جلسه چت بین {ender_id} و {partner_id} توسط {ender_id} خاتمه یافت.")

    await context.bot.send_message(chat_id=ender_id, text="جلسه چت شما با موفقیت پایان یافت.")
    try:
        await context.bot.send_message(chat_id=partner_id, text="جلسه چت شما توسط طرف مقابل پایان یافت.")
    except Exception as e:
        log.warning(f"نتوانستیم پیام پایان چت را به {partner_id} ارسال کنیم: {e}")

# هندلر پیام برای فوروارد کردن
live_chat_message_handler = MessageHandler(filters.TEXT & ~filters.COMMAND & filters.ChatType.PRIVATE, forward_message)

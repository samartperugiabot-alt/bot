"""
ماژول هندلر ثبت‌نام کاربر (/register) - نسخه کامل

این فایل مسئولیت مدیریت فرآیند ثبت‌نام چندمرحله‌ای کاربر را با استفاده از
`ConversationHandler` بر عهده دارد. این یک مثال کامل از نحوه ساخت فرم‌های
تعاملی در ربات است.
"""
import datetime
from telegram.ext import ConversationHandler, CommandHandler, MessageHandler, filters
from telegram import Update
from telegram.ext import ContextTypes
from utils.i18n import get_text
from utils.common import validate_age, validate_email, sanitize_markdown
from utils.gsheets import get_db

# تعریف حالت‌های مکالمه (States)
# این حالت‌ها به ConversationHandler می‌گویند که در هر مرحله منتظر چه نوع ورودی باشد.
(NAME, AGE, COUNTRY, FIELD, EMAIL) = range(5)

async def start_register(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    مرحله اول ثبت‌نام: شروع فرآیند با دستور /register.
    به کاربر خوشامد گفته و از او می‌خواهد نامش را وارد کند.
    """
    user = update.effective_user
    db = get_db()

    # بررسی اینکه آیا کاربر قبلاً ثبت‌نام کرده است یا خیر
    if db and db.get_user(user.id):
        lang = context.user_data.get("lang", "fa")
        await update.message.reply_text("شما قبلاً ثبت‌نام کرده‌اید!")
        return ConversationHandler.END

    # شروع مکالمه جدید
    context.user_data["register_info"] = {}
    lang = context.user_data.get("lang", "fa")

    await update.message.reply_text(get_text("register_welcome", lang))
    await update.message.reply_text(get_text("register_prompt_name", lang))

    return NAME

async def received_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """مرحله دوم: نام کاربر را دریافت کرده و سن او را می‌پرسد."""
    lang = context.user_data.get("lang", "fa")
    user_input = update.message.text
    context.user_data["register_info"]["name"] = sanitize_markdown(user_input)

    await update.message.reply_text(get_text("register_prompt_age", lang))

    return AGE

async def received_age(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """مرحله سوم: سن کاربر را دریافت، اعتبارسنجی کرده و کشور را می‌پرسد."""
    lang = context.user_data.get("lang", "fa")
    user_input = update.message.text

    if not validate_age(user_input):
        await update.message.reply_text(get_text("register_invalid_age", lang))
        return AGE # کاربر در همین مرحله باقی می‌ماند تا ورودی صحیح را وارد کند

    context.user_data["register_info"]["age"] = int(user_input)
    await update.message.reply_text(get_text("register_prompt_country", lang))

    return COUNTRY

async def received_country(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """مرحله چهارم: کشور را دریافت کرده و رشته تحصیلی را می‌پرسد."""
    lang = context.user_data.get("lang", "fa")
    user_input = update.message.text
    context.user_data["register_info"]["country"] = sanitize_markdown(user_input)

    await update.message.reply_text(get_text("register_prompt_field", lang))

    return FIELD

async def received_field(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """مرحله پنجم: رشته تحصیلی را دریافت کرده و ایمیل را می‌پرسد."""
    lang = context.user_data.get("lang", "fa")
    user_input = update.message.text
    context.user_data["register_info"]["field"] = sanitize_markdown(user_input)

    await update.message.reply_text(get_text("register_prompt_email", lang))

    return EMAIL

async def received_email(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    مرحله نهایی: ایمیل را دریافت، اعتبارسنجی کرده، تمام اطلاعات را ذخیره
    و مکالمه را به پایان می‌رساند.
    """
    lang = context.user_data.get("lang", "fa")
    user_input = update.message.text

    if not validate_email(user_input):
        await update.message.reply_text(get_text("register_invalid_email", lang))
        return EMAIL # کاربر در همین مرحله باقی می‌ماند

    context.user_data["register_info"]["email"] = user_input.lower()

    # --- جمع‌آوری و ذخیره نهایی اطلاعات ---
    user = update.effective_user
    final_data = {
        "user_id": user.id,
        "username": user.username,
        "first_name": user.first_name,
        "registration_date": datetime.datetime.now().isoformat(),
        "lang": lang,
        **context.user_data["register_info"]
    }

    # ذخیره در Google Sheets (با استفاده از متد stub)
    db = get_db()
    if db:
        db.save_user(final_data)
        print(f"کاربر جدید ذخیره شد: {final_data}")

    await update.message.reply_text(get_text("register_success", lang))

    # پاک کردن داده‌های موقت ثبت‌نام
    del context.user_data["register_info"]

    return ConversationHandler.END

async def cancel_register(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """مکالمه ثبت‌نام را در هر مرحله‌ای لغو می‌کند."""
    lang = context.user_data.get("lang", "fa")
    await update.message.reply_text("عملیات ثبت‌نام لغو شد.")

    # پاک کردن داده‌های موقت
    if "register_info" in context.user_data:
        del context.user_data["register_info"]

    return ConversationHandler.END

# --- ساخت ConversationHandler ---
# این هندلر تمام منطق مکالمه را مدیریت می‌کند.
register_conv_handler = ConversationHandler(
    entry_points=[CommandHandler('register', start_register)],
    states={
        NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, received_name)],
        AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, received_age)],
        COUNTRY: [MessageHandler(filters.TEXT & ~filters.COMMAND, received_country)],
        FIELD: [MessageHandler(filters.TEXT & ~filters.COMMAND, received_field)],
        EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, received_email)],
    },
    fallbacks=[CommandHandler('cancel', cancel_register)],
    conversation_timeout=300 # مکالمه پس از ۵ دقیقه عدم فعالیت لغو می‌شود
)

"""
ماژول هندلر محاسبه‌گر ISEE (/isee) - نسخه کامل

این فایل یک محاسبه‌گر ساده و آموزشی برای شاخص ISEE پیاده‌سازی می‌کند.
"""
from telegram import Update
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    filters,
)
from utils.i18n import get_text
from utils.common import get_family_coefficient
from utils.logger import log
import config

# تعریف حالت‌های مکالمه
INCOME, PROPERTY_SIZE, FAMILY_MEMBERS = range(3)

def calculate_isee_value(income: float, property_size: float, family_n: int) -> float:
    """مقدار ISEE را بر اساس فرمول آموزشی محاسبه می‌کند."""
    # ارزش ملک (ISP) به صورت تقریبی: متراژ * ۵۰۰ یورو
    isp = property_size * 500.0
    # ۲۰ درصد از ارزش ملک در محاسبه لحاظ می‌شود.
    isr = income + (isp * 0.2)

    coeff = get_family_coefficient(family_n)
    if coeff == 0: return float('inf') # جلوگیری از تقسیم بر صفر

    return isr / coeff

async def start_isee(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """شروع مکالمه محاسبه ISEE و درخواست درآمد."""
    lang = context.user_data.get("lang", "fa")
    context.user_data["isee_info"] = {}

    # TODO: این پیام‌ها را به i18n منتقل کن
    await update.message.reply_text(
        "به محاسبه‌گر آموزشی ISEE خوش آمدید.\n"
        "توجه: این محاسبه فقط یک تخمین است و جایگزین محاسبه رسمی CAF نیست.\n\n"
        "لطفاً مجموع درآمد سالانه خانواده خود را به یورو وارد کنید:"
    )
    return INCOME

async def received_income(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """درآمد را دریافت و متراژ ملک را درخواست می‌کند."""
    user_input = update.message.text
    try:
        income = float(user_input)
        context.user_data["isee_info"]["income"] = income
        await update.message.reply_text("عالی. حالا لطفاً کل متراژ املاک تحت تملک خانواده (در هر کجای دنیا) را به متر مربع وارد کنید (اگر ملکی ندارید 0 وارد کنید):")
        return PROPERTY_SIZE
    except (ValueError, TypeError):
        await update.message.reply_text("مقدار نامعتبر است. لطفاً درآمد را به صورت یک عدد (مثلاً: 15000) وارد کنید.")
        return INCOME

async def received_property_size(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """متراژ ملک را دریافت و تعداد اعضای خانواده را درخواست می‌کند."""
    user_input = update.message.text
    try:
        property_size = float(user_input)
        context.user_data["isee_info"]["property_size"] = property_size
        await update.message.reply_text("بسیار خب. لطفاً تعداد کل اعضای خانواده (تحت تکفل) را وارد کنید:")
        return FAMILY_MEMBERS
    except (ValueError, TypeError):
        await update.message.reply_text("مقدار نامعتبر است. لطفاً متراژ را به صورت یک عدد (مثلاً: 80) وارد کنید.")
        return PROPERTY_SIZE

async def received_family_members(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """تعداد اعضا را دریافت، محاسبه و نتیجه را اعلام می‌کند."""
    user_input = update.message.text
    try:
        family_n = int(user_input)
        if family_n <= 0:
            raise ValueError("تعداد اعضای خانواده باید مثبت باشد.")

        # بازیابی اطلاعات و محاسبه
        info = context.user_data["isee_info"]
        isee_value = calculate_isee_value(info["income"], info["property_size"], family_n)

        # تعیین وضعیت بورسیه
        status = ""
        if isee_value <= config.ISEE_THRESHOLD:
            status = "شما احتمالاً واجد شرایط بورسیه کامل و تخفیف حداکثری هستید. 🎉"
        elif isee_value <= config.ISEE_THRESHOLD * 1.5:
            status = "شما احتمالاً واجد شرایط بورسیه درصدی و تخفیف‌های نسبی هستید."
        else:
            status = "به نظر می‌رسد ISEE شما بالاتر از آستانه بورسیه باشد. با این حال ممکن است شامل تخفیف‌های دیگری شوید."

        result_text = (
            f"📊 *نتیجه محاسبه ISEE (تخمینی)*\n\n"
            f"مقدار ISEE شما: *€{isee_value:,.2f}*\n\n"
            f"*{status}*"
        )
        await update.message.reply_text(result_text, parse_mode='Markdown')

        # پاک کردن داده‌های موقت
        del context.user_data["isee_info"]
        return ConversationHandler.END

    except (ValueError, TypeError):
        await update.message.reply_text("مقدار نامعتبر است. لطفاً تعداد اعضا را به صورت یک عدد صحیح (مثلاً: 4) وارد کنید.")
        return FAMILY_MEMBERS

async def cancel_isee(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """مکالمه را لغو می‌کند."""
    if "isee_info" in context.user_data:
        del context.user_data["isee_info"]
    await update.message.reply_text("محاسبه ISEE لغو شد.")
    return ConversationHandler.END

isee_conv_handler = ConversationHandler(
    entry_points=[CommandHandler('isee', start_isee)],
    states={
        INCOME: [MessageHandler(filters.TEXT & ~filters.COMMAND, received_income)],
        PROPERTY_SIZE: [MessageHandler(filters.TEXT & ~filters.COMMAND, received_property_size)],
        FAMILY_MEMBERS: [MessageHandler(filters.TEXT & ~filters.COMMAND, received_family_members)],
    },
    fallbacks=[CommandHandler('cancel', cancel_isee)],
    conversation_timeout=300
)

"""
ماژول هندلر آب و هوا (/weather) - نسخه کامل

این فایل مسئولیت دریافت و نمایش اطلاعات آب و هوا را بر عهده دارد.
"""
from telegram import Update
from telegram.ext import ContextTypes
from utils.weather_api import get_weather
from utils.i18n import get_text
from utils.logger import log

# مپ کردن کد آیکون OpenWeatherMap به ایموجی
WEATHER_ICONS = {
    "01d": "☀️", "01n": "🌙",
    "02d": "⛅️", "02n": "☁️",
    "03d": "☁️", "03n": "☁️",
    "04d": "☁️", "04n": "☁️",
    "09d": "🌧", "09n": "🌧",
    "10d": "🌦", "10n": "🌧",
    "11d": "⛈", "11n": "⛈",
    "13d": "❄️", "13n": "❄️",
    "50d": "🌫", "50n": "🌫",
}

async def weather_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    دستور /weather را مدیریت می‌کند.
    شهر را از آرگومان‌های دستور می‌خواند، اطلاعات آب و هوا را دریافت کرده
    و برای کاربر ارسال می‌کند.
    """
    lang = context.user_data.get("lang", "fa")

    # استخراج نام شهر از دستور. اگر وارد نشده بود، از "Perugia" استفاده کن.
    if context.args:
        city_name = " ".join(context.args)
    else:
        city_name = "Perugia"

    log.info(f"درخواست آب و هوا برای شهر '{city_name}' توسط کاربر {update.effective_user.id}")

    weather_info = get_weather(city=city_name, lang=lang)

    if not weather_info:
        # TODO: این پیام‌ها را به i18n منتقل کن
        if lang == 'fa':
            await update.message.reply_text(f"متأسفانه نتوانستم اطلاعات آب و هوای شهر '{city_name}' را پیدا کنم. لطفاً نام شهر را به انگلیسی بررسی کنید.")
        else:
            await update.message.reply_text(f"Sorry, I couldn't find the weather for '{city_name}'. Please check the city name.")
        return

    # قالب‌بندی پیام خروجی
    icon = WEATHER_ICONS.get(weather_info["icon"], "🌐")

    if lang == 'fa':
        text = (
            f"{icon} *آب و هوای فعلی در {weather_info['city']}*\n\n"
            f"🌡️ *دما:* {weather_info['temp']:.1f}°C\n"
            f"🤔 *دمای محسوس:* {weather_info['feels_like']:.1f}°C\n"
            f"📝 *وضعیت:* {weather_info['description'].capitalize()}"
        )
    else: # English
        text = (
            f"{icon} *Current Weather in {weather_info['city']}*\n\n"
            f"🌡️ *Temperature:* {weather_info['temp']:.1f}°C\n"
            f"🤔 *Feels Like:* {weather_info['feels_like']:.1f}°C\n"
            f"📝 *Description:* {weather_info['description'].capitalize()}"
        )

    await update.message.reply_text(text, parse_mode='Markdown')

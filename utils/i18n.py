"""
ماژول بین‌المللی‌سازی (Internationalization - i18n)

این فایل مسئولیت مدیریت تمام متن‌های چندزبانه ربات را بر عهده دارد.
تمام رشته‌های متنی که به کاربر نمایش داده می‌شوند در یک دیکشنری به نام `MESSAGES`
نگهداری می‌شوند. این ساختار به ما اجازه می‌دهد تا به راحتی زبان‌های جدید را
اضافه کرده و متن‌ها را در یک مکان واحد مدیریت کنیم.

ساختار:
MESSAGES = {
    "fa": {
        "welcome": "سلام!",
        ...
    },
    "en": {
        "welcome": "Hello!",
        ...
    }
}

تابع get_text برای دسترسی آسان به این پیام‌ها طراحی شده است.
"""

# زبان پیش‌فرض ربات در صورتی که زبان کاربر مشخص نباشد.
DEFAULT_LANG = "fa"

MESSAGES = {
    "fa": {
        # --- پیام‌های عمومی ---
        "welcome": "🇮🇹 به ربات دانشجویی پروجا خوش آمدید!",
        "main_menu_header": "👇 لطفاً یکی از گزینه‌های زیر را انتخاب کنید:",
        "go_back": "🔙 بازگشت",
        "main_menu": "🏠 منوی اصلی",
        "error_generic": "🚫 خطایی رخ داد. لطفاً دوباره تلاش کنید.",
        "not_registered": "⚠️ شما هنوز ثبت‌نام نکرده‌اید. لطفاً ابتدا از طریق دستور /register ثبت‌نام کنید.",
        "coming_soon": "🚧 این بخش به زودی فعال خواهد شد.",

        # --- دکمه‌های منوی اصلی ---
        "btn_resources_hub": "📚 مرکز منابع",
        "btn_scholarships": "🎓 بورسیه‌ها",
        "btn_isee": "🧮 محاسبه ISEE",
        "btn_weather": "🌦 آب و هوا",
        "btn_news": "📰 اخبار",
        "btn_currency_exchange": "💱 تبدیل ارز",
        "btn_profile": "👤 پروفایل من",
        "btn_roommate_finder": "👥 هم‌اتاقی‌یابی",
        "btn_live_chat": "💬 چت با ادمین",

        # --- ثبت‌نام (/register) ---
        "register_welcome": "✅ برای شروع فرآیند ثبت‌نام، لطفاً اطلاعات زیر را وارد کنید.",
        "register_prompt_name": "📝 لطفاً نام کامل خود را وارد کنید:",
        "register_prompt_age": "🎂 لطفاً سن خود را به عدد وارد کنید (مثلاً: 25):",
        "register_prompt_country": "🌍 لطفاً کشور خود را وارد کنید (مثلاً: ایران):",
        "register_prompt_field": "🎓 لطفاً رشته تحصیلی خود را وارد کنید:",
        "register_prompt_email": "✉️ لطفاً ایمیل خود را وارد کنید:",
        "register_success": "🎉 ثبت‌نام شما با موفقیت انجام شد! به خانواده ما خوش آمدید.",
        "register_invalid_age": "❌ سن وارد شده نامعتبر است. لطفاً یک عدد بین 16 تا 100 وارد کنید.",
        "register_invalid_email": "❌ ایمیل وارد شده نامعتبر است. لطفاً یک ایمیل صحیح وارد کنید.",
    },
    "en": {
        # --- General Messages ---
        "welcome": "🇮🇹 Welcome to the Perugia Student Bot!",
        "main_menu_header": "👇 Please choose one of the options below:",
        "go_back": "🔙 Back",
        "main_menu": "🏠 Main Menu",
        "error_generic": "🚫 An error occurred. Please try again.",
        "not_registered": "⚠️ You are not registered yet. Please register first using the /register command.",
        "coming_soon": "🚧 This feature is coming soon.",

        # --- Main Menu Buttons ---
        "btn_resources_hub": "📚 Resources Hub",
        "btn_scholarships": "🎓 Scholarships",
        "btn_isee": "🧮 ISEE Calculator",
        "btn_weather": "🌦 Weather",
        "btn_news": "📰 News",
        "btn_currency_exchange": "💱 Currency Exchange",
        "btn_profile": "👤 My Profile",
        "btn_roommate_finder": "👥 Roommate Finder",
        "btn_live_chat": "💬 Chat with Admin",

        # --- Registration (/register) ---
        "register_welcome": "✅ To start the registration process, please provide the following information.",
        "register_prompt_name": "📝 Please enter your full name:",
        "register_prompt_age": "🎂 Please enter your age as a number (e.g., 25):",
        "register_prompt_country": "🌍 Please enter your country (e.g., Iran):",
        "register_prompt_field": "🎓 Please enter your field of study:",
        "register_prompt_email": "✉️ Please enter your email:",
        "register_success": "🎉 Your registration was successful! Welcome to our family.",
        "register_invalid_age": "❌ Invalid age. Please enter a number between 16 and 100.",
        "register_invalid_email": "❌ Invalid email. Please enter a valid email address.",
    },
    "it": {
        # --- Messaggi Generali ---
        "welcome": "🇮🇹 Benvenuto al Bot per Studenti di Perugia!",
        "main_menu_header": "👇 Scegli una delle opzioni qui sotto:",
        "go_back": "🔙 Indietro",
        "main_menu": "🏠 Menu Principale",
        "error_generic": "🚫 Si è verificato un errore. Per favore, riprova.",
        "not_registered": "⚠️ Non sei ancora registrato. Per favore, registrati prima usando il comando /register.",
        "coming_soon": "🚧 Questa funzionalità sarà presto disponibile.",

        # --- Pulsanti Menu Principale ---
        "btn_resources_hub": "📚 Centro Risorse",
        "btn_scholarships": "🎓 Borse di Studio",
        "btn_isee": "🧮 Calcolo ISEE",
        "btn_weather": "🌦 Meteo",
        "btn_news": "📰 Notizie",
        "btn_currency_exchange": "💱 Cambio Valuta",
        "btn_profile": "👤 Il Mio Profilo",
        "btn_roommate_finder": "👥 Trova Coinquilino",
        "btn_live_chat": "💬 Chatta con l'Admin",

        # --- Registrazione (/register) ---
        "register_welcome": "✅ Per avviare il processo di registrazione, fornisci le seguenti informazioni.",
        "register_prompt_name": "📝 Inserisci il tuo nome completo:",
        "register_prompt_age": "🎂 Inserisci la tua età in numero (es: 25):",
        "register_prompt_country": "🌍 Inserisci il tuo paese (es: Italia):",
        "register_prompt_field": "🎓 Inserisci il tuo campo di studi:",
        "register_prompt_email": "✉️ Inserisci il tuo indirizzo email:",
        "register_success": "🎉 Registrazione completata con successo! Benvenuto nella nostra famiglia.",
        "register_invalid_age": "❌ Età non valida. Inserisci un numero tra 16 e 100.",
        "register_invalid_email": "❌ Email non valida. Inserisci un indirizzo email valido.",
    }
}

# زبان عربی می‌تواند به همین شکل اضافه شود
# "ar": { ... }

def get_text(key: str, lang: str) -> str:
    """
    یک کلید و زبان دریافت کرده و متن مربوطه را از دیکشنری MESSAGES برمی‌گرداند.
    اگر کلید یا زبان وجود نداشته باشد، به زبان پیش‌فرض (فارسی) بازگشت می‌کند.

    Args:
        key (str): کلید پیام (مانند 'welcome').
        lang (str): کد زبان (مانند 'fa', 'en').

    Returns:
        str: متن پیام.
    """
    return MESSAGES.get(lang, MESSAGES[DEFAULT_LANG]).get(key, f"_{key}_")

# مثال استفاده:
# lang = "en"
# welcome_message = get_text("welcome", lang)
# print(welcome_message) -> "Welcome to the Perugia Student Bot!"

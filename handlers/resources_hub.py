"""
ماژول هندلر مرکز منابع (Resources Hub) - نسخه کامل

این فایل مسئولیت نمایش محتوای مرکز منابع را بر عهده دارد.
"""
import requests
from telegram import Update, InlineKeyboardButton
from telegram.ext import ContextTypes
from utils.redis_utils import get_redis_client
from utils.common import build_menu
from utils.logger import log
from utils.i18n import get_text
import config

# --- Data Fetching Helper ---

def _get_hub_data(file_path: str) -> dict | None:
    """
    داده‌های JSON را از ریپازیتوری GitHub دریافت و کش می‌کند.
    file_path: مسیر فایل در ریپازیتوری (مثال: 'hub/index.json').
    """
    if not config.DATA_REPO_URL:
        log.error("متغیر DATA_REPO_URL در تنظیمات تعریف نشده است.")
        return None

    url = f"{config.DATA_REPO_URL}/{file_path}"
    cache_key = f"hub_data:{file_path}"

    try:
        redis = get_redis_client()
        cached_data = redis.get_cache(cache_key)
        if cached_data:
            log.info(f"داده مرکز منابع از کش خوانده شد: {file_path}")
            return cached_data
    except ConnectionError as e:
        log.error(f"خطای اتصال به Redis در _get_hub_data: {e}")
        redis = None

    try:
        log.info(f"درخواست به GitHub برای دریافت: {url}")
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        data = response.json()
        if redis:
            # کش برای ۱۵ دقیقه
            redis.set_cache(cache_key, data, ttl=900)
        return data
    except (requests.RequestException, ValueError) as e:
        log.error(f"خطا در دریافت یا تجزیه JSON از {url}: {e}")
        return None

# --- Menu Handlers ---

async def hub_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """منوی اصلی مرکز منابع (لیست دسته‌بندی‌ها) را نمایش می‌دهد."""
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get("lang", "fa")

    index_data = _get_hub_data("hub/index.json")
    if not index_data or "categories" not in index_data:
        await query.edit_message_text(get_text("error_generic", lang))
        return

    buttons = []
    for category in index_data["categories"]:
        buttons.append(
            InlineKeyboardButton(
                category[f"title_{lang}"],
                callback_data=f"hub_cat:{category['id']}"
            )
        )

    keyboard = build_menu(buttons, n_cols=2)
    await query.edit_message_text("لطفاً یک دسته‌بندی را انتخاب کنید:", reply_markup=keyboard)


async def hub_category_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """لیست مقالات یک دسته‌بندی خاص را نمایش می‌دهد."""
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get("lang", "fa")
    category_id = query.data.split(":")[1]

    index_data = _get_hub_data("hub/index.json")
    if not index_data or "items" not in index_data:
        await query.edit_message_text(get_text("error_generic", lang))
        return

    articles = [item for item in index_data["items"] if item["category_id"] == category_id]

    buttons = []
    for article in articles:
        buttons.append(
            InlineKeyboardButton(
                article[f"title_{lang}"],
                callback_data=f"hub_art:{article['id']}:0" # 0: index بخش
            )
        )

    buttons.append(InlineKeyboardButton(get_text("go_back", lang), callback_data="hub_main"))
    keyboard = build_menu(buttons, n_cols=1)
    await query.edit_message_text("لطفاً یک مقاله را انتخاب کنید:", reply_markup=keyboard)


async def hub_show_article(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """محتوای یک مقاله را نمایش می‌دهد."""
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get("lang", "fa")

    try:
        _, article_id, section_index_str = query.data.split(":")
        section_index = int(section_index_str)
    except (ValueError, IndexError):
        await query.edit_message_text(get_text("error_generic", lang))
        return

    index_data = _get_hub_data("hub/index.json")
    article_meta = next((item for item in index_data["items"] if item["id"] == article_id), None)

    if not article_meta:
        await query.edit_message_text(get_text("error_generic", lang))
        return

    article_data = _get_hub_data(f"hub/{article_meta['file']}")
    if not article_data or "content" not in article_data:
        await query.edit_message_text(get_text("error_generic", lang))
        return

    sections = article_data["content"]
    current_section = sections[section_index]

    text = f"*{current_section[f'title_{lang}']}*\n\n{current_section[f'body_{lang}']}"

    # --- دکمه‌های ناوبری ---
    buttons = []
    nav_row = []
    if section_index > 0:
        nav_row.append(InlineKeyboardButton("◀️ قبلی", callback_data=f"hub_art:{article_id}:{section_index-1}"))
    if section_index < len(sections) - 1:
        nav_row.append(InlineKeyboardButton("بعدی ▶️", callback_data=f"hub_art:{article_id}:{section_index+1}"))

    if nav_row:
        buttons.append(nav_row)

    buttons.append([InlineKeyboardButton(get_text("go_back", lang), callback_data=f"hub_cat:{article_meta['category_id']}")])

    keyboard = build_menu([btn for row in buttons for btn in row], n_cols=2) # Flatten and build
    await query.edit_message_text(text, reply_markup=keyboard, parse_mode="Markdown")

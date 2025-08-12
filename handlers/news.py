"""
ماژول هندلر اخبار (/news) - نسخه کامل

این فایل مسئولیت نمایش و مدیریت اخبار را بر عهده دارد.
"""
import datetime
import uuid
from telegram import Update
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    filters,
)
from utils.news_store import get_news_store
from utils.gates import require_admin
from utils.i18n import get_text

# --- حالت‌های مکالمه برای ارسال خبر ---
TITLE, CONTENT = range(2)

# ========== دستورات کاربری ==========

async def show_latest_news(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """آخرین اخبار را به کاربر نمایش می‌دهد."""
    lang = context.user_data.get("lang", "fa")
    news_store = get_news_store()
    latest_news = news_store.get_latest_news(count=5)

    if not latest_news:
        # TODO: i18n
        await update.message.reply_text("در حال حاضر خبر جدیدی وجود ندارد.")
        return

    response_text = "📰 *آخرین اخبار*\n\n"
    for news in latest_news:
        # TODO: i18n
        title = news.get(f"title_{lang}", news.get("title_fa", "بدون عنوان"))
        content_snippet = news.get(f"content_{lang}", news.get("content_fa", ""_))[:100]
        response_text += f"*{title}*\n_{content_snippet}..._\n\n---\n\n"

    await update.message.reply_text(response_text, parse_mode="Markdown")

# ========== دستورات ادمین ==========

@require_admin
async def post_news_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """شروع فرآیند ارسال خبر جدید."""
    context.user_data['new_post'] = {}
    # TODO: i18n
    await update.message.reply_text("لطفاً عنوان خبر را به فارسی وارد کنید:")
    return TITLE

async def received_title_fa(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """عنوان فارسی را دریافت و درخواست محتوای فارسی می‌کند."""
    context.user_data['new_post']['title_fa'] = update.message.text
    await update.message.reply_text("اکنون محتوای خبر را به فارسی وارد کنید:")
    return CONTENT

async def received_content_fa(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """محتوای فارسی را دریافت، خبر را ذخیره و فرآیند را تمام می‌کند."""
    context.user_data['new_post']['content_fa'] = update.message.text

    news_store = get_news_store()
    news_item = {
        "id": str(uuid.uuid4()),
        "timestamp": datetime.datetime.now().isoformat(),
        "author_id": update.effective_user.id,
        **context.user_data['new_post']
    }

    if news_store.add_news(news_item):
        await update.message.reply_text("✅ خبر با موفقیت منتشر شد.")
    else:
        await update.message.reply_text("❌ خطایی در انتشار خبر رخ داد.")

    del context.user_data['new_post']
    return ConversationHandler.END

async def cancel_post_news(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """عملیات ارسال خبر را لغو می‌کند."""
    if 'new_post' in context.user_data:
        del context.user_data['new_post']
    await update.message.reply_text("ارسال خبر لغو شد.")
    return ConversationHandler.END

# --- Conversation Handler ---
post_news_conv_handler = ConversationHandler(
    entry_points=[CommandHandler("post_news", post_news_start)],
    states={
        TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, received_title_fa)],
        CONTENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, received_content_fa)],
    },
    fallbacks=[CommandHandler("cancel", cancel_post_news)],
)

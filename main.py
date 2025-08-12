"""
نقطه ورود اصلی برنامه (Main Entry Point)

این فایل مسئولیت‌های اصلی زیر را بر عهده دارد:
1.  **راه‌اندازی سرور FastAPI:** یک وب‌سرور سبک برای دریافت آپدیت‌های تلگرام از طریق وب‌هوک.
    این روش برای هاستینگ روی پلتفرم‌هایی مانند Render ایده‌آل است.
2.  **پیکربندی اپلیکیشن ربات:** ایجاد یک نمونه از `telegram.ext.Application` و
    اتصال آن به توکن ربات.
3.  **مدیریت وب‌هوک:**
    -   تعریف یک مسیر (route) `POST /telegram/webhook` که آپدیت‌ها را از تلگرام دریافت می‌کند.
    -   بررسی توکن مخفی (`X-Telegram-Bot-Api-Secret-Token`) برای اطمینان از اینکه
        درخواست‌ها واقعاً از سمت تلگرام ارسال شده‌اند (مسئله امنیتی).
    -   ثبت (set) وب‌هوک در سرورهای تلگرام هنگام بالا آمدن برنامه (`startup` event).
    -   حذف (delete) وب‌هوک هنگام خاموش شدن برنامه (`shutdown` event).
4.  **ثبت هندلرها (Registering Handlers):** اتصال دستورات (مانند `/start`) و مکالمات
    (مانند `/register`) به توابع مربوطه که در پوشه `handlers/` تعریف شده‌اند.
5.  **اجرای برنامه:** با استفاده از `uvicorn` سرور FastAPI را اجرا می‌کند.
"""
import asyncio
import uvicorn
from fastapi import FastAPI, Request, Response
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
import config

# --- وارد کردن هندلرها از پوشه handlers ---
from handlers import start_menu, register, weather, isee, resources_hub

# 1. --- مقداردهی اولیه اپلیکیشن FastAPI ---
app = FastAPI(
    title="Perugia Student Bot",
    description="یک ربات تلگرامی برای کمک به دانشجویان و مهاجران در پروجا.",
    version="1.0.0"
)

# 2. --- پیکربندی اپلیکیشن ربات تلگرام ---
# استفاده از ContextTypes برای تایپ‌هینتینگ بهتر
# context_types = ContextTypes(context=CustomContext) # در صورت نیاز به کانتکست سفارشی
application = (
    Application.builder()
    .token(config.TELEGRAM_BOT_TOKEN)
    .read_timeout(30)
    .write_timeout(30)
    .build()
)

# 3. --- مدیریت وب‌هوک ---
@app.post("/telegram/webhook")
async def telegram_webhook(request: Request):
    """
    این اندپوینت آپدیت‌های تلگرام را دریافت می‌کند.
    اولین کار، بررسی توکن مخفی برای امنیت است.
    """
    secret_token = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
    if secret_token != config.WEBHOOK_SECRET:
        return Response(status_code=403) # Forbidden

    # پردازش آپدیت دریافت شده
    async with application.update_queue.put(
        Update.de_json(await request.json(), application.bot)
    ):
        pass
    return Response(status_code=200)

@app.on_event("startup")
async def on_startup():
    """
    هنگام شروع به کار برنامه، این تابع فراخوانی می‌شود.
    آدرس وب‌هوک را روی سرورهای تلگرام تنظیم می‌کند.
    """
    webhook_url = f"{config.BASE_URL}/telegram/webhook"
    await application.bot.set_webhook(
        url=webhook_url,
        secret_token=config.WEBHOOK_SECRET,
        allowed_updates=Update.ALL_TYPES
    )
    print(f"✅ وب‌هوک با موفقیت روی آدرس {webhook_url} تنظیم شد.")

    # اجرای پردازشگر آپدیت‌ها در پس‌زمینه
    application.job_queue.start()
    await application.start()


@app.on_event("shutdown")
async def on_shutdown():
    """هنگام خاموش شدن برنامه، وب‌هوک را حذف می‌کند."""
    await application.stop()
    await application.bot.delete_webhook()
    application.job_queue.stop()
    print("ℹ️ وب‌هوک با موفقیت حذف شد.")


# --- اندپوینت‌های کمکی برای مانیتورینگ ---
@app.get("/healthz", status_code=200)
def health_check():
    """برای بررسی زنده بودن سرویس (Health Check) توسط Render."""
    return {"status": "ok"}

@app.get("/readyz", status_code=200)
def ready_check():
    """برای بررسی آمادگی سرویس (آماده بودن اتصالات به Redis, DB و ...)."""
    # TODO: در پیاده‌سازی کامل، وضعیت اتصال به Redis و GSheets چک شود.
    return {"status": "ready"}


# 4. --- ثبت هندلرها ---
# این بخش منطق ربات را به اپلیکیشن متصل می‌کند.
application.add_handler(CommandHandler("start", start_menu.start))
application.add_handler(CommandHandler("weather", weather.weather_handler))
application.add_handler(register.register_conv_handler)
application.add_handler(isee.isee_conv_handler)

# --- CallbackQueryHandler اصلی برای مدیریت دکمه‌های شیشه‌ای ---
async def main_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    این تابع تمام callback query ها را دریافت کرده و بر اساس پیشوند داده،
    آنها را به هندلر مناسب هدایت می‌کند.
    """
    query = update.callback_query
    data = query.data

    if data.startswith("hub_"):
        if data == "hub_main":
            await resources_hub.hub_main_menu(update, context)
        elif data.startswith("hub_cat:"):
            await resources_hub.hub_category_menu(update, context)
        elif data.startswith("hub_art:"):
            await resources_hub.hub_show_article(update, context)
    else:
        # برای سایر دکمه‌ها در آینده
        await query.answer("این دکمه هنوز فعال نشده است.")

application.add_handler(CallbackQueryHandler(main_callback_handler))

print("ℹ️ هندلرهای ربات با موفقیت ثبت شدند.")

# 5. --- اجرای برنامه ---
if __name__ == "__main__":
    # این بخش برای اجرای محلی (local) برنامه استفاده می‌شود.
    # در محیط پروداکشن Render، از دستور uvicorn در فایل start command استفاده می‌شود.
    # مثال: uvicorn main:app --host 0.0.0.0 --port 8000
    uvicorn.run(app, host="0.0.0.0", port=config.PORT)

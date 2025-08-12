"""
ماژول زمان‌بندی وظایف (Task Scheduler)

این فایل مسئولیت زمان‌بندی و اجرای وظایف در آینده را بر عهده دارد.
به جای استفاده از کتابخانه‌های سنگین مانند APScheduler، از راه‌حل‌های سبک‌تر
مانند `python-telegram-bot.JobQueue` یا یک صف مبتنی بر Redis ZSET استفاده می‌شود.

قابلیت‌ها:
-   ارسال یادآوری برای جلسات مشاوره یا انقضای کارت اقامت.
-   ارسال کلمات روزانه برای آموزش زبان.
-   ارسال اخبار به صورت دسته‌ای (batch).

مثال با JobQueue:
context.job_queue.run_once(callback_function, when=60, data={'user_id': 123})
"""
from telegram.ext import ContextTypes

def schedule_reminder(context: ContextTypes.DEFAULT_TYPE, chat_id: int, when: int, text: str):
    """
    یک یادآوری را با استفاده از JobQueue داخلی کتابخانه python-telegram-bot زمان‌بندی می‌کند.

    Args:
        context: کانتکست ربات.
        chat_id: شناسه چت کاربر.
        when: زمان تا اجرای وظیفه به ثانیه.
        text: متن یادآوری.
    """

    async def alarm(context: ContextTypes.DEFAULT_TYPE):
        """تابع callback که پیام را ارسال می‌کند."""
        await context.bot.send_message(chat_id=context.job.chat_id, text=context.job.data)

    context.job_queue.run_once(alarm, when, data=text, chat_id=chat_id)
    print(f"یک یادآوری برای کاربر {chat_id} تا {when} ثانیه دیگر تنظیم شد.")

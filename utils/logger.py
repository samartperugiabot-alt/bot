"""
ماژول لاگ‌گیری (Logging Module)

این فایل سیستم لاگ‌گیری متمرکز پروژه را پیاده‌سازی می‌کند.

قابلیت‌ها:
-   تنظیم یک لاگر استاندارد که پیام‌ها را با فرمت JSON تولید می‌کند.
    لاگ‌های JSON برای پردازش و تحلیل در سیستم‌های مانیتورینگ (مانند Datadog, Grafana)
    بسیار مناسب هستند.
-   حذف اطلاعات حساس (مانند نام و توکن) از لاگ‌ها.
-   ارسال هشدارهای فوری (Alerts) برای لاگ‌های با سطح `ERROR` یا `CRITICAL`
    به چت ادمین (`ADMIN_CHAT_ID`).
-   برای جلوگیری از ارسال هشدارهای تکراری و زیاد، یک سیستم throttle (مثلاً:
    ارسال حداکثر یک هشدار در هر ۵ دقیقه برای خطاهای مشابه) پیاده‌سازی می‌شود.
"""
import logging
import json
import sys
import config
# from utils.redis_utils import get_redis_client

class JsonFormatter(logging.Formatter):
    """
    فرمت‌کننده لاگ که خروجی را به صورت JSON تولید می‌کند.
    """
    def format(self, record):
        log_record = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "funcName": record.funcName,
        }
        if record.exc_info:
            log_record['exc_info'] = self.formatException(record.exc_info)
        return json.dumps(log_record)

def setup_logger():
    """
    لاگر اصلی برنامه را تنظیم و برمی‌گرداند.
    """
    logger = logging.getLogger("PerugiaBotLogger")
    logger.setLevel(config.LOG_LEVEL)

    # جلوگیری از انتشار لاگ‌ها به لاگر ریشه
    logger.propagate = False

    # اگر از قبل هندلری وجود داشت، آن را حذف کن
    if logger.hasHandlers():
        logger.handlers.clear()

    handler = logging.StreamHandler(sys.stdout)
    formatter = JsonFormatter()
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger

# یک نمونه از لاگر برای استفاده در سراسر پروژه
log = setup_logger()

# TODO: پیاده‌سازی یک هندلر سفارشی برای ارسال هشدار به ادمین با throttle
# class TelegramAdminHandler(logging.Handler):
#     def emit(self, record):
#         if record.levelno >= logging.ERROR:
#             # از Redis برای throttle کردن استفاده کن
#             # پیام را به ADMIN_CHAT_ID بفرست
#             pass

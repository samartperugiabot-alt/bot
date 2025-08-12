"""
ماژول مدیریت ردیس (Redis Utilities)

این فایل ابزارهایی برای تعامل با سرور Redis (مانند Upstash) فراهم می‌کند.
Redis در این پروژه برای موارد زیر استفاده می‌شود:
1.  **کش (Caching):** ذخیره موقت داده‌هایی که به کندی تغییر می‌کنند (مانند
    محتوای JSONها از GitHub، نتایج API آب و هوا) برای کاهش درخواست‌های تکراری
    و افزایش سرعت پاسخ‌دهی ربات.
2.  **محدودسازی نرخ (Rate Limiting):** جلوگیری از ارسال درخواست‌های بیش از حد
    توسط یک کاربر در یک بازه زمانی مشخص برای محافظت از ربات در برابر اسپم و حملات.
3.  **صف (Queueing):** مدیریت وظایف زمان‌بندی‌شده (مانند ارسال یادآوری) با
    استفاده از ساختار داده Sorted Set در Redis.

کلاس `RedisClient`:
-   یک کلاینت Redis را با استفاده از URL موجود در `config.py` مقداردهی اولیه می‌کند.
-   متدهایی برای عملیات رایج Redis مانند set, get, delete و ... فراهم می‌کند.
"""
import redis
import config
from typing import Optional, Any
import json

class RedisClient:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RedisClient, cls).__new__(cls)
            try:
                # اتصال به Redis با استفاده از URL
                cls._instance.r = redis.from_url(config.REDIS_URL, decode_responses=True)
                # بررسی اتصال
                cls._instance.r.ping()
                print("✅ اتصال به Redis با موفقیت برقرار شد.")
            except redis.exceptions.ConnectionError as e:
                print(f"❌ خطای اتصال به Redis: {e}")
                cls._instance = None
                raise e
        return cls._instance

    def get_client(self):
        """کلاینت اصلی redis را برمی‌گرداند."""
        return self.r

    # --- Caching Methods ---

    def set_cache(self, key: str, value: Any, ttl: int = 3600):
        """
        یک مقدار را در کش Redis ذخیره می‌کند. مقدار به صورت JSON سریالایز می‌شود.

        Args:
            key (str): کلید کش.
            value (Any): مقداری که باید ذخیره شود.
            ttl (int): زمان انقضا به ثانیه (Time To Live). پیش‌فرض یک ساعت.
        """
        try:
            serialized_value = json.dumps(value)
            self.r.setex(name=key, time=ttl, value=serialized_value)
        except TypeError as e:
            print(f"خطا در سریالایز کردن مقدار برای کلید '{key}': {e}")


    def get_cache(self, key: str) -> Optional[Any]:
        """
        یک مقدار را از کش Redis می‌خواند. مقدار از JSON دی‌سریالایز می‌شود.
        """
        cached_value = self.r.get(key)
        if cached_value:
            return json.loads(cached_value)
        return None

    def delete_cache(self, key: str):
        """یک کلید را از کش حذف می‌کند."""
        self.r.delete(key)

    # --- Rate Limiting Method ---

    def check_rate_limit(self, user_id: int) -> bool:
        """
        بررسی می‌کند که آیا کاربر از محدودیت نرخ درخواست عبور کرده است یا خیر.
        از الگوریتم Fixed Window Counter استفاده می‌کند.

        Returns:
            True اگر کاربر محدود شده باشد، در غیر این صورت False.
        """
        # TODO: پیاده‌سازی واقعی
        # 1. یک کلید منحصر به فرد برای کاربر بساز (مثلاً `rate_limit:{user_id}`).
        # 2. با استفاده از INCR، شمارنده را افزایش بده.
        # 3. اگر شمارنده 1 بود، EXPIRE را برای کلید تنظیم کن.
        # 4. اگر شمارنده از `config.RATE_LIMIT_REQUESTS` بیشتر بود، True برگردان.

        key = f"rate_limit:{user_id}"
        count = self.r.incr(key)
        if count == 1:
            self.r.expire(key, config.RATE_LIMIT_WINDOW)

        return count > config.RATE_LIMIT_REQUESTS

# ایجاد یک نمونه Singleton
try:
    redis_client_instance = RedisClient()
except Exception:
    redis_client_instance = None

def get_redis_client():
    """این تابع یک نمونه از کلاینت Redis را برمی‌گرداند."""
    if not redis_client_instance:
        raise ConnectionError("اتصال به Redis برقرار نیست.")
    return redis_client_instance

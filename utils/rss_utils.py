"""
ماژول ابزارهای کمکی برای خواندن فیدهای RSS

این فایل توابعی برای دریافت و تجزیه (parse) فیدهای خبری RSS از منابع
مختلف (مانند وب‌سایت دانشگاه‌ها یا خبرگزاری‌ها) فراهم می‌کند.

قابلیت‌ها:
-   `fetch_feed`: یک URL فید RSS دریافت کرده و لیستی از آخرین آیتم‌ها
    (عنوان، لینک، توضیحات) را برمی‌گرداند.
-   از کتابخانه `feedparser` برای تجزیه فید استفاده می‌شود.
-   نتایج برای جلوگیری از درخواست‌های مکرر، در Redis کش می‌شوند.
"""
import feedparser
# from utils.redis_utils import get_redis_client

def fetch_feed(feed_url: str, limit: int = 5):
    """
    آخرین آیتم‌ها را از یک فید RSS دریافت می‌کند.
    """
    # TODO: پیاده‌سازی کامل با کش Redis
    # redis = get_redis_client()
    # cached_feed = redis.get_cache(f"rss:{feed_url}")
    # if cached_feed:
    #     return cached_feed

    try:
        feed = feedparser.parse(feed_url)
        entries = []
        for entry in feed.entries[:limit]:
            entries.append({
                "title": entry.title,
                "link": entry.link,
                "summary": entry.summary,
                "published": entry.published
            })
        # redis.set_cache(f"rss:{feed_url}", entries, ttl=900) # کش برای ۱۵ دقیقه
        return entries
    except Exception as e:
        print(f"خطا در دریافت فید RSS از {feed_url}: {e}")
        return []

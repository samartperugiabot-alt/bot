"""
ماژول تبدیل ارز (Foreign Exchange - FX)

این فایل توابعی برای دریافت نرخ تبدیل ارزهای مختلف فراهم می‌کند.

روش کار:
-   از یک API رایگان مانند ExchangeRate-API یا FreeCurrencyAPI استفاده می‌کند.
-   کلید API از `config.EXCHANGE_RATE_API_KEY` خوانده می‌شود.
-   یک تابع `get_exchange_rate(base_currency, target_currency)` نرخ تبدیل
    را برمی‌گرداند.
-   نتایج برای کاهش هزینه‌ها و درخواست‌های API، در Redis با TTL مناسب (مثلاً چند ساعت)
    کش می‌شوند.
"""
import requests
import config
# from utils.redis_utils import get_redis_client

def get_exchange_rate(base: str = 'EUR', target: str = 'USD') -> float:
    """
    نرخ تبدیل یک ارز به ارز دیگر را برمی‌گرداند.
    """
    # TODO: پیاده‌سازی کامل با کش Redis
    # redis = get_redis_client()
    # cache_key = f"fx:{base}:{target}"
    # cached_rate = redis.get_cache(cache_key)
    # if cached_rate:
    #     return cached_rate

    api_key = config.EXCHANGE_RATE_API_KEY
    url = f"https://v6.exchangerate-api.com/v6/{api_key}/latest/{base}"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        rate = data['conversion_rates'].get(target)
        if rate:
            # redis.set_cache(cache_key, rate, ttl=3600 * 4) # کش برای ۴ ساعت
            return float(rate)
        return 0.0
    except requests.exceptions.RequestException as e:
        print(f"خطا در دریافت نرخ ارز: {e}")
        return 0.0

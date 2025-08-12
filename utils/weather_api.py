"""
ماژول API آب و هوا (Weather API) - نسخه کامل با کش

این فایل یک لایه انتزاعی برای تعامل با سرویس‌دهنده اطلاعات آب و هوا
(مانند OpenWeatherMap) فراهم می‌کند و نتایج را در Redis کش می‌کند.
"""
import requests
import config
from utils.redis_utils import get_redis_client
from utils.logger import log

def get_weather(city: str = "Perugia", lang: str = "fa"):
    """
    اطلاعات آب و هوای یک شهر را از OpenWeatherMap API دریافت می‌کند.
    ابتدا در کش Redis جستجو می‌کند، اگر نبود به API درخواست می‌زند.
    """
    try:
        redis = get_redis_client()
        cache_key = f"weather:{city.lower()}:{lang}"

        # ۱. جستجو در کش
        cached_weather = redis.get_cache(cache_key)
        if cached_weather:
            log.info(f"اطلاعات آب و هوای '{city}' از کش خوانده شد.")
            return cached_weather
    except ConnectionError as e:
        log.error(f"خطای اتصال به Redis در get_weather: {e}")
        redis = None # ادامه بدون کش

    # ۲. در صورت نبودن در کش، درخواست به API
    log.info(f"درخواست به API آب و هوا برای شهر '{city}'.")
    api_key = config.OWM_API_KEY
    if not api_key:
        log.error("کلید API برای OpenWeatherMap (OWM_API_KEY) تنظیم نشده است.")
        return None

    lang_map = {'fa': 'fa', 'en': 'en', 'it': 'it'}
    api_lang = lang_map.get(lang, 'en')

    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric&lang={api_lang}"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        weather_info = {
            "city": data["name"],
            "temp": data["main"]["temp"],
            "feels_like": data["main"]["feels_like"],
            "description": data["weather"][0]["description"],
            "icon": data["weather"][0]["icon"]
        }

        # ۳. ذخیره نتیجه در کش
        if redis:
            redis.set_cache(cache_key, weather_info, ttl=1800) # کش برای ۳۰ دقیقه
            log.info(f"اطلاعات آب و هوای '{city}' در کش ذخیره شد.")

        return weather_info
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            log.warning(f"شهر '{city}' در API آب و هوا یافت نشد.")
        else:
            log.error(f"خطای HTTP در دریافت اطلاعات آب و هوا برای '{city}': {e}")
        return None
    except requests.exceptions.RequestException as e:
        log.error(f"خطای شبکه در دریافت اطلاعات آب و هوا برای '{city}': {e}")
        return None

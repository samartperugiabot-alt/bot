"""
ماژول ذخیره‌سازی اخبار (News Storage) - نسخه کامل

این فایل یک لایه انتزاعی برای ذخیره و بازیابی اخبار فراهم می‌کند.
"""
import json
from typing import List, Dict, Any
from utils.logger import log

class BaseNewsStore:
    """کلاس پایه برای انواع روش‌های ذخیره‌سازی اخبار."""
    def get_latest_news(self, count: int) -> List[Dict[str, Any]]:
        raise NotImplementedError

    def add_news(self, news_item: Dict[str, Any]) -> bool:
        raise NotImplementedError

class JsonNewsStore(BaseNewsStore):
    """اخبار را در یک فایل JSON محلی ذخیره و بازیابی می‌کند."""
    def __init__(self, json_path="data/news.json"):
        self.path = json_path
        self.data = self._load_data()

    def _load_data(self) -> Dict[str, Any]:
        """داده‌ها را از فایل JSON بارگذاری می‌کند."""
        try:
            with open(self.path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            log.warning(f"فایل اخبار در {self.path} یافت نشد یا خالی است. یک فایل جدید ایجاد می‌شود.")
            return {"metadata": {"version": "1.0"}, "news": []}

    def _save_data(self):
        """داده‌ها را در فایل JSON ذخیره می‌کند."""
        try:
            with open(self.path, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
        except IOError as e:
            log.error(f"خطا در نوشتن فایل اخبار در {self.path}: {e}")

    def get_latest_news(self, count: int) -> List[Dict[str, Any]]:
        """آخرین اخبار را بر اساس timestamp برمی‌گرداند."""
        try:
            # مرتب‌سازی اخبار بر اساس تاریخ (جدیدترین اول)
            sorted_news = sorted(self.data.get("news", []), key=lambda x: x['timestamp'], reverse=True)
            return sorted_news[:count]
        except Exception as e:
            log.error(f"خطا در مرتب‌سازی یا خواندن اخبار: {e}")
            return []

    def add_news(self, news_item: Dict[str, Any]) -> bool:
        """یک خبر جدید اضافه کرده و فایل را ذخیره می‌کند."""
        try:
            self.data.get("news", []).append(news_item)
            self._save_data()
            log.info(f"خبر جدید با شناسه '{news_item.get('id')}' با موفقیت اضافه شد.")
            return True
        except Exception as e:
            log.error(f"خطا در افزودن خبر جدید: {e}")
            return False

# --- Factory Function ---
def get_news_store() -> BaseNewsStore:
    """
    بر اساس تنظیمات پروژه، یک نمونه از کلاس ذخیره‌سازی اخبار را برمی‌گرداند.
    در حال حاضر فقط JsonNewsStore پیاده‌سازی شده است.
    """
    # TODO: در آینده می‌توان بر اساس یک متغیر در config، نوع store را انتخاب کرد.
    return JsonNewsStore()

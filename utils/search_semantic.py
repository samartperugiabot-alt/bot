"""
ماژول جستجوی معنایی (Semantic Search)

این فایل قابلیت جستجوی معنایی را با استفاده از مدل‌های زبان طبیعی فراهم می‌کند.
این یک قابلیت اختیاری و پیشرفته برای بهبود تجربه کاربری در جستجو و FAQ است.

روش کار:
-   از API سرویس Hugging Face Inference استفاده می‌شود.
-   یک مدل Sentence Transformer (مانند `paraphrase-multilingual-MiniLM-L12-v2`)
    برای تبدیل سؤال کاربر و متون موجود (مثلاً سؤالات FAQ) به بردار عددی (embedding)
    استفاده می‌شود.
-   با محاسبه شباهت کسینوسی (Cosine Similarity) بین بردار سؤال کاربر و بردارهای
    متون، نزدیک‌ترین و مرتبط‌ترین پاسخ پیدا می‌شود.
-   در صورت عدم دسترسی به API یا نبود کلید، سیستم به یک جستجوی ساده مبتنی بر
    تطبیق کلمات کلیدی (keyword matching) بازگشت (fallback) می‌کند.
"""
import requests
import config

API_URL = "https://api-inference.huggingface.co/models/sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
headers = {"Authorization": f"Bearer {config.HUGGINGFACE_API_KEY}"}

def semantic_search(query: str, documents: list[str]) -> list[float]:
    """
    امتیاز شباهت معنایی یک کوئری را با لیستی از اسناد محاسبه می‌کند.
    """
    if not config.HUGGINGFACE_API_KEY:
        # Fallback to simple keyword matching
        scores = [1.0 if query.lower() in doc.lower() else 0.0 for doc in documents]
        return scores

    try:
        response = requests.post(API_URL, headers=headers, json={
            "inputs": {
                "source_sentence": query,
                "sentences": documents
            }
        }, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"خطا در ارتباط با Hugging Face API: {e}")
        # Fallback
        scores = [1.0 if query.lower() in doc.lower() else 0.0 for doc in documents]
        return scores

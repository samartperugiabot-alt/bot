"""
ماژول ابزارهای کمکی عمومی (Common Utilities)

این فایل شامل توابع کمکی است که در سراسر پروژه به طور مکرر استفاده می‌شوند.
هدف از این ماژول، کاهش تکرار کد و ایجاد یک مجموعه ابزار استاندارد برای وظایف
رایج مانند اعتبارسنجی ورودی، پاک‌سازی متن و ساخت منوهای دکمه‌ای است.

توابع کلیدی:
- validate_email: بررسی صحت فرمت ایمیل.
- validate_age: بررسی محدوده مجاز سن.
- sanitize_markdown: پاک‌سازی متن برای جلوگیری از Markdown Injection.
- build_menu: ساخت منوهای دکمه‌ای از لیست.
"""
import re
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from typing import List

# --- Validators (اعتبارسنج‌ها) ---

def validate_email(email: str) -> bool:
    """
    بررسی می‌کند که آیا رشته ورودی یک فرمت ایمیل معتبر دارد یا خیر.
    این یک اعتبارسنجی ساده بر اساس regex است.
    """
    # الگوی Regex برای اعتبارسنجی ایمیل
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return re.match(pattern, email) is not None

def validate_age(age_str: str) -> bool:
    """
    بررسی می‌کند که آیا سن وارد شده یک عدد در محدوده مجاز (16-100) است یا خیر.
    """
    try:
        age = int(age_str)
        return 16 <= age <= 100
    except (ValueError, TypeError):
        return False

# --- Sanitizers (پاک‌کننده‌ها) ---

def sanitize_markdown(text: str) -> str:
    """
    کاراکترهای خاص Markdown V2 را از متن حذف (escape) می‌کند تا از خطاهای
    پارس تلگرام و حملات Markdown Injection جلوگیری شود.
    """
    escape_chars = r"[_*\[\]()~`>#+-=|{}.!]"
    return re.sub(f"({escape_chars})", r"\\\1", text)

# --- UI Helpers (ابزارهای رابط کاربری) ---

def build_menu(buttons: List[InlineKeyboardButton], n_cols: int) -> InlineKeyboardMarkup:
    """
    یک لیست از دکمه‌های InlineKeyboardButton را به یک ساختار ماتریسی برای نمایش
    در منو تبدیل می‌کند.

    Args:
        buttons (List[InlineKeyboardButton]): لیست دکمه‌ها.
        n_cols (int): تعداد ستون‌های مورد نظر برای منو.

    Returns:
        InlineKeyboardMarkup: کیبورد آماده برای ارسال در پیام.
    """
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    return InlineKeyboardMarkup(menu)

# --- ISEE Calculator Helpers ---

def get_family_coefficient(family_members: int) -> float:
    """
    ضریب مقیاس مربوط به تعداد اعضای خانواده را برای محاسبه ISEE برمی‌گرداند.
    این ضرایب بر اساس قوانین رسمی ایتالیا هستند.
    """
    coeffs = {
        1: 1.00,
        2: 1.57,
        3: 2.04,
        4: 2.46,
        5: 2.85,
    }
    if family_members in coeffs:
        return coeffs[family_members]
    elif family_members > 5:
        return 2.85 + (0.35 * (family_members - 5))
    else:
        return 1.00 # برای حالت‌های غیرمنتظره

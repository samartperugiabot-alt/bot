"""
ماژول مدیریت گوگل شیت (Google Sheets Module)

این فایل مسئولیت تمام تعاملات با Google Sheets را بر عهده دارد. از Google Sheets
به عنوان یک پایگاه داده ساده برای ذخیره اطلاعات کاربران، پروفایل‌ها، لاگ‌ها و ...
استفاده می‌شود.

کلاس `GSheetsDB`:
-   ارتباط با Google Sheets API را با استفاده از `gspread` و اعتبارنامه‌های
    موجود در `config.py` برقرار می‌کند.
-   متدهایی برای انجام عملیات CRUD (Create, Read, Update, Delete) روی شیت‌های
    مختلف فراهم می‌کند.
-   این کلاس به صورت Singleton پیاده‌سازی می‌شود تا از اتصالات متعدد جلوگیری شود.

نکات پیاده‌سازی:
-   در پیاده‌سازی واقعی، باید مدیریت خطا (exception handling) برای مشکلات شبکه
    یا دسترسی به API در نظر گرفته شود.
-   برای بهبود عملکرد، نتایج می‌تواند در Redis کش شود.
"""
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import config
from typing import Dict, Any, Optional, List

# تعریف محدوده‌های دسترسی (scopes) برای Google Sheets و Google Drive
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

class GSheetsDB:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GSheetsDB, cls).__new__(cls)
            try:
                # --- احراز هویت ---
                # استفاده از اعتبارنامه‌های سرویس اکانت که از config خوانده شده
                creds = ServiceAccountCredentials.from_json_keyfile_dict(config.GOOGLE_CREDS, SCOPES)
                client = gspread.authorize(creds)

                # --- باز کردن اسپردشیت اصلی ---
                cls._instance.spreadsheet = client.open(config.SPREADSHEET_NAME)
                print("✅ اتصال به Google Sheets با موفقیت برقرار شد.")

            except Exception as e:
                print(f"❌ خطای اتصال به Google Sheets: {e}")
                # در محیط پروداکشن، این خطا باید به ادمین اطلاع داده شود
                cls._instance = None
                raise e
        return cls._instance

    def _get_worksheet(self, sheet_name: str):
        """یک شیت را با نام آن باز می‌کند. در صورت عدم وجود، آن را ایجاد می‌کند."""
        try:
            return self.spreadsheet.worksheet(sheet_name)
        except gspread.WorksheetNotFound:
            return self.spreadsheet.add_worksheet(title=sheet_name, rows="100", cols="20")

    # --- متدهای نمونه برای مدیریت کاربران (شیت 'users') ---

    def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        اطلاعات یک کاربر را بر اساس شناسه تلگرام او از شیت 'users' می‌خواند.

        Returns:
            یک دیکشنری از اطلاعات کاربر یا None اگر پیدا نشود.
        """
        # TODO: پیاده‌سازی واقعی
        # 1. شیت 'users' را باز کن.
        # 2. به دنبال user_id در ستون اول بگرد.
        # 3. اگر پیدا شد، ردیف را به صورت دیکشنری برگردان.
        # 4. اگر پیدا نشد، None برگردان.
        print(f"[GSHEETS_STUB] جستجو برای کاربر با شناسه: {user_id}")
        # Stub:
        # users_sheet = self._get_worksheet("users")
        # user_row = users_sheet.find(str(user_id))
        # if user_row:
        #     return users_sheet.get_all_records()[user_row.row - 1]
        return None # برای اینکه گیت ثبت‌نام همیشه کار کند

    def save_user(self, user_data: Dict[str, Any]) -> bool:
        """
        اطلاعات یک کاربر جدید یا آپدیت شده را در شیت 'users' ذخیره می‌کند.
        """
        # TODO: پیاده‌سازی واقعی
        # 1. شیت 'users' را باز کن.
        # 2. بررسی کن آیا کاربر از قبل وجود دارد یا نه.
        # 3. اگر وجود داشت، ردیف او را آپدیت کن.
        # 4. اگر وجود نداشت، یک ردیف جدید اضافه کن.
        print(f"[GSHEETS_STUB] ذخیره اطلاعات کاربر: {user_data['user_id']}")
        # Stub:
        # users_sheet = self._get_worksheet("users")
        # headers = users_sheet.row_values(1)
        # new_row = [user_data.get(h) for h in headers]
        # users_sheet.append_row(new_row)
        return True

    def get_all_records(self, sheet_name: str) -> List[Dict[str, Any]]:
        """
        تمام رکوردهای یک شیت را به صورت لیستی از دیکشنری‌ها برمی‌گرداند.
        """
        # TODO: پیاده‌سازی واقعی با کش در Redis
        print(f"[GSHEETS_STUB] خواندن تمام رکوردها از شیت: {sheet_name}")
        # Stub:
        # work_sheet = self._get_worksheet(sheet_name)
        # return work_sheet.get_all_records()
        return []

# ایجاد یک نمونه Singleton برای استفاده در سراسر برنامه
# اگر اتصال اولیه ناموفق باشد، این مقدار None خواهد بود.
try:
    db_instance = GSheetsDB()
except Exception:
    db_instance = None

def get_db():
    """این تابع یک نمونه از پایگاه داده شیت را برمی‌گرداند."""
    if not db_instance:
        raise ConnectionError("اتصال به Google Sheets برقرار نیست.")
    return db_instance

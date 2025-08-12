"""
ماژول مدیریت گوگل شیت (Google Sheets Module) - نسخه کامل

این فایل مسئولیت تمام تعاملات با Google Sheets را بر عهده دارد.
"""
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import config
from typing import Dict, Any, Optional, List
from utils.logger import log

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

class GSheetsDB:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'spreadsheet'): # جلوگیری از مقداردهی مجدد
            try:
                creds = ServiceAccountCredentials.from_json_keyfile_dict(config.GOOGLE_CREDS, SCOPES)
                client = gspread.authorize(creds)
                self.spreadsheet = client.open(config.SPREADSHEET_NAME)
                log.info("✅ اتصال به Google Sheets با موفقیت برقرار شد.")
            except gspread.exceptions.SpreadsheetNotFound:
                log.error(f"اسپردشیت با نام '{config.SPREADSHEET_NAME}' یافت نشد.")
                raise
            except Exception as e:
                log.error(f"❌ خطای ناشناخته در اتصال به Google Sheets: {e}")
                raise ConnectionError(f"خطای اتصال به Google Sheets: {e}")

    def _get_worksheet(self, sheet_name: str) -> gspread.Worksheet:
        """یک شیت را با نام آن باز می‌کند. در صورت عدم وجود، آن را ایجاد می‌کند."""
        try:
            return self.spreadsheet.worksheet(sheet_name)
        except gspread.WorksheetNotFound:
            log.warning(f"شیت '{sheet_name}' یافت نشد، در حال ایجاد شیت جدید...")
            return self.spreadsheet.add_worksheet(title=sheet_name, rows=100, cols=20)
        except Exception as e:
            log.error(f"خطا در دریافت شیت '{sheet_name}': {e}")
            raise

    def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """اطلاعات یک کاربر را بر اساس شناسه تلگرام او از شیت 'users' می‌خواند."""
        try:
            users_sheet = self._get_worksheet("users")
            user_row = users_sheet.find(str(user_id), in_column=1)
            if user_row:
                headers = users_sheet.row_values(1)
                values = users_sheet.row_values(user_row.row)
                return dict(zip(headers, values))
            return None
        except gspread.exceptions.GSpreadException as e:
            log.error(f"خطای GSpread در get_user برای user_id {user_id}: {e}")
            return None

    def save_user(self, user_data: Dict[str, Any]) -> bool:
        """اطلاعات یک کاربر جدید یا آپدیت شده را در شیت 'users' ذخیره می‌کند."""
        try:
            users_sheet = self._get_worksheet("users")
            headers = users_sheet.row_values(1)
            if not headers:
                headers = list(user_data.keys())
                users_sheet.append_row(headers, value_input_option='USER_ENTERED')

            user_id_str = str(user_data.get("user_id"))
            cell = users_sheet.find(user_id_str, in_column=1)

            # مرتب کردن داده‌ها بر اساس هدر
            row_values = [user_data.get(h, "") for h in headers]

            if cell:
                users_sheet.update(f'A{cell.row}', [row_values])
                log.info(f"اطلاعات کاربر {user_id_str} به‌روزرسانی شد.")
            else:
                users_sheet.append_row(row_values, value_input_option='USER_ENTERED')
                log.info(f"کاربر جدید {user_id_str} به شیت اضافه شد.")
            return True
        except gspread.exceptions.GSpreadException as e:
            log.error(f"خطای GSpread در save_user: {e}")
            return False

    def delete_user(self, user_id: int) -> bool:
        """یک کاربر را از شیت 'users' حذف می‌کند."""
        try:
            users_sheet = self._get_worksheet("users")
            cell = users_sheet.find(str(user_id), in_column=1)
            if cell:
                users_sheet.delete_rows(cell.row)
                log.info(f"کاربر {user_id} با موفقیت حذف شد.")
                return True
            log.warning(f"کاربر {user_id} برای حذف یافت نشد.")
            return False
        except gspread.exceptions.GSpreadException as e:
            log.error(f"خطای GSpread در delete_user برای user_id {user_id}: {e}")
            return False

    def get_all_records(self, sheet_name: str) -> List[Dict[str, Any]]:
        """تمام رکوردهای یک شیت را به صورت لیستی از دیکشنری‌ها برمی‌گرداند."""
        try:
            work_sheet = self._get_worksheet(sheet_name)
            return work_sheet.get_all_records()
        except gspread.exceptions.GSpreadException as e:
            log.error(f"خطای GSpread در get_all_records برای شیت '{sheet_name}': {e}")
            return []

try:
    db_instance = GSheetsDB()
except Exception as e:
    log.critical(f"راه‌اندازی اولیه GSheetsDB ناموفق بود: {e}")
    db_instance = None

def get_db() -> Optional[GSheetsDB]:
    """این تابع یک نمونه از پایگاه داده شیت را برمی‌گرداند."""
    if not db_instance:
        log.error("نمونه GSheetsDB در دسترس نیست.")
        return None
    return db_instance

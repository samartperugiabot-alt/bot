"""
ماژول مدیریت گوگل درایو (Google Drive Module)

این فایل مسئولیت تعامل با Google Drive API را برای آپلود فایل‌ها (مانند رزومه،
مدارک و فایل‌های تولید شده توسط ربات) بر عهده دارد.

کلاس `GDriveUploader`:
-   از همان اعتبارنامه‌های سرویس اکانت (`config.GOOGLE_CREDS`) که برای Google Sheets
    استفاده می‌شود، برای احراز هویت در Google Drive API بهره می‌برد.
-   یک متد اصلی `upload_file` دارد که یک فایل را از سیستم محلی دریافت کرده و
    در فولدر مشخص شده در `config.GOOGLE_DRIVE_UPLOAD_FOLDER_ID` آپلود می‌کند.

نکات پیاده‌سازی:
-   باید نوع فایل (MIME type) بررسی شود تا از آپلود فایل‌های مخرب جلوگیری شود.
-   برای فایل‌های بزرگ، باید از آپلود چندبخشی (multipart upload) استفاده شود.
-   لینک قابل اشتراک‌گذاری فایل آپلود شده باید برگردانده شود تا در Google Sheets
    ذخیره شود.
"""
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from oauth2client.service_account import ServiceAccountCredentials
import config
from typing import Optional

# همان scopes که در gsheets.py تعریف شد، برای Drive نیز کافی است.
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

class GDriveUploader:
    _instance = None
    _service = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GDriveUploader, cls).__new__(cls)
            try:
                # --- احراز هویت ---
                creds = ServiceAccountCredentials.from_json_keyfile_dict(config.GOOGLE_CREDS, SCOPES)
                # ساخت سرویس Drive API
                cls._instance._service = build('drive', 'v3', credentials=creds)
                print("✅ اتصال به Google Drive با موفقیت برقرار شد.")
            except Exception as e:
                print(f"❌ خطای اتصال به Google Drive: {e}")
                cls._instance = None
                raise e
        return cls._instance

    def upload_file(self, local_filepath: str, remote_filename: str) -> Optional[str]:
        """
        یک فایل را در فولدر مشخص شده در Google Drive آپلود می‌کند.

        Args:
            local_filepath (str): مسیر فایل در سیستم محلی.
            remote_filename (str): نام فایلی که در Drive ذخیره خواهد شد.

        Returns:
            آدرس (ID) فایل آپلود شده در Drive یا None در صورت خطا.
        """
        # TODO: پیاده‌سازی واقعی
        # 1. نوع MIME فایل را مشخص کن.
        # 2. متادیتای فایل را بساز (نام فایل، فولدر والد).
        # 3. با استفاده از MediaFileUpload، فایل را آپلود کن.
        # 4. دسترسی فایل را به "anyone with link" تغییر بده (اختیاری).
        # 5. ID فایل آپلود شده را برگردان.

        print(f"[GDRIVE_STUB] آپلود فایل '{local_filepath}' با نام '{remote_filename}'")
        # Stub:
        # file_metadata = {
        #     'name': remote_filename,
        #     'parents': [config.GOOGLE_DRIVE_UPLOAD_FOLDER_ID]
        # }
        # media = MediaFileUpload(local_filepath, mimetype='application/pdf', resumable=True)
        # file = self._service.files().create(
        #     body=file_metadata,
        #     media_body=media,
        #     fields='id'
        # ).execute()
        # return file.get('id')

        # برای تست، یک ID ساختگی برمی‌گردانیم.
        return "stub_drive_file_id_12345"

# ایجاد یک نمونه Singleton
try:
    drive_uploader_instance = GDriveUploader()
except Exception:
    drive_uploader_instance = None

def get_drive_uploader():
    """این تابع یک نمونه از آپلودر درایو را برمی‌گرداند."""
    if not drive_uploader_instance:
        raise ConnectionError("اتصال به Google Drive برقرار نیست.")
    return drive_uploader_instance

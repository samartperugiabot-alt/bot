"""
ماژول مدیریت گوگل درایو (Google Drive Module) - نسخه کامل

این فایل مسئولیت تعامل با Google Drive API را برای آپلود فایل‌ها بر عهده دارد.
"""
import mimetypes
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from oauth2client.service_account import ServiceAccountCredentials
import config
from typing import Optional
from utils.logger import log

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

class GDriveUploader:
    _instance = None
    _service = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, '_service'):
            try:
                creds = ServiceAccountCredentials.from_json_keyfile_dict(config.GOOGLE_CREDS, SCOPES)
                self._service = build('drive', 'v3', credentials=creds)
                log.info("✅ اتصال به Google Drive با موفقیت برقرار شد.")
            except Exception as e:
                log.error(f"❌ خطای اتصال به Google Drive: {e}")
                self._service = None
                raise ConnectionError(f"خطای اتصال به Google Drive: {e}")

    def upload_file(self, local_filepath: str, remote_filename: str) -> Optional[str]:
        """
        یک فایل را در فولدر مشخص شده در Google Drive آپلود می‌کند.

        Args:
            local_filepath (str): مسیر فایل در سیستم محلی.
            remote_filename (str): نام فایلی که در Drive ذخیره خواهد شد.

        Returns:
            ID فایل آپلود شده در Drive یا None در صورت خطا.
        """
        if not self._service:
            log.error("سرویس Google Drive در دسترس نیست. آپلود لغو شد.")
            return None

        try:
            # تعیین نوع MIME فایل
            mimetype, _ = mimetypes.guess_type(local_filepath)
            if mimetype is None:
                mimetype = 'application/octet-stream' # نوع پیش‌فرض

            file_metadata = {
                'name': remote_filename,
                'parents': [config.GOOGLE_DRIVE_UPLOAD_FOLDER_ID]
            }

            media = MediaFileUpload(local_filepath, mimetype=mimetype, resumable=True)

            log.info(f"شروع آپلود فایل '{remote_filename}' به Google Drive...")

            file = self._service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()

            file_id = file.get('id')
            log.info(f"فایل با موفقیت آپلود شد. شناسه فایل: {file_id}")

            return file_id

        except FileNotFoundError:
            log.error(f"فایل محلی برای آپلود یافت نشد: {local_filepath}")
            return None
        except HttpError as error:
            log.error(f"خطای HTTP هنگام آپلود به Google Drive رخ داد: {error}")
            return None
        except Exception as e:
            log.error(f"خطای ناشناخته هنگام آپلود به Google Drive: {e}")
            return None

try:
    drive_uploader_instance = GDriveUploader()
except Exception as e:
    log.critical(f"راه‌اندازی اولیه GDriveUploader ناموفق بود: {e}")
    drive_uploader_instance = None

def get_drive_uploader() -> Optional[GDriveUploader]:
    """این تابع یک نمونه از آپلودر درایو را برمی‌گرداند."""
    if not drive_uploader_instance:
        log.error("نمونه GDriveUploader در دسترس نیست.")
        return None
    return drive_uploader_instance

import os
import shutil
from typing import Optional
from abc import ABC, abstractmethod
import boto3
from botocore.exceptions import NoCredentialsError
from backend.core.config import settings

class BaseStorage(ABC):
    @abstractmethod
    def save_file(self, file_obj, filename: str) -> str:
        pass

    @abstractmethod
    def get_url(self, filename: str) -> str:
        pass

class LocalStorage(BaseStorage):
    def __init__(self):
        self.upload_dir = settings.STORAGE_LOCAL_PATH
        os.makedirs(self.upload_dir, exist_ok=True)

    def save_file(self, file_obj, filename: str) -> str:
        file_path = os.path.join(self.upload_dir, filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file_obj, buffer)
        return filename # In local storage, we just store relative path or filename

    def get_url(self, filename: str) -> str:
        # Assuming frontend or nginx serves this folder
        return f"/uploads/{filename}"

class S3Storage(BaseStorage):
    def __init__(self):
        self.bucket = settings.S3_BUCKET
        self.s3 = boto3.client(
            's3',
            aws_access_key_id=settings.S3_ACCESS_KEY,
            aws_secret_access_key=settings.S3_SECRET_KEY,
            endpoint_url=settings.S3_ENDPOINT_URL, # For MinIO compatibility
            region_name=settings.S3_REGION
        )

    def save_file(self, file_obj, filename: str) -> str:
        try:
            self.s3.upload_fileobj(file_obj, self.bucket, filename)
            return filename
        except NoCredentialsError:
            raise Exception("S3 Credentials not available")

    def get_url(self, filename: str) -> str:
        # Generate presigned URL or public URL
        try:
            url = self.s3.generate_presigned_url('get_object',
                                                    Params={'Bucket': self.bucket,
                                                            'Key': filename},
                                                    ExpiresIn=3600)
            return url
        except Exception as e:
            return ""

def get_storage_service() -> BaseStorage:
    if settings.STORAGE_TYPE == "s3":
        return S3Storage()
    return LocalStorage()

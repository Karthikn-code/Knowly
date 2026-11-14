
import asyncio
import logging
import os
import uuid
from pathlib import Path

import boto3
from botocore.exceptions import BotoCoreError, ClientError

from app.core.config import settings


logger = logging.getLogger(__name__)


class DocumentStorageError(Exception):
    """Raised when a document storage operation fails."""


class DocumentStorage:
    """Private document storage supporting local filesystem and Tigris."""

    def __init__(self) -> None:
        self.provider = settings.DOCUMENT_STORAGE_PROVIDER.strip().lower()
        self.max_size = settings.MAX_UPLOAD_SIZE_BYTES

        self.storage_dir = settings.DOCUMENT_STORAGE_DIR.resolve()

        self.bucket_name = None
        self._s3_client = None

        if self.provider not in {"local", "tigris"}:
            raise DocumentStorageError(
                "Unsupported document storage provider."
            )

        # Tigris initialization is intentionally lazy.
        # Credentials are checked only when a Tigris operation is requested.

    def _initialize_tigris(self) -> None:
        """Initialize the S3-compatible Tigris client."""

        access_key = settings.TIGRIS_ACCESS_KEY_ID
        secret_key = settings.TIGRIS_SECRET_ACCESS_KEY
        bucket_name = settings.TIGRIS_BUCKET_NAME

        if not access_key or not secret_key or not bucket_name:
            raise DocumentStorageError(
                "Tigris storage configuration is incomplete."
            )

        self.bucket_name = bucket_name.strip()

        if not self.bucket_name:
            raise DocumentStorageError(
                "Tigris bucket name cannot be empty."
            )

        try:
            self._s3_client = boto3.client(
                "s3",
                endpoint_url=settings.TIGRIS_ENDPOINT_URL,
                aws_access_key_id=access_key.get_secret_value(),
                aws_secret_access_key=secret_key.get_secret_value(),
                region_name=settings.TIGRIS_REGION,
            )

        except Exception as exc:
            logger.exception("Failed to initialize Tigris storage client.")

            raise DocumentStorageError(
                "Unable to initialize Tigris storage."
            ) from exc

    def _get_s3_client(self):
        """Initialize the Tigris client only when first needed."""

        if self.provider != "tigris":
            raise DocumentStorageError(
                "Tigris client requested for a non-Tigris provider."
            )

        if self._s3_client is None:
            self._initialize_tigris()

        return self._s3_client

    def _resolve_path(self, storage_key: str) -> Path:
        """Resolve a UUID storage key without allowing path traversal."""

        try:
            key = uuid.UUID(storage_key)

        except (ValueError, TypeError, AttributeError) as exc:
            raise DocumentStorageError(
                "Invalid storage key."
            ) from exc

        path = (self.storage_dir / str(key)).resolve()

        if path.parent != self.storage_dir:
            raise DocumentStorageError(
                "Invalid storage path."
            )

        return path

    @staticmethod
    def _resolve_object_key(storage_key: str) -> str:
        """Convert a UUID storage key into a private object key."""

        try:
            key = uuid.UUID(storage_key)

        except (ValueError, TypeError, AttributeError) as exc:
            raise DocumentStorageError(
                "Invalid storage key."
            ) from exc

        return f"documents/{key}"

    async def save(self, file_content: bytes) -> tuple[str, int]:
        """Save a document using the configured storage provider."""

        if not isinstance(file_content, bytes):
            raise DocumentStorageError(
                "File content must be bytes."
            )

        file_size = len(file_content)

        if file_size == 0:
            raise DocumentStorageError(
                "Empty files are not allowed."
            )

        if file_size > self.max_size:
            raise DocumentStorageError(
                "File exceeds the 20 MB limit."
            )

        storage_key = str(uuid.uuid4())

        try:
            if self.provider == "local":
                destination = self._resolve_path(storage_key)

                await asyncio.to_thread(
                    self._write_file,
                    destination,
                    file_content,
                )

            else:
                object_key = self._resolve_object_key(storage_key)

                await asyncio.to_thread(
                    self._put_object,
                    object_key,
                    file_content,
                )

        except Exception as exc:
            logger.exception(
                "Failed to save document using %s storage.",
                self.provider,
            )

            raise DocumentStorageError(
                "Unable to save the uploaded document."
            ) from exc

        return storage_key, file_size

    @staticmethod
    def _write_file(destination: Path, content: bytes) -> None:
        """Create a private local file without overwriting existing files."""

        destination.parent.mkdir(
            parents=True,
            exist_ok=True,
            mode=0o700,
        )

        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL

        if hasattr(os, "O_BINARY"):
            flags |= os.O_BINARY

        descriptor = os.open(destination, flags, 0o600)

        try:
            with os.fdopen(descriptor, "wb") as file:
                descriptor = -1
                file.write(content)

        finally:
            if descriptor != -1:
                os.close(descriptor)

    def _put_object(self, object_key: str, content: bytes) -> None:
        """Upload a private object to Tigris."""

        self._get_s3_client().put_object(
            Bucket=self.bucket_name,
            Key=object_key,
            Body=content,
            ContentLength=len(content),
            ContentType="application/octet-stream",
        )

    async def read(self, storage_key: str) -> bytes:
        """Read a document from the configured storage provider."""

        try:
            if self.provider == "local":
                path = self._resolve_path(storage_key)

                return await asyncio.to_thread(
                    path.read_bytes
                )

            object_key = self._resolve_object_key(storage_key)

            return await asyncio.to_thread(
                self._read_object,
                object_key,
            )

        except FileNotFoundError as exc:
            raise DocumentStorageError(
                "Stored document was not found."
            ) from exc

        except ClientError as exc:
            error_code = (
                exc.response.get("Error", {}).get("Code", "")
            )

            if error_code in {"NoSuchKey", "NotFound", "404"}:
                raise DocumentStorageError(
                    "Stored document was not found."
                ) from exc

            logger.exception(
                "Failed to read document from Tigris."
            )

            raise DocumentStorageError(
                "Unable to read the stored document."
            ) from exc

        except (BotoCoreError, OSError) as exc:
            logger.exception(
                "Failed to read document using %s storage.",
                self.provider,
            )

            raise DocumentStorageError(
                "Unable to read the stored document."
            ) from exc

        except Exception as exc:
            logger.exception(
                "Unexpected error while reading document using %s storage.",
                self.provider,
            )

            raise DocumentStorageError(
                "Unable to read the stored document."
            ) from exc

    def _read_object(self, object_key: str) -> bytes:
        """Download an object from Tigris."""

        response = self._get_s3_client().get_object(
            Bucket=self.bucket_name,
            Key=object_key,
        )

        body = response["Body"]

        try:
            return body.read()

        finally:
            body.close()

    async def delete(self, storage_key: str) -> None:
        """Delete a document from the configured storage provider."""

        try:
            if self.provider == "local":
                path = self._resolve_path(storage_key)

                await asyncio.to_thread(
                    path.unlink,
                    missing_ok=True,
                )

            else:
                object_key = self._resolve_object_key(storage_key)

                await asyncio.to_thread(
                    self._delete_object,
                    object_key,
                )

        except Exception as exc:
            logger.exception(
                "Failed to delete document using %s storage.",
                self.provider,
            )

            raise DocumentStorageError(
                "Unable to delete the stored document."
            ) from exc

    def _delete_object(self, object_key: str) -> None:
        """Delete an object from Tigris."""

        self._get_s3_client().delete_object(
            Bucket=self.bucket_name,
            Key=object_key,
        )


# Create the storage service without initializing cloud credentials.
document_storage = DocumentStorage()

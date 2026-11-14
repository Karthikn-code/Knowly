
import asyncio
import os
import uuid
from pathlib import Path

from app.core.config import settings


class DocumentStorageError(Exception):
    """Raised when a document storage operation fails."""


class DocumentStorage:
    """Private filesystem storage for user-uploaded documents."""

    def __init__(self) -> None:
        self.storage_dir = settings.DOCUMENT_STORAGE_DIR.resolve()
        self.max_size = settings.MAX_UPLOAD_SIZE_BYTES

    def _resolve_path(self, storage_key: str) -> Path:
        """Resolve a storage key without allowing path traversal."""

        try:
            key = uuid.UUID(storage_key)
        except (ValueError, TypeError, AttributeError) as exc:
            raise DocumentStorageError("Invalid storage key.") from exc

        path = (self.storage_dir / str(key)).resolve()

        if path.parent != self.storage_dir:
            raise DocumentStorageError("Invalid storage path.")

        return path

    async def save(
        self,
        file_content: bytes,
    ) -> tuple[str, int]:
        """Save file bytes under a random UUID filename."""

        if not isinstance(file_content, bytes):
            raise DocumentStorageError("File content must be bytes.")

        file_size = len(file_content)

        if file_size == 0:
            raise DocumentStorageError("Empty files are not allowed.")

        if file_size > self.max_size:
            raise DocumentStorageError("File exceeds the 10 MB limit.")

        storage_key = str(uuid.uuid4())
        destination = self._resolve_path(storage_key)

        try:
            await asyncio.to_thread(
                self._write_file,
                destination,
                file_content,
            )
        except OSError as exc:
            raise DocumentStorageError(
                "Unable to save the uploaded document."
            ) from exc

        return storage_key, file_size

    @staticmethod
    def _write_file(destination: Path, content: bytes) -> None:
        """Write a file atomically without overwriting existing files."""

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

    async def read(self, storage_key: str) -> bytes:
        """Read a privately stored document."""

        path = self._resolve_path(storage_key)

        try:
            return await asyncio.to_thread(path.read_bytes)
        except FileNotFoundError as exc:
            raise DocumentStorageError(
                "Stored document was not found."
            ) from exc
        except OSError as exc:
            raise DocumentStorageError(
                "Unable to read the stored document."
            ) from exc

    async def delete(self, storage_key: str) -> None:
        """Delete a privately stored document."""

        path = self._resolve_path(storage_key)

        try:
            await asyncio.to_thread(path.unlink, missing_ok=True)
        except OSError as exc:
            raise DocumentStorageError(
                "Unable to delete the stored document."
            ) from exc


document_storage = DocumentStorage()

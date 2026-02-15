"""
OneLake (Azure Data Lake Storage Gen2) service layer.

Connects to Microsoft Fabric OneLake using Service Principal credentials
via azure-identity and azure-storage-file-datalake SDKs.
"""

import logging
import re
from io import BytesIO

from azure.identity import ClientSecretCredential
from azure.storage.filedatalake import DataLakeServiceClient

from app.config import Settings, get_settings

logger = logging.getLogger(__name__)

# Pre-compiled regex for filename validation
_SAFE_FILENAME_RE = re.compile(r"^[a-zA-Z0-9_\-][a-zA-Z0-9_\-. ]{0,253}\.pdf$")


class OneLakeService:
    """Encapsulates interactions with OneLake / Azure Data Lake Storage."""

    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()
        self._client: DataLakeServiceClient | None = None

    # ------------------------------------------------------------------
    # Connection helpers
    # ------------------------------------------------------------------

    def _get_credential(self) -> ClientSecretCredential:
        """Create an Azure AD credential from Service Principal secrets."""
        return ClientSecretCredential(
            tenant_id=self._settings.TENANT_ID,
            client_id=self._settings.CLIENT_ID,
            client_secret=self._settings.CLIENT_SECRET,
        )

    def _get_service_client(self) -> DataLakeServiceClient:
        """Return (and cache) a DataLakeServiceClient connected to OneLake."""
        if self._client is None:
            credential = self._get_credential()
            self._client = DataLakeServiceClient(
                account_url=self._settings.ONELAKE_DFS_URL,
                credential=credential,
            )
            logger.info("DataLakeServiceClient initialised for OneLake.")
        return self._client

    def _get_file_system_name(self) -> str:
        """
        Build the OneLake filesystem (container) name.
        Format: <WorkspaceName>
        """
        return self._settings.WORKSPACE_NAME

    def _get_directory_path(self) -> str:
        """
        Build the full directory path inside the filesystem.
        Format: <LakehouseName>.Lakehouse/<PDF_FOLDER_PATH>
        """
        return (
            f"{self._settings.LAKEHOUSE_NAME}.Lakehouse"
            f"/{self._settings.PDF_FOLDER_PATH}"
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @staticmethod
    def validate_filename(filename: str) -> bool:
        """
        Validate that the filename is safe (no path traversal, must be .pdf).

        Rules:
        - Must end with .pdf
        - Must not contain path separators or relative-path components
        - Only alphanumeric, dashes, underscores, dots, and spaces allowed
        """
        if ".." in filename or "/" in filename or "\\" in filename:
            return False
        return bool(_SAFE_FILENAME_RE.match(filename))

    def list_pdf_files(self) -> list[str]:
        """Return a list of PDF filenames in the configured OneLake folder."""
        client = self._get_service_client()
        file_system_client = client.get_file_system_client(
            file_system=self._get_file_system_name()
        )
        directory_client = file_system_client.get_directory_client(
            self._get_directory_path()
        )

        pdf_files: list[str] = []
        for path in directory_client.get_paths():
            name: str = path.name.split("/")[-1]
            if name.lower().endswith(".pdf"):
                pdf_files.append(name)

        logger.info("Listed %d PDF(s) from OneLake.", len(pdf_files))
        return sorted(pdf_files)

    def download_pdf(self, filename: str) -> BytesIO:
        """
        Download a single PDF from OneLake and return it as an in-memory buffer.

        Raises ValueError if the filename fails validation.
        Raises FileNotFoundError if the file does not exist.
        """
        if not self.validate_filename(filename):
            raise ValueError(f"Invalid filename: {filename}")

        client = self._get_service_client()
        file_system_client = client.get_file_system_client(
            file_system=self._get_file_system_name()
        )

        file_path = f"{self._get_directory_path()}/{filename}"
        file_client = file_system_client.get_file_client(file_path)

        try:
            download = file_client.download_file()
            buffer = BytesIO()
            download.readinto(buffer)
            buffer.seek(0)
            logger.info("Downloaded '%s' (%d bytes).", filename, buffer.getbuffer().nbytes)
            return buffer
        except Exception as exc:
            logger.error("Failed to download '%s': %s", filename, exc)
            raise FileNotFoundError(f"File not found: {filename}") from exc


# ---------------------------------------------------------------------------
# Dependency injection helper for FastAPI
# ---------------------------------------------------------------------------

_service_instance: OneLakeService | None = None


def get_onelake_service() -> OneLakeService:
    """Return a singleton OneLakeService instance."""
    global _service_instance  # noqa: PLW0603
    if _service_instance is None:
        _service_instance = OneLakeService()
    return _service_instance

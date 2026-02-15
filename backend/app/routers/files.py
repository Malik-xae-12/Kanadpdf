"""
File-serving API endpoints.

GET /files        → list PDF file names
GET /files/{name} → stream a single PDF
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse


from app.services.onelake import OneLakeService, get_onelake_service

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/files",
    tags=["files"],

)


@router.get(    
    "",
    summary="List PDF files",
    response_model=list[str],
)
async def list_files(
    service: OneLakeService = Depends(get_onelake_service),
) -> list[str]:
    """Return the names of all PDF files in the OneLake reports folder."""
    try:
        return service.list_pdf_files()
    except Exception as exc:
        logger.exception("Error listing files.")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list files: {exc}",
        ) from exc


@router.get(
    "/{filename}",
    summary="Download / stream a PDF file",
    response_class=StreamingResponse,
)
async def get_file(
    filename: str,
    service: OneLakeService = Depends(get_onelake_service),
) -> StreamingResponse:
    """Stream the requested PDF from OneLake."""
    # Validate filename
    if not OneLakeService.validate_filename(filename):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid filename. Only .pdf files with safe characters are allowed.",
        )

    try:
        buffer = service.download_pdf(filename)
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File not found: {filename}",
        )
    except Exception as exc:
        logger.exception("Error downloading file '%s'.", filename)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to download file: {exc}",
        ) from exc

    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'inline; filename="{filename}"',
            "Cache-Control": "no-store",
        },
    )

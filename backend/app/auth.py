"""
Placeholder authentication middleware.

In production, replace this with proper Azure AD token validation
(e.g. using python-jose or msal to verify JWT bearer tokens).
For now it checks for a simple API key in the X-API-Key header.
"""

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader

from app.config import Settings, get_settings

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def verify_api_key(
    api_key: str | None = Security(api_key_header),
    settings: Settings = Depends(get_settings),
) -> str:
    """
    Validate the incoming API key against the configured value.

    Replace this dependency with real Azure AD / OAuth2 validation
    in production environments.
    """
    if api_key is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication credentials. Provide X-API-Key header.",
        )
    if api_key != settings.API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key.",
        )
    return api_key

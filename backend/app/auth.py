from fastapi import Depends, HTTPException, Security, status, Request

async def verify_api_key(
    request: Request,
    api_key: str | None = Security(api_key_header),
    settings: Settings = Depends(get_settings),
) -> str:
    # ✅ Allow preflight requests
    if request.method == "OPTIONS":
        return "preflight"

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

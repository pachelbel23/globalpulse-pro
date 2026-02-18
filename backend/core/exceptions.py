from fastapi import HTTPException


class UpstreamError(HTTPException):
    def __init__(self, source: str, detail: str = ""):
        super().__init__(
            status_code=502,
            detail=f"Upstream error from {source}: {detail}",
        )

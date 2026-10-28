from datetime import UTC, datetime

from fastapi import APIRouter, HTTPException, status

from app.api.v1.admin.deps import AdminGuard
from app.core.config import get_settings
from app.core.security import create_access_token, verify_password
from app.db.deps import DatabaseSession
from app.repositories.admin import get_admin_credential
from app.schemas.admin import AdminMeData, LoginRequest, TokenData
from app.schemas.common import DataResponse, MessageData

router = APIRouter(prefix="/auth", tags=["admin-auth"])


@router.post("/login", response_model=DataResponse[TokenData])
async def login(
    payload: LoginRequest,
    db: DatabaseSession,
) -> DataResponse[TokenData]:
    credential = get_admin_credential(db)
    if credential is None or not verify_password(
        payload.password.get_secret_value(),
        credential.password_hash,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    credential.last_login = datetime.now(UTC)
    db.commit()

    settings = get_settings()
    return DataResponse(
        data=TokenData(
            access_token=create_access_token(),
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )
    )


@router.post("/logout", response_model=DataResponse[MessageData])
async def logout(_admin: AdminGuard) -> DataResponse[MessageData]:
    return DataResponse(data=MessageData(message="Logged out"))


@router.get("/me", response_model=DataResponse[AdminMeData])
async def me(_admin: AdminGuard) -> DataResponse[AdminMeData]:
    return DataResponse(data=AdminMeData(is_admin=True))

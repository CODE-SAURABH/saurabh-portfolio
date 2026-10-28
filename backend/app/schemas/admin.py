from pydantic import BaseModel, Field, SecretStr


class LoginRequest(BaseModel):
    password: SecretStr = Field(min_length=1, max_length=200)


class TokenData(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class AdminMeData(BaseModel):
    is_admin: bool

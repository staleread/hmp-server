from pydantic import BaseModel


class PublicKeyResponse(BaseModel):
    public_key: str

from pydantic import BaseModel
from typing import Optional, Literal

class GenerateRequest(BaseModel):
    prompt: str
    css_framework: Literal["tailwind", "angular-material", "custom"]
    session_id: str


class GenerateResponse(BaseModel):
    session_id: str
    code: str
    retries: int
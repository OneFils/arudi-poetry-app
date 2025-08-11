from pydantic import BaseModel
from typing import List, Optional

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"

class AnalyzeIn(BaseModel):
    text: str

class LineOut(BaseModel):
    line: str
    meter: str
    tafail: str
    qafiyah: str
    confidence: float

class AnalyzeOut(BaseModel):
    results: List[LineOut]

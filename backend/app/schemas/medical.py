from pydantic import BaseModel
from typing import List


class MedicalAnalysis(BaseModel):

    summary: str

    findings: List[str]

    risk_level: str

    recommended_action: str

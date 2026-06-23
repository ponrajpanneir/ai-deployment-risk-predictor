from pydantic import BaseModel
from typing import Literal

class DeploymentResult(BaseModel):
    actual_result: Literal["SUCCESS", "FAILED"]

class RiskRequest(BaseModel):
    commit_id: str
    branch: str
    files_changed: list[str]
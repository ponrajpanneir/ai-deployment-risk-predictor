from sqlalchemy import Column, Integer, String, Text, TIMESTAMP
from sqlalchemy.sql import func
from app.database import Base

class DeploymentRisk(Base):
    __tablename__ = "deployment_risks"

    id = Column(Integer, primary_key=True, index=True)

    commit_id = Column(String(100), nullable=False)

    branch = Column(String(100), nullable=False)

    files_changed = Column(Text)

    risk_score = Column(Integer)

    risk_level = Column(String(20))

    prediction_reason = Column(Text)

    actual_result = Column(String(20))

    created_at = Column(
        TIMESTAMP,
        server_default=func.now()
    )
from fastapi import FastAPI
from app.database import engine, Base
from app.schemas import RiskRequest,DeploymentResult
from app.risk_engine import calculate_risk

from sqlalchemy.orm import Session
from fastapi import Depends

from app.database import get_db
from app.models import DeploymentRisk

from fastapi import Request

Base.metadata.create_all(bind=engine)

app = FastAPI()


@app.get("/")
def home():
    return {
        "project": "AI Deployment Risk Predictor",
        "database": "PostgreSQL",
        "status": "running"
    }


@app.post("/predict-risk")
def predict_risk(
    request: RiskRequest,
    db: Session = Depends(get_db)
):

    score, level, reasons = calculate_risk(
        request.files_changed
    )

    prediction = DeploymentRisk(
        commit_id=request.commit_id,
        branch=request.branch,
        files_changed=",".join(request.files_changed),
        risk_score=score,
        risk_level=level,
        prediction_reason="; ".join(reasons)
    )

    db.add(prediction)
    db.commit()
    db.refresh(prediction)

    return {
        "id": prediction.id,
        "risk_score": score,
        "risk_level": level,
        "reasons": reasons
    }

@app.get("/deployments")
def get_deployments(db: Session = Depends(get_db)):
    deployments = db.query(DeploymentRisk).all()

    return deployments

@app.get("/risk-summary")
def risk_summary(db: Session = Depends(get_db)):

    total = db.query(DeploymentRisk).count()

    high = db.query(DeploymentRisk)\
             .filter(DeploymentRisk.risk_level == "HIGH")\
             .count()

    medium = db.query(DeploymentRisk)\
               .filter(DeploymentRisk.risk_level == "MEDIUM")\
               .count()

    low = db.query(DeploymentRisk)\
            .filter(DeploymentRisk.risk_level == "LOW")\
            .count()

    return {
        "total_predictions": total,
        "high_risk": high,
        "medium_risk": medium,
        "low_risk": low
    }

@app.post("/github-webhook")
async def github_webhook(request: Request):

    payload = await request.json()

    commit_id = payload["head_commit"]["id"]
    branch = payload["ref"].split("/")[-1]

    files_changed = []

    for commit in payload["commits"]:
        files_changed.extend(commit.get("modified", []))

    return {
        "commit_id": commit_id,
        "branch": branch,
        "files_changed": files_changed
    }

@app.put("/deployment/{deployment_id}/result")
def update_result(
    deployment_id: int,
    result: DeploymentResult,
    db: Session = Depends(get_db)
):

    deployment = db.query(DeploymentRisk)\
        .filter(DeploymentRisk.id == deployment_id)\
        .first()

    if not deployment:
        return {"message": "Deployment not found"}

    deployment.actual_result = result.actual_result

    db.commit()

    return {
        "message": "Deployment updated"
    }

@app.get("/accuracy")
def get_accuracy(db: Session = Depends(get_db)):

    deployments = db.query(DeploymentRisk).all()

    total = 0
    correct = 0

    for d in deployments:

        if not d.actual_result:
            continue

        total += 1

        if (
            (d.risk_level == "HIGH" and d.actual_result == "FAILED")
            or
            (d.risk_level in ["LOW", "MEDIUM"] and d.actual_result == "SUCCESS")
        ):
            correct += 1

    accuracy = 0

    if total > 0:
        accuracy = round((correct / total) * 100, 2)

    return {
        "total_evaluated": total,
        "correct_predictions": correct,
        "accuracy_percent": accuracy
    }
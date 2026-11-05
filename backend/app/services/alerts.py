from sqlalchemy.orm import Session
from app.models.entities import AlertRule, Alert

def _compare(value: float, operator: str, threshold: float) -> bool:
    return {">": value > threshold, ">=": value >= threshold, "<": value < threshold, "<=": value <= threshold, "==": value == threshold}.get(operator, False)

def evaluate_rules(db: Session, station_id: int, values: dict):
    created=[]
    rules=db.query(AlertRule).filter(AlertRule.active.is_(True)).all()
    for rule in rules:
        value=values.get(rule.variable)
        if value is not None and _compare(float(value), rule.operator, rule.threshold):
            alert=Alert(station_id=station_id, rule_id=rule.id, trigger_value=float(value))
            db.add(alert); created.append(alert)
    return created

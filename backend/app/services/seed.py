from sqlalchemy.orm import Session
from app.models.entities import Role, User, Station, AlertRule
from app.core.security import hash_password

DEMO_USERS = [
    ("ADMIN", "admin@skysense.co", "Admin123!"),
    ("OPERATOR", "operador@skysense.co", "Operador123!"),
    ("MAINTENANCE", "mantenimiento@skysense.co", "Mantenimiento123!"),
    ("VIEWER", "consulta@skysense.co", "Consulta123!"),
]

def seed(db: Session):
    role_defs = [
        ("ADMIN", "Administrador"),
        ("OPERATOR", "Operador"),
        ("VIEWER", "Consulta"),
        ("MAINTENANCE", "Mantenimiento"),
    ]
    for name, description in role_defs:
        if not db.query(Role).filter_by(name=name).first():
            db.add(Role(name=name, description=description))
    db.commit()

    for role_name, email, password in DEMO_USERS:
        if not db.query(User).filter_by(email=email).first():
            role = db.query(Role).filter_by(name=role_name).first()
            db.add(User(role_id=role.id, email=email, password_hash=hash_password(password)))
    db.commit()

    stations = [
        ("SKY-001", "Estación Bogotá Norte", 4.7110, -74.0721),
        ("SKY-002", "Estación Bogotá Sur", 4.6047, -74.0817),
    ]
    for code, name, lat, lon in stations:
        if not db.query(Station).filter_by(station_code=code).first():
            db.add(Station(station_code=code, name=name, latitude=lat, longitude=lon, firmware="1.0.0"))
    db.commit()

    rules = [
        ("Viento fuerte", "wind_speed", ">", 12.0, "WARNING"),
        ("Temperatura alta", "temperature", ">", 35.0, "CRITICAL"),
    ]
    for name, variable, operator, threshold, severity in rules:
        if not db.query(AlertRule).filter_by(name=name).first():
            db.add(AlertRule(name=name, variable=variable, operator=operator, threshold=threshold, severity=severity))
    db.commit()

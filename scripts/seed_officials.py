"""Seed demo municipal accounts. Run: python scripts/seed_officials.py"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.app.database import Base, SessionLocal, engine
from backend.app.models import MunicipalOfficial
from backend.app.routers.auth import password_context

OFFICIALS = [
    ("Aditi Sharma", "anand.officer@urbanair.demo", "Ward Officer", "anand_vihar"),
    ("Rahul Verma", "mandir.officer@urbanair.demo", "Ward Officer", "mandir_marg"),
    ("Neha Kapoor", "zonal.head@urbanair.demo", "Zonal Head", "anand_vihar"),
]
DEMO_PASSWORD = "Demo@123"


def main():
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        for name, email, designation, assigned_ward in OFFICIALS:
            if db.query(MunicipalOfficial).filter_by(email=email).first() is None:
                db.add(MunicipalOfficial(name=name, email=email, password_hash=password_context.hash(DEMO_PASSWORD), designation=designation, assigned_ward=assigned_ward))
        db.commit()
    print("Seeded demo officials. Password for all accounts: Demo@123")


if __name__ == "__main__":
    main()

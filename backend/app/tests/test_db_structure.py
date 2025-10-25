from sqlalchemy import inspect
from app.extensions import db
import pytest
from sqlalchemy.exc import IntegrityError

@pytest.fixture
def inspector(app):
    """Create a SQLAlchemy inspector to examine DB metadata."""
    with app.app_context():
        yield inspect(db.engine)


def test_tables_exist(inspector):
    tables = inspector.get_table_names()
    expected = {
        "users",
        "companies",
        "company_users",
        "availabilities",
        "shifts",
        "shift_assignments",
        "swaps",
        "alembic_version",
    }
    for t in expected:
        assert t in tables, f"Missing expected table: {t}"


def test_company_user_primary_key(inspector):
    pk = inspector.get_pk_constraint("company_users")
    assert set(pk["constrained_columns"]) == {"id"}


def test_shift_assignments_user_set_null_on_delete(app):
    from app.models import ShiftAssignment, User, Shift, Company
    import datetime

    with app.app_context():
        db.session.query(ShiftAssignment).delete()
        db.session.query(Shift).delete()
        db.session.query(User).delete()
        db.session.query(Company).delete()
        db.session.commit()

        company = Company(name="Test Co")
        db.session.add(company)
        db.session.flush()

        user = User(username="testuser", email="test@test.com", hash="hash_password", active=True)
        shift = Shift(
            company_id=company.id,
            date=datetime.date(2025, 8, 10),
            start_time=datetime.time(9, 0),
            end_time=datetime.time(17, 0),
            capacity=5
        )
        db.session.add_all([user, shift])
        db.session.commit()

        shift_assignment = ShiftAssignment(user_id=user.id, shift_id=shift.id)
        db.session.add(shift_assignment)
        db.session.commit()

        db.session.delete(user)
        db.session.commit()

        assignments = ShiftAssignment.query.all()
        assert all(sa.user_id is None for sa in assignments)
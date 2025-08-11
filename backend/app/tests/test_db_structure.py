from sqlalchemy import inspect
from app.extensions import db
import pytest
from sqlalchemy.exc import IntegrityError


@pytest.fixture
def inspector(test_app):
    return inspect(db.engine)


def test_tables_exist(inspector):
    tables = inspector.get_table_names()
    assert "users" in tables
    assert "roles" in tables
    assert "shifts" in tables
    assert "availabilities" in tables
    assert "swaps" in tables

 
def test_user_role_primary_key(inspector):
    pk = inspector.get_pk_constraint("user_roles")
    assert set(pk['constrained_columns']) == {"user_id", "role_id"}


def test_shift_assignments_user_set_null_on_delete(test_app):
    from app.models import ShiftAssignment, User, Shift
    import datetime
    with test_app.app_context():
        # Create a user and a shift assignment
        user = User(username="testuser", email="test@test.com", hash="hash_password", active=True)
        shift = Shift(
            date=datetime.date(2025, 8, 10),
            start_time=datetime.time(9, 0), 
            end_time=datetime.time(17, 0),
            capacity=5
        )
        db.session.add(user)
        db.session.add(shift)
        db.session.commit()

        shift_assignment = ShiftAssignment(user_id=user.id, shift_id=shift.id)
        db.session.add(shift_assignment)
        db.session.commit()


        db.session.delete(user)
        db.session.commit()


        assignments = ShiftAssignment.query.all()
        assert all(sa.user_id is None for sa in assignments)
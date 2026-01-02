from backend.services.matching import MatchService
from backend.models.student import Student
from sqlalchemy.orm import Session
from unittest.mock import MagicMock

def test_match_student():
    db = MagicMock(spec=Session)
    school_id = 1
    service = MatchService(db, school_id)

    # Mock DB Query for number match
    mock_student = Student(id=1, name="Alice", student_number="123", school_id=1)
    db.query.return_value.filter.return_value.first.return_value = mock_student

    # Test Number Match
    result = service.match_student("123", "Bob")
    assert result.name == "Alice"

    # Mock DB Query for name match (simulate number mismatch returning None first)
    db.query.return_value.filter.return_value.first.side_effect = [None, mock_student]

    # Test Name Match
    result = service.match_student("999", "Alice")
    assert result.name == "Alice"

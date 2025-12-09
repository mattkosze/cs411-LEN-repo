"""
Shared test utilities and fake implementations for testing.

This module provides reusable mock objects and utilities to avoid
code duplication across test files and ensure consistent testing patterns.
"""
from typing import Any, Dict, List, Optional, Type


class FakeQuery:
    """
    A mock SQLAlchemy query object that supports common query operations.
    
    Usage:
        query = FakeQuery([obj1, obj2])
        result = query.filter(...).first()
    """
    def __init__(self, data_list: Optional[List] = None, first_result: Optional[Any] = None):
        self._data_list = data_list or []
        self._first_result = first_result

    def filter(self, *args, **kwargs) -> 'FakeQuery':
        """Ignore filters; tests control which objects are present."""
        return self

    def order_by(self, *args, **kwargs) -> 'FakeQuery':
        """Ignore ordering; return self for chaining."""
        return self

    def all(self) -> List:
        """Return all objects in the data list."""
        return list(self._data_list)

    def first(self) -> Optional[Any]:
        """Return the first object or explicit first_result."""
        if self._first_result is not None:
            return self._first_result
        return self._data_list[0] if self._data_list else None

    def count(self) -> int:
        """Return count of objects."""
        return len(self._data_list)

    def get(self, obj_id: int) -> Optional[Any]:
        """Get object by id attribute."""
        for obj in self._data_list:
            if getattr(obj, "id", None) == obj_id:
                return obj
        return None


class FakeSession:
    """
    A mock SQLAlchemy Session that tracks added objects and commits.
    
    Usage:
        db = FakeSession({User: [user1, user2]})
        db.add(new_user)
        db.commit()
        assert db.committed is True
    """
    def __init__(self, data: Optional[Dict[Type, List]] = None):
        # data maps model class -> list[instances]
        self.data: Dict[Type, List] = data or {}
        self.committed = False
        self._added_objects: List = []

    def query(self, model: Type) -> FakeQuery:
        """Return a FakeQuery for the given model class."""
        lst = self.data.setdefault(model, [])
        return FakeQuery(lst)

    def add(self, obj: Any) -> None:
        """Add an object to the session."""
        self._added_objects.append(obj)
        self.data.setdefault(obj.__class__, []).append(obj)

    def commit(self) -> None:
        """Mark the session as committed."""
        self.committed = True

    def refresh(self, obj: Any) -> None:
        """No-op for tests - simulates refreshing from database."""
        pass

    def close(self) -> None:
        """No-op for tests - simulates closing the session."""
        pass


class FakeDB:
    """
    Simple fake DB object for router testing.
    
    Usage:
        fake_db = FakeDB(result_list=[user1, user2])
        results = fake_db.query(User).all()
    """
    def __init__(
        self, 
        result_list: Optional[List] = None, 
        first_result: Optional[Any] = None
    ):
        self._result_list = result_list or []
        self._first_result = first_result

    def query(self, *args, **kwargs) -> FakeQuery:
        """Return a FakeQuery with configured results."""
        return FakeQuery(
            data_list=self._result_list, 
            first_result=self._first_result
        )

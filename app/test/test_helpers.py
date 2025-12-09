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


def create_fake_user(
    id: int = 1,
    email: str = "test@example.com",
    display_name: str = "Test User",
    is_anonymous: bool = False,
    is_active: bool = True,
    is_banned: bool = False,
    role: str = "user"
):
    """
    Create a fake user object for testing.
    
    Returns a SimpleNamespace that mimics a User model.
    """
    from types import SimpleNamespace
    return SimpleNamespace(
        id=id,
        email=email,
        display_name=display_name,
        is_anonymous=is_anonymous,
        is_active=is_active,
        is_banned=is_banned,
        role=role
    )


def create_fake_post(
    id: int = 1,
    author_id: int = 1,
    group_id: Optional[int] = None,
    content: str = "Test post content",
    status: str = "active",
    created_at: Optional[float] = None
):
    """
    Create a fake post object for testing.
    
    Returns a SimpleNamespace that mimics a Post model.
    """
    from types import SimpleNamespace
    from datetime import datetime
    
    return SimpleNamespace(
        id=id,
        author_id=author_id,
        group_id=group_id,
        content=content,
        status=status,
        created_at=created_at or datetime.now().timestamp()
    )


def create_fake_report(
    id: int = 1,
    reporting_user_id: int = 1,
    reported_user_id: Optional[int] = 2,
    post_id: Optional[int] = 1,
    reason: str = "harassment",
    details: Optional[str] = None,
    is_crisis: bool = False,
    status: str = "open",
    created_at: Optional[float] = None
):
    """
    Create a fake report object for testing.
    
    Returns a SimpleNamespace that mimics a Report model.
    """
    from types import SimpleNamespace
    from datetime import datetime
    
    return SimpleNamespace(
        id=id,
        reporting_user_id=reporting_user_id,
        reported_user_id=reported_user_id,
        post_id=post_id,
        reason=reason,
        details=details,
        is_crisis=is_crisis,
        status=status,
        created_at=created_at or datetime.now().timestamp(),
        resolved_at=None,
        resolution_impact=None
    )

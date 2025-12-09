"""
Tests for authentication dependencies.
"""
import pytest
from unittest.mock import MagicMock, patch
from fastapi import HTTPException
from jose import jwt

from app.dependencies import get_current_user, require_moderator
from app import models
from app.config import settings


class TestGetCurrentUser:
    """Tests for get_current_user dependency."""
    
    def test_valid_jwt_token_returns_user(self):
        """Test that a valid JWT token returns the associated user."""
        # Create a mock user
        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.is_active = True
        
        # Create a mock DB session
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user
        
        # Create a valid token
        token = jwt.encode({"sub": "1"}, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        mock_credentials = MagicMock()
        mock_credentials.credentials = token
        
        result = get_current_user(credentials=mock_credentials, db=mock_db, x_user_id=None)
        
        assert result == mock_user
    
    def test_missing_credentials_raises_401(self):
        """Test that missing credentials raise HTTPException."""
        mock_db = MagicMock()
        
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(credentials=None, db=mock_db, x_user_id=None)
        
        assert exc_info.value.status_code == 401
        assert "Not authenticated" in exc_info.value.detail
    
    def test_invalid_token_raises_401(self):
        """Test that an invalid token raises HTTPException."""
        mock_db = MagicMock()
        mock_credentials = MagicMock()
        mock_credentials.credentials = "invalid-token"
        
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(credentials=mock_credentials, db=mock_db, x_user_id=None)
        
        assert exc_info.value.status_code == 401
    
    def test_token_without_sub_raises_401(self):
        """Test that a token without 'sub' claim raises HTTPException."""
        mock_db = MagicMock()
        
        # Create a token without 'sub' claim
        token = jwt.encode({}, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        mock_credentials = MagicMock()
        mock_credentials.credentials = token
        
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(credentials=mock_credentials, db=mock_db, x_user_id=None)
        
        assert exc_info.value.status_code == 401
    
    def test_user_not_found_raises_401(self):
        """Test that a valid token for non-existent user raises HTTPException."""
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        token = jwt.encode({"sub": "999"}, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        mock_credentials = MagicMock()
        mock_credentials.credentials = token
        
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(credentials=mock_credentials, db=mock_db, x_user_id=None)
        
        assert exc_info.value.status_code == 401
    
    def test_inactive_user_raises_403(self):
        """Test that an inactive user raises HTTPException."""
        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.is_active = False
        
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user
        
        token = jwt.encode({"sub": "1"}, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        mock_credentials = MagicMock()
        mock_credentials.credentials = token
        
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(credentials=mock_credentials, db=mock_db, x_user_id=None)
        
        assert exc_info.value.status_code == 403
        assert "deleted" in exc_info.value.detail.lower()
    
    @patch('app.dependencies.settings')
    def test_x_user_id_allowed_in_development(self, mock_settings):
        """Test that X-User-Id header works in development mode."""
        mock_settings.ENV = "development"
        mock_settings.SECRET_KEY = settings.SECRET_KEY
        mock_settings.ALGORITHM = settings.ALGORITHM
        
        mock_user = MagicMock()
        mock_user.id = 5
        mock_user.is_active = True
        
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user
        
        result = get_current_user(credentials=None, db=mock_db, x_user_id="5")
        
        assert result == mock_user
    
    @patch('app.dependencies.settings')
    def test_x_user_id_ignored_in_production(self, mock_settings):
        """Test that X-User-Id header is ignored in production mode."""
        mock_settings.ENV = "production"
        mock_settings.SECRET_KEY = settings.SECRET_KEY
        mock_settings.ALGORITHM = settings.ALGORITHM
        
        mock_db = MagicMock()
        
        # Should raise 401 because X-User-Id is ignored and no JWT provided
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(credentials=None, db=mock_db, x_user_id="5")
        
        assert exc_info.value.status_code == 401


class TestRequireModerator:
    """Tests for require_moderator dependency."""
    
    def test_moderator_role_passes(self):
        """Test that moderator role passes the check."""
        mock_user = MagicMock()
        mock_user.role = models.UserRole.MODERATOR
        
        result = require_moderator(mock_user)
        assert result == mock_user
    
    def test_admin_role_passes(self):
        """Test that admin role passes the check."""
        mock_user = MagicMock()
        mock_user.role = models.UserRole.ADMIN
        
        result = require_moderator(mock_user)
        assert result == mock_user
    
    def test_regular_user_raises_403(self):
        """Test that regular user raises HTTPException."""
        mock_user = MagicMock()
        mock_user.role = models.UserRole.USER
        
        with pytest.raises(HTTPException) as exc_info:
            require_moderator(mock_user)
        
        assert exc_info.value.status_code == 403
        assert "Moderator" in exc_info.value.detail

"""
Tests for centralized constants and utility functions.
"""
import pytest

from app.constants import CRISIS_KEYWORDS, detect_crisis


class TestCrisisDetection:
    """Tests for crisis keyword detection."""
    
    def test_detect_crisis_with_exact_keyword(self):
        """Test detection with exact keyword match."""
        assert detect_crisis("I want to end it all") is True
        assert detect_crisis("kill myself") is True
        assert detect_crisis("feeling suicidal") is True
    
    def test_detect_crisis_case_insensitive(self):
        """Test that detection is case insensitive."""
        assert detect_crisis("I WANT TO END IT ALL") is True
        assert detect_crisis("Kill Myself") is True
        assert detect_crisis("SUICIDE") is True
    
    def test_detect_crisis_with_surrounding_text(self):
        """Test detection when keyword is within other text."""
        assert detect_crisis("I've been feeling down lately and need help") is True
        assert detect_crisis("Sometimes I think about ending it") is True
    
    def test_detect_crisis_no_match(self):
        """Test that non-crisis content returns False."""
        assert detect_crisis("I love this community!") is False
        assert detect_crisis("Having a great day") is False
        assert detect_crisis("Thanks for the support") is False
    
    def test_detect_crisis_empty_content(self):
        """Test detection with empty content."""
        assert detect_crisis("") is False
    
    def test_detect_crisis_whitespace_only(self):
        """Test detection with whitespace-only content."""
        assert detect_crisis("   \n\t   ") is False
    
    def test_crisis_keywords_list_not_empty(self):
        """Test that crisis keywords list is defined and not empty."""
        assert len(CRISIS_KEYWORDS) > 0
        assert all(isinstance(k, str) for k in CRISIS_KEYWORDS)
    
    def test_all_keywords_trigger_detection(self):
        """Test that every keyword in the list triggers detection."""
        for keyword in CRISIS_KEYWORDS:
            assert detect_crisis(keyword) is True, f"Keyword '{keyword}' should trigger detection"
    
    def test_partial_keyword_match(self):
        """Test that partial matches within words also trigger."""
        # 'suicidal' contains 'suicide' but we want exact phrase matching
        # This tests the current behavior
        assert detect_crisis("suicidal thoughts") is True

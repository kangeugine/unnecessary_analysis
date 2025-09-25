#!/usr/bin/env python3
import pytest
import sys
import os

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from clean_csv import split_competition

class TestSplitCompetition:
    """Test cases for the split_competition function."""
    
    def test_premier_league_format(self):
        """Test Premier League format."""
        result = split_competition("Premier League 22/23")
        assert result == ("Premier League", "22/23")
        
    def test_laliga_format(self):
        """Test LaLiga format."""
        result = split_competition("LaLiga 17/18")
        assert result == ("LaLiga", "17/18")
        
    def test_ligue_1_format(self):
        """Test Ligue 1 format."""
        result = split_competition("Ligue 1 23/24")
        assert result == ("Ligue 1", "23/24")
        
    def test_serie_a_format(self):
        """Test Serie A format."""
        result = split_competition("Serie A 19/20")
        assert result == ("Serie A", "19/20")
        
    def test_bundesliga_format(self):
        """Test Bundesliga format."""
        result = split_competition("Bundesliga 23/24")
        assert result == ("Bundesliga", "23/24")
        
    def test_saudi_pro_league_format(self):
        """Test Saudi Pro League format."""
        result = split_competition("Saudi Pro League 23/24")
        assert result == ("Saudi Pro League", "23/24")
        
    def test_multiple_word_league(self):
        """Test leagues with multiple words."""
        result = split_competition("Premier League 25/26")
        assert result == ("Premier League", "25/26")
        
    def test_single_digit_season(self):
        """Test season with single digits."""
        result = split_competition("Premier League 09/10")
        assert result == ("Premier League", "09/10")
        
    def test_no_season_format(self):
        """Test string without season format."""
        result = split_competition("Premier League")
        assert result == ("Premier League", "")
        
    def test_empty_string(self):
        """Test empty string."""
        result = split_competition("")
        assert result == ("", "")
        
    def test_none_input(self):
        """Test None input."""
        result = split_competition(None)
        assert result == ("", "")
        
    def test_non_string_input(self):
        """Test non-string input."""
        result = split_competition(123)
        assert result == ("", "")
        
    def test_malformed_season(self):
        """Test malformed season format."""
        result = split_competition("Premier League 2022/23")
        assert result == ("Premier League 2022/23", "")  # Should not match 4-digit year
        
    def test_season_in_middle(self):
        """Test season format in middle of string."""
        result = split_competition("Premier League 22/23 Extra")
        assert result == ("Premier League 22/23 Extra", "")  # Should only match at end
        
    def test_with_extra_whitespace(self):
        """Test with extra whitespace."""
        result = split_competition("  Premier League   22/23  ")
        assert result == ("Premier League", "22/23")
        
    def test_complex_league_name(self):
        """Test complex league names."""
        result = split_competition("UEFA Champions League 22/23")
        assert result == ("UEFA Champions League", "22/23")

    @pytest.mark.parametrize("competition,expected_league,expected_season", [
        ("Premier League 22/23", "Premier League", "22/23"),
        ("LaLiga 17/18", "LaLiga", "17/18"),
        ("Ligue 1 23/24", "Ligue 1", "23/24"),
        ("Serie A 19/20", "Serie A", "19/20"),
        ("Bundesliga 23/24", "Bundesliga", "23/24"),
        ("Saudi Pro League 23/24", "Saudi Pro League", "23/24"),
        ("Premier League 25/26", "Premier League", "25/26"),
        ("Premier League 09/10", "Premier League", "09/10"),
        ("Premier League", "Premier League", ""),
        ("", "", ""),
    ])
    def test_parametrized_splits(self, competition, expected_league, expected_season):
        """Parametrized test for various competition formats."""
        result = split_competition(competition)
        assert result == (expected_league, expected_season)

if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"])
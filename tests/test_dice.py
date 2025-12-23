"""Unit tests for dice handling."""
import pytest
from src.dice import Dice


class TestDiceCreation:
    """Tests for dice creation."""

    def test_dice_creation_default(self):
        """Test creating dice with default count."""
        dice = Dice()
        assert dice.count == 5
        assert dice.values == []

    def test_dice_creation_custom_count(self):
        """Test creating dice with custom count."""
        dice = Dice(3)
        assert dice.count == 3
        assert dice.values == []


class TestDiceRolling:
    """Tests for dice rolling."""

    def test_roll_dice(self):
        """Test rolling dice returns correct number of values."""
        dice = Dice(5)
        values = dice.roll()
        assert len(values) == 5
        assert all(1 <= v <= 6 for v in values)

    def test_roll_custom_count(self):
        """Test rolling custom number of dice."""
        dice = Dice(3)
        values = dice.roll()
        assert len(values) == 3

    def test_roll_stores_values(self):
        """Test that roll() stores values in dice object."""
        dice = Dice(4)
        rolled_values = dice.roll()
        stored_values = dice.get_values()
        assert rolled_values == stored_values

    def test_roll_randomness(self):
        """Test that rolling produces different results."""
        dice = Dice(20)
        # Roll many dice, should get different values
        values = dice.roll()
        unique_values = set(values)
        # With 20 dice, very unlikely to get all same value
        assert len(unique_values) > 1

    def test_multiple_rolls(self):
        """Test rolling multiple times."""
        dice = Dice(5)
        first_roll = dice.roll()
        second_roll = dice.roll()
        # Both should be 5 dice
        assert len(first_roll) == 5
        assert len(second_roll) == 5
        # Should overwrite previous values
        assert dice.get_values() == second_roll


class TestGetValues:
    """Tests for getting dice values."""

    def test_get_values_empty(self):
        """Test getting values before rolling."""
        dice = Dice()
        assert dice.get_values() == []

    def test_get_values_returns_copy(self):
        """Test that get_values returns a copy."""
        dice = Dice(3)
        dice.roll()
        values1 = dice.get_values()
        values1.append(7)  # Modify the returned list
        values2 = dice.get_values()
        # Original should be unchanged
        assert 7 not in values2
        assert len(values2) == 3


class TestCountFace:
    """Tests for counting specific face values."""

    def test_count_face_with_wilds(self):
        """Test counting face value with wilds active."""
        dice = Dice(5)
        dice.values = [1, 3, 3, 4, 1]
        # Should count 3s plus the two 1s (wild)
        count = dice.count_face(3, wilds_active=True)
        assert count == 4  # Two 3s + two 1s

    def test_count_face_without_wilds(self):
        """Test counting face value without wilds (Palifico)."""
        dice = Dice(5)
        dice.values = [1, 3, 3, 4, 1]
        # Should only count actual 3s
        count = dice.count_face(3, wilds_active=False)
        assert count == 2

    def test_count_ones_ignores_wild_flag(self):
        """Test that counting ones always returns actual ones."""
        dice = Dice(5)
        dice.values = [1, 1, 2, 3, 4]
        # When counting 1s, should only count actual 1s
        count_with_wilds = dice.count_face(1, wilds_active=True)
        count_without_wilds = dice.count_face(1, wilds_active=False)
        assert count_with_wilds == 2
        assert count_without_wilds == 2

    def test_count_face_no_matches(self):
        """Test counting when no matches exist."""
        dice = Dice(5)
        dice.values = [2, 3, 4, 5, 6]
        count = dice.count_face(1, wilds_active=True)
        assert count == 0

    def test_count_all_wilds(self):
        """Test counting when all dice are wild."""
        dice = Dice(5)
        dice.values = [1, 1, 1, 1, 1]
        # Counting any face should return 5 (all wilds)
        assert dice.count_face(2, wilds_active=True) == 5
        assert dice.count_face(3, wilds_active=True) == 5
        # But counting 1s should only count actual 1s
        assert dice.count_face(1, wilds_active=True) == 5

    def test_count_face_all_same_non_wild(self):
        """Test counting when all dice show same non-wild value."""
        dice = Dice(5)
        dice.values = [4, 4, 4, 4, 4]
        assert dice.count_face(4, wilds_active=True) == 5
        assert dice.count_face(2, wilds_active=True) == 0

    def test_count_face_mixed(self):
        """Test counting with mixed values."""
        dice = Dice(6)
        dice.values = [1, 2, 2, 3, 4, 5]
        # Counting 2s with wilds: one 1 (wild) + two 2s = 3
        assert dice.count_face(2, wilds_active=True) == 3
        # Counting 2s without wilds: just two 2s
        assert dice.count_face(2, wilds_active=False) == 2

    def test_count_face_palifico_scenario(self):
        """Test Palifico scenario where wilds don't count."""
        dice = Dice(5)
        dice.values = [1, 1, 4, 4, 6]
        # In Palifico, ones are not wild
        count_4s = dice.count_face(4, wilds_active=False)
        assert count_4s == 2  # Only actual 4s
        count_1s = dice.count_face(1, wilds_active=False)
        assert count_1s == 2  # Only actual 1s


class TestEdgeCases:
    """Tests for edge cases."""

    def test_zero_dice(self):
        """Test dice with zero count."""
        dice = Dice(0)
        values = dice.roll()
        assert len(values) == 0
        assert dice.count_face(3, wilds_active=True) == 0

    def test_count_face_invalid_face(self):
        """Test counting invalid face values."""
        dice = Dice(3)
        dice.values = [1, 2, 3]
        # Counting face value 7 (invalid) will still count wild 1s
        # This is okay since game rules prevent invalid face values
        assert dice.count_face(7, wilds_active=True) == 1  # One wild 1
        assert dice.count_face(0, wilds_active=True) == 1  # One wild 1
        # Without wilds, should return 0
        assert dice.count_face(7, wilds_active=False) == 0
        assert dice.count_face(0, wilds_active=False) == 0

    def test_changing_dice_count(self):
        """Test behavior when dice count changes."""
        dice = Dice(5)
        dice.roll()
        assert len(dice.values) == 5
        # Change count and roll again
        dice.count = 3
        dice.roll()
        assert len(dice.values) == 3

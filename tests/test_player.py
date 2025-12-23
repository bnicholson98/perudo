"""Unit tests for player management."""
import pytest
from src.player import Player


class TestPlayerCreation:
    """Tests for player creation and initialization."""

    def test_player_creation(self):
        """Test basic player creation."""
        player = Player("Alice")
        assert player.name == "Alice"
        assert player.dice.count == 5
        assert player.is_active is True
        assert player.has_had_palifico is False

    def test_player_starts_with_five_dice(self):
        """Test that players start with 5 dice."""
        player = Player("Bob")
        assert player.get_dice_count() == 5


class TestDiceManagement:
    """Tests for player dice management."""

    def test_roll_dice(self):
        """Test rolling dice."""
        player = Player("Charlie")
        player.roll_dice()
        assert len(player.dice.get_values()) == 5
        # All values should be between 1 and 6
        for value in player.dice.get_values():
            assert 1 <= value <= 6

    def test_lose_die(self):
        """Test losing a die."""
        player = Player("Diana")
        initial_count = player.get_dice_count()
        player.lose_die()
        assert player.get_dice_count() == initial_count - 1
        assert player.is_active is True

    def test_lose_last_die(self):
        """Test losing all dice deactivates player."""
        player = Player("Eve")
        # Lose all 5 dice
        for _ in range(5):
            player.lose_die()
        assert player.get_dice_count() == 0
        assert player.is_active is False

    def test_gain_die(self):
        """Test gaining a die."""
        player = Player("Frank")
        player.lose_die()  # Down to 4
        player.gain_die()  # Back to 5
        assert player.get_dice_count() == 5

    def test_cannot_gain_beyond_five_dice(self):
        """Test that players cannot have more than 5 dice."""
        player = Player("Grace")
        player.gain_die()  # Already at 5, should stay at 5
        assert player.get_dice_count() == 5

    def test_gain_die_after_loss(self):
        """Test gaining dice after losing some."""
        player = Player("Henry")
        player.lose_die()
        player.lose_die()
        assert player.get_dice_count() == 3
        player.gain_die()
        assert player.get_dice_count() == 4


class TestPalifico:
    """Tests for Palifico state management."""

    def test_not_in_palifico_initially(self):
        """Test that players don't start in Palifico."""
        player = Player("Iris")
        assert player.is_in_palifico() is False

    def test_in_palifico_with_one_die(self):
        """Test Palifico is triggered with 1 die."""
        player = Player("Jack")
        # Lose 4 dice to get down to 1
        for _ in range(4):
            player.lose_die()
        assert player.get_dice_count() == 1
        assert player.is_in_palifico() is True

    def test_palifico_triggers_only_once(self):
        """Test that Palifico only triggers once per player."""
        player = Player("Kate")
        # Get down to 1 die
        for _ in range(4):
            player.lose_die()
        assert player.is_in_palifico() is True

        # Trigger palifico
        player.trigger_palifico()
        assert player.has_had_palifico is True

        # Even at 1 die, should not be in palifico anymore
        assert player.is_in_palifico() is False

    def test_palifico_after_gaining_and_losing_again(self):
        """Test Palifico doesn't trigger again after being used."""
        player = Player("Leo")
        # Get down to 1 die and trigger palifico
        for _ in range(4):
            player.lose_die()
        player.trigger_palifico()

        # Gain a die and lose it again
        player.gain_die()
        assert player.get_dice_count() == 2
        player.lose_die()
        assert player.get_dice_count() == 1

        # Should not be in palifico again
        assert player.is_in_palifico() is False

    def test_not_in_palifico_with_zero_dice(self):
        """Test that eliminated players are not in Palifico."""
        player = Player("Mia")
        for _ in range(5):
            player.lose_die()
        assert player.get_dice_count() == 0
        assert player.is_in_palifico() is False


class TestPlayerStatus:
    """Tests for player status and string representation."""

    def test_active_player_string(self):
        """Test string representation of active player."""
        player = Player("Nina")
        player_str = str(player)
        assert "Nina" in player_str
        assert "5 dice" in player_str
        assert "Active" in player_str

    def test_eliminated_player_string(self):
        """Test string representation of eliminated player."""
        player = Player("Oscar")
        for _ in range(5):
            player.lose_die()
        player_str = str(player)
        assert "Oscar" in player_str
        assert "0 dice" in player_str
        assert "Eliminated" in player_str

    def test_inactive_player_cannot_roll(self):
        """Test that inactive players don't roll dice."""
        player = Player("Paul")
        # Eliminate player
        for _ in range(5):
            player.lose_die()

        # Try to roll - should not crash, but dice count stays 0
        player.roll_dice()
        assert player.get_dice_count() == 0


class TestEdgeCases:
    """Tests for edge cases in player management."""

    def test_multiple_lose_die_calls_when_zero(self):
        """Test losing dice when already at zero."""
        player = Player("Quinn")
        for _ in range(5):
            player.lose_die()

        # Try to lose another die
        player.lose_die()
        assert player.get_dice_count() == 0
        assert player.is_active is False

    def test_player_reactivation_not_possible(self):
        """Test that eliminated players stay eliminated."""
        player = Player("Rachel")
        for _ in range(5):
            player.lose_die()
        assert player.is_active is False

        # Gaining a die doesn't reactivate
        player.gain_die()
        assert player.is_active is False
        assert player.get_dice_count() == 1

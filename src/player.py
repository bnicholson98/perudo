"""Player management for Perudo game."""
from src.dice import Dice


class Player:
    """Represents a player in the game."""

    def __init__(self, name: str):
        """Initialize a player.

        Args:
            name: Player's name
        """
        self.name = name
        self.dice = Dice(5)
        self.is_active = True
        self.has_had_palifico = False

    def roll_dice(self):
        """Roll all dice for this player."""
        if self.is_active:
            self.dice.roll()

    def get_dice_count(self) -> int:
        """Get the number of dice the player has.

        Returns:
            Number of dice
        """
        return self.dice.count

    def lose_die(self):
        """Remove one die from the player."""
        if self.dice.count > 0:
            self.dice.count -= 1
            if self.dice.count == 0:
                self.is_active = False

    def gain_die(self):
        """Add one die to the player (max 5)."""
        if self.dice.count < 5:
            self.dice.count += 1

    def is_in_palifico(self) -> bool:
        """Check if player is in Palifico state.

        Returns:
            True if player has exactly 1 die and hasn't had Palifico yet
        """
        return self.dice.count == 1 and not self.has_had_palifico

    def trigger_palifico(self):
        """Mark that this player has triggered their Palifico round."""
        self.has_had_palifico = True

    def __str__(self) -> str:
        """String representation of the player."""
        status = "Active" if self.is_active else "Eliminated"
        return f"{self.name} ({self.dice.count} dice) - {status}"

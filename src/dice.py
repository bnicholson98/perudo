"""Dice management for Perudo game."""
import random
from typing import List


class Dice:
    """Represents a collection of dice for a player."""

    def __init__(self, count: int = 5):
        """Initialize dice collection.

        Args:
            count: Number of dice (default 5)
        """
        self.count = count
        self.values: List[int] = []

    def roll(self) -> List[int]:
        """Roll all dice and return their values.

        Returns:
            List of dice values (1-6)
        """
        self.values = [random.randint(1, 6) for _ in range(self.count)]
        return self.values

    def get_values(self) -> List[int]:
        """Get current dice values.

        Returns:
            List of current dice values
        """
        return self.values.copy()

    def count_face(self, face: int, wilds_active: bool = True) -> int:
        """Count occurrences of a specific face value.

        Args:
            face: Face value to count (1-6)
            wilds_active: Whether ones count as wild (default True)

        Returns:
            Count of matching dice
        """
        if face == 1:
            # When counting ones, only count actual ones
            return self.values.count(1)

        if wilds_active:
            # Count the face value plus wild ones
            return self.values.count(face) + self.values.count(1)
        else:
            # During Palifico, ones are not wild
            return self.values.count(face)

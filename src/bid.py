"""Bid representation and validation for Perudo game."""
import math
from typing import Optional


class Bid:
    """Represents a bid in the game."""

    def __init__(self, quantity: int, face: int):
        """Initialize a bid.

        Args:
            quantity: Number of dice bid
            face: Face value bid (1-6)
        """
        self.quantity = quantity
        self.face = face

    def __str__(self) -> str:
        """String representation of the bid."""
        return f"{self.quantity} {self.face}s"

    def __repr__(self) -> str:
        """Developer representation of the bid."""
        return f"Bid({self.quantity}, {self.face})"

    def is_valid_raise(self, previous_bid: Optional['Bid'], is_palifico: bool = False, total_dice: int = 0) -> tuple[bool, str]:
        """Check if this bid is a valid raise from the previous bid.

        Args:
            previous_bid: The previous bid to compare against (None if first bid)
            is_palifico: Whether the current round is Palifico
            total_dice: Total number of dice in play (for max validation)

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check max quantity
        if total_dice > 0 and self.quantity > total_dice:
            return False, f"Cannot bid more than {total_dice} dice (total in play)"

        # First bid of the round
        if previous_bid is None:
            if self.quantity < 1 or self.face < 1 or self.face > 6:
                return False, "Invalid bid values"
            if self.face == 1:
                return False, "Cannot start the round with a bid on ones"
            return True, ""

        # During Palifico, face value must stay the same
        if is_palifico:
            if self.face != previous_bid.face:
                return False, "During Palifico, face value cannot change"
            if self.quantity <= previous_bid.quantity:
                return False, "Must increase quantity during Palifico"
            return True, ""

        # Bidding on ones from non-ones
        if self.face == 1 and previous_bid.face != 1:
            min_quantity = math.ceil(previous_bid.quantity / 2)
            if self.quantity < min_quantity:
                return False, f"When bidding on ones, quantity must be at least {min_quantity}"
            return True, ""

        # Bidding away from ones to non-ones
        if previous_bid.face == 1 and self.face != 1:
            min_quantity = (previous_bid.quantity * 2) + 1
            if self.quantity < min_quantity:
                return False, f"When bidding away from ones, quantity must be at least {min_quantity}"
            return True, ""

        # Standard bid (both on ones or both not on ones)
        if self.face == previous_bid.face:
            # Same face, must increase quantity
            if self.quantity <= previous_bid.quantity:
                return False, "Must increase quantity when keeping same face value"
            return True, ""
        else:
            # Different face, can have same quantity if face is higher
            if self.quantity < previous_bid.quantity:
                return False, "Must have higher quantity if face value is lower"
            if self.quantity == previous_bid.quantity and self.face <= previous_bid.face:
                return False, "If quantity is the same, face value must be higher"
            return True, ""

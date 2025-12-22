"""Game rules engine for Perudo."""
from typing import List
from src.player import Player
from src.bid import Bid


class RulesEngine:
    """Handles game rule validation and resolution."""

    @staticmethod
    def count_dice_in_play(players: List[Player], face: int, wilds_active: bool = True) -> int:
        """Count total number of a specific face value across all active players.

        Args:
            players: List of all players
            face: Face value to count (1-6)
            wilds_active: Whether ones count as wild

        Returns:
            Total count of matching dice
        """
        total = 0
        for player in players:
            if player.is_active and player.dice.count > 0:
                total += player.dice.count_face(face, wilds_active)
        return total

    @staticmethod
    def resolve_dudo(players: List[Player], bid: Bid, bidder_idx: int,
                     challenger_idx: int, wilds_active: bool = True) -> tuple[bool, int, str]:
        """Resolve a Dudo challenge.

        Args:
            players: List of all players
            bid: The bid being challenged
            bidder_idx: Index of player who made the bid
            challenger_idx: Index of player who called Dudo
            wilds_active: Whether ones are wild

        Returns:
            Tuple of (bid_was_correct, loser_idx, message)
        """
        actual_count = RulesEngine.count_dice_in_play(players, bid.face, wilds_active)

        if actual_count >= bid.quantity:
            # Bid was correct or exceeded, challenger loses
            message = f"Bid was correct! There are {actual_count} {bid.face}s. {players[challenger_idx].name} loses a die."
            return True, challenger_idx, message
        else:
            # Bid was wrong, bidder loses
            message = f"Bid was wrong! There are only {actual_count} {bid.face}s. {players[bidder_idx].name} loses a die."
            return False, bidder_idx, message

    @staticmethod
    def resolve_calza(players: List[Player], bid: Bid, caller_idx: int,
                     wilds_active: bool = True) -> tuple[bool, str]:
        """Resolve a Calza call.

        Args:
            players: List of all players
            bid: The bid being called as exact
            caller_idx: Index of player who called Calza
            wilds_active: Whether ones are wild

        Returns:
            Tuple of (was_exact, message)
        """
        actual_count = RulesEngine.count_dice_in_play(players, bid.face, wilds_active)

        if actual_count == bid.quantity:
            # Exact! Caller gains a die
            message = f"Calza! Exactly {actual_count} {bid.face}s! {players[caller_idx].name} gains a die."
            return True, message
        else:
            # Wrong! Caller loses a die
            message = f"Not exact! There are {actual_count} {bid.face}s, not {bid.quantity}. {players[caller_idx].name} loses a die."
            return False, message

    @staticmethod
    def check_palifico_trigger(players: List[Player]) -> int:
        """Check if any player just triggered Palifico.

        Args:
            players: List of all players

        Returns:
            Index of player in Palifico, or -1 if none
        """
        for idx, player in enumerate(players):
            if player.is_in_palifico():
                return idx
        return -1

    @staticmethod
    def check_winner(players: List[Player]) -> int:
        """Check if there's a winner.

        Args:
            players: List of all players

        Returns:
            Index of winning player, or -1 if no winner yet
        """
        active_players = [i for i, p in enumerate(players) if p.is_active]
        if len(active_players) == 1:
            return active_players[0]
        return -1

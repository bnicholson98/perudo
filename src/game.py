"""Main game orchestration for Perudo."""
from typing import List, Optional
from src.player import Player
from src.bid import Bid
from src.rules import RulesEngine
from src.ui import UI


class PerudoGame:
    """Main game controller for Perudo."""

    def __init__(self):
        """Initialize the game."""
        self.players: List[Player] = []
        self.current_player_idx: int = 0
        self.current_bid: Optional[Bid] = None
        self.last_bidder_idx: int = -1
        self.is_palifico: bool = False
        self.palifico_player_idx: int = -1
        self.ui = UI()
        self.rules = RulesEngine()

    def setup(self):
        """Set up the game with players."""
        self.ui.print_banner()
        self.ui.print_rules_summary()

        player_count = self.ui.get_player_count()
        names = self.ui.get_player_names(player_count)

        self.players = [Player(name) for name in names]
        self.ui.show_message(f"Game starting with {player_count} players!")

    def start_new_round(self, starting_player_idx: int):
        """Start a new round.

        Args:
            starting_player_idx: Index of player who starts the round
        """
        self.ui.show_round_start()

        # Roll dice for all active players
        for player in self.players:
            if player.is_active:
                player.roll_dice()

        # Check for Palifico trigger
        palifico_idx = self.rules.check_palifico_trigger(self.players)
        if palifico_idx >= 0:
            self.is_palifico = True
            self.palifico_player_idx = palifico_idx
            self.players[palifico_idx].trigger_palifico()
            self.ui.show_message(
                f"{self.players[palifico_idx].name} has triggered PALIFICO! "
                f"Face value will be locked this round, and ones are NOT wild."
            )
        else:
            self.is_palifico = False
            self.palifico_player_idx = -1

        # Reset bid state
        self.current_bid = None
        self.last_bidder_idx = -1
        self.current_player_idx = starting_player_idx

        # Show each player their dice
        for player in self.players:
            if player.is_active:
                self.ui.pause_for_player_change(player)
                self.ui.show_player_dice(player)
                input("\nPress Enter when done viewing...")
                self.ui.clear_screen()

    def get_next_active_player(self, current_idx: int) -> int:
        """Get the index of the next active player.

        Args:
            current_idx: Current player index

        Returns:
            Index of next active player
        """
        idx = (current_idx + 1) % len(self.players)
        while not self.players[idx].is_active:
            idx = (idx + 1) % len(self.players)
        return idx

    def get_total_dice(self) -> int:
        """Get total number of dice in play.

        Returns:
            Total dice count across all active players
        """
        return sum(p.dice.count for p in self.players if p.is_active)

    def play_turn(self) -> bool:
        """Play one turn.

        Returns:
            True if round continues, False if round ended
        """
        current_player = self.players[self.current_player_idx]

        self.ui.pause_for_player_change(current_player)
        self.ui.show_game_state(
            self.players,
            self.current_bid,
            self.current_player_idx,
            self.is_palifico
        )
        self.ui.show_player_dice(current_player)

        # Get player action
        action = self.ui.get_player_action(current_player, self.current_bid is not None)

        if action == "bid":
            return self.handle_bid()
        elif action == "dudo":
            return self.handle_dudo()
        elif action == "calza":
            return self.handle_calza()

        return True

    def handle_bid(self) -> bool:
        """Handle a bid action.

        Returns:
            True (continue round)
        """
        while True:
            bid = self.ui.get_bid_input(self.current_bid, self.is_palifico)
            if bid is None:
                continue

            total_dice = self.get_total_dice()
            is_valid, error = bid.is_valid_raise(self.current_bid, self.is_palifico, total_dice)
            if is_valid:
                self.current_bid = bid
                self.last_bidder_idx = self.current_player_idx
                self.ui.show_message(f"{self.players[self.current_player_idx].name} bids: {bid}")
                input("Press Enter to continue...")
                self.ui.clear_screen()
                self.current_player_idx = self.get_next_active_player(self.current_player_idx)
                return True
            else:
                self.ui.show_message(f"Invalid bid: {error}")

    def handle_dudo(self) -> bool:
        """Handle a Dudo challenge.

        Returns:
            False (end round)
        """
        if self.current_bid is None:
            self.ui.show_message("Cannot call Dudo - no bid yet!")
            return True

        self.ui.show_message(f"{self.players[self.current_player_idx].name} calls DUDO!")
        self.ui.show_all_dice(self.players)

        wilds_active = not self.is_palifico
        bid_correct, loser_idx, message = self.rules.resolve_dudo(
            self.players,
            self.current_bid,
            self.last_bidder_idx,
            self.current_player_idx,
            wilds_active
        )

        self.ui.show_message(message)
        self.players[loser_idx].lose_die()

        input("Press Enter to continue...")

        # Next round starts with the loser (if still active) or next player
        if self.players[loser_idx].is_active:
            self.current_player_idx = loser_idx
        else:
            self.current_player_idx = self.get_next_active_player(loser_idx)

        return False

    def handle_calza(self) -> bool:
        """Handle a Calza call.

        Returns:
            False (end round)
        """
        if self.current_bid is None:
            self.ui.show_message("Cannot call Calza - no bid yet!")
            return True

        self.ui.show_message(f"{self.players[self.current_player_idx].name} calls CALZA!")
        self.ui.show_all_dice(self.players)

        wilds_active = not self.is_palifico
        was_exact, message = self.rules.resolve_calza(
            self.players,
            self.current_bid,
            self.current_player_idx,
            wilds_active
        )

        self.ui.show_message(message)

        if was_exact:
            self.players[self.current_player_idx].gain_die()
            # Caller starts next round
        else:
            self.players[self.current_player_idx].lose_die()
            # Loser starts next round if still active
            if not self.players[self.current_player_idx].is_active:
                self.current_player_idx = self.get_next_active_player(self.current_player_idx)

        input("Press Enter to continue...")
        return False

    def play(self):
        """Main game loop."""
        self.setup()

        while True:
            # Check for winner
            winner_idx = self.rules.check_winner(self.players)
            if winner_idx >= 0:
                self.ui.show_winner(self.players[winner_idx])
                break

            # Start new round
            self.start_new_round(self.current_player_idx)

            # Play turns until round ends
            while True:
                continue_round = self.play_turn()
                if not continue_round:
                    break

                # Check for winner after each turn
                winner_idx = self.rules.check_winner(self.players)
                if winner_idx >= 0:
                    self.ui.show_winner(self.players[winner_idx])
                    return

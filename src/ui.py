"""Terminal UI for Perudo game."""
from typing import List, Optional
from src.player import Player
from src.bid import Bid


class UI:
    """Handles all terminal input/output for the game."""

    @staticmethod
    def clear_screen():
        """Clear the terminal screen."""
        print("\n" * 50)

    @staticmethod
    def print_banner():
        """Print the game banner."""
        print("=" * 50)
        print("                    PERUDO")
        print("=" * 50)
        print()

    @staticmethod
    def print_rules_summary():
        """Print a brief rules summary."""
        print("Quick Rules:")
        print("- Ones are WILD (except during Palifico)")
        print("- Bid higher quantity OR higher face value")
        print("- Call 'dudo' to challenge, 'calza' for exact match")
        print("- Palifico: When reduced to 1 die, face value locks")
        print()

    @staticmethod
    def get_player_count() -> int:
        """Get number of players from user.

        Returns:
            Number of players (2-6)
        """
        while True:
            try:
                count = int(input("Enter number of players (2-6): "))
                if 2 <= count <= 6:
                    return count
                print("Please enter a number between 2 and 6.")
            except ValueError:
                print("Please enter a valid number.")

    @staticmethod
    def get_player_names(count: int) -> List[str]:
        """Get player names from user.

        Args:
            count: Number of players

        Returns:
            List of player names
        """
        names = []
        for i in range(count):
            name = input(f"Enter name for Player {i + 1}: ").strip()
            if not name:
                name = f"Player {i + 1}"
            names.append(name)
        return names

    @staticmethod
    def show_player_dice(player: Player):
        """Show a player their dice.

        Args:
            player: The player whose dice to show
        """
        print(f"\n{player.name}, your dice: {player.dice.get_values()}")

    @staticmethod
    def show_all_dice(players: List[Player]):
        """Show all players' dice (for reveal).

        Args:
            players: List of all players
        """
        print("\n" + "=" * 50)
        print("REVEALING ALL DICE:")
        print("=" * 50)
        for player in players:
            if player.is_active and player.dice.count > 0:
                print(f"{player.name}: {player.dice.get_values()}")
        print("=" * 50 + "\n")

    @staticmethod
    def show_game_state(players: List[Player], current_bid: Optional[Bid],
                       current_player_idx: int, is_palifico: bool):
        """Show current game state.

        Args:
            players: List of all players
            current_bid: Current bid (None if start of round)
            current_player_idx: Index of current player
            is_palifico: Whether this is a Palifico round
        """
        print("\n" + "-" * 50)
        print("GAME STATE:")
        for idx, player in enumerate(players):
            marker = " <- CURRENT" if idx == current_player_idx else ""
            if player.is_active:
                palifico_marker = " [PALIFICO]" if player.is_in_palifico() else ""
                print(f"  {player.name}: {player.dice.count} dice{palifico_marker}{marker}")
            else:
                print(f"  {player.name}: ELIMINATED{marker}")

        if is_palifico:
            print("\n  *** PALIFICO ROUND - Face value locked, ones NOT wild ***")

        if current_bid:
            print(f"\nCurrent bid: {current_bid}")
        else:
            print("\nNo bid yet this round.")
        print("-" * 50 + "\n")

    @staticmethod
    def get_player_action(player: Player, has_bid: bool) -> str:
        """Get action from player.

        Args:
            player: The current player
            has_bid: Whether there's a current bid

        Returns:
            Action string ('bid', 'dudo', or 'calza')
        """
        print(f"\n{player.name}'s turn:")

        if not has_bid:
            print("  [1] Make a bid")
            while True:
                choice = input("Choose action (1): ").strip()
                if choice == "1" or choice == "":
                    return "bid"
        else:
            print("  [1] Raise the bid")
            print("  [2] Call 'Dudo' (challenge)")
            print("  [3] Call 'Calza' (claim exact)")

            while True:
                choice = input("Choose action (1/2/3): ").strip()
                if choice == "1":
                    return "bid"
                elif choice == "2":
                    return "dudo"
                elif choice == "3":
                    return "calza"
                print("Invalid choice. Please enter 1, 2, or 3.")

    @staticmethod
    def get_bid_input(previous_bid: Optional[Bid], is_palifico: bool) -> Optional[Bid]:
        """Get bid from user.

        Args:
            previous_bid: Previous bid (None if first)
            is_palifico: Whether this is a Palifico round

        Returns:
            Bid object or None if cancelled
        """
        print("\nEnter your bid:")

        while True:
            try:
                quantity = int(input("  Quantity: "))

                if is_palifico and previous_bid:
                    face = previous_bid.face
                    print(f"  Face value locked at: {face} (Palifico)")
                else:
                    face = int(input("  Face value (1-6): "))

                if face < 1 or face > 6:
                    print("Face value must be between 1 and 6.")
                    continue

                return Bid(quantity, face)

            except ValueError:
                print("Please enter valid numbers.")

    @staticmethod
    def pause_for_player_change(next_player: Player):
        """Pause and prompt for next player.

        Args:
            next_player: The next player
        """
        print(f"\n--- Pass to {next_player.name} ---")
        input("Press Enter when ready...")
        UI.clear_screen()

    @staticmethod
    def show_message(message: str):
        """Show a message to the user.

        Args:
            message: Message to display
        """
        print(f"\n{message}\n")

    @staticmethod
    def show_winner(player: Player):
        """Display the winner.

        Args:
            player: The winning player
        """
        print("\n" + "=" * 50)
        print(f"         {player.name} WINS!")
        print("=" * 50 + "\n")

    @staticmethod
    def show_round_start():
        """Display round start message."""
        print("\n" + "=" * 50)
        print("           NEW ROUND - ROLLING DICE")
        print("=" * 50)

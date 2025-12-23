"""Integration tests for game flow."""
import pytest
from src.game import PerudoGame
from src.player import Player
from src.bid import Bid
from src.rules import RulesEngine


class TestGameInitialization:
    """Tests for game initialization."""

    def test_game_creation(self):
        """Test basic game creation."""
        game = PerudoGame()
        assert game.players == []
        assert game.current_player_idx == 0
        assert game.current_bid is None
        assert game.is_palifico is False

    def test_get_total_dice(self):
        """Test calculating total dice in play."""
        game = PerudoGame()
        game.players = [Player("Alice"), Player("Bob"), Player("Charlie")]

        # All players have 5 dice = 15 total
        assert game.get_total_dice() == 15

        # Reduce one player
        game.players[0].lose_die()
        assert game.get_total_dice() == 14

        # Eliminate one player
        for _ in range(5):
            game.players[1].lose_die()
        assert game.get_total_dice() == 9  # 4 + 0 + 5


class TestNextActivePlayer:
    """Tests for finding next active player."""

    def test_get_next_active_player_all_active(self):
        """Test getting next player when all are active."""
        game = PerudoGame()
        game.players = [Player("Alice"), Player("Bob"), Player("Charlie")]

        next_idx = game.get_next_active_player(0)
        assert next_idx == 1

        next_idx = game.get_next_active_player(2)
        assert next_idx == 0  # Wraps around

    def test_get_next_active_player_skip_inactive(self):
        """Test getting next player skipping inactive ones."""
        game = PerudoGame()
        game.players = [Player("Alice"), Player("Bob"), Player("Charlie")]

        # Eliminate Bob
        for _ in range(5):
            game.players[1].lose_die()

        # From Alice, should skip Bob and go to Charlie
        next_idx = game.get_next_active_player(0)
        assert next_idx == 2

        # From Charlie, should wrap to Alice
        next_idx = game.get_next_active_player(2)
        assert next_idx == 0

    def test_get_next_active_player_multiple_inactive(self):
        """Test with multiple inactive players."""
        game = PerudoGame()
        game.players = [
            Player("Alice"),
            Player("Bob"),
            Player("Charlie"),
            Player("Diana")
        ]

        # Eliminate Bob and Charlie
        for _ in range(5):
            game.players[1].lose_die()
            game.players[2].lose_die()

        # From Alice, should skip Bob and Charlie, go to Diana
        next_idx = game.get_next_active_player(0)
        assert next_idx == 3


class TestBidValidationIntegration:
    """Integration tests for bid validation with game state."""

    def test_first_bid_validation(self):
        """Test first bid validation with total dice."""
        game = PerudoGame()
        game.players = [Player("Alice"), Player("Bob")]

        total_dice = game.get_total_dice()

        # Valid first bid
        bid = Bid(5, 3)
        is_valid, _ = bid.is_valid_raise(None, False, total_dice)
        assert is_valid

        # Invalid first bid (exceeds total)
        bid = Bid(15, 3)
        is_valid, _ = bid.is_valid_raise(None, False, total_dice)
        assert not is_valid

        # Invalid first bid (face value 1)
        bid = Bid(3, 1)
        is_valid, _ = bid.is_valid_raise(None, False, total_dice)
        assert not is_valid

    def test_bid_validation_as_dice_decrease(self):
        """Test bid validation as total dice decrease."""
        game = PerudoGame()
        game.players = [Player("Alice"), Player("Bob")]

        # Initially 10 dice
        bid = Bid(10, 3)
        is_valid, _ = bid.is_valid_raise(None, False, game.get_total_dice())
        assert is_valid

        # Lose some dice
        game.players[0].lose_die()
        game.players[0].lose_die()

        # Now 8 dice total, bidding 10 should fail
        bid = Bid(10, 3)
        is_valid, _ = bid.is_valid_raise(None, False, game.get_total_dice())
        assert not is_valid


class TestPalificoIntegration:
    """Integration tests for Palifico rounds."""

    def test_palifico_detection(self):
        """Test Palifico detection in game."""
        game = PerudoGame()
        game.players = [Player("Alice"), Player("Bob")]

        # No palifico initially
        palifico_idx = game.rules.check_palifico_trigger(game.players)
        assert palifico_idx == -1

        # Reduce Alice to 1 die
        for _ in range(4):
            game.players[0].lose_die()

        palifico_idx = game.rules.check_palifico_trigger(game.players)
        assert palifico_idx == 0

    def test_palifico_bid_restrictions(self):
        """Test bid restrictions during Palifico."""
        game = PerudoGame()
        game.players = [Player("Alice"), Player("Bob")]

        # Trigger palifico
        for _ in range(4):
            game.players[0].lose_die()
        game.is_palifico = True

        # Set up first bid
        previous_bid = Bid(2, 4)

        # Valid: increase quantity, same face
        bid = Bid(3, 4)
        is_valid, _ = bid.is_valid_raise(previous_bid, True, game.get_total_dice())
        assert is_valid

        # Invalid: change face
        bid = Bid(3, 5)
        is_valid, _ = bid.is_valid_raise(previous_bid, True, game.get_total_dice())
        assert not is_valid


class TestWinnerDetection:
    """Integration tests for winner detection."""

    def test_no_winner_initially(self):
        """Test no winner at game start."""
        game = PerudoGame()
        game.players = [Player("Alice"), Player("Bob"), Player("Charlie")]

        winner_idx = game.rules.check_winner(game.players)
        assert winner_idx == -1

    def test_winner_after_eliminations(self):
        """Test winner detection after eliminations."""
        game = PerudoGame()
        game.players = [Player("Alice"), Player("Bob"), Player("Charlie")]

        # Eliminate Bob and Charlie
        for _ in range(5):
            game.players[1].lose_die()
            game.players[2].lose_die()

        winner_idx = game.rules.check_winner(game.players)
        assert winner_idx == 0  # Alice wins


class TestRoundFlow:
    """Integration tests for round flow."""

    def test_dudo_resolution_updates_players(self):
        """Test that Dudo resolution properly updates player state."""
        game = PerudoGame()
        game.players = [Player("Alice"), Player("Bob")]
        game.players[0].dice.values = [2, 2, 2, 2, 2]
        game.players[1].dice.values = [3, 3, 3, 3, 3]

        # Alice bids 5 twos, Bob challenges
        bid = Bid(5, 2)
        bid_correct, loser_idx, message = game.rules.resolve_dudo(
            game.players, bid, bidder_idx=0, challenger_idx=1, wilds_active=True
        )

        # Bid is correct (5 twos), Bob should be the loser
        assert loser_idx == 1

        # Simulate losing die
        game.players[loser_idx].lose_die()
        assert game.players[1].get_dice_count() == 4

    def test_calza_resolution_updates_players(self):
        """Test that Calza resolution properly updates player state."""
        game = PerudoGame()
        game.players = [Player("Alice"), Player("Bob")]
        game.players[0].dice.values = [3, 3, 4, 5, 6]
        game.players[1].dice.values = [1, 3, 2, 4, 5]

        # Bid exactly 4 threes
        bid = Bid(4, 3)
        was_exact, message = game.rules.resolve_calza(
            game.players, bid, caller_idx=1, wilds_active=True
        )

        assert was_exact is True

        # Simulate gaining die
        game.players[1].gain_die()
        assert game.players[1].get_dice_count() == 5  # Can't go above 5


class TestGameStateTransitions:
    """Integration tests for game state transitions."""

    def test_normal_to_palifico_transition(self):
        """Test transition from normal round to Palifico."""
        game = PerudoGame()
        game.players = [Player("Alice"), Player("Bob")]

        # Normal state
        assert game.is_palifico is False

        # Reduce Alice to 1 die
        for _ in range(4):
            game.players[0].lose_die()

        # Check if palifico should trigger
        palifico_idx = game.rules.check_palifico_trigger(game.players)
        if palifico_idx >= 0:
            game.is_palifico = True
            game.players[palifico_idx].trigger_palifico()

        assert game.is_palifico is True
        assert game.players[0].has_had_palifico is True

    def test_palifico_ends_after_dice_change(self):
        """Test that Palifico state ends when player's dice change."""
        game = PerudoGame()
        game.players = [Player("Alice"), Player("Bob")]

        # Trigger palifico
        for _ in range(4):
            game.players[0].lose_die()
        game.players[0].trigger_palifico()
        game.is_palifico = True

        # Player gains a die
        game.players[0].gain_die()

        # Check palifico should not retrigger
        palifico_idx = game.rules.check_palifico_trigger(game.players)
        assert palifico_idx == -1


class TestMultiPlayerScenarios:
    """Integration tests for multi-player scenarios."""

    def test_three_player_elimination_order(self):
        """Test elimination order with three players."""
        game = PerudoGame()
        game.players = [
            Player("Alice"),
            Player("Bob"),
            Player("Charlie")
        ]

        # Eliminate Bob first
        for _ in range(5):
            game.players[1].lose_die()

        assert game.players[1].is_active is False
        assert game.rules.check_winner(game.players) == -1

        # Eliminate Charlie
        for _ in range(5):
            game.players[2].lose_die()

        # Alice should win
        winner_idx = game.rules.check_winner(game.players)
        assert winner_idx == 0

    def test_four_player_game_flow(self):
        """Test basic flow with four players."""
        game = PerudoGame()
        game.players = [
            Player("Alice"),
            Player("Bob"),
            Player("Charlie"),
            Player("Diana")
        ]

        # Everyone starts with 5 dice
        assert game.get_total_dice() == 20

        # Simulate some losses
        game.players[0].lose_die()  # Alice: 4
        game.players[1].lose_die()
        game.players[1].lose_die()  # Bob: 3
        game.players[2].lose_die()
        game.players[2].lose_die()
        game.players[2].lose_die()  # Charlie: 2

        assert game.get_total_dice() == 14  # 4+3+2+5
        assert game.rules.check_winner(game.players) == -1


class TestEdgeCasesIntegration:
    """Integration tests for edge cases."""

    def test_bidding_max_dice_as_game_progresses(self):
        """Test maximum bid validation throughout game."""
        game = PerudoGame()
        game.players = [Player("Alice"), Player("Bob")]

        # Can bid 10 at start
        bid = Bid(10, 3)
        is_valid, _ = bid.is_valid_raise(None, False, game.get_total_dice())
        assert is_valid

        # After losses, can't bid original max
        for _ in range(3):
            game.players[0].lose_die()
            game.players[1].lose_die()

        bid = Bid(10, 3)
        is_valid, _ = bid.is_valid_raise(None, False, game.get_total_dice())
        assert not is_valid

        # But can bid current total
        total = game.get_total_dice()
        bid = Bid(total, 3)
        is_valid, _ = bid.is_valid_raise(None, False, total)
        assert is_valid

    def test_last_player_cannot_lose(self):
        """Test that game ends when only one player remains."""
        game = PerudoGame()
        game.players = [Player("Alice"), Player("Bob")]

        # Eliminate Alice
        for _ in range(5):
            game.players[0].lose_die()

        winner_idx = game.rules.check_winner(game.players)
        assert winner_idx == 1  # Bob wins
        assert not game.players[0].is_active
        assert game.players[1].is_active

"""Unit tests for game rules engine."""
import pytest
from src.player import Player
from src.bid import Bid
from src.rules import RulesEngine


class TestCountDiceInPlay:
    """Tests for counting dice across all players."""

    def test_count_dice_basic(self):
        """Test counting dice with basic values."""
        players = [Player("Alice"), Player("Bob")]
        players[0].dice.values = [3, 3, 4, 5, 6]
        players[1].dice.values = [1, 3, 2, 4, 5]

        # Count 3s with wilds: Alice has 2, Bob has 1 (3) + 1 (wild 1) = 4 total
        count = RulesEngine.count_dice_in_play(players, 3, wilds_active=True)
        assert count == 4

    def test_count_dice_without_wilds(self):
        """Test counting dice without wilds (Palifico)."""
        players = [Player("Alice"), Player("Bob")]
        players[0].dice.values = [1, 1, 3, 3, 5]
        players[1].dice.values = [1, 3, 2, 4, 5]

        # Count 3s without wilds: Alice has 2, Bob has 1 = 3 total
        count = RulesEngine.count_dice_in_play(players, 3, wilds_active=False)
        assert count == 3

    def test_count_dice_with_inactive_player(self):
        """Test that inactive players are not counted."""
        players = [Player("Alice"), Player("Bob"), Player("Charlie")]
        players[0].dice.values = [3, 3, 3, 3, 3]
        players[1].dice.values = [3, 3, 3, 3, 3]
        players[2].dice.values = [3, 3, 3, 3, 3]
        players[2].is_active = False

        # Should only count Alice and Bob
        count = RulesEngine.count_dice_in_play(players, 3, wilds_active=True)
        assert count == 10  # 5 from Alice + 5 from Bob

    def test_count_ones(self):
        """Test counting ones specifically."""
        players = [Player("Alice"), Player("Bob")]
        players[0].dice.values = [1, 1, 2, 3, 4]
        players[1].dice.values = [1, 5, 6, 2, 3]

        # When counting 1s, only actual 1s count
        count = RulesEngine.count_dice_in_play(players, 1, wilds_active=True)
        assert count == 3

    def test_count_with_all_wilds(self):
        """Test counting when all dice are wild."""
        players = [Player("Alice"), Player("Bob")]
        players[0].dice.values = [1, 1, 1, 1, 1]
        players[1].dice.values = [1, 1, 1, 1, 1]

        # Counting any face should count all 10 wild 1s
        count = RulesEngine.count_dice_in_play(players, 4, wilds_active=True)
        assert count == 10


class TestResolveDudo:
    """Tests for Dudo challenge resolution."""

    def test_dudo_bid_was_correct(self):
        """Test Dudo when bid is correct."""
        players = [Player("Alice"), Player("Bob")]
        players[0].dice.values = [3, 3, 4, 5, 6]
        players[1].dice.values = [1, 3, 2, 4, 5]  # One wild 1, one 3

        bid = Bid(4, 3)  # Bid: four 3s
        # There are exactly 4 (2 from Alice, 1 from Bob, 1 wild from Bob)
        bid_correct, loser_idx, message = RulesEngine.resolve_dudo(
            players, bid, bidder_idx=0, challenger_idx=1, wilds_active=True
        )

        assert bid_correct is True
        assert loser_idx == 1  # Challenger loses
        assert "Bob" in message
        assert "loses a die" in message

    def test_dudo_bid_was_wrong(self):
        """Test Dudo when bid is wrong."""
        players = [Player("Alice"), Player("Bob")]
        players[0].dice.values = [2, 2, 4, 5, 6]
        players[1].dice.values = [3, 3, 2, 4, 5]

        bid = Bid(10, 3)  # Bid: ten 3s (impossible with 10 dice)
        bid_correct, loser_idx, message = RulesEngine.resolve_dudo(
            players, bid, bidder_idx=0, challenger_idx=1, wilds_active=True
        )

        assert bid_correct is False
        assert loser_idx == 0  # Bidder loses
        assert "Alice" in message
        assert "loses a die" in message

    def test_dudo_bid_exceeded(self):
        """Test Dudo when actual count exceeds bid."""
        players = [Player("Alice"), Player("Bob")]
        players[0].dice.values = [3, 3, 3, 3, 3]
        players[1].dice.values = [3, 3, 3, 3, 3]

        bid = Bid(5, 3)  # Bid: five 3s (but there are 10)
        bid_correct, loser_idx, message = RulesEngine.resolve_dudo(
            players, bid, bidder_idx=0, challenger_idx=1, wilds_active=True
        )

        assert bid_correct is True  # Bid was correct (actually exceeded)
        assert loser_idx == 1  # Challenger loses

    def test_dudo_palifico_no_wilds(self):
        """Test Dudo during Palifico (no wilds)."""
        players = [Player("Alice"), Player("Bob")]
        players[0].dice.values = [1, 1, 3, 3, 5]
        players[1].dice.values = [1, 3, 2, 4, 5]

        bid = Bid(4, 3)  # Bid: four 3s
        # Without wilds: only 3 actual 3s
        bid_correct, loser_idx, message = RulesEngine.resolve_dudo(
            players, bid, bidder_idx=0, challenger_idx=1, wilds_active=False
        )

        assert bid_correct is False
        assert loser_idx == 0  # Bidder loses


class TestResolveCalza:
    """Tests for Calza resolution."""

    def test_calza_exact_match(self):
        """Test Calza when bid is exactly correct."""
        players = [Player("Alice"), Player("Bob")]
        players[0].dice.values = [3, 3, 4, 5, 6]
        players[1].dice.values = [1, 3, 2, 4, 5]

        bid = Bid(4, 3)  # Exactly 4 threes
        was_exact, message = RulesEngine.resolve_calza(
            players, bid, caller_idx=1, wilds_active=True
        )

        assert was_exact is True
        assert "Calza" in message
        assert "Bob" in message
        assert "gains a die" in message

    def test_calza_too_high(self):
        """Test Calza when bid is too high."""
        players = [Player("Alice"), Player("Bob")]
        players[0].dice.values = [3, 3, 4, 5, 6]
        players[1].dice.values = [3, 2, 2, 4, 5]

        bid = Bid(5, 3)  # Bid 5, but only 3 actual threes
        was_exact, message = RulesEngine.resolve_calza(
            players, bid, caller_idx=1, wilds_active=True
        )

        assert was_exact is False
        assert "Not exact" in message
        assert "Bob" in message
        assert "loses a die" in message

    def test_calza_too_low(self):
        """Test Calza when bid is too low."""
        players = [Player("Alice"), Player("Bob")]
        players[0].dice.values = [3, 3, 3, 3, 3]
        players[1].dice.values = [1, 1, 1, 3, 3]

        bid = Bid(5, 3)  # Bid 5, but there are 8
        was_exact, message = RulesEngine.resolve_calza(
            players, bid, caller_idx=1, wilds_active=True
        )

        assert was_exact is False
        assert "Not exact" in message

    def test_calza_palifico(self):
        """Test Calza during Palifico."""
        players = [Player("Alice"), Player("Bob")]
        players[0].dice.values = [1, 1, 3, 3, 5]
        players[1].dice.values = [3, 2, 2, 4, 5]

        bid = Bid(3, 3)  # Exactly 3 threes without wilds
        was_exact, message = RulesEngine.resolve_calza(
            players, bid, caller_idx=0, wilds_active=False
        )

        assert was_exact is True


class TestCheckPalificoTrigger:
    """Tests for Palifico trigger detection."""

    def test_no_palifico_trigger(self):
        """Test when no player is in Palifico."""
        players = [Player("Alice"), Player("Bob")]
        idx = RulesEngine.check_palifico_trigger(players)
        assert idx == -1

    def test_palifico_trigger_one_die(self):
        """Test Palifico trigger when player has 1 die."""
        players = [Player("Alice"), Player("Bob")]
        # Reduce Alice to 1 die
        for _ in range(4):
            players[0].lose_die()

        idx = RulesEngine.check_palifico_trigger(players)
        assert idx == 0  # Alice triggers Palifico

    def test_palifico_not_triggered_twice(self):
        """Test Palifico doesn't trigger again for same player."""
        players = [Player("Alice"), Player("Bob")]
        # Reduce Alice to 1 die and trigger palifico
        for _ in range(4):
            players[0].lose_die()
        players[0].trigger_palifico()

        idx = RulesEngine.check_palifico_trigger(players)
        assert idx == -1  # Should not trigger again

    def test_palifico_multiple_players(self):
        """Test Palifico with multiple players."""
        players = [Player("Alice"), Player("Bob"), Player("Charlie")]
        # Reduce Bob to 1 die
        for _ in range(4):
            players[1].lose_die()

        idx = RulesEngine.check_palifico_trigger(players)
        assert idx == 1  # Bob triggers Palifico


class TestCheckWinner:
    """Tests for winner detection."""

    def test_no_winner_all_active(self):
        """Test when all players are still active."""
        players = [Player("Alice"), Player("Bob"), Player("Charlie")]
        winner_idx = RulesEngine.check_winner(players)
        assert winner_idx == -1

    def test_winner_one_active(self):
        """Test when only one player remains."""
        players = [Player("Alice"), Player("Bob"), Player("Charlie")]
        # Eliminate Bob and Charlie
        for _ in range(5):
            players[1].lose_die()
            players[2].lose_die()

        winner_idx = RulesEngine.check_winner(players)
        assert winner_idx == 0  # Alice wins

    def test_no_winner_two_active(self):
        """Test when two players are still active."""
        players = [Player("Alice"), Player("Bob"), Player("Charlie")]
        # Eliminate only Charlie
        for _ in range(5):
            players[2].lose_die()

        winner_idx = RulesEngine.check_winner(players)
        assert winner_idx == -1  # No winner yet

    def test_winner_last_player_standing(self):
        """Test winner with multiple eliminations."""
        players = [
            Player("Alice"),
            Player("Bob"),
            Player("Charlie"),
            Player("Diana")
        ]
        # Eliminate everyone except Diana
        for _ in range(5):
            players[0].lose_die()
            players[1].lose_die()
            players[2].lose_die()

        winner_idx = RulesEngine.check_winner(players)
        assert winner_idx == 3  # Diana wins


class TestIntegrationScenarios:
    """Integration tests for complex game scenarios."""

    def test_full_round_scenario(self):
        """Test a complete round scenario."""
        players = [Player("Alice"), Player("Bob")]
        players[0].roll_dice()
        players[1].roll_dice()

        # Create a bid and challenge it
        bid = Bid(5, 3)
        bid_correct, loser_idx, message = RulesEngine.resolve_dudo(
            players, bid, bidder_idx=0, challenger_idx=1, wilds_active=True
        )

        # Verify one player loses
        assert loser_idx in [0, 1]
        assert "loses a die" in message

    def test_game_to_completion(self):
        """Test game scenario to completion."""
        players = [Player("Alice"), Player("Bob")]

        # Simulate Alice losing all dice
        for _ in range(5):
            players[0].lose_die()

        # Check winner
        winner_idx = RulesEngine.check_winner(players)
        assert winner_idx == 1  # Bob wins
        assert not players[0].is_active
        assert players[1].is_active

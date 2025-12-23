"""Unit tests for bid validation logic."""
import pytest
from src.bid import Bid


class TestBidCreation:
    """Tests for bid creation and representation."""

    def test_bid_creation(self):
        """Test basic bid creation."""
        bid = Bid(5, 3)
        assert bid.quantity == 5
        assert bid.face == 3

    def test_bid_string_representation(self):
        """Test bid string formatting."""
        bid = Bid(7, 4)
        assert str(bid) == "7 4s"

    def test_bid_repr(self):
        """Test bid developer representation."""
        bid = Bid(3, 2)
        assert repr(bid) == "Bid(3, 2)"


class TestFirstBid:
    """Tests for first bid of a round."""

    def test_valid_first_bid(self):
        """Test valid first bid."""
        bid = Bid(3, 4)
        is_valid, error = bid.is_valid_raise(None, False, 10)
        assert is_valid
        assert error == ""

    def test_first_bid_cannot_be_ones(self):
        """Test that first bid cannot be on ones."""
        bid = Bid(3, 1)
        is_valid, error = bid.is_valid_raise(None, False, 10)
        assert not is_valid
        assert "Cannot start the round with a bid on ones" in error

    def test_first_bid_invalid_quantity(self):
        """Test first bid with invalid quantity."""
        bid = Bid(0, 3)
        is_valid, error = bid.is_valid_raise(None, False, 10)
        assert not is_valid
        assert "Invalid bid values" in error

    def test_first_bid_invalid_face(self):
        """Test first bid with invalid face value."""
        bid = Bid(3, 7)
        is_valid, error = bid.is_valid_raise(None, False, 10)
        assert not is_valid
        assert "Invalid bid values" in error

    def test_first_bid_exceeds_total_dice(self):
        """Test first bid exceeding total dice in play."""
        bid = Bid(15, 3)
        is_valid, error = bid.is_valid_raise(None, False, 10)
        assert not is_valid
        assert "Cannot bid more than 10 dice" in error


class TestStandardBidding:
    """Tests for standard bidding (non-ones to non-ones)."""

    def test_increase_quantity_same_face(self):
        """Test increasing quantity with same face value."""
        previous = Bid(5, 3)
        bid = Bid(6, 3)
        is_valid, error = bid.is_valid_raise(previous, False, 20)
        assert is_valid
        assert error == ""

    def test_cannot_keep_same_quantity_and_face(self):
        """Test that you can't bid the same quantity and face."""
        previous = Bid(5, 3)
        bid = Bid(5, 3)
        is_valid, error = bid.is_valid_raise(previous, False, 20)
        assert not is_valid

    def test_increase_face_same_quantity(self):
        """Test increasing face value with same quantity."""
        previous = Bid(5, 3)
        bid = Bid(5, 5)
        is_valid, error = bid.is_valid_raise(previous, False, 20)
        assert is_valid

    def test_cannot_decrease_face_same_quantity(self):
        """Test that you can't decrease face value with same quantity."""
        previous = Bid(5, 4)
        bid = Bid(5, 3)
        is_valid, error = bid.is_valid_raise(previous, False, 20)
        assert not is_valid

    def test_increase_both_quantity_and_face(self):
        """Test increasing both quantity and face value."""
        previous = Bid(5, 3)
        bid = Bid(6, 4)
        is_valid, error = bid.is_valid_raise(previous, False, 20)
        assert is_valid

    def test_cannot_decrease_quantity(self):
        """Test that you can't decrease quantity."""
        previous = Bid(5, 3)
        bid = Bid(4, 6)
        is_valid, error = bid.is_valid_raise(previous, False, 20)
        assert not is_valid


class TestBiddingOnOnes:
    """Tests for bidding on ones (wild)."""

    def test_bid_on_ones_from_non_ones(self):
        """Test valid bid on ones from non-ones."""
        previous = Bid(6, 4)
        bid = Bid(3, 1)
        is_valid, error = bid.is_valid_raise(previous, False, 20)
        assert is_valid
        assert error == ""

    def test_bid_on_ones_minimum_quantity(self):
        """Test minimum quantity when bidding on ones."""
        previous = Bid(7, 4)
        bid = Bid(4, 1)  # 7/2 = 3.5, rounded up to 4
        is_valid, error = bid.is_valid_raise(previous, False, 20)
        assert is_valid

    def test_bid_on_ones_too_low(self):
        """Test bidding on ones with too low quantity."""
        previous = Bid(7, 4)
        bid = Bid(3, 1)  # Need at least 4
        is_valid, error = bid.is_valid_raise(previous, False, 20)
        assert not is_valid
        assert "at least 4" in error

    def test_bid_away_from_ones(self):
        """Test bidding away from ones to non-ones."""
        previous = Bid(3, 1)
        bid = Bid(7, 4)  # 3*2+1 = 7
        is_valid, error = bid.is_valid_raise(previous, False, 20)
        assert is_valid

    def test_bid_away_from_ones_too_low(self):
        """Test bidding away from ones with too low quantity."""
        previous = Bid(3, 1)
        bid = Bid(6, 4)  # Need at least 7
        is_valid, error = bid.is_valid_raise(previous, False, 20)
        assert not is_valid
        assert "at least 7" in error


class TestPalificoBidding:
    """Tests for Palifico round bidding."""

    def test_palifico_increase_quantity(self):
        """Test increasing quantity during Palifico."""
        previous = Bid(3, 4)
        bid = Bid(4, 4)
        is_valid, error = bid.is_valid_raise(previous, True, 10)
        assert is_valid

    def test_palifico_cannot_change_face(self):
        """Test that face value cannot change during Palifico."""
        previous = Bid(3, 4)
        bid = Bid(4, 5)
        is_valid, error = bid.is_valid_raise(previous, True, 10)
        assert not is_valid
        assert "face value cannot change" in error

    def test_palifico_cannot_decrease_quantity(self):
        """Test that quantity cannot decrease during Palifico."""
        previous = Bid(5, 4)
        bid = Bid(4, 4)
        is_valid, error = bid.is_valid_raise(previous, True, 10)
        assert not is_valid
        assert "Must increase quantity" in error

    def test_palifico_cannot_keep_same_quantity(self):
        """Test that quantity must increase during Palifico."""
        previous = Bid(5, 4)
        bid = Bid(5, 4)
        is_valid, error = bid.is_valid_raise(previous, True, 10)
        assert not is_valid


class TestMaxDiceValidation:
    """Tests for maximum dice validation."""

    def test_bid_at_max_dice(self):
        """Test bidding exactly the total number of dice."""
        bid = Bid(10, 3)
        is_valid, error = bid.is_valid_raise(None, False, 10)
        assert is_valid

    def test_bid_exceeds_max_dice(self):
        """Test bidding more than total dice in play."""
        previous = Bid(5, 3)
        bid = Bid(11, 4)
        is_valid, error = bid.is_valid_raise(previous, False, 10)
        assert not is_valid
        assert "Cannot bid more than 10 dice" in error

    def test_first_bid_exceeds_max_dice(self):
        """Test first bid exceeding max dice."""
        bid = Bid(15, 2)
        is_valid, error = bid.is_valid_raise(None, False, 10)
        assert not is_valid

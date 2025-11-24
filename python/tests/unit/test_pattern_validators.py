"""Tests for PlayFormationValidator utilities."""

from datongzi_rules import Card, PlayFormationValidator, Rank, Suit


def test_can_form_consecutive_pairs_basic():
    """Test basic consecutive pairs formation validation."""
    hand = [
        Card(Suit.SPADES, Rank.FIVE),
        Card(Suit.HEARTS, Rank.FIVE),
        Card(Suit.SPADES, Rank.SIX),
        Card(Suit.HEARTS, Rank.SIX),
        Card(Suit.SPADES, Rank.SEVEN),
        Card(Suit.HEARTS, Rank.SEVEN),
    ]
    # Can form 5-6 or 6-7, both beat min_rank=FIVE
    assert PlayFormationValidator.can_form_consecutive_pairs(hand, 2, Rank.FIVE)
    print("✓ Can form consecutive pairs basic test passed")


def test_can_form_consecutive_pairs_min_rank():
    """Test consecutive pairs must beat minimum rank."""
    hand = [
        Card(Suit.SPADES, Rank.FIVE),
        Card(Suit.HEARTS, Rank.FIVE),
        Card(Suit.SPADES, Rank.SIX),
        Card(Suit.HEARTS, Rank.SIX),
    ]
    # Highest rank is 6, can beat 5 but not 6
    assert PlayFormationValidator.can_form_consecutive_pairs(hand, 2, Rank.FIVE)
    assert not PlayFormationValidator.can_form_consecutive_pairs(hand, 2, Rank.SIX)
    print("✓ Consecutive pairs min rank test passed")


def test_can_form_consecutive_pairs_insufficient():
    """Test can_form_consecutive_pairs with insufficient pairs."""
    hand = [
        Card(Suit.SPADES, Rank.FIVE),
        Card(Suit.HEARTS, Rank.FIVE),
        Card(Suit.SPADES, Rank.KING),
        Card(Suit.HEARTS, Rank.KING),
    ]
    # Have 5-5 and K-K, but not consecutive
    assert not PlayFormationValidator.can_form_consecutive_pairs(hand, 2, Rank.FIVE)
    print("✓ Consecutive pairs insufficient test passed")


def test_can_form_airplane_basic():
    """Test basic airplane formation validation."""
    hand = [
        Card(Suit.SPADES, Rank.FIVE),
        Card(Suit.HEARTS, Rank.FIVE),
        Card(Suit.CLUBS, Rank.FIVE),
        Card(Suit.SPADES, Rank.SIX),
        Card(Suit.HEARTS, Rank.SIX),
        Card(Suit.CLUBS, Rank.SIX),
        Card(Suit.SPADES, Rank.SEVEN),
        Card(Suit.HEARTS, Rank.SEVEN),
        Card(Suit.CLUBS, Rank.SEVEN),
    ]
    # Can form 5-6, 6-7
    assert PlayFormationValidator.can_form_airplane(hand, 2, Rank.FIVE)
    print("✓ Can form airplane basic test passed")


def test_can_form_airplane_min_rank():
    """Test airplane must beat minimum rank."""
    hand = [
        Card(Suit.SPADES, Rank.FIVE),
        Card(Suit.HEARTS, Rank.FIVE),
        Card(Suit.CLUBS, Rank.FIVE),
        Card(Suit.SPADES, Rank.SIX),
        Card(Suit.HEARTS, Rank.SIX),
        Card(Suit.CLUBS, Rank.SIX),
    ]
    # Highest rank is 6
    assert PlayFormationValidator.can_form_airplane(hand, 2, Rank.FIVE)
    assert not PlayFormationValidator.can_form_airplane(hand, 2, Rank.SIX)
    print("✓ Airplane min rank test passed")


def test_can_form_airplane_insufficient():
    """Test can_form_airplane with insufficient triples."""
    hand = [
        Card(Suit.SPADES, Rank.FIVE),
        Card(Suit.HEARTS, Rank.FIVE),
        Card(Suit.CLUBS, Rank.FIVE),
        Card(Suit.SPADES, Rank.KING),
        Card(Suit.HEARTS, Rank.KING),
        Card(Suit.CLUBS, Rank.KING),
    ]
    # Have 5-5-5 and K-K-K, but not consecutive
    assert not PlayFormationValidator.can_form_airplane(hand, 2, Rank.FIVE)
    print("✓ Airplane insufficient test passed")


def test_can_form_airplane_with_wings_basic():
    """Test basic airplane_with_wings formation validation."""
    hand = [
        Card(Suit.SPADES, Rank.FIVE),
        Card(Suit.HEARTS, Rank.FIVE),
        Card(Suit.CLUBS, Rank.FIVE),
        Card(Suit.SPADES, Rank.SIX),
        Card(Suit.HEARTS, Rank.SIX),
        Card(Suit.CLUBS, Rank.SIX),
        Card(Suit.SPADES, Rank.KING),
        Card(Suit.HEARTS, Rank.KING),
        Card(Suit.SPADES, Rank.ACE),
        Card(Suit.HEARTS, Rank.ACE),
    ]
    # Can form 5-6 airplane + K-K + A-A wings
    assert PlayFormationValidator.can_form_airplane_with_wings(hand, 2, Rank.FIVE)
    print("✓ Can form airplane with wings basic test passed")


def test_can_form_airplane_with_wings_insufficient_pairs():
    """Test airplane_with_wings needs enough pairs for wings."""
    hand = [
        Card(Suit.SPADES, Rank.FIVE),
        Card(Suit.HEARTS, Rank.FIVE),
        Card(Suit.CLUBS, Rank.FIVE),
        Card(Suit.SPADES, Rank.SIX),
        Card(Suit.HEARTS, Rank.SIX),
        Card(Suit.CLUBS, Rank.SIX),
        Card(Suit.SPADES, Rank.KING),
        Card(Suit.HEARTS, Rank.KING),
    ]
    # Have airplane but only 1 pair for wings (need 2)
    assert not PlayFormationValidator.can_form_airplane_with_wings(hand, 2, Rank.FIVE)
    print("✓ Airplane with wings insufficient pairs test passed")


def test_can_form_airplane_with_wings_min_rank():
    """Test airplane_with_wings must beat minimum rank."""
    hand = [
        Card(Suit.SPADES, Rank.FIVE),
        Card(Suit.HEARTS, Rank.FIVE),
        Card(Suit.CLUBS, Rank.FIVE),
        Card(Suit.SPADES, Rank.SIX),
        Card(Suit.HEARTS, Rank.SIX),
        Card(Suit.CLUBS, Rank.SIX),
        Card(Suit.SPADES, Rank.KING),
        Card(Suit.HEARTS, Rank.KING),
        Card(Suit.SPADES, Rank.ACE),
        Card(Suit.HEARTS, Rank.ACE),
    ]
    # Highest airplane rank is 6
    assert PlayFormationValidator.can_form_airplane_with_wings(hand, 2, Rank.FIVE)
    assert not PlayFormationValidator.can_form_airplane_with_wings(hand, 2, Rank.SIX)
    print("✓ Airplane with wings min rank test passed")


def test_can_form_triple_with_two_basic():
    """Test basic triple_with_two formation validation."""
    hand = [
        Card(Suit.SPADES, Rank.SIX),
        Card(Suit.HEARTS, Rank.SIX),
        Card(Suit.CLUBS, Rank.SIX),
        Card(Suit.SPADES, Rank.KING),
        Card(Suit.HEARTS, Rank.KING),
    ]
    # Can form 6-6-6-K-K (6 > 5)
    assert PlayFormationValidator.can_form_triple_with_two(hand, Rank.FIVE)
    print("✓ Can form triple with two basic test passed")


def test_can_form_triple_with_two_min_rank():
    """Test triple_with_two must beat minimum rank."""
    hand = [
        Card(Suit.SPADES, Rank.FIVE),
        Card(Suit.HEARTS, Rank.FIVE),
        Card(Suit.CLUBS, Rank.FIVE),
        Card(Suit.SPADES, Rank.SIX),
        Card(Suit.HEARTS, Rank.SIX),
        Card(Suit.CLUBS, Rank.SIX),
        Card(Suit.SPADES, Rank.KING),
        Card(Suit.HEARTS, Rank.KING),
    ]
    # Have 5-5-5 and 6-6-6, can beat min_rank=5 but not 6
    assert PlayFormationValidator.can_form_triple_with_two(hand, Rank.FIVE)
    assert not PlayFormationValidator.can_form_triple_with_two(hand, Rank.SIX)
    print("✓ Triple with two min rank test passed")


def test_can_form_triple_with_two_same_rank():
    """Test triple_with_two can use same rank for triple and pair."""
    hand = [
        Card(Suit.SPADES, Rank.KING),
        Card(Suit.HEARTS, Rank.KING),
        Card(Suit.CLUBS, Rank.KING),
        Card(Suit.DIAMONDS, Rank.KING),
        Card(Suit.SPADES, Rank.KING),  # 5 kings total
    ]
    # Can form K-K-K-K-K (3 for triple + 2 for pair)
    assert PlayFormationValidator.can_form_triple_with_two(hand, Rank.FIVE)
    print("✓ Triple with two same rank test passed")


def test_can_form_triple_with_two_insufficient():
    """Test can_form_triple_with_two with insufficient cards."""
    hand = [
        Card(Suit.SPADES, Rank.FIVE),
        Card(Suit.HEARTS, Rank.FIVE),
        Card(Suit.CLUBS, Rank.FIVE),
        Card(Suit.SPADES, Rank.KING),  # Only 1 king
    ]
    # No pair available
    assert not PlayFormationValidator.can_form_triple_with_two(hand, Rank.FIVE)
    print("✓ Triple with two insufficient test passed")

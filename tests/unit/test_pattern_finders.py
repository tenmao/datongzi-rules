"""Tests for PatternFinder utilities."""

from datongzi_rules import Card, Rank, Suit, PatternFinder


def test_find_pairs_basic():
    """Test finding pairs in a simple hand."""
    hand = [
        Card(Suit.SPADES, Rank.FIVE),
        Card(Suit.HEARTS, Rank.FIVE),
        Card(Suit.SPADES, Rank.KING),
        Card(Suit.HEARTS, Rank.KING),
        Card(Suit.SPADES, Rank.ACE),
    ]
    pairs = PatternFinder.find_pairs(hand)

    assert len(pairs) == 4  # 2 pairs = 4 cards
    assert all(card.rank in [Rank.FIVE, Rank.KING] for card in pairs)
    print("✓ Find pairs basic test passed")


def test_find_pairs_multiple():
    """Test finding multiple pairs from same rank."""
    hand = [
        Card(Suit.SPADES, Rank.SEVEN),
        Card(Suit.HEARTS, Rank.SEVEN),
        Card(Suit.CLUBS, Rank.SEVEN),
        Card(Suit.DIAMONDS, Rank.SEVEN),
    ]
    pairs = PatternFinder.find_pairs(hand)

    assert len(pairs) == 4  # 4 cards = 2 pairs
    assert all(card.rank == Rank.SEVEN for card in pairs)
    print("✓ Find multiple pairs test passed")


def test_find_pairs_empty():
    """Test finding pairs in empty hand."""
    hand = []
    pairs = PatternFinder.find_pairs(hand)

    assert len(pairs) == 0
    print("✓ Find pairs empty hand test passed")


def test_find_triples_basic():
    """Test finding triples in hand."""
    hand = [
        Card(Suit.SPADES, Rank.FIVE),
        Card(Suit.HEARTS, Rank.FIVE),
        Card(Suit.CLUBS, Rank.FIVE),
        Card(Suit.SPADES, Rank.KING),
        Card(Suit.HEARTS, Rank.KING),
    ]
    triples = PatternFinder.find_triples(hand)

    assert len(triples) == 3
    assert all(card.rank == Rank.FIVE for card in triples)
    print("✓ Find triples basic test passed")


def test_find_triples_multiple():
    """Test finding multiple triples."""
    hand = [
        Card(Suit.SPADES, Rank.FIVE),
        Card(Suit.HEARTS, Rank.FIVE),
        Card(Suit.CLUBS, Rank.FIVE),
        Card(Suit.SPADES, Rank.KING),
        Card(Suit.HEARTS, Rank.KING),
        Card(Suit.CLUBS, Rank.KING),
    ]
    triples = PatternFinder.find_triples(hand)

    assert len(triples) == 6  # 2 triples
    print("✓ Find multiple triples test passed")


def test_find_bombs_basic():
    """Test finding bombs (4+ cards of same rank)."""
    hand = [
        Card(Suit.SPADES, Rank.KING),
        Card(Suit.HEARTS, Rank.KING),
        Card(Suit.CLUBS, Rank.KING),
        Card(Suit.DIAMONDS, Rank.KING),
    ]
    bombs = PatternFinder.find_bombs(hand)

    assert len(bombs) == 1
    assert len(bombs[0]) == 4
    assert all(card.rank == Rank.KING for card in bombs[0])
    print("✓ Find bombs basic test passed")


def test_find_bombs_multiple_sizes():
    """Test finding bombs of different sizes from same rank."""
    hand = [
        Card(Suit.SPADES, Rank.ACE),
        Card(Suit.HEARTS, Rank.ACE),
        Card(Suit.CLUBS, Rank.ACE),
        Card(Suit.DIAMONDS, Rank.ACE),
        Card(Suit.SPADES, Rank.ACE),  # 5th card
    ]
    bombs = PatternFinder.find_bombs(hand)

    # Should return bombs of size 4 and 5
    assert len(bombs) == 2
    assert len(bombs[0]) == 4
    assert len(bombs[1]) == 5
    print("✓ Find bombs multiple sizes test passed")


def test_find_consecutive_pairs_basic():
    """Test finding consecutive pairs."""
    hand = [
        Card(Suit.SPADES, Rank.FIVE),
        Card(Suit.HEARTS, Rank.FIVE),
        Card(Suit.SPADES, Rank.SIX),
        Card(Suit.HEARTS, Rank.SIX),
        Card(Suit.SPADES, Rank.KING),
    ]
    consecutive = PatternFinder.find_consecutive_pairs(hand)

    assert len(consecutive) == 4  # 2 consecutive pairs
    print("✓ Find consecutive pairs basic test passed")


def test_find_consecutive_pairs_longest():
    """Test finding longest consecutive pairs."""
    hand = [
        Card(Suit.SPADES, Rank.FIVE),
        Card(Suit.HEARTS, Rank.FIVE),
        Card(Suit.SPADES, Rank.SIX),
        Card(Suit.HEARTS, Rank.SIX),
        Card(Suit.SPADES, Rank.SEVEN),
        Card(Suit.HEARTS, Rank.SEVEN),
        Card(Suit.SPADES, Rank.KING),
        Card(Suit.HEARTS, Rank.KING),
    ]
    consecutive = PatternFinder.find_consecutive_pairs(hand)

    # Should find 5-6-7 (6 cards) instead of K (2 cards)
    assert len(consecutive) == 6
    print("✓ Find longest consecutive pairs test passed")


def test_find_all_consecutive_pairs():
    """Test finding all consecutive pairs of specific length."""
    hand = [
        Card(Suit.SPADES, Rank.FIVE),
        Card(Suit.HEARTS, Rank.FIVE),
        Card(Suit.SPADES, Rank.SIX),
        Card(Suit.HEARTS, Rank.SIX),
        Card(Suit.SPADES, Rank.SEVEN),
        Card(Suit.HEARTS, Rank.SEVEN),
        Card(Suit.SPADES, Rank.EIGHT),
        Card(Suit.HEARTS, Rank.EIGHT),
    ]
    combos = PatternFinder.find_all_consecutive_pairs(hand, 2)

    # Should find: 5-6, 6-7, 7-8
    assert len(combos) == 3
    assert all(len(combo) == 4 for combo in combos)
    print("✓ Find all consecutive pairs test passed")


def test_find_all_consecutive_pairs_invalid_num():
    """Test find_all_consecutive_pairs with invalid num_pairs."""
    hand = [
        Card(Suit.SPADES, Rank.FIVE),
        Card(Suit.HEARTS, Rank.FIVE),
    ]
    combos = PatternFinder.find_all_consecutive_pairs(hand, 1)

    assert len(combos) == 0  # num_pairs must be >= 2
    print("✓ Find all consecutive pairs invalid num test passed")


def test_find_all_tongzi():
    """Test finding all tongzi (3 of same rank and suit)."""
    hand = [
        Card(Suit.SPADES, Rank.KING),
        Card(Suit.SPADES, Rank.KING),
        Card(Suit.SPADES, Rank.KING),
        Card(Suit.HEARTS, Rank.SEVEN),
        Card(Suit.HEARTS, Rank.SEVEN),
        Card(Suit.HEARTS, Rank.SEVEN),
    ]
    tongzi_list = PatternFinder.find_all_tongzi(hand)

    assert len(tongzi_list) == 2  # 2 tongzi
    assert all(len(tongzi) == 3 for tongzi in tongzi_list)
    print("✓ Find all tongzi test passed")


def test_find_all_tongzi_mixed_suits():
    """Test tongzi detection with mixed suits."""
    hand = [
        Card(Suit.SPADES, Rank.KING),
        Card(Suit.HEARTS, Rank.KING),
        Card(Suit.CLUBS, Rank.KING),
    ]
    tongzi_list = PatternFinder.find_all_tongzi(hand)

    assert len(tongzi_list) == 0  # Not tongzi (different suits)
    print("✓ Find all tongzi mixed suits test passed")


def test_find_triple_with_two_basic():
    """Test finding triple with two pattern."""
    hand = [
        Card(Suit.SPADES, Rank.FIVE),
        Card(Suit.HEARTS, Rank.FIVE),
        Card(Suit.CLUBS, Rank.FIVE),
        Card(Suit.SPADES, Rank.KING),
        Card(Suit.HEARTS, Rank.KING),
    ]
    pattern = PatternFinder.find_triple_with_two(hand)

    assert pattern is not None
    assert len(pattern) == 5
    print("✓ Find triple with two basic test passed")


def test_find_triple_with_two_none():
    """Test find_triple_with_two when not possible."""
    hand = [
        Card(Suit.SPADES, Rank.FIVE),
        Card(Suit.HEARTS, Rank.FIVE),
        Card(Suit.CLUBS, Rank.FIVE),
        Card(Suit.SPADES, Rank.KING),  # Only 1 king
    ]
    pattern = PatternFinder.find_triple_with_two(hand)

    assert pattern is None
    print("✓ Find triple with two none test passed")


def test_find_all_triple_with_two():
    """Test finding all triple_with_two combinations."""
    hand = [
        Card(Suit.SPADES, Rank.FIVE),
        Card(Suit.HEARTS, Rank.FIVE),
        Card(Suit.CLUBS, Rank.FIVE),
        Card(Suit.SPADES, Rank.KING),
        Card(Suit.HEARTS, Rank.KING),
        Card(Suit.SPADES, Rank.ACE),
        Card(Suit.HEARTS, Rank.ACE),
    ]
    combos = PatternFinder.find_all_triple_with_two(hand)

    # Can form: 5-5-5-K-K or 5-5-5-A-A
    assert len(combos) == 2
    assert all(len(combo) == 5 for combo in combos)
    print("✓ Find all triple with two test passed")


def test_find_airplane_basic():
    """Test finding airplane (consecutive triples)."""
    hand = [
        Card(Suit.SPADES, Rank.FIVE),
        Card(Suit.HEARTS, Rank.FIVE),
        Card(Suit.CLUBS, Rank.FIVE),
        Card(Suit.SPADES, Rank.SIX),
        Card(Suit.HEARTS, Rank.SIX),
        Card(Suit.CLUBS, Rank.SIX),
    ]
    airplane = PatternFinder.find_airplane(hand)

    assert airplane is not None
    assert len(airplane) == 6  # 2 consecutive triples
    print("✓ Find airplane basic test passed")


def test_find_airplane_none():
    """Test find_airplane when not possible."""
    hand = [
        Card(Suit.SPADES, Rank.FIVE),
        Card(Suit.HEARTS, Rank.FIVE),
        Card(Suit.CLUBS, Rank.FIVE),
        Card(Suit.SPADES, Rank.KING),
        Card(Suit.HEARTS, Rank.KING),
        Card(Suit.CLUBS, Rank.KING),
    ]
    airplane = PatternFinder.find_airplane(hand)

    assert airplane is None  # Not consecutive
    print("✓ Find airplane none test passed")


def test_find_all_airplanes():
    """Test finding all airplanes of specific length."""
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
    combos = PatternFinder.find_all_airplanes(hand, 2)

    # Should find: 5-6, 6-7
    assert len(combos) == 2
    assert all(len(combo) == 6 for combo in combos)
    print("✓ Find all airplanes test passed")


def test_find_airplane_with_wings_basic():
    """Test finding airplane with wings."""
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
    pattern = PatternFinder.find_airplane_with_wings(hand)

    assert pattern is not None
    assert len(pattern) == 10  # 2 triples + 2 pairs
    print("✓ Find airplane with wings basic test passed")


def test_find_airplane_with_wings_none():
    """Test find_airplane_with_wings when not enough wings."""
    hand = [
        Card(Suit.SPADES, Rank.FIVE),
        Card(Suit.HEARTS, Rank.FIVE),
        Card(Suit.CLUBS, Rank.FIVE),
        Card(Suit.SPADES, Rank.SIX),
        Card(Suit.HEARTS, Rank.SIX),
        Card(Suit.CLUBS, Rank.SIX),
        Card(Suit.SPADES, Rank.KING),  # Only 1 pair
        Card(Suit.HEARTS, Rank.KING),
    ]
    pattern = PatternFinder.find_airplane_with_wings(hand)

    assert pattern is None  # Need 2 pairs for wings
    print("✓ Find airplane with wings none test passed")


def test_find_all_airplane_with_wings():
    """Test finding all airplane_with_wings combinations."""
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
        Card(Suit.SPADES, Rank.SEVEN),
        Card(Suit.HEARTS, Rank.SEVEN),
    ]
    combos = PatternFinder.find_all_airplane_with_wings(hand, 10)

    # Should find combinations with different wing pairs
    assert len(combos) >= 1
    assert all(len(combo) == 10 for combo in combos)
    print("✓ Find all airplane with wings test passed")


def test_find_all_airplane_with_wings_invalid_count():
    """Test find_all_airplane_with_wings with invalid card count."""
    hand = [
        Card(Suit.SPADES, Rank.FIVE),
    ]
    combos = PatternFinder.find_all_airplane_with_wings(hand, 7)

    assert len(combos) == 0  # 7 is not divisible by 5
    print("✓ Find all airplane with wings invalid count test passed")


def test_find_pairs_odd_cards():
    """Test find_pairs with odd number of cards per rank."""
    hand = [
        Card(Suit.SPADES, Rank.FIVE),
        Card(Suit.HEARTS, Rank.FIVE),
        Card(Suit.CLUBS, Rank.FIVE),  # 3 cards = 1 pair + 1 leftover
    ]
    pairs = PatternFinder.find_pairs(hand)

    assert len(pairs) == 2  # Only 1 pair
    print("✓ Find pairs with odd cards test passed")


def test_find_triples_with_extras():
    """Test find_triples with extra cards."""
    hand = [
        Card(Suit.SPADES, Rank.KING),
        Card(Suit.HEARTS, Rank.KING),
        Card(Suit.CLUBS, Rank.KING),
        Card(Suit.DIAMONDS, Rank.KING),
        Card(Suit.SPADES, Rank.KING),
        Card(Suit.HEARTS, Rank.KING),
        Card(Suit.CLUBS, Rank.KING),  # 7 cards = 2 triples + 1 leftover
    ]
    triples = PatternFinder.find_triples(hand)

    assert len(triples) == 6  # 2 triples
    print("✓ Find triples with extras test passed")


def test_find_consecutive_pairs_insufficient():
    """Test find_consecutive_pairs with insufficient pairs."""
    hand = [
        Card(Suit.SPADES, Rank.FIVE),
        Card(Suit.HEARTS, Rank.FIVE),
    ]
    consecutive = PatternFinder.find_consecutive_pairs(hand)

    assert len(consecutive) == 0  # Need at least 2 pairs
    print("✓ Find consecutive pairs insufficient test passed")


def test_find_all_consecutive_pairs_insufficient():
    """Test find_all_consecutive_pairs with insufficient pairs."""
    hand = [
        Card(Suit.SPADES, Rank.FIVE),
        Card(Suit.HEARTS, Rank.FIVE),
        Card(Suit.SPADES, Rank.SIX),
        Card(Suit.HEARTS, Rank.SIX),
    ]
    combos = PatternFinder.find_all_consecutive_pairs(hand, 3)

    assert len(combos) == 0  # Need 3 consecutive pairs
    print("✓ Find all consecutive pairs insufficient test passed")


def test_find_all_airplanes_insufficient():
    """Test find_all_airplanes with insufficient triples."""
    hand = [
        Card(Suit.SPADES, Rank.FIVE),
        Card(Suit.HEARTS, Rank.FIVE),
        Card(Suit.CLUBS, Rank.FIVE),
    ]
    combos = PatternFinder.find_all_airplanes(hand, 2)

    assert len(combos) == 0  # Need 2 consecutive triples
    print("✓ Find all airplanes insufficient test passed")

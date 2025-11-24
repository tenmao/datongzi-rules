"""Unit tests for AI helper modules."""

from datongzi_rules import (
    Card,
    PatternRecognizer,
    PlayGenerator,
    PlayType,
    Rank,
    Suit,
)

# PlayGenerator Tests


def test_play_generator_singles():
    """Test generating all single plays."""
    hand = [
        Card(Suit.SPADES, Rank.FIVE),
        Card(Suit.HEARTS, Rank.SIX),
        Card(Suit.CLUBS, Rank.SEVEN),
    ]

    plays = PlayGenerator.generate_all_plays(hand)

    # Should include 3 singles + possible combos
    singles = [p for p in plays if len(p) == 1]
    assert len(singles) == 3
    print("✓ Single play generation test passed")


def test_play_generator_pairs():
    """Test generating pairs."""
    hand = [
        Card(Suit.SPADES, Rank.KING),
        Card(Suit.HEARTS, Rank.KING),
        Card(Suit.CLUBS, Rank.FIVE),
    ]

    plays = PlayGenerator.generate_all_plays(hand)

    # Should include the pair
    pairs = [p for p in plays if len(p) == 2]
    assert len(pairs) >= 1
    print("✓ Pair play generation test passed")


def test_play_generator_triples():
    """Test generating triples."""
    hand = [
        Card(Suit.SPADES, Rank.ACE),
        Card(Suit.HEARTS, Rank.ACE),
        Card(Suit.CLUBS, Rank.ACE),
    ]

    plays = PlayGenerator.generate_all_plays(hand)

    # Should include the triple
    triples = [p for p in plays if len(p) == 3]
    assert len(triples) >= 1

    # Verify it's a valid triple
    triple = triples[0]
    pattern = PatternRecognizer.analyze_cards(triple)
    assert pattern.play_type == PlayType.TRIPLE
    print("✓ Triple play generation test passed")


def test_play_generator_bombs():
    """Test generating bombs."""
    hand = [
        Card(Suit.SPADES, Rank.TEN),
        Card(Suit.HEARTS, Rank.TEN),
        Card(Suit.CLUBS, Rank.TEN),
        Card(Suit.DIAMONDS, Rank.TEN),
    ]

    plays = PlayGenerator.generate_all_plays(hand)

    # Should include the bomb
    bombs = [p for p in plays if len(p) == 4]
    assert len(bombs) >= 1

    # Verify it's a valid bomb
    bomb = bombs[0]
    pattern = PatternRecognizer.analyze_cards(bomb)
    assert pattern.play_type == PlayType.BOMB
    print("✓ Bomb play generation test passed")


def test_play_generator_tongzi():
    """Test generating tongzi (3 same suit, same rank)."""
    hand = [
        Card(Suit.SPADES, Rank.KING),
        Card(Suit.SPADES, Rank.KING),
        Card(Suit.SPADES, Rank.KING),
    ]

    plays = PlayGenerator.generate_all_plays(hand)

    # Should include the tongzi
    tongzi_plays = [p for p in plays if len(p) == 3]
    assert len(tongzi_plays) >= 1

    # Verify it's a valid tongzi
    tongzi = tongzi_plays[0]
    pattern = PatternRecognizer.analyze_cards(tongzi)
    assert pattern.play_type == PlayType.TONGZI
    print("✓ Tongzi play generation test passed")


def test_play_generator_consecutive_pairs():
    """Test generating consecutive pairs."""
    hand = [
        Card(Suit.SPADES, Rank.FIVE),
        Card(Suit.HEARTS, Rank.FIVE),
        Card(Suit.SPADES, Rank.SIX),
        Card(Suit.HEARTS, Rank.SIX),
    ]

    plays = PlayGenerator.generate_all_plays(hand)

    # Should include consecutive pairs
    consec_pairs = [p for p in plays if len(p) == 4]
    assert len(consec_pairs) >= 1

    # Verify it's consecutive pairs
    pattern = PatternRecognizer.analyze_cards(consec_pairs[0])
    assert pattern.play_type == PlayType.CONSECUTIVE_PAIRS
    print("✓ Consecutive pairs play generation test passed")


def test_play_generator_valid_responses():
    """Test generating valid responses to current play."""
    hand = [
        Card(Suit.SPADES, Rank.KING),
        Card(Suit.HEARTS, Rank.KING),
        Card(Suit.SPADES, Rank.FIVE),
    ]

    # Current play: pair of 5s
    current_cards = [
        Card(Suit.SPADES, Rank.FIVE),
        Card(Suit.HEARTS, Rank.FIVE),
    ]
    current_pattern = PatternRecognizer.analyze_cards(current_cards)

    # Generate valid responses
    responses = PlayGenerator.generate_valid_responses(hand, current_pattern)

    # Should be able to beat with pair of Kings
    assert len(responses) >= 1
    print("✓ Valid response generation test passed")


# HandEvaluator Tests

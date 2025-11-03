"""Advanced pattern recognition tests."""

from datongzi_rules import Card, Rank, Suit, PatternRecognizer, PlayType, PlayValidator


def test_consecutive_pairs():
    """Test consecutive pairs pattern (连对)."""
    cards = [
        Card(Suit.SPADES, Rank.FIVE),
        Card(Suit.HEARTS, Rank.FIVE),
        Card(Suit.SPADES, Rank.SIX),
        Card(Suit.HEARTS, Rank.SIX),
    ]
    pattern = PatternRecognizer.analyze_cards(cards)
    
    assert pattern is not None
    assert pattern.play_type == PlayType.CONSECUTIVE_PAIRS
    assert pattern.card_count == 4
    print("✓ Consecutive pairs test passed")


def test_consecutive_pairs_long():
    """Test longer consecutive pairs."""
    cards = [
        Card(Suit.SPADES, Rank.SEVEN),
        Card(Suit.HEARTS, Rank.SEVEN),
        Card(Suit.SPADES, Rank.EIGHT),
        Card(Suit.HEARTS, Rank.EIGHT),
        Card(Suit.SPADES, Rank.NINE),
        Card(Suit.HEARTS, Rank.NINE),
    ]
    pattern = PatternRecognizer.analyze_cards(cards)
    
    assert pattern is not None
    assert pattern.play_type == PlayType.CONSECUTIVE_PAIRS
    assert pattern.card_count == 6
    print("✓ Long consecutive pairs test passed")


def test_triple_with_two():
    """Test triple with two pattern (三带二)."""
    cards = [
        Card(Suit.SPADES, Rank.KING),
        Card(Suit.HEARTS, Rank.KING),
        Card(Suit.CLUBS, Rank.KING),
        Card(Suit.SPADES, Rank.FIVE),
        Card(Suit.HEARTS, Rank.FIVE),
    ]
    pattern = PatternRecognizer.analyze_cards(cards)
    
    assert pattern is not None
    assert pattern.play_type == PlayType.TRIPLE_WITH_TWO
    assert pattern.primary_rank == Rank.KING
    assert pattern.card_count == 5
    print("✓ Triple with two test passed")


def test_airplane():
    """Test airplane pattern (consecutive triples)."""
    cards = [
        Card(Suit.SPADES, Rank.FIVE),
        Card(Suit.HEARTS, Rank.FIVE),
        Card(Suit.CLUBS, Rank.FIVE),
        Card(Suit.SPADES, Rank.SIX),
        Card(Suit.HEARTS, Rank.SIX),
        Card(Suit.CLUBS, Rank.SIX),
    ]
    pattern = PatternRecognizer.analyze_cards(cards)
    
    assert pattern is not None
    assert pattern.play_type == PlayType.AIRPLANE
    assert pattern.card_count == 6
    print("✓ Airplane pattern test passed")


def test_airplane_with_wings():
    """Test airplane with wings pattern."""
    cards = [
        # Two consecutive triples (airplane)
        Card(Suit.SPADES, Rank.SEVEN),
        Card(Suit.HEARTS, Rank.SEVEN),
        Card(Suit.CLUBS, Rank.SEVEN),
        Card(Suit.SPADES, Rank.EIGHT),
        Card(Suit.HEARTS, Rank.EIGHT),
        Card(Suit.CLUBS, Rank.EIGHT),
        # Two pairs (wings)
        Card(Suit.SPADES, Rank.FIVE),
        Card(Suit.HEARTS, Rank.FIVE),
        Card(Suit.SPADES, Rank.SIX),
        Card(Suit.HEARTS, Rank.SIX),
    ]
    pattern = PatternRecognizer.analyze_cards(cards)
    
    assert pattern is not None
    assert pattern.play_type == PlayType.AIRPLANE_WITH_WINGS
    assert pattern.card_count == 10
    print("✓ Airplane with wings test passed")


def test_bomb_beats_tongzi():
    """Test that bomb can be beaten by tongzi."""
    # Current play: Bomb (4 cards, different suits)
    current_cards = [
        Card(Suit.SPADES, Rank.FIVE),
        Card(Suit.HEARTS, Rank.FIVE),
        Card(Suit.CLUBS, Rank.FIVE),
        Card(Suit.DIAMONDS, Rank.FIVE),
    ]
    current_pattern = PatternRecognizer.analyze_cards(current_cards)
    
    # New play: Tongzi (3 cards, same suit, higher rank)
    tongzi_cards = [
        Card(Suit.SPADES, Rank.KING),
        Card(Suit.SPADES, Rank.KING),
        Card(Suit.SPADES, Rank.KING),
    ]
    
    # Tongzi should beat Bomb
    assert PlayValidator.can_beat_play(tongzi_cards, current_pattern)
    print("✓ Tongzi beats bomb test passed")


def test_dizha_beats_all():
    """Test that dizha beats everything."""
    # Dizha
    dizha_cards = [
        Card(Suit.SPADES, Rank.TEN),
        Card(Suit.SPADES, Rank.TEN),
        Card(Suit.HEARTS, Rank.TEN),
        Card(Suit.HEARTS, Rank.TEN),
        Card(Suit.CLUBS, Rank.TEN),
        Card(Suit.CLUBS, Rank.TEN),
        Card(Suit.DIAMONDS, Rank.TEN),
        Card(Suit.DIAMONDS, Rank.TEN),
    ]
    
    # Tongzi
    tongzi_pattern = PatternRecognizer.analyze_cards([
        Card(Suit.SPADES, Rank.ACE),
        Card(Suit.SPADES, Rank.ACE),
        Card(Suit.SPADES, Rank.ACE),
    ])
    
    # Dizha should beat Tongzi
    assert PlayValidator.can_beat_play(dizha_cards, tongzi_pattern)
    print("✓ Dizha beats tongzi test passed")


def test_dizha_vs_dizha():
    """Test dizha vs dizha comparison."""
    # Lower rank dizha
    lower_dizha = [
        Card(Suit.SPADES, Rank.SEVEN),
        Card(Suit.SPADES, Rank.SEVEN),
        Card(Suit.HEARTS, Rank.SEVEN),
        Card(Suit.HEARTS, Rank.SEVEN),
        Card(Suit.CLUBS, Rank.SEVEN),
        Card(Suit.CLUBS, Rank.SEVEN),
        Card(Suit.DIAMONDS, Rank.SEVEN),
        Card(Suit.DIAMONDS, Rank.SEVEN),
    ]
    lower_pattern = PatternRecognizer.analyze_cards(lower_dizha)
    
    # Higher rank dizha
    higher_dizha = [
        Card(Suit.SPADES, Rank.KING),
        Card(Suit.SPADES, Rank.KING),
        Card(Suit.HEARTS, Rank.KING),
        Card(Suit.HEARTS, Rank.KING),
        Card(Suit.CLUBS, Rank.KING),
        Card(Suit.CLUBS, Rank.KING),
        Card(Suit.DIAMONDS, Rank.KING),
        Card(Suit.DIAMONDS, Rank.KING),
    ]
    
    # Higher rank dizha should beat lower
    assert PlayValidator.can_beat_play(higher_dizha, lower_pattern)
    print("✓ Dizha vs dizha test passed")


def test_bomb_vs_bomb():
    """Test bomb vs bomb comparison."""
    # Lower rank bomb
    lower_bomb = [
        Card(Suit.SPADES, Rank.FIVE),
        Card(Suit.HEARTS, Rank.FIVE),
        Card(Suit.CLUBS, Rank.FIVE),
        Card(Suit.DIAMONDS, Rank.FIVE),
    ]
    lower_pattern = PatternRecognizer.analyze_cards(lower_bomb)
    
    # Higher rank bomb
    higher_bomb = [
        Card(Suit.SPADES, Rank.KING),
        Card(Suit.HEARTS, Rank.KING),
        Card(Suit.CLUBS, Rank.KING),
        Card(Suit.DIAMONDS, Rank.KING),
    ]
    
    # Higher rank should beat lower
    assert PlayValidator.can_beat_play(higher_bomb, lower_pattern)
    print("✓ Bomb vs bomb test passed")


def test_larger_bomb_beats_smaller():
    """Test that larger bomb beats smaller bomb of same rank."""
    # 4-card bomb
    small_bomb = [
        Card(Suit.SPADES, Rank.KING),
        Card(Suit.HEARTS, Rank.KING),
        Card(Suit.CLUBS, Rank.KING),
        Card(Suit.DIAMONDS, Rank.KING),
    ]
    small_pattern = PatternRecognizer.analyze_cards(small_bomb)
    
    # 5-card bomb (same rank)
    large_bomb = [
        Card(Suit.SPADES, Rank.KING),
        Card(Suit.HEARTS, Rank.KING),
        Card(Suit.CLUBS, Rank.KING),
        Card(Suit.DIAMONDS, Rank.KING),
        Card(Suit.SPADES, Rank.KING),  # From second deck
    ]
    
    # Larger count should beat smaller
    assert PlayValidator.can_beat_play(large_bomb, small_pattern)
    print("✓ Larger bomb beats smaller test passed")


def test_consecutive_pairs_comparison():
    """Test consecutive pairs must match length."""
    # 2-pair consecutive
    short_pairs = [
        Card(Suit.SPADES, Rank.FIVE),
        Card(Suit.HEARTS, Rank.FIVE),
        Card(Suit.SPADES, Rank.SIX),
        Card(Suit.HEARTS, Rank.SIX),
    ]
    short_pattern = PatternRecognizer.analyze_cards(short_pairs)
    
    # 3-pair consecutive (different length)
    long_pairs = [
        Card(Suit.SPADES, Rank.SEVEN),
        Card(Suit.HEARTS, Rank.SEVEN),
        Card(Suit.SPADES, Rank.EIGHT),
        Card(Suit.HEARTS, Rank.EIGHT),
        Card(Suit.SPADES, Rank.NINE),
        Card(Suit.HEARTS, Rank.NINE),
    ]
    
    # Different lengths should not beat
    assert not PlayValidator.can_beat_play(long_pairs, short_pattern)
    print("✓ Consecutive pairs length comparison test passed")


def test_same_type_strength_comparison():
    """Test same type patterns compare by strength."""
    # Lower consecutive pairs
    lower_pairs = [
        Card(Suit.SPADES, Rank.FIVE),
        Card(Suit.HEARTS, Rank.FIVE),
        Card(Suit.SPADES, Rank.SIX),
        Card(Suit.HEARTS, Rank.SIX),
    ]
    lower_pattern = PatternRecognizer.analyze_cards(lower_pairs)
    
    # Higher consecutive pairs (same length)
    higher_pairs = [
        Card(Suit.SPADES, Rank.KING),
        Card(Suit.HEARTS, Rank.KING),
        Card(Suit.SPADES, Rank.ACE),
        Card(Suit.HEARTS, Rank.ACE),
    ]
    
    # Higher strength should beat lower
    assert PlayValidator.can_beat_play(higher_pairs, lower_pattern)
    print("✓ Same type strength comparison test passed")


def test_play_validator_starting_round():
    """Test that any valid pattern can start a new round."""
    single = [Card(Suit.SPADES, Rank.FIVE)]
    
    # Starting round (current_play = None)
    assert PlayValidator.can_beat_play(single, None)
    print("✓ Play validator starting round test passed")


def test_play_validator_invalid_pattern():
    """Test that invalid patterns cannot beat anything."""
    # Valid current play
    current_cards = [Card(Suit.SPADES, Rank.FIVE)]
    current_pattern = PatternRecognizer.analyze_cards(current_cards)
    
    # Invalid new play (mismatched cards)
    invalid_cards = [
        Card(Suit.SPADES, Rank.ACE),
        Card(Suit.HEARTS, Rank.KING),
    ]
    
    assert not PlayValidator.can_beat_play(invalid_cards, current_pattern)
    print("✓ Invalid pattern cannot beat test passed")


# All tests can be run with pytest
# pytest will autodiscover all test_* functions

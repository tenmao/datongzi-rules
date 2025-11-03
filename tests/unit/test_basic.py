"""Basic unit tests for datongzi-rules."""

from datongzi_rules import Card, Rank, Suit, PatternRecognizer, PlayType, PlayValidator


def test_card_creation():
    """Test basic card creation and properties."""
    card = Card(Suit.SPADES, Rank.ACE)
    assert card.suit == Suit.SPADES
    assert card.rank == Rank.ACE
    assert not card.is_scoring_card
    assert card.score_value == 0
    print("✓ Card creation test passed")


def test_card_scoring():
    """Test card scoring properties."""
    five = Card(Suit.HEARTS, Rank.FIVE)
    ten = Card(Suit.CLUBS, Rank.TEN)
    king = Card(Suit.DIAMONDS, Rank.KING)

    assert five.is_scoring_card
    assert five.score_value == 5
    assert ten.is_scoring_card
    assert ten.score_value == 10
    assert king.is_scoring_card
    assert king.score_value == 10
    print("✓ Card scoring test passed")


def test_card_string_representation():
    """Test card string representations."""
    card = Card(Suit.SPADES, Rank.ACE)
    assert str(card) == "♠A"
    assert "SPADES" in repr(card)
    assert "ACE" in repr(card)
    print("✓ Card string representation test passed")


def test_card_from_string():
    """Test creating card from string."""
    card = Card.from_string("♠A")
    assert card.suit == Suit.SPADES
    assert card.rank == Rank.ACE

    card2 = Card.from_string("♥10")
    assert card2.suit == Suit.HEARTS
    assert card2.rank == Rank.TEN
    print("✓ Card from_string test passed")


def test_pattern_single():
    """Test single card pattern recognition."""
    cards = [Card(Suit.SPADES, Rank.ACE)]
    pattern = PatternRecognizer.analyze_cards(cards)

    assert pattern is not None
    assert pattern.play_type == PlayType.SINGLE
    assert pattern.primary_rank == Rank.ACE
    assert pattern.card_count == 1
    print("✓ Single pattern test passed")


def test_pattern_pair():
    """Test pair pattern recognition."""
    cards = [Card(Suit.SPADES, Rank.ACE), Card(Suit.HEARTS, Rank.ACE)]
    pattern = PatternRecognizer.analyze_cards(cards)

    assert pattern is not None
    assert pattern.play_type == PlayType.PAIR
    assert pattern.primary_rank == Rank.ACE
    assert pattern.card_count == 2
    print("✓ Pair pattern test passed")


def test_pattern_triple():
    """Test triple pattern recognition."""
    cards = [
        Card(Suit.SPADES, Rank.KING),
        Card(Suit.HEARTS, Rank.KING),
        Card(Suit.CLUBS, Rank.KING),
    ]
    pattern = PatternRecognizer.analyze_cards(cards)

    assert pattern is not None
    assert pattern.play_type == PlayType.TRIPLE
    assert pattern.primary_rank == Rank.KING
    assert pattern.card_count == 3
    print("✓ Triple pattern test passed")


def test_pattern_bomb():
    """Test bomb pattern recognition."""
    cards = [
        Card(Suit.SPADES, Rank.TEN),
        Card(Suit.HEARTS, Rank.TEN),
        Card(Suit.CLUBS, Rank.TEN),
        Card(Suit.DIAMONDS, Rank.TEN),
    ]
    pattern = PatternRecognizer.analyze_cards(cards)

    assert pattern is not None
    assert pattern.play_type == PlayType.BOMB
    assert pattern.primary_rank == Rank.TEN
    assert pattern.card_count == 4
    print("✓ Bomb pattern test passed")


def test_pattern_invalid():
    """Test invalid pattern recognition."""
    # Mismatched cards
    cards = [Card(Suit.SPADES, Rank.ACE), Card(Suit.HEARTS, Rank.KING)]
    pattern = PatternRecognizer.analyze_cards(cards)
    assert pattern is None
    print("✓ Invalid pattern test passed")


def test_play_validator_same_type():
    """Test play validation for same type plays."""
    # Lower pair
    current_cards = [Card(Suit.SPADES, Rank.FIVE), Card(Suit.HEARTS, Rank.FIVE)]
    current_pattern = PatternRecognizer.analyze_cards(current_cards)

    # Higher pair
    new_cards = [Card(Suit.SPADES, Rank.KING), Card(Suit.HEARTS, Rank.KING)]
    assert PlayValidator.can_beat_play(new_cards, current_pattern)

    # Lower pair cannot beat
    lower_cards = [Card(Suit.SPADES, Rank.FIVE), Card(Suit.CLUBS, Rank.FIVE)]
    assert not PlayValidator.can_beat_play(lower_cards, current_pattern)

    print("✓ Play validator same type test passed")


def test_play_validator_bomb_beats_all():
    """Test that bomb beats non-bomb plays."""
    # Current play: Triple
    current_cards = [
        Card(Suit.SPADES, Rank.KING),
        Card(Suit.HEARTS, Rank.KING),
        Card(Suit.CLUBS, Rank.KING),
    ]
    current_pattern = PatternRecognizer.analyze_cards(current_cards)

    # Bomb beats triple
    bomb_cards = [
        Card(Suit.SPADES, Rank.FIVE),
        Card(Suit.HEARTS, Rank.FIVE),
        Card(Suit.CLUBS, Rank.FIVE),
        Card(Suit.DIAMONDS, Rank.FIVE),
    ]
    assert PlayValidator.can_beat_play(bomb_cards, current_pattern)

    print("✓ Play validator bomb test passed")


def test_play_validator_different_types_cannot_beat():
    """Test that different types (except bomb) cannot beat each other."""
    # Current play: Pair
    current_cards = [Card(Suit.SPADES, Rank.ACE), Card(Suit.HEARTS, Rank.ACE)]
    current_pattern = PatternRecognizer.analyze_cards(current_cards)

    # Triple cannot beat pair (different types)
    triple_cards = [
        Card(Suit.SPADES, Rank.FIVE),
        Card(Suit.HEARTS, Rank.FIVE),
        Card(Suit.CLUBS, Rank.FIVE),
    ]
    assert not PlayValidator.can_beat_play(triple_cards, current_pattern)

    print("✓ Play validator different types test passed")


# Tests can be run with pytest, no need for main function
# pytest will autodiscover all test_* functions

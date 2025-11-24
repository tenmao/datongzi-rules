"""Unit tests for models (Card, Deck, GameConfig)."""

import pytest
from datongzi_rules import Card, Rank, Suit, Deck, GameConfig


def test_deck_creation():
    """Test basic deck creation."""
    deck = Deck.create_standard_deck(num_decks=1)

    # Should have 11 ranks * 4 suits = 44 cards per deck
    assert len(deck) == 44
    print("✓ Deck creation test passed")


def test_deck_multiple_decks():
    """Test creating deck with multiple decks."""
    deck = Deck.create_standard_deck(num_decks=3)

    # 3 decks = 44 * 3 = 132 cards
    assert len(deck) == 132
    print("✓ Multiple decks test passed")


def test_deck_with_excluded_ranks():
    """Test deck with excluded ranks."""
    deck = Deck.create_standard_deck(num_decks=1, excluded_ranks={Rank.FIVE, Rank.SIX})

    # Should have (11 - 2) ranks * 4 suits = 36 cards
    assert len(deck) == 36

    # Verify excluded ranks are not present
    for card in deck.cards:
        assert card.rank not in {Rank.FIVE, Rank.SIX}

    print("✓ Deck with excluded ranks test passed")


def test_deck_shuffle():
    """Test deck shuffling."""
    deck1 = Deck.create_standard_deck(num_decks=1)
    original_order = [str(c) for c in deck1.cards[:10]]

    deck1.shuffle()
    shuffled_order = [str(c) for c in deck1.cards[:10]]

    # After shuffle, order should be different (with very high probability)
    # Note: There's a tiny chance this could fail randomly
    assert original_order != shuffled_order

    print("✓ Deck shuffle test passed")


def test_deck_deal():
    """Test dealing cards from deck."""
    deck = Deck.create_standard_deck(num_decks=1)
    initial_count = len(deck)

    dealt_cards = deck.deal_cards(5)

    assert len(dealt_cards) == 5
    assert len(deck) == initial_count - 5

    print("✓ Deck deal test passed")


def test_deck_deal_too_many():
    """Test dealing more cards than available."""
    deck = Deck.create_standard_deck(num_decks=1)
    total_cards = len(deck)

    with pytest.raises(ValueError, match="Cannot deal"):
        deck.deal_cards(total_cards + 1)

    print("✓ Deck deal too many test passed")


def test_deck_remaining_count():
    """Test remaining card count."""
    deck = Deck.create_standard_deck(num_decks=1)
    initial = len(deck)

    deck.deal_cards(10)

    assert len(deck) == initial - 10
    print("✓ Deck remaining count test passed")


def test_card_equality():
    """Test card equality comparison."""
    card1 = Card(Suit.SPADES, Rank.ACE)
    card2 = Card(Suit.SPADES, Rank.ACE)
    card3 = Card(Suit.HEARTS, Rank.ACE)
    
    assert card1 == card2
    assert card1 != card3
    
    print("✓ Card equality test passed")


def test_card_ordering():
    """Test card ordering (comparison)."""
    ace = Card(Suit.SPADES, Rank.ACE)
    king = Card(Suit.SPADES, Rank.KING)
    two = Card(Suit.SPADES, Rank.TWO)
    
    # TWO (15) > ACE (14) > KING (13)
    assert two > ace > king
    
    print("✓ Card ordering test passed")


def test_card_hash():
    """Test card hashing (for use in sets/dicts)."""
    card1 = Card(Suit.SPADES, Rank.ACE)
    card2 = Card(Suit.SPADES, Rank.ACE)

    # Same cards should have same hash
    assert hash(card1) == hash(card2)

    # Can be used in set
    card_set = {card1, card2}
    assert len(card_set) == 1  # Same card only counted once

    print("✓ Card hash test passed")


def test_card_invalid_suit():
    """Test creating card with invalid suit."""
    with pytest.raises((ValueError, TypeError)):
        Card("invalid", Rank.ACE)

    print("✓ Card invalid suit test passed")


def test_card_invalid_rank():
    """Test creating card with invalid rank."""
    with pytest.raises((ValueError, TypeError)):
        Card(Suit.SPADES, "invalid")

    print("✓ Card invalid rank test passed")


def test_card_scoring_cards():
    """Test identifying scoring cards."""
    five = Card(Suit.SPADES, Rank.FIVE)
    ten = Card(Suit.HEARTS, Rank.TEN)
    king = Card(Suit.CLUBS, Rank.KING)
    ace = Card(Suit.DIAMONDS, Rank.ACE)

    assert five.is_scoring_card
    assert ten.is_scoring_card
    assert king.is_scoring_card
    assert not ace.is_scoring_card

    print("✓ Card scoring cards test passed")


def test_card_score_values():
    """Test card score values."""
    five = Card(Suit.SPADES, Rank.FIVE)
    ten = Card(Suit.HEARTS, Rank.TEN)
    king = Card(Suit.CLUBS, Rank.KING)
    ace = Card(Suit.DIAMONDS, Rank.ACE)

    assert five.score_value == 5
    assert ten.score_value == 10
    assert king.score_value == 10
    assert ace.score_value == 0

    print("✓ Card score values test passed")


def test_card_string_representation():
    """Test card string representation."""
    card_ace = Card(Suit.SPADES, Rank.ACE)
    card_ten = Card(Suit.HEARTS, Rank.TEN)

    assert str(card_ace) == "♠A"
    assert str(card_ten) == "♥10"

    print("✓ Card string representation test passed")


def test_deck_deal_single_card():
    """Test dealing a single card."""
    deck = Deck.create_standard_deck(num_decks=1)
    original_count = len(deck)

    card = deck.deal_card()

    assert isinstance(card, Card)
    assert len(deck) == original_count - 1

    print("✓ Deck deal single card test passed")


def test_deck_deal_from_empty():
    """Test dealing from empty deck."""
    deck = Deck([])  # Empty deck

    with pytest.raises(ValueError, match="Cannot deal from empty deck"):
        deck.deal_card()

    print("✓ Deck deal from empty test passed")


def test_game_config_default():
    """Test default game configuration."""
    config = GameConfig()
    
    assert config.num_decks == 3
    assert config.num_players == 3
    assert config.cards_dealt_aside == 9
    assert config.finish_bonus == [100, -40, -60]
    assert config.must_beat_rule is True
    
    print("✓ Game config default test passed")


def test_game_config_custom():
    """Test custom game configuration."""
    config = GameConfig(
        num_decks=2,
        num_players=4,
        cards_dealt_aside=8,
        k_tongzi_bonus=150,
    )
    
    assert config.num_decks == 2
    assert config.num_players == 4
    assert config.k_tongzi_bonus == 150
    
    # finish_bonus should auto-adjust for 4 players
    assert len(config.finish_bonus) == 4
    assert config.finish_bonus[0] == 100  # First place always +100
    
    print("✓ Game config custom test passed")


def test_game_config_validation_players():
    """Test game config validation for player count."""
    with pytest.raises(ValueError, match="Must have at least 2 players"):
        GameConfig(num_players=1)
    
    print("✓ Game config player validation test passed")


def test_game_config_validation_decks():
    """Test game config validation for deck count."""
    with pytest.raises(ValueError, match="Must have at least 1 deck"):
        GameConfig(num_decks=0)
    
    print("✓ Game config deck validation test passed")


def test_game_config_total_cards():
    """Test total cards calculation."""
    config = GameConfig(num_decks=3, excluded_ranks=set())
    
    # 3 decks * 11 ranks * 4 suits = 132 cards
    assert config.total_cards == 132
    
    print("✓ Game config total cards test passed")


def test_game_config_cards_per_player():
    """Test cards per player calculation."""
    config = GameConfig(num_decks=3, num_players=3, cards_dealt_aside=9)
    
    # (132 - 9) / 3 = 41 cards per player
    assert config.cards_per_player == 41
    
    print("✓ Game config cards per player test passed")


def test_game_config_two_players():
    """Test game config for 2 players."""
    config = GameConfig(num_players=2)
    
    # 2 players should have finish_bonus = [100, -100]
    assert config.finish_bonus == [100, -100]
    
    print("✓ Game config two players test passed")


def test_game_config_four_players():
    """Test game config for 4 players."""
    config = GameConfig(num_players=4)

    # 4 players should have finish_bonus = [100, -20, -40, -80]
    assert config.finish_bonus == [100, -20, -40, -80]

    print("✓ Game config four players test passed")


def test_card_from_string_basic():
    """Test basic card string parsing."""
    # Test all suits
    assert Card.from_string("♠A") == Card(Suit.SPADES, Rank.ACE)
    assert Card.from_string("♥K") == Card(Suit.HEARTS, Rank.KING)
    assert Card.from_string("♣Q") == Card(Suit.CLUBS, Rank.QUEEN)
    assert Card.from_string("♦J") == Card(Suit.DIAMONDS, Rank.JACK)

    print("✓ Card from string basic test passed")


def test_card_from_string_all_ranks():
    """Test parsing all possible ranks."""
    test_cases = [
        ("♠5", Suit.SPADES, Rank.FIVE),
        ("♠6", Suit.SPADES, Rank.SIX),
        ("♠7", Suit.SPADES, Rank.SEVEN),
        ("♠8", Suit.SPADES, Rank.EIGHT),
        ("♠9", Suit.SPADES, Rank.NINE),
        ("♠10", Suit.SPADES, Rank.TEN),
        ("♠J", Suit.SPADES, Rank.JACK),
        ("♠Q", Suit.SPADES, Rank.QUEEN),
        ("♠K", Suit.SPADES, Rank.KING),
        ("♠A", Suit.SPADES, Rank.ACE),
        ("♠2", Suit.SPADES, Rank.TWO),
    ]

    for card_str, expected_suit, expected_rank in test_cases:
        card = Card.from_string(card_str)
        assert card.suit == expected_suit
        assert card.rank == expected_rank

    print("✓ Card from string all ranks test passed")


def test_card_from_string_invalid_inputs():
    """Test card string parsing with invalid inputs."""
    invalid_inputs = [
        "",           # Empty string
        "A",          # No suit
        "♠",          # No rank
        "XA",         # Invalid suit
        "♠X",         # Invalid rank
        "♠3",         # Excluded rank
        "♠4",         # Excluded rank
        "♠11",        # Invalid rank
        "♠♠A",        # Too many characters
    ]

    for invalid_input in invalid_inputs:
        with pytest.raises(ValueError):
            Card.from_string(invalid_input)

    print("✓ Card from string invalid inputs test passed")


def test_card_string_round_trip():
    """Test that str(card) and Card.from_string() are consistent."""
    # Test all valid combinations
    for suit in Suit:
        for rank in Rank:
            original_card = Card(suit, rank)
            card_str = str(original_card)
            parsed_card = Card.from_string(card_str)
            assert parsed_card == original_card

    print("✓ Card string round trip test passed")


def test_deck_creation_edge_cases():
    """Test deck creation with various parameters."""
    # Empty deck (exclude all ranks)
    all_ranks = set(Rank)
    empty_deck = Deck.create_standard_deck(num_decks=1, excluded_ranks=all_ranks)
    assert len(empty_deck.cards) == 0

    # Single card deck
    most_ranks = set(Rank) - {Rank.ACE}
    single_deck = Deck.create_standard_deck(num_decks=1, excluded_ranks=most_ranks)
    assert len(single_deck.cards) == 4  # 4 suits × 1 rank

    print("✓ Deck creation edge cases test passed")


def test_deck_dealing_edge_cases():
    """Test deck dealing edge cases."""
    deck = Deck.create_standard_deck(num_decks=1)
    initial_count = len(deck)

    # Deal all cards
    all_cards = deck.deal_cards(initial_count)
    assert len(all_cards) == initial_count
    assert len(deck) == 0

    # Try to deal from empty deck
    with pytest.raises(ValueError):
        deck.deal_card()

    with pytest.raises(ValueError):
        deck.deal_cards(1)

    print("✓ Deck dealing edge cases test passed")


# All tests can be run with pytest
# pytest will autodiscover all test_* functions

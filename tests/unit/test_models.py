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


# All tests can be run with pytest
# pytest will autodiscover all test_* functions

"""Integration tests for complete game flow."""

from datongzi_rules import (
    Deck,
    ConfigFactory,
    PatternRecognizer,
    PlayValidator,
    ScoringEngine,
    PlayGenerator,
    HandEvaluator,
    PlayType,
)


def test_complete_game_setup():
    """Test complete game setup from configuration to dealing."""
    # Create configuration
    config = ConfigFactory.create_standard_3deck_3player()
    
    # Create and shuffle deck
    deck = Deck.create_standard_deck(num_decks=config.num_decks)
    assert len(deck) == 132
    
    deck.shuffle()
    
    # Deal cards
    hands = []
    for _ in range(config.num_players):
        hand = deck.deal_cards(config.cards_per_player)
        hands.append(hand)
        assert len(hand) == 41
    
    # Deal aside cards
    aside = deck.deal_cards(config.cards_dealt_aside)
    assert len(aside) == 9
    assert len(deck) == 0  # All cards dealt
    
    print("✓ Complete game setup test passed")


def test_pattern_recognition_and_validation_flow():
    """Test pattern recognition followed by play validation."""
    # Create some cards
    pair_low = [
        Deck.create_standard_deck().cards[0],
        Deck.create_standard_deck().cards[1],
    ]
    
    # Ensure they're actually a pair for testing
    from datongzi_rules import Card, Rank, Suit
    pair_low = [
        Card(Suit.SPADES, Rank.FIVE),
        Card(Suit.HEARTS, Rank.FIVE),
    ]
    
    # Recognize pattern
    pattern = PatternRecognizer.analyze_cards(pair_low)
    assert pattern is not None
    assert pattern.play_type == PlayType.PAIR
    
    # Create higher pair
    pair_high = [
        Card(Suit.SPADES, Rank.KING),
        Card(Suit.HEARTS, Rank.KING),
    ]
    
    # Validate it beats the lower pair
    assert PlayValidator.can_beat_play(pair_high, pattern)
    
    # Create single card
    single = [Card(Suit.SPADES, Rank.ACE)]
    
    # Single cannot beat pair (different types)
    assert not PlayValidator.can_beat_play(single, pattern)
    
    print("✓ Pattern recognition and validation flow test passed")


def test_ai_helper_integration():
    """Test AI helpers working together."""
    from datongzi_rules import Card, Rank, Suit
    
    # Create a hand
    hand = [
        Card(Suit.SPADES, Rank.FIVE),
        Card(Suit.HEARTS, Rank.FIVE),
        Card(Suit.SPADES, Rank.KING),
        Card(Suit.HEARTS, Rank.KING),
        Card(Suit.CLUBS, Rank.KING),
        Card(Suit.DIAMONDS, Rank.ACE),
    ]
    
    # Generate all possible plays
    all_plays = PlayGenerator.generate_all_plays(hand)
    assert len(all_plays) > 0
    
    # All generated plays should be valid
    for play in all_plays:
        pattern = PatternRecognizer.analyze_cards(play)
        assert pattern is not None
    
    # Evaluate hand strength
    strength = HandEvaluator.evaluate_hand(hand)
    assert strength > 0
    
    # Suggest best play
    best_play = HandEvaluator.suggest_best_play(hand)
    assert best_play is not None
    assert len(best_play) > 0
    
    print("✓ AI helper integration test passed")


def test_scoring_flow():
    """Test complete scoring flow."""
    from datongzi_rules import Card, Rank, Suit
    
    config = ConfigFactory.create_standard_3deck_3player()
    engine = ScoringEngine(config)
    
    # Create round cards with scoring cards
    round_cards = [
        Card(Suit.SPADES, Rank.FIVE),  # 5 points
        Card(Suit.HEARTS, Rank.TEN),  # 10 points
        Card(Suit.CLUBS, Rank.KING),  # 10 points
    ]
    
    # Player 1 wins the round
    win_event = engine.create_round_win_event("player1", round_cards, round_number=1)
    assert win_event is not None
    assert win_event.points == 25
    
    # Create special bonus (Tongzi)
    tongzi_cards = [
        Card(Suit.SPADES, Rank.ACE),
        Card(Suit.SPADES, Rank.ACE),
        Card(Suit.SPADES, Rank.ACE),
    ]
    tongzi_pattern = PatternRecognizer.analyze_cards(tongzi_cards)
    
    bonus_events = engine.create_special_bonus_events(
        "player1", tongzi_pattern, round_number=2
    )
    assert len(bonus_events) == 1
    assert bonus_events[0].points == 200  # A Tongzi bonus
    
    # Create finish bonuses
    finish_events = engine.create_finish_bonus_events(
        ["player1", "player2", "player3"]
    )
    assert len(finish_events) == 3
    
    # Calculate totals
    total_p1 = engine.calculate_total_score_for_player("player1")
    assert total_p1 == 25 + 200 + 100  # Round + Tongzi + Finish
    
    # Validate scores
    player_scores = {
        "player1": total_p1,
        "player2": engine.calculate_total_score_for_player("player2"),
        "player3": engine.calculate_total_score_for_player("player3"),
    }
    
    assert engine.validate_scores(player_scores) is True
    
    print("✓ Scoring flow test passed")


def test_variant_playability():
    """Test that different variants are playable."""
    variants = [
        ConfigFactory.create_standard_3deck_3player(),
        ConfigFactory.create_4deck_4player(),
        ConfigFactory.create_2player(),
        ConfigFactory.create_quick_game(),
    ]
    
    for config in variants:
        # Create deck
        deck = Deck.create_standard_deck(num_decks=config.num_decks)
        
        # Should have enough cards
        assert len(deck) >= config.num_players * 10
        
        # Deal cards
        for _ in range(config.num_players):
            hand = deck.deal_cards(config.cards_per_player)
            assert len(hand) == config.cards_per_player
        
        # Verify finish bonuses
        assert len(config.finish_bonus) == config.num_players
    
    print("✓ Variant playability test passed")


def test_round_trip_serialization():
    """Test that patterns can be analyzed and recreated."""
    from datongzi_rules import Card, Rank, Suit
    
    # Create original cards
    original_cards = [
        Card(Suit.SPADES, Rank.KING),
        Card(Suit.HEARTS, Rank.KING),
        Card(Suit.CLUBS, Rank.KING),
    ]
    
    # Analyze pattern
    pattern = PatternRecognizer.analyze_cards(original_cards)
    assert pattern is not None
    
    # Pattern properties should match cards
    assert pattern.play_type == PlayType.TRIPLE
    assert pattern.primary_rank == Rank.KING
    assert pattern.card_count == 3
    
    # Can use pattern for validation
    higher_triple = [
        Card(Suit.SPADES, Rank.ACE),
        Card(Suit.HEARTS, Rank.ACE),
        Card(Suit.CLUBS, Rank.ACE),
    ]
    
    assert PlayValidator.can_beat_play(higher_triple, pattern)
    
    print("✓ Round-trip serialization test passed")


# All tests can be run with pytest
# pytest will autodiscover all test_* functions

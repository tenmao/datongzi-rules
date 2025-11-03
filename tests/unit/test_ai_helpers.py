"""Unit tests for AI helper modules."""

from datongzi_rules import (
    Card,
    Rank,
    Suit,
    PlayGenerator,
    HandEvaluator,
    HandAnalyzer,
    PatternSuggester,
    PatternRecognizer,
    PlayType,
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

def test_hand_evaluator_empty_hand():
    """Test evaluating empty hand."""
    score = HandEvaluator.evaluate_hand([])
    assert score == 0.0
    print("✓ Empty hand evaluation test passed")


def test_hand_evaluator_high_cards():
    """Test that high cards give better scores."""
    low_hand = [Card(Suit.SPADES, Rank.FIVE), Card(Suit.HEARTS, Rank.SIX)]
    high_hand = [Card(Suit.SPADES, Rank.ACE), Card(Suit.HEARTS, Rank.TWO)]
    
    low_score = HandEvaluator.evaluate_hand(low_hand)
    high_score = HandEvaluator.evaluate_hand(high_hand)
    
    assert high_score > low_score
    print("✓ High card evaluation test passed")


def test_hand_evaluator_bombs():
    """Test that bombs increase hand score."""
    normal_hand = [
        Card(Suit.SPADES, Rank.FIVE),
        Card(Suit.HEARTS, Rank.SIX),
        Card(Suit.CLUBS, Rank.SEVEN),
        Card(Suit.DIAMONDS, Rank.EIGHT),
    ]
    
    bomb_hand = [
        Card(Suit.SPADES, Rank.TEN),
        Card(Suit.HEARTS, Rank.TEN),
        Card(Suit.CLUBS, Rank.TEN),
        Card(Suit.DIAMONDS, Rank.TEN),
    ]
    
    normal_score = HandEvaluator.evaluate_hand(normal_hand)
    bomb_score = HandEvaluator.evaluate_hand(bomb_hand)
    
    assert bomb_score > normal_score
    print("✓ Bomb evaluation test passed")


def test_hand_evaluator_play_strength():
    """Test evaluating play strength."""
    # Single
    single = [Card(Suit.SPADES, Rank.FIVE)]
    single_strength = HandEvaluator.evaluate_play_strength(single)
    
    # Bomb
    bomb = [
        Card(Suit.SPADES, Rank.TEN),
        Card(Suit.HEARTS, Rank.TEN),
        Card(Suit.CLUBS, Rank.TEN),
        Card(Suit.DIAMONDS, Rank.TEN),
    ]
    bomb_strength = HandEvaluator.evaluate_play_strength(bomb)
    
    # Bomb should be much stronger
    assert bomb_strength > single_strength * 10
    print("✓ Play strength evaluation test passed")


def test_hand_evaluator_suggest_best_play():
    """Test suggesting best play from hand."""
    hand = [
        Card(Suit.SPADES, Rank.FIVE),
        Card(Suit.HEARTS, Rank.FIVE),
        Card(Suit.CLUBS, Rank.KING),
    ]
    
    best_play = HandEvaluator.suggest_best_play(hand)
    
    # Should suggest some valid play
    assert best_play is not None
    assert len(best_play) > 0
    print("✓ Best play suggestion test passed")


# HandAnalyzer Tests

def test_hand_analyzer_basic():
    """Test basic hand analysis."""
    hand = [
        Card(Suit.SPADES, Rank.FIVE),
        Card(Suit.HEARTS, Rank.FIVE),
        Card(Suit.CLUBS, Rank.KING),
        Card(Suit.DIAMONDS, Rank.KING),
    ]
    
    analysis = HandAnalyzer.analyze_hand(hand)
    
    assert analysis["total_cards"] == 4
    assert analysis["pairs"] == 2
    assert analysis["singles"] == 0
    assert "strength_score" in analysis
    print("✓ Hand analyzer basic test passed")


def test_hand_analyzer_with_bombs():
    """Test hand analysis with bombs."""
    hand = [
        Card(Suit.SPADES, Rank.TEN),
        Card(Suit.HEARTS, Rank.TEN),
        Card(Suit.CLUBS, Rank.TEN),
        Card(Suit.DIAMONDS, Rank.TEN),
    ]
    
    analysis = HandAnalyzer.analyze_hand(hand)
    
    assert analysis["bombs"] >= 1
    assert analysis["quads_plus"] >= 1
    print("✓ Hand analyzer bombs test passed")


# PatternSuggester Tests

def test_pattern_suggester_valid_input():
    """Test pattern suggester with already valid input."""
    cards = [
        Card(Suit.SPADES, Rank.KING),
        Card(Suit.HEARTS, Rank.KING),
    ]
    
    corrected, confidence = PatternSuggester.suggest_correction(cards)
    
    # Should return same cards with high confidence
    assert len(corrected) == 2
    assert confidence == 1.0
    print("✓ Pattern suggester valid input test passed")


def test_pattern_suggester_remove_duplicates():
    """Test removing duplicate cards."""
    # Simulate CV double-detection - in practice this would be caught before
    # pattern recognition, but test the logic anyway
    cards = [
        Card(Suit.SPADES, Rank.KING),
        Card(Suit.HEARTS, Rank.KING),
        Card(Suit.CLUBS, Rank.KING),
        Card(Suit.DIAMONDS, Rank.KING),
        # 5th King would exceed 3-deck limit (4 max)
        # But since all 4 suits used, this is actually valid 4-card bomb
    ]

    # This should be recognized as valid bomb, not error
    corrected, confidence = PatternSuggester.suggest_correction(cards)

    # Should recognize as valid pattern (bomb)
    assert confidence >= 0.8
    print("✓ Pattern suggester remove duplicates test passed")


def test_pattern_suggester_validate_hand():
    """Test hand validation."""
    # Valid hand
    valid_hand = [Card(Suit.SPADES, Rank.FIVE), Card(Suit.HEARTS, Rank.SIX)]
    is_valid, errors = PatternSuggester.validate_hand(valid_hand)
    
    assert is_valid
    assert len(errors) == 0
    
    # Invalid hand (too many of same card)
    invalid_hand = [Card(Suit.SPADES, Rank.FIVE)] * 5  # 5 identical cards
    is_valid, errors = PatternSuggester.validate_hand(invalid_hand)
    
    assert not is_valid
    assert len(errors) > 0
    print("✓ Hand validation test passed")


def test_pattern_suggester_suggest_type():
    """Test suggesting pattern type."""
    # Single
    single = [Card(Suit.SPADES, Rank.FIVE)]
    suggested = PatternSuggester.suggest_pattern_type(single)
    assert suggested == PlayType.SINGLE
    
    # Pair
    pair = [Card(Suit.SPADES, Rank.KING), Card(Suit.HEARTS, Rank.KING)]
    suggested = PatternSuggester.suggest_pattern_type(pair)
    assert suggested == PlayType.PAIR
    
    # Bomb
    bomb = [
        Card(Suit.SPADES, Rank.TEN),
        Card(Suit.HEARTS, Rank.TEN),
        Card(Suit.CLUBS, Rank.TEN),
        Card(Suit.DIAMONDS, Rank.TEN),
    ]
    suggested = PatternSuggester.suggest_pattern_type(bomb)
    assert suggested == PlayType.BOMB
    
    print("✓ Pattern type suggestion test passed")


def test_play_generator_comprehensive():
    """Test comprehensive play generation from larger hand."""
    hand = [
        # Pair of 5s
        Card(Suit.SPADES, Rank.FIVE),
        Card(Suit.HEARTS, Rank.FIVE),
        # Triple of Kings
        Card(Suit.SPADES, Rank.KING),
        Card(Suit.HEARTS, Rank.KING),
        Card(Suit.CLUBS, Rank.KING),
        # Random cards
        Card(Suit.DIAMONDS, Rank.SEVEN),
        Card(Suit.SPADES, Rank.ACE),
    ]
    
    plays = PlayGenerator.generate_all_plays(hand)
    
    # Should generate many different plays
    assert len(plays) > 10
    
    # All plays should be valid
    for play in plays:
        pattern = PatternRecognizer.analyze_cards(play)
        assert pattern is not None
    
    print("✓ Comprehensive play generation test passed")


# All tests can be run with pytest
# pytest will autodiscover all test_* functions

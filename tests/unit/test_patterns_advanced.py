"""Advanced pattern recognition tests."""

from datongzi_rules import Card, Rank, Suit, PatternRecognizer, PlayType, PlayValidator, PlayPattern


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
class TestEnhancedPlayValidation:
    """Test enhanced play validation with comprehensive edge cases."""

    def test_invalid_mixed_rank_combinations(self):
        """Test various invalid mixed rank combinations."""
        # Invalid: 5, 6 (not a valid combination)
        cards = [
            Card(Suit.SPADES, Rank.FIVE),
            Card(Suit.HEARTS, Rank.SIX)
        ]
        pattern = PatternRecognizer.analyze_cards(cards)
        assert pattern is None

        # Invalid: 5, 6, 7 (straight not allowed in this game)
        cards = [
            Card(Suit.SPADES, Rank.FIVE),
            Card(Suit.HEARTS, Rank.SIX),
            Card(Suit.CLUBS, Rank.SEVEN)
        ]
        pattern = PatternRecognizer.analyze_cards(cards)
        assert pattern is None

        # Invalid: A, K, Q (not consecutive for this game)
        cards = [
            Card(Suit.SPADES, Rank.ACE),
            Card(Suit.HEARTS, Rank.KING),
            Card(Suit.CLUBS, Rank.QUEEN)
        ]
        pattern = PatternRecognizer.analyze_cards(cards)
        assert pattern is None

    def test_invalid_pair_variations(self):
        """Test invalid pair variations."""
        # Invalid: triple pretending to be pair
        cards = [
            Card(Suit.SPADES, Rank.KING),
            Card(Suit.HEARTS, Rank.KING),
            Card(Suit.CLUBS, Rank.KING)
        ]
        # This should be TRIPLE, not PAIR
        pattern = PatternRecognizer.analyze_cards(cards)
        assert pattern.play_type == PlayType.TRIPLE

        # Invalid: mixed ranks
        cards = [
            Card(Suit.SPADES, Rank.FIVE),
            Card(Suit.HEARTS, Rank.SIX),
            Card(Suit.CLUBS, Rank.SEVEN),
            Card(Suit.DIAMONDS, Rank.EIGHT)
        ]
        pattern = PatternRecognizer.analyze_cards(cards)
        assert pattern is None

    def test_incomplete_patterns(self):
        """Test incomplete or broken patterns."""
        # Incomplete consecutive pairs (only one pair)
        cards = [
            Card(Suit.SPADES, Rank.JACK),
            Card(Suit.HEARTS, Rank.JACK)
        ]
        pattern = PatternRecognizer.analyze_cards(cards)
        assert pattern.play_type == PlayType.PAIR  # Should be pair, not consecutive

        # Incomplete airplane (only one triple)
        cards = [
            Card(Suit.SPADES, Rank.QUEEN),
            Card(Suit.HEARTS, Rank.QUEEN),
            Card(Suit.CLUBS, Rank.QUEEN)
        ]
        pattern = PatternRecognizer.analyze_cards(cards)
        assert pattern.play_type == PlayType.TRIPLE  # Should be triple, not airplane

        # Incomplete bomb (only 3 cards)
        cards = [
            Card(Suit.SPADES, Rank.SEVEN),
            Card(Suit.HEARTS, Rank.SEVEN),
            Card(Suit.CLUBS, Rank.SEVEN)
        ]
        pattern = PatternRecognizer.analyze_cards(cards)
        assert pattern.play_type == PlayType.TRIPLE  # Should be triple, not bomb

    def test_invalid_triple_with_two_variations(self):
        """Test invalid triple with two variations."""
        # Invalid: two triples
        cards = [
            Card(Suit.SPADES, Rank.KING),
            Card(Suit.HEARTS, Rank.KING),
            Card(Suit.CLUBS, Rank.KING),
            Card(Suit.SPADES, Rank.QUEEN),
            Card(Suit.HEARTS, Rank.QUEEN),
            Card(Suit.CLUBS, Rank.QUEEN)
        ]
        pattern = PatternRecognizer.analyze_cards(cards)
        assert pattern.play_type == PlayType.AIRPLANE  # Should be airplane

        # Invalid: triple with single
        cards = [
            Card(Suit.SPADES, Rank.KING),
            Card(Suit.HEARTS, Rank.KING),
            Card(Suit.CLUBS, Rank.KING),
            Card(Suit.SPADES, Rank.FIVE)
        ]
        pattern = PatternRecognizer.analyze_cards(cards)
        assert pattern is None  # Invalid combination

        # Invalid: triple with three singles
        cards = [
            Card(Suit.SPADES, Rank.KING),
            Card(Suit.HEARTS, Rank.KING),
            Card(Suit.CLUBS, Rank.KING),
            Card(Suit.SPADES, Rank.FIVE),
            Card(Suit.HEARTS, Rank.SIX),
            Card(Suit.CLUBS, Rank.SEVEN)
        ]
        pattern = PatternRecognizer.analyze_cards(cards)
        assert pattern is None  # Invalid combination

    def test_complex_invalid_combinations(self):
        """Test complex invalid card combinations."""
        # Mixed pattern types
        cards = [
            Card(Suit.SPADES, Rank.ACE),      # Single
            Card(Suit.HEARTS, Rank.KING),    # Another single
            Card(Suit.CLUBS, Rank.QUEEN),    # Another single
            Card(Suit.SPADES, Rank.JACK),    # Pair start
            Card(Suit.HEARTS, Rank.JACK)     # Pair end
        ]
        pattern = PatternRecognizer.analyze_cards(cards)
        assert pattern is None

        # Too many cards for any valid pattern
        cards = [
            Card(Suit.SPADES, Rank.FIVE),
            Card(Suit.HEARTS, Rank.SIX),
            Card(Suit.CLUBS, Rank.SEVEN),
            Card(Suit.DIAMONDS, Rank.EIGHT),
            Card(Suit.SPADES, Rank.NINE),
            Card(Suit.HEARTS, Rank.TEN),
            Card(Suit.CLUBS, Rank.JACK),
            Card(Suit.DIAMONDS, Rank.QUEEN),
            Card(Suit.SPADES, Rank.KING),
            Card(Suit.HEARTS, Rank.ACE)
        ]
        pattern = PatternRecognizer.analyze_cards(cards)
        assert pattern is None

    def test_edge_case_rank_boundaries(self):
        """Test edge cases with rank boundaries."""
        # Highest rank single
        cards = [Card(Suit.SPADES, Rank.TWO)]
        pattern = PatternRecognizer.analyze_cards(cards)
        assert pattern.play_type == PlayType.SINGLE
        assert pattern.primary_rank == Rank.TWO

        # Lowest rank single
        cards = [Card(Suit.SPADES, Rank.FIVE)]
        pattern = PatternRecognizer.analyze_cards(cards)
        assert pattern.play_type == PlayType.SINGLE
        assert pattern.primary_rank == Rank.FIVE

        # Edge case: Can TWO beat ACE?
        current_cards = [Card(Suit.SPADES, Rank.ACE)]
        new_cards = [Card(Suit.HEARTS, Rank.TWO)]

        current_pattern = PatternRecognizer.analyze_cards(current_cards)
        assert PlayValidator.can_beat_play(new_cards, current_pattern)

    def test_consecutive_pattern_edge_cases(self):
        """Test edge cases in consecutive patterns."""
        # Non-consecutive pairs
        cards = [
            Card(Suit.SPADES, Rank.FIVE),
            Card(Suit.HEARTS, Rank.FIVE),
            Card(Suit.CLUBS, Rank.SEVEN),  # Gap here
            Card(Suit.DIAMONDS, Rank.SEVEN)
        ]
        pattern = PatternRecognizer.analyze_cards(cards)
        assert pattern is None  # Should be invalid due to gap

        # Too few consecutive pairs (need at least 2)
        cards = [
            Card(Suit.SPADES, Rank.JACK),
            Card(Suit.HEARTS, Rank.JACK)
        ]
        pattern = PatternRecognizer.analyze_cards(cards)
        assert pattern.play_type == PlayType.PAIR  # Should be pair, not consecutive

        # Boundary consecutive pairs (5-6, highest possible start)
        cards = [
            Card(Suit.SPADES, Rank.FIVE),
            Card(Suit.HEARTS, Rank.FIVE),
            Card(Suit.CLUBS, Rank.SIX),
            Card(Suit.DIAMONDS, Rank.SIX)
        ]
        pattern = PatternRecognizer.analyze_cards(cards)
        assert pattern.play_type == PlayType.CONSECUTIVE_PAIRS

    def test_special_pattern_edge_cases(self):
        """Test edge cases for special patterns (tongzi, dizha)."""
        # Tongzi with wrong suit count
        cards = [
            Card(Suit.SPADES, Rank.KING),
            Card(Suit.SPADES, Rank.KING),
            Card(Suit.HEARTS, Rank.KING)  # Different suit
        ]
        pattern = PatternRecognizer.analyze_cards(cards)
        assert pattern.play_type == PlayType.TRIPLE  # Should be triple, not tongzi

        # Incomplete dizha (missing some suits) - should be recognized as bomb
        cards = [
            Card(Suit.SPADES, Rank.ACE),
            Card(Suit.SPADES, Rank.ACE),
            Card(Suit.HEARTS, Rank.ACE),
            Card(Suit.HEARTS, Rank.ACE),
            Card(Suit.CLUBS, Rank.ACE),
            Card(Suit.CLUBS, Rank.ACE)
            # Missing diamonds
        ]
        pattern = PatternRecognizer.analyze_cards(cards)
        assert pattern.play_type == PlayType.BOMB  # Should be bomb (6 of same rank)

        # Dizha with wrong count per suit - should be recognized as bomb
        cards = [
            Card(Suit.SPADES, Rank.ACE),      # Only 1 spade
            Card(Suit.HEARTS, Rank.ACE),
            Card(Suit.HEARTS, Rank.ACE),
            Card(Suit.CLUBS, Rank.ACE),
            Card(Suit.CLUBS, Rank.ACE),
            Card(Suit.DIAMONDS, Rank.ACE),
            Card(Suit.DIAMONDS, Rank.ACE)
        ]
        pattern = PatternRecognizer.analyze_cards(cards)
        assert pattern.play_type == PlayType.BOMB  # Should be bomb (7 of same rank)

    def test_beating_validation_edge_cases(self):
        """Test edge cases in beating validation."""
        # Same rank shouldn't beat
        current_cards = [Card(Suit.SPADES, Rank.KING)]
        new_cards = [Card(Suit.HEARTS, Rank.KING)]

        current_pattern = PatternRecognizer.analyze_cards(current_cards)
        assert not PlayValidator.can_beat_play(new_cards, current_pattern)

        # Wrong pattern type shouldn't beat
        current_cards = [
            Card(Suit.SPADES, Rank.KING),
            Card(Suit.HEARTS, Rank.KING)
        ]
        new_cards = [
            Card(Suit.CLUBS, Rank.ACE),
            Card(Suit.DIAMONDS, Rank.ACE),
            Card(Suit.SPADES, Rank.ACE)
        ]

        current_pattern = PatternRecognizer.analyze_cards(current_cards)
        assert not PlayValidator.can_beat_play(new_cards, current_pattern)

        # Higher dizha should beat lower dizha
        current_cards = [
            Card(Suit.SPADES, Rank.FIVE),
            Card(Suit.SPADES, Rank.FIVE),
            Card(Suit.HEARTS, Rank.FIVE),
            Card(Suit.HEARTS, Rank.FIVE),
            Card(Suit.CLUBS, Rank.FIVE),
            Card(Suit.CLUBS, Rank.FIVE),
            Card(Suit.DIAMONDS, Rank.FIVE),
            Card(Suit.DIAMONDS, Rank.FIVE)
        ]
        new_cards = [
            Card(Suit.SPADES, Rank.ACE),
            Card(Suit.SPADES, Rank.ACE),
            Card(Suit.HEARTS, Rank.ACE),
            Card(Suit.HEARTS, Rank.ACE),
            Card(Suit.CLUBS, Rank.ACE),
            Card(Suit.CLUBS, Rank.ACE),
            Card(Suit.DIAMONDS, Rank.ACE),
            Card(Suit.DIAMONDS, Rank.ACE)
        ]

        current_pattern = PatternRecognizer.analyze_cards(current_cards)
        assert PlayValidator.can_beat_play(new_cards, current_pattern)

    def test_null_and_empty_inputs(self):
        """Test null and empty input handling."""
        # Empty card list
        pattern = PatternRecognizer.analyze_cards([])
        assert pattern is None

        # None input
        pattern = PatternRecognizer.analyze_cards(None)
        assert pattern is None

        # Beating with empty cards
        current_pattern = PlayPattern(
            play_type=PlayType.SINGLE,
            primary_rank=Rank.KING,
            primary_suit=Suit.SPADES,
            secondary_ranks=[],
            card_count=1,
            strength=1300
        )
        assert not PlayValidator.can_beat_play([], current_pattern)
        assert not PlayValidator.can_beat_play(None, current_pattern)

    def test_card_count_validation(self):
        """Test card count validation for each pattern type."""
        # Single must be exactly 1 card
        cards = [Card(Suit.SPADES, Rank.ACE)]
        pattern = PatternRecognizer.analyze_cards(cards)
        assert pattern.card_count == 1

        # Pair must be exactly 2 cards
        cards = [
            Card(Suit.SPADES, Rank.ACE),
            Card(Suit.HEARTS, Rank.ACE)
        ]
        pattern = PatternRecognizer.analyze_cards(cards)
        assert pattern.card_count == 2

        # Triple must be exactly 3 cards
        cards = [
            Card(Suit.SPADES, Rank.ACE),
            Card(Suit.HEARTS, Rank.ACE),
            Card(Suit.CLUBS, Rank.ACE)
        ]
        pattern = PatternRecognizer.analyze_cards(cards)
        assert pattern.card_count == 3

        # Bomb must be at least 4 cards
        cards = [
            Card(Suit.SPADES, Rank.ACE),
            Card(Suit.HEARTS, Rank.ACE),
            Card(Suit.CLUBS, Rank.ACE),
            Card(Suit.DIAMONDS, Rank.ACE)
        ]
        pattern = PatternRecognizer.analyze_cards(cards)
        assert pattern.card_count == 4

        # Tongzi must be exactly 3 cards
        cards = [
            Card(Suit.SPADES, Rank.ACE),
            Card(Suit.SPADES, Rank.ACE),
            Card(Suit.SPADES, Rank.ACE)
        ]
        pattern = PatternRecognizer.analyze_cards(cards)
        assert pattern.card_count == 3

        # Dizha must be exactly 8 cards
        cards = [
            Card(Suit.SPADES, Rank.ACE),
            Card(Suit.SPADES, Rank.ACE),
            Card(Suit.HEARTS, Rank.ACE),
            Card(Suit.HEARTS, Rank.ACE),
            Card(Suit.CLUBS, Rank.ACE),
            Card(Suit.CLUBS, Rank.ACE),
            Card(Suit.DIAMONDS, Rank.ACE),
            Card(Suit.DIAMONDS, Rank.ACE)
        ]
        pattern = PatternRecognizer.analyze_cards(cards)
        assert pattern.card_count == 8

    def test_must_beat_rule_enforcement(self):
        """Test 有牌必打 (must beat) rule enforcement."""
        # Player should be forced to play if they can beat
        current_cards = [Card(Suit.SPADES, Rank.KING)]
        current_pattern = PatternRecognizer.analyze_cards(current_cards)

        # Player has ACE, can beat KING
        player_cards = [Card(Suit.HEARTS, Rank.ACE)]
        can_beat = PlayValidator.can_beat_play(player_cards, current_pattern)
        assert can_beat  # Player must play, cannot pass

        # Player has lower card, can pass
        player_cards = [Card(Suit.HEARTS, Rank.QUEEN)]
        can_beat = PlayValidator.can_beat_play(player_cards, current_pattern)
        assert not can_beat  # Player can pass

    def test_strength_calculation_consistency(self):
        """Test that strength calculations are consistent and logical."""
        # Higher rank should have higher strength
        ace_single = PatternRecognizer.analyze_cards([Card(Suit.SPADES, Rank.ACE)])
        king_single = PatternRecognizer.analyze_cards([Card(Suit.SPADES, Rank.KING)])
        assert ace_single.strength > king_single.strength

        # Special patterns should have higher strength than regular patterns
        ace_tongzi = PatternRecognizer.analyze_cards([
            Card(Suit.SPADES, Rank.ACE),
            Card(Suit.SPADES, Rank.ACE),
            Card(Suit.SPADES, Rank.ACE)
        ])
        ace_triple = PatternRecognizer.analyze_cards([
            Card(Suit.SPADES, Rank.ACE),
            Card(Suit.HEARTS, Rank.ACE),
            Card(Suit.CLUBS, Rank.ACE)
        ])
        assert ace_tongzi.strength > ace_triple.strength

        # Dizha should have highest strength
        five_dizha = PatternRecognizer.analyze_cards([
            Card(Suit.SPADES, Rank.FIVE),
            Card(Suit.SPADES, Rank.FIVE),
            Card(Suit.HEARTS, Rank.FIVE),
            Card(Suit.HEARTS, Rank.FIVE),
            Card(Suit.CLUBS, Rank.FIVE),
            Card(Suit.CLUBS, Rank.FIVE),
            Card(Suit.DIAMONDS, Rank.FIVE),
            Card(Suit.DIAMONDS, Rank.FIVE)
        ])
        two_tongzi = PatternRecognizer.analyze_cards([
            Card(Suit.SPADES, Rank.TWO),
            Card(Suit.SPADES, Rank.TWO),
            Card(Suit.SPADES, Rank.TWO)
        ])
        assert five_dizha.strength > two_tongzi.strength


class TestPatternRecognitionEdgeCases:
    """Test pattern recognition edge cases."""

    def test_pattern_recognition_empty_input(self):
        """Test pattern recognition with empty or invalid input."""
        # Empty list
        pattern = PatternRecognizer.analyze_cards([])
        assert pattern is None

        # Single card should work
        single_card = [Card(Suit.SPADES, Rank.ACE)]
        pattern = PatternRecognizer.analyze_cards(single_card)
        assert pattern is not None
        assert pattern.play_type == PlayType.SINGLE

    def test_pattern_recognition_boundary_ranks(self):
        """Test pattern recognition with boundary ranks."""
        # Test with lowest rank (5)
        fives = [Card(suit, Rank.FIVE) for suit in Suit]
        pattern = PatternRecognizer.analyze_cards(fives)
        assert pattern is not None
        assert pattern.primary_rank == Rank.FIVE

        # Test with highest rank (2)
        twos = [Card(suit, Rank.TWO) for suit in Suit]
        pattern = PatternRecognizer.analyze_cards(twos)
        assert pattern is not None
        assert pattern.primary_rank == Rank.TWO


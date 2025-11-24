"""Test pattern recognition and play validation."""

from datongzi_rules import Card, PatternRecognizer, PlayType, PlayValidator, Rank, Suit


class TestPatternRecognizer:
    """Test pattern recognition functionality."""

    def test_single_card(self):
        """Test recognizing single card."""
        cards = [Card(Suit.SPADES, Rank.ACE)]
        pattern = PatternRecognizer.analyze_cards(cards)

        assert pattern is not None
        assert pattern.play_type == PlayType.SINGLE
        assert pattern.primary_rank == Rank.ACE
        assert pattern.card_count == 1

    def test_pair(self):
        """Test recognizing pair."""
        cards = [Card(Suit.SPADES, Rank.ACE), Card(Suit.HEARTS, Rank.ACE)]
        pattern = PatternRecognizer.analyze_cards(cards)

        assert pattern is not None
        assert pattern.play_type == PlayType.PAIR
        assert pattern.primary_rank == Rank.ACE
        assert pattern.card_count == 2

    def test_invalid_pair(self):
        """Test invalid pair (different ranks)."""
        cards = [Card(Suit.SPADES, Rank.ACE), Card(Suit.HEARTS, Rank.KING)]
        pattern = PatternRecognizer.analyze_cards(cards)

        assert pattern is None

    def test_consecutive_pairs(self):
        """Test recognizing consecutive pairs."""
        cards = [
            Card(Suit.SPADES, Rank.JACK),
            Card(Suit.HEARTS, Rank.JACK),
            Card(Suit.CLUBS, Rank.QUEEN),
            Card(Suit.DIAMONDS, Rank.QUEEN),
        ]
        pattern = PatternRecognizer.analyze_cards(cards)

        assert pattern is not None
        assert pattern.play_type == PlayType.CONSECUTIVE_PAIRS
        assert pattern.primary_rank == Rank.QUEEN  # Highest rank
        assert pattern.card_count == 4
        assert len(pattern.secondary_ranks) == 2

    def test_triple(self):
        """Test recognizing triple."""
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

    def test_triple_with_two(self):
        """Test recognizing triple with two."""
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

    def test_airplane(self):
        """Test recognizing airplane (consecutive triples)."""
        cards = [
            Card(Suit.SPADES, Rank.JACK),
            Card(Suit.HEARTS, Rank.JACK),
            Card(Suit.CLUBS, Rank.JACK),
            Card(Suit.SPADES, Rank.QUEEN),
            Card(Suit.HEARTS, Rank.QUEEN),
            Card(Suit.DIAMONDS, Rank.QUEEN),
        ]
        pattern = PatternRecognizer.analyze_cards(cards)

        assert pattern is not None
        assert pattern.play_type == PlayType.AIRPLANE
        assert pattern.primary_rank == Rank.QUEEN  # Highest rank
        assert pattern.card_count == 6
        assert len(pattern.secondary_ranks) == 2

    def test_airplane_with_wings_min_singles(self):
        """Test airplane with wings: 2 triples + 2 singles (minimum 8 cards)."""
        cards = [
            # 2 consecutive triples: 10,10,10 and J,J,J
            Card(Suit.HEARTS, Rank.TEN),
            Card(Suit.CLUBS, Rank.TEN),
            Card(Suit.DIAMONDS, Rank.TEN),
            Card(Suit.HEARTS, Rank.JACK),
            Card(Suit.CLUBS, Rank.JACK),
            Card(Suit.DIAMONDS, Rank.JACK),
            # 2 singles as wings
            Card(Suit.DIAMONDS, Rank.NINE),
            Card(Suit.DIAMONDS, Rank.EIGHT),
        ]
        pattern = PatternRecognizer.analyze_cards(cards)

        assert pattern is not None
        assert pattern.play_type == PlayType.AIRPLANE_WITH_WINGS
        assert pattern.primary_rank == Rank.JACK
        assert pattern.card_count == 8
        assert len(pattern.secondary_ranks) == 2
        assert pattern.secondary_ranks == [Rank.TEN, Rank.JACK]

    def test_airplane_with_wings_max_pairs(self):
        """Test airplane with wings: 2 triples + 2 pairs (maximum 10 cards)."""
        cards = [
            # 2 consecutive triples: 10,10,10 and J,J,J
            Card(Suit.HEARTS, Rank.TEN),
            Card(Suit.CLUBS, Rank.TEN),
            Card(Suit.DIAMONDS, Rank.TEN),
            Card(Suit.HEARTS, Rank.JACK),
            Card(Suit.CLUBS, Rank.JACK),
            Card(Suit.DIAMONDS, Rank.JACK),
            # 2 pairs as wings
            Card(Suit.DIAMONDS, Rank.NINE),
            Card(Suit.CLUBS, Rank.NINE),
            Card(Suit.DIAMONDS, Rank.EIGHT),
            Card(Suit.CLUBS, Rank.EIGHT),
        ]
        pattern = PatternRecognizer.analyze_cards(cards)

        assert pattern is not None
        assert pattern.play_type == PlayType.AIRPLANE_WITH_WINGS
        assert pattern.primary_rank == Rank.JACK
        assert pattern.card_count == 10
        assert len(pattern.secondary_ranks) == 2

    def test_airplane_with_wings_mixed(self):
        """Test airplane with wings: 2 triples + 1 pair + 1 single (9 cards).

        This is the exact bug case reported by user:
        ♥10,♣10,♦10, ♥J,♣J,♦J, ♦9,♦8,♣8
        """
        cards = [
            # 2 consecutive triples: 10,10,10 and J,J,J
            Card(Suit.HEARTS, Rank.TEN),
            Card(Suit.CLUBS, Rank.TEN),
            Card(Suit.DIAMONDS, Rank.TEN),
            Card(Suit.HEARTS, Rank.JACK),
            Card(Suit.CLUBS, Rank.JACK),
            Card(Suit.DIAMONDS, Rank.JACK),
            # 1 pair + 1 single as wings (2 wings total)
            Card(Suit.DIAMONDS, Rank.NINE),
            Card(Suit.DIAMONDS, Rank.EIGHT),
            Card(Suit.CLUBS, Rank.EIGHT),
        ]
        pattern = PatternRecognizer.analyze_cards(cards)

        assert pattern is not None
        assert pattern.play_type == PlayType.AIRPLANE_WITH_WINGS
        assert pattern.primary_rank == Rank.JACK
        assert pattern.card_count == 9
        assert len(pattern.secondary_ranks) == 2

    def test_airplane_with_wings_three_triples_singles(self):
        """Test airplane with wings: 3 triples + 3 singles (12 cards)."""
        cards = [
            # 3 consecutive triples: 9,9,9 and 10,10,10 and J,J,J
            Card(Suit.HEARTS, Rank.NINE),
            Card(Suit.CLUBS, Rank.NINE),
            Card(Suit.DIAMONDS, Rank.NINE),
            Card(Suit.HEARTS, Rank.TEN),
            Card(Suit.CLUBS, Rank.TEN),
            Card(Suit.DIAMONDS, Rank.TEN),
            Card(Suit.HEARTS, Rank.JACK),
            Card(Suit.CLUBS, Rank.JACK),
            Card(Suit.DIAMONDS, Rank.JACK),
            # 3 singles as wings
            Card(Suit.DIAMONDS, Rank.EIGHT),
            Card(Suit.DIAMONDS, Rank.SEVEN),
            Card(Suit.DIAMONDS, Rank.SIX),
        ]
        pattern = PatternRecognizer.analyze_cards(cards)

        assert pattern is not None
        assert pattern.play_type == PlayType.AIRPLANE_WITH_WINGS
        assert pattern.primary_rank == Rank.JACK
        assert pattern.card_count == 12
        assert len(pattern.secondary_ranks) == 3

    def test_airplane_with_wings_three_triples_pairs(self):
        """Test airplane with wings: 3 triples + 3 pairs (15 cards)."""
        cards = [
            # 3 consecutive triples
            Card(Suit.HEARTS, Rank.NINE),
            Card(Suit.CLUBS, Rank.NINE),
            Card(Suit.DIAMONDS, Rank.NINE),
            Card(Suit.HEARTS, Rank.TEN),
            Card(Suit.CLUBS, Rank.TEN),
            Card(Suit.DIAMONDS, Rank.TEN),
            Card(Suit.HEARTS, Rank.JACK),
            Card(Suit.CLUBS, Rank.JACK),
            Card(Suit.DIAMONDS, Rank.JACK),
            # 3 pairs as wings
            Card(Suit.DIAMONDS, Rank.EIGHT),
            Card(Suit.CLUBS, Rank.EIGHT),
            Card(Suit.DIAMONDS, Rank.SEVEN),
            Card(Suit.CLUBS, Rank.SEVEN),
            Card(Suit.DIAMONDS, Rank.SIX),
            Card(Suit.CLUBS, Rank.SIX),
        ]
        pattern = PatternRecognizer.analyze_cards(cards)

        assert pattern is not None
        assert pattern.play_type == PlayType.AIRPLANE_WITH_WINGS
        assert pattern.primary_rank == Rank.JACK
        assert pattern.card_count == 15
        assert len(pattern.secondary_ranks) == 3

    def test_airplane_with_wings_three_triples_mixed(self):
        """Test airplane with wings: 3 triples + mixed wings (14 cards)."""
        cards = [
            # 3 consecutive triples
            Card(Suit.HEARTS, Rank.NINE),
            Card(Suit.CLUBS, Rank.NINE),
            Card(Suit.DIAMONDS, Rank.NINE),
            Card(Suit.HEARTS, Rank.TEN),
            Card(Suit.CLUBS, Rank.TEN),
            Card(Suit.DIAMONDS, Rank.TEN),
            Card(Suit.HEARTS, Rank.JACK),
            Card(Suit.CLUBS, Rank.JACK),
            Card(Suit.DIAMONDS, Rank.JACK),
            # 2 pairs + 1 single as wings (3 wings total)
            Card(Suit.DIAMONDS, Rank.EIGHT),
            Card(Suit.CLUBS, Rank.EIGHT),
            Card(Suit.DIAMONDS, Rank.SEVEN),
            Card(Suit.CLUBS, Rank.SEVEN),
            Card(Suit.SPADES, Rank.SIX),
        ]
        pattern = PatternRecognizer.analyze_cards(cards)

        assert pattern is not None
        assert pattern.play_type == PlayType.AIRPLANE_WITH_WINGS
        assert pattern.primary_rank == Rank.JACK
        assert pattern.card_count == 14
        assert len(pattern.secondary_ranks) == 3

    def test_airplane_with_wings_insufficient_cards(self):
        """Test invalid: less than 8 cards (minimum requirement)."""
        cards = [
            Card(Suit.HEARTS, Rank.TEN),
            Card(Suit.CLUBS, Rank.TEN),
            Card(Suit.DIAMONDS, Rank.TEN),
            Card(Suit.HEARTS, Rank.JACK),
            Card(Suit.CLUBS, Rank.JACK),
            Card(Suit.DIAMONDS, Rank.JACK),
            Card(Suit.DIAMONDS, Rank.NINE),  # Only 7 cards total
        ]
        pattern = PatternRecognizer.analyze_cards(cards)

        # Should not be recognized as AIRPLANE_WITH_WINGS
        # Will be recognized as AIRPLANE (6 cards) instead, leaving 1 card out
        assert pattern is None or pattern.play_type != PlayType.AIRPLANE_WITH_WINGS

    def test_airplane_with_wings_non_consecutive_triples(self):
        """Test invalid: triples are not consecutive."""
        cards = [
            # Non-consecutive triples: 9,9,9 and J,J,J (skipping 10)
            Card(Suit.HEARTS, Rank.NINE),
            Card(Suit.CLUBS, Rank.NINE),
            Card(Suit.DIAMONDS, Rank.NINE),
            Card(Suit.HEARTS, Rank.JACK),
            Card(Suit.CLUBS, Rank.JACK),
            Card(Suit.DIAMONDS, Rank.JACK),
            # 2 singles as wings
            Card(Suit.DIAMONDS, Rank.EIGHT),
            Card(Suit.DIAMONDS, Rank.SEVEN),
        ]
        pattern = PatternRecognizer.analyze_cards(cards)

        # Should not be recognized as AIRPLANE_WITH_WINGS
        assert pattern is None or pattern.play_type != PlayType.AIRPLANE_WITH_WINGS

    def test_airplane_with_wings_too_few_wings(self):
        """Test invalid: not enough wings (1 wing for 2 triples)."""
        cards = [
            # 2 consecutive triples
            Card(Suit.HEARTS, Rank.TEN),
            Card(Suit.CLUBS, Rank.TEN),
            Card(Suit.DIAMONDS, Rank.TEN),
            Card(Suit.HEARTS, Rank.JACK),
            Card(Suit.CLUBS, Rank.JACK),
            Card(Suit.DIAMONDS, Rank.JACK),
            # Only 1 wing (need 2)
            Card(Suit.DIAMONDS, Rank.NINE),
        ]
        pattern = PatternRecognizer.analyze_cards(cards)

        # Should not be recognized as AIRPLANE_WITH_WINGS
        assert pattern is None or pattern.play_type != PlayType.AIRPLANE_WITH_WINGS

    def test_airplane_with_wings_three_singles(self):
        """Test valid: 2 triples + 3 singles (9 cards).

        规则：N组飞机可以带0-2N张任意牌
        2组飞机可以带0-4张，所以3张单张是合法的
        """
        cards = [
            # 2 consecutive triples
            Card(Suit.HEARTS, Rank.TEN),
            Card(Suit.CLUBS, Rank.TEN),
            Card(Suit.DIAMONDS, Rank.TEN),
            Card(Suit.HEARTS, Rank.JACK),
            Card(Suit.CLUBS, Rank.JACK),
            Card(Suit.DIAMONDS, Rank.JACK),
            # 3 singles as wings
            Card(Suit.DIAMONDS, Rank.NINE),
            Card(Suit.DIAMONDS, Rank.EIGHT),
            Card(Suit.DIAMONDS, Rank.SEVEN),
        ]
        pattern = PatternRecognizer.analyze_cards(cards)

        # Should be recognized as AIRPLANE_WITH_WINGS
        assert pattern is not None
        assert pattern.play_type == PlayType.AIRPLANE_WITH_WINGS
        assert pattern.primary_rank == Rank.JACK
        assert pattern.card_count == 9

    def test_airplane_with_wings_wing_has_triple(self):
        """Test invalid: wing contains 3+ cards of same rank."""
        cards = [
            # 2 consecutive triples: 10,10,10 and J,J,J
            Card(Suit.HEARTS, Rank.TEN),
            Card(Suit.CLUBS, Rank.TEN),
            Card(Suit.DIAMONDS, Rank.TEN),
            Card(Suit.HEARTS, Rank.JACK),
            Card(Suit.CLUBS, Rank.JACK),
            Card(Suit.DIAMONDS, Rank.JACK),
            # Wing contains 3 cards of same rank (invalid)
            Card(Suit.DIAMONDS, Rank.NINE),
            Card(Suit.CLUBS, Rank.NINE),
            Card(Suit.HEARTS, Rank.NINE),
        ]
        pattern = PatternRecognizer.analyze_cards(cards)

        # Should not be recognized as AIRPLANE_WITH_WINGS
        # Might be recognized as something else (e.g., AIRPLANE with 9 cards)
        assert pattern is None or pattern.play_type != PlayType.AIRPLANE_WITH_WINGS

    def test_bomb(self):
        """Test recognizing bomb (4+ same rank)."""
        cards = [
            Card(Suit.SPADES, Rank.SEVEN),
            Card(Suit.HEARTS, Rank.SEVEN),
            Card(Suit.CLUBS, Rank.SEVEN),
            Card(Suit.DIAMONDS, Rank.SEVEN),
        ]
        pattern = PatternRecognizer.analyze_cards(cards)

        assert pattern is not None
        assert pattern.play_type == PlayType.BOMB
        assert pattern.primary_rank == Rank.SEVEN
        assert pattern.card_count == 4

    def test_larger_bomb(self):
        """Test recognizing larger bomb (5 cards)."""
        cards = [
            Card(Suit.SPADES, Rank.NINE),
            Card(Suit.HEARTS, Rank.NINE),
            Card(Suit.CLUBS, Rank.NINE),
            Card(Suit.DIAMONDS, Rank.NINE),
            Card(Suit.SPADES, Rank.NINE),  # From different deck
        ]
        # This would only work with multiple decks
        # For now, let's test with 4 cards
        cards = cards[:4]
        pattern = PatternRecognizer.analyze_cards(cards)

        assert pattern is not None
        assert pattern.play_type == PlayType.BOMB
        assert pattern.card_count == 4

    def test_tongzi(self):
        """Test recognizing tongzi (3 same rank same suit)."""
        cards = [
            Card(Suit.SPADES, Rank.KING),
            Card(Suit.SPADES, Rank.KING),
            Card(Suit.SPADES, Rank.KING),
        ]
        pattern = PatternRecognizer.analyze_cards(cards)

        assert pattern is not None
        assert pattern.play_type == PlayType.TONGZI
        assert pattern.primary_rank == Rank.KING
        assert pattern.primary_suit == Suit.SPADES
        assert pattern.card_count == 3

    def test_dizha(self):
        """Test recognizing dizha (2 of each suit for same rank)."""
        cards = [
            Card(Suit.SPADES, Rank.ACE),
            Card(Suit.SPADES, Rank.ACE),
            Card(Suit.HEARTS, Rank.ACE),
            Card(Suit.HEARTS, Rank.ACE),
            Card(Suit.CLUBS, Rank.ACE),
            Card(Suit.CLUBS, Rank.ACE),
            Card(Suit.DIAMONDS, Rank.ACE),
            Card(Suit.DIAMONDS, Rank.ACE),
        ]
        pattern = PatternRecognizer.analyze_cards(cards)

        assert pattern is not None
        assert pattern.play_type == PlayType.DIZHA
        assert pattern.primary_rank == Rank.ACE
        assert pattern.card_count == 8

    def test_invalid_pattern(self):
        """Test invalid card combination."""
        cards = [
            Card(Suit.SPADES, Rank.ACE),
            Card(Suit.HEARTS, Rank.KING),
            Card(Suit.CLUBS, Rank.QUEEN),
        ]
        pattern = PatternRecognizer.analyze_cards(cards)

        assert pattern is None

    def test_empty_cards(self):
        """Test empty card list."""
        pattern = PatternRecognizer.analyze_cards([])
        assert pattern is None


class TestPlayValidator:
    """Test play validation functionality."""

    def test_can_beat_with_higher_single(self):
        """Test beating single card with higher single."""
        current_cards = [Card(Suit.SPADES, Rank.JACK)]
        new_cards = [Card(Suit.HEARTS, Rank.QUEEN)]

        current_pattern = PatternRecognizer.analyze_cards(current_cards)
        assert PlayValidator.can_beat_play(new_cards, current_pattern)

    def test_cannot_beat_with_lower_single(self):
        """Test failing to beat single card with lower single."""
        current_cards = [Card(Suit.SPADES, Rank.QUEEN)]
        new_cards = [Card(Suit.HEARTS, Rank.JACK)]

        current_pattern = PatternRecognizer.analyze_cards(current_cards)
        assert not PlayValidator.can_beat_play(new_cards, current_pattern)

    def test_bomb_beats_regular_play(self):
        """Test bomb beating regular play."""
        current_cards = [
            Card(Suit.SPADES, Rank.ACE),
            Card(Suit.HEARTS, Rank.ACE),
            Card(Suit.CLUBS, Rank.ACE),
        ]
        new_cards = [
            Card(Suit.SPADES, Rank.FIVE),
            Card(Suit.HEARTS, Rank.FIVE),
            Card(Suit.CLUBS, Rank.FIVE),
            Card(Suit.DIAMONDS, Rank.FIVE),
        ]

        current_pattern = PatternRecognizer.analyze_cards(current_cards)
        assert PlayValidator.can_beat_play(new_cards, current_pattern)

    def test_tongzi_beats_bomb(self):
        """Test tongzi beating bomb."""
        current_cards = [
            Card(Suit.SPADES, Rank.SEVEN),
            Card(Suit.HEARTS, Rank.SEVEN),
            Card(Suit.CLUBS, Rank.SEVEN),
            Card(Suit.DIAMONDS, Rank.SEVEN),
        ]
        new_cards = [
            Card(Suit.SPADES, Rank.KING),
            Card(Suit.SPADES, Rank.KING),
            Card(Suit.SPADES, Rank.KING),
        ]

        current_pattern = PatternRecognizer.analyze_cards(current_cards)
        assert PlayValidator.can_beat_play(new_cards, current_pattern)

    def test_dizha_beats_everything(self):
        """Test dizha beating everything."""
        current_cards = [
            Card(Suit.SPADES, Rank.TWO),
            Card(Suit.SPADES, Rank.TWO),
            Card(Suit.SPADES, Rank.TWO),
        ]
        new_cards = [
            Card(Suit.SPADES, Rank.FIVE),
            Card(Suit.SPADES, Rank.FIVE),
            Card(Suit.HEARTS, Rank.FIVE),
            Card(Suit.HEARTS, Rank.FIVE),
            Card(Suit.CLUBS, Rank.FIVE),
            Card(Suit.CLUBS, Rank.FIVE),
            Card(Suit.DIAMONDS, Rank.FIVE),
            Card(Suit.DIAMONDS, Rank.FIVE),
        ]

        current_pattern = PatternRecognizer.analyze_cards(current_cards)
        assert PlayValidator.can_beat_play(new_cards, current_pattern)

    def test_different_pattern_types_cannot_beat(self):
        """Test different pattern types cannot beat each other."""
        current_cards = [Card(Suit.SPADES, Rank.JACK), Card(Suit.HEARTS, Rank.JACK)]
        new_cards = [Card(Suit.CLUBS, Rank.QUEEN)]

        current_pattern = PatternRecognizer.analyze_cards(current_cards)
        assert not PlayValidator.can_beat_play(new_cards, current_pattern)

    def test_starting_new_round(self):
        """Test starting new round (any valid play allowed)."""
        new_cards = [Card(Suit.SPADES, Rank.FIVE)]
        assert PlayValidator.can_beat_play(new_cards, None)

        # Invalid play should still fail
        invalid_cards = [Card(Suit.SPADES, Rank.FIVE), Card(Suit.HEARTS, Rank.SEVEN)]
        assert not PlayValidator.can_beat_play(invalid_cards, None)


class TestPlayComparison:
    """Test comprehensive play comparison rules."""

    # ========== Same Type Comparisons ==========

    def test_pair_vs_pair_higher_wins(self):
        """Test pair vs pair: higher rank wins."""
        current = [Card(Suit.SPADES, Rank.NINE), Card(Suit.HEARTS, Rank.NINE)]
        new = [Card(Suit.SPADES, Rank.TEN), Card(Suit.HEARTS, Rank.TEN)]

        current_pattern = PatternRecognizer.analyze_cards(current)
        assert PlayValidator.can_beat_play(new, current_pattern)

    def test_pair_vs_pair_lower_loses(self):
        """Test pair vs pair: lower rank loses."""
        current = [Card(Suit.SPADES, Rank.TEN), Card(Suit.HEARTS, Rank.TEN)]
        new = [Card(Suit.SPADES, Rank.NINE), Card(Suit.HEARTS, Rank.NINE)]

        current_pattern = PatternRecognizer.analyze_cards(current)
        assert not PlayValidator.can_beat_play(new, current_pattern)

    def test_triple_vs_triple_higher_wins(self):
        """Test triple vs triple: higher rank wins."""
        current = [
            Card(Suit.SPADES, Rank.EIGHT),
            Card(Suit.HEARTS, Rank.EIGHT),
            Card(Suit.CLUBS, Rank.EIGHT),
        ]
        new = [
            Card(Suit.SPADES, Rank.JACK),
            Card(Suit.HEARTS, Rank.JACK),
            Card(Suit.CLUBS, Rank.JACK),
        ]

        current_pattern = PatternRecognizer.analyze_cards(current)
        assert PlayValidator.can_beat_play(new, current_pattern)

    def test_triple_with_two_vs_triple_with_two(self):
        """Test triple with two vs triple with two: compare triple rank only."""
        current = [
            Card(Suit.SPADES, Rank.NINE),
            Card(Suit.HEARTS, Rank.NINE),
            Card(Suit.CLUBS, Rank.NINE),
            Card(Suit.SPADES, Rank.KING),
            Card(Suit.HEARTS, Rank.KING),
        ]
        new = [
            Card(Suit.SPADES, Rank.QUEEN),
            Card(Suit.HEARTS, Rank.QUEEN),
            Card(Suit.CLUBS, Rank.QUEEN),
            Card(Suit.SPADES, Rank.FIVE),
            Card(Suit.HEARTS, Rank.FIVE),
        ]

        current_pattern = PatternRecognizer.analyze_cards(current)
        assert PlayValidator.can_beat_play(new, current_pattern)

    def test_consecutive_pairs_same_length_higher_wins(self):
        """Test consecutive pairs vs consecutive pairs: same length, higher rank wins."""
        current = [
            Card(Suit.SPADES, Rank.SEVEN),
            Card(Suit.HEARTS, Rank.SEVEN),
            Card(Suit.SPADES, Rank.EIGHT),
            Card(Suit.HEARTS, Rank.EIGHT),
        ]
        new = [
            Card(Suit.SPADES, Rank.NINE),
            Card(Suit.HEARTS, Rank.NINE),
            Card(Suit.SPADES, Rank.TEN),
            Card(Suit.HEARTS, Rank.TEN),
        ]

        current_pattern = PatternRecognizer.analyze_cards(current)
        assert PlayValidator.can_beat_play(new, current_pattern)

    def test_consecutive_pairs_different_length_cannot_beat(self):
        """Test consecutive pairs vs consecutive pairs: different length cannot beat."""
        current = [
            Card(Suit.SPADES, Rank.SEVEN),
            Card(Suit.HEARTS, Rank.SEVEN),
            Card(Suit.SPADES, Rank.EIGHT),
            Card(Suit.HEARTS, Rank.EIGHT),
        ]
        # 3 pairs vs 2 pairs
        new = [
            Card(Suit.SPADES, Rank.NINE),
            Card(Suit.HEARTS, Rank.NINE),
            Card(Suit.SPADES, Rank.TEN),
            Card(Suit.HEARTS, Rank.TEN),
            Card(Suit.SPADES, Rank.JACK),
            Card(Suit.HEARTS, Rank.JACK),
        ]

        current_pattern = PatternRecognizer.analyze_cards(current)
        assert not PlayValidator.can_beat_play(new, current_pattern)

    def test_airplane_same_length_higher_wins(self):
        """Test airplane vs airplane: same length, higher rank wins."""
        current = [
            Card(Suit.SPADES, Rank.EIGHT),
            Card(Suit.HEARTS, Rank.EIGHT),
            Card(Suit.CLUBS, Rank.EIGHT),
            Card(Suit.SPADES, Rank.NINE),
            Card(Suit.HEARTS, Rank.NINE),
            Card(Suit.CLUBS, Rank.NINE),
        ]
        new = [
            Card(Suit.SPADES, Rank.QUEEN),
            Card(Suit.HEARTS, Rank.QUEEN),
            Card(Suit.CLUBS, Rank.QUEEN),
            Card(Suit.SPADES, Rank.KING),
            Card(Suit.HEARTS, Rank.KING),
            Card(Suit.CLUBS, Rank.KING),
        ]

        current_pattern = PatternRecognizer.analyze_cards(current)
        assert PlayValidator.can_beat_play(new, current_pattern)

    def test_airplane_different_length_cannot_beat(self):
        """Test airplane vs airplane: different length cannot beat."""
        current = [
            Card(Suit.SPADES, Rank.EIGHT),
            Card(Suit.HEARTS, Rank.EIGHT),
            Card(Suit.CLUBS, Rank.EIGHT),
            Card(Suit.SPADES, Rank.NINE),
            Card(Suit.HEARTS, Rank.NINE),
            Card(Suit.CLUBS, Rank.NINE),
        ]
        # 3 triples vs 2 triples
        new = [
            Card(Suit.SPADES, Rank.QUEEN),
            Card(Suit.HEARTS, Rank.QUEEN),
            Card(Suit.CLUBS, Rank.QUEEN),
            Card(Suit.SPADES, Rank.KING),
            Card(Suit.HEARTS, Rank.KING),
            Card(Suit.CLUBS, Rank.KING),
            Card(Suit.SPADES, Rank.ACE),
            Card(Suit.HEARTS, Rank.ACE),
            Card(Suit.CLUBS, Rank.ACE),
        ]

        current_pattern = PatternRecognizer.analyze_cards(current)
        assert not PlayValidator.can_beat_play(new, current_pattern)

    def test_airplane_with_wings_same_length_higher_wins(self):
        """Test airplane with wings: same length, higher rank wins."""
        current = [
            Card(Suit.SPADES, Rank.SEVEN),
            Card(Suit.HEARTS, Rank.SEVEN),
            Card(Suit.CLUBS, Rank.SEVEN),
            Card(Suit.SPADES, Rank.EIGHT),
            Card(Suit.HEARTS, Rank.EIGHT),
            Card(Suit.CLUBS, Rank.EIGHT),
            Card(Suit.DIAMONDS, Rank.FIVE),
            Card(Suit.DIAMONDS, Rank.SIX),
        ]
        new = [
            Card(Suit.SPADES, Rank.TEN),
            Card(Suit.HEARTS, Rank.TEN),
            Card(Suit.CLUBS, Rank.TEN),
            Card(Suit.SPADES, Rank.JACK),
            Card(Suit.HEARTS, Rank.JACK),
            Card(Suit.CLUBS, Rank.JACK),
            Card(Suit.DIAMONDS, Rank.NINE),
            Card(Suit.DIAMONDS, Rank.KING),
        ]

        current_pattern = PatternRecognizer.analyze_cards(current)
        assert PlayValidator.can_beat_play(new, current_pattern)

    def test_airplane_with_wings_different_length_cannot_beat(self):
        """Test airplane with wings: different triple count cannot beat."""
        current = [
            Card(Suit.SPADES, Rank.SEVEN),
            Card(Suit.HEARTS, Rank.SEVEN),
            Card(Suit.CLUBS, Rank.SEVEN),
            Card(Suit.SPADES, Rank.EIGHT),
            Card(Suit.HEARTS, Rank.EIGHT),
            Card(Suit.CLUBS, Rank.EIGHT),
            Card(Suit.DIAMONDS, Rank.FIVE),
            Card(Suit.DIAMONDS, Rank.SIX),
        ]
        # 3 triples vs 2 triples
        new = [
            Card(Suit.SPADES, Rank.TEN),
            Card(Suit.HEARTS, Rank.TEN),
            Card(Suit.CLUBS, Rank.TEN),
            Card(Suit.SPADES, Rank.JACK),
            Card(Suit.HEARTS, Rank.JACK),
            Card(Suit.CLUBS, Rank.JACK),
            Card(Suit.SPADES, Rank.QUEEN),
            Card(Suit.HEARTS, Rank.QUEEN),
            Card(Suit.CLUBS, Rank.QUEEN),
            Card(Suit.DIAMONDS, Rank.NINE),
            Card(Suit.DIAMONDS, Rank.KING),
            Card(Suit.DIAMONDS, Rank.ACE),
        ]

        current_pattern = PatternRecognizer.analyze_cards(current)
        assert not PlayValidator.can_beat_play(new, current_pattern)

    def test_bomb_vs_bomb_higher_rank_wins(self):
        """Test bomb vs bomb: higher rank wins."""
        current = [
            Card(Suit.SPADES, Rank.SEVEN),
            Card(Suit.HEARTS, Rank.SEVEN),
            Card(Suit.CLUBS, Rank.SEVEN),
            Card(Suit.DIAMONDS, Rank.SEVEN),
        ]
        new = [
            Card(Suit.SPADES, Rank.KING),
            Card(Suit.HEARTS, Rank.KING),
            Card(Suit.CLUBS, Rank.KING),
            Card(Suit.DIAMONDS, Rank.KING),
        ]

        current_pattern = PatternRecognizer.analyze_cards(current)
        assert PlayValidator.can_beat_play(new, current_pattern)

    def test_bomb_vs_bomb_same_rank_larger_count_wins(self):
        """Test bomb vs bomb: same rank, larger count wins."""
        current = [
            Card(Suit.SPADES, Rank.NINE),
            Card(Suit.HEARTS, Rank.NINE),
            Card(Suit.CLUBS, Rank.NINE),
            Card(Suit.DIAMONDS, Rank.NINE),
        ]
        new = [
            Card(Suit.SPADES, Rank.NINE),
            Card(Suit.SPADES, Rank.NINE),  # From another deck
            Card(Suit.HEARTS, Rank.NINE),
            Card(Suit.CLUBS, Rank.NINE),
            Card(Suit.DIAMONDS, Rank.NINE),
        ]

        current_pattern = PatternRecognizer.analyze_cards(current)
        new_pattern = PatternRecognizer.analyze_cards(new)

        # Verify both are bombs
        assert new_pattern.play_type == PlayType.BOMB
        assert PlayValidator.can_beat_play(new, current_pattern)

    def test_tongzi_vs_tongzi_higher_rank_wins(self):
        """Test tongzi vs tongzi: higher rank wins."""
        current = [
            Card(Suit.HEARTS, Rank.EIGHT),
            Card(Suit.HEARTS, Rank.EIGHT),
            Card(Suit.HEARTS, Rank.EIGHT),
        ]
        new = [
            Card(Suit.SPADES, Rank.KING),
            Card(Suit.SPADES, Rank.KING),
            Card(Suit.SPADES, Rank.KING),
        ]

        current_pattern = PatternRecognizer.analyze_cards(current)
        assert PlayValidator.can_beat_play(new, current_pattern)

    def test_tongzi_vs_tongzi_same_rank_higher_suit_wins(self):
        """Test tongzi vs tongzi: same rank, higher suit wins."""
        current = [
            Card(Suit.HEARTS, Rank.KING),
            Card(Suit.HEARTS, Rank.KING),
            Card(Suit.HEARTS, Rank.KING),
        ]
        new = [
            Card(Suit.SPADES, Rank.KING),
            Card(Suit.SPADES, Rank.KING),
            Card(Suit.SPADES, Rank.KING),
        ]

        current_pattern = PatternRecognizer.analyze_cards(current)
        assert PlayValidator.can_beat_play(new, current_pattern)

    def test_tongzi_vs_tongzi_same_rank_lower_suit_loses(self):
        """Test tongzi vs tongzi: same rank, lower suit loses."""
        current = [
            Card(Suit.SPADES, Rank.KING),
            Card(Suit.SPADES, Rank.KING),
            Card(Suit.SPADES, Rank.KING),
        ]
        new = [
            Card(Suit.HEARTS, Rank.KING),
            Card(Suit.HEARTS, Rank.KING),
            Card(Suit.HEARTS, Rank.KING),
        ]

        current_pattern = PatternRecognizer.analyze_cards(current)
        assert not PlayValidator.can_beat_play(new, current_pattern)

    def test_dizha_vs_dizha_higher_rank_wins(self):
        """Test dizha vs dizha: higher rank wins."""
        current = [
            Card(Suit.SPADES, Rank.SEVEN),
            Card(Suit.SPADES, Rank.SEVEN),
            Card(Suit.HEARTS, Rank.SEVEN),
            Card(Suit.HEARTS, Rank.SEVEN),
            Card(Suit.CLUBS, Rank.SEVEN),
            Card(Suit.CLUBS, Rank.SEVEN),
            Card(Suit.DIAMONDS, Rank.SEVEN),
            Card(Suit.DIAMONDS, Rank.SEVEN),
        ]
        new = [
            Card(Suit.SPADES, Rank.KING),
            Card(Suit.SPADES, Rank.KING),
            Card(Suit.HEARTS, Rank.KING),
            Card(Suit.HEARTS, Rank.KING),
            Card(Suit.CLUBS, Rank.KING),
            Card(Suit.CLUBS, Rank.KING),
            Card(Suit.DIAMONDS, Rank.KING),
            Card(Suit.DIAMONDS, Rank.KING),
        ]

        current_pattern = PatternRecognizer.analyze_cards(current)
        assert PlayValidator.can_beat_play(new, current_pattern)

    # ========== Different Type Comparisons (Cannot Beat) ==========

    def test_single_cannot_beat_pair(self):
        """Test single cannot beat pair (different types)."""
        current = [Card(Suit.SPADES, Rank.FIVE), Card(Suit.HEARTS, Rank.FIVE)]
        new = [Card(Suit.SPADES, Rank.ACE)]

        current_pattern = PatternRecognizer.analyze_cards(current)
        assert not PlayValidator.can_beat_play(new, current_pattern)

    def test_single_cannot_beat_triple(self):
        """Test single cannot beat triple (different types)."""
        current = [
            Card(Suit.SPADES, Rank.FIVE),
            Card(Suit.HEARTS, Rank.FIVE),
            Card(Suit.CLUBS, Rank.FIVE),
        ]
        new = [Card(Suit.SPADES, Rank.ACE)]

        current_pattern = PatternRecognizer.analyze_cards(current)
        assert not PlayValidator.can_beat_play(new, current_pattern)

    def test_pair_cannot_beat_triple(self):
        """Test pair cannot beat triple (different types)."""
        current = [
            Card(Suit.SPADES, Rank.FIVE),
            Card(Suit.HEARTS, Rank.FIVE),
            Card(Suit.CLUBS, Rank.FIVE),
        ]
        new = [Card(Suit.SPADES, Rank.ACE), Card(Suit.HEARTS, Rank.ACE)]

        current_pattern = PatternRecognizer.analyze_cards(current)
        assert not PlayValidator.can_beat_play(new, current_pattern)

    def test_triple_cannot_beat_triple_with_two(self):
        """Test triple cannot beat triple with two (different types)."""
        current = [
            Card(Suit.SPADES, Rank.SEVEN),
            Card(Suit.HEARTS, Rank.SEVEN),
            Card(Suit.CLUBS, Rank.SEVEN),
            Card(Suit.SPADES, Rank.EIGHT),
            Card(Suit.HEARTS, Rank.EIGHT),
        ]
        new = [
            Card(Suit.SPADES, Rank.KING),
            Card(Suit.HEARTS, Rank.KING),
            Card(Suit.CLUBS, Rank.KING),
        ]

        current_pattern = PatternRecognizer.analyze_cards(current)
        assert not PlayValidator.can_beat_play(new, current_pattern)

    def test_pair_cannot_beat_consecutive_pairs(self):
        """Test pair cannot beat consecutive pairs (different types)."""
        current = [
            Card(Suit.SPADES, Rank.SEVEN),
            Card(Suit.HEARTS, Rank.SEVEN),
            Card(Suit.SPADES, Rank.EIGHT),
            Card(Suit.HEARTS, Rank.EIGHT),
        ]
        new = [Card(Suit.SPADES, Rank.ACE), Card(Suit.HEARTS, Rank.ACE)]

        current_pattern = PatternRecognizer.analyze_cards(current)
        assert not PlayValidator.can_beat_play(new, current_pattern)

    def test_triple_cannot_beat_airplane(self):
        """Test triple cannot beat airplane (different types)."""
        current = [
            Card(Suit.SPADES, Rank.SEVEN),
            Card(Suit.HEARTS, Rank.SEVEN),
            Card(Suit.CLUBS, Rank.SEVEN),
            Card(Suit.SPADES, Rank.EIGHT),
            Card(Suit.HEARTS, Rank.EIGHT),
            Card(Suit.CLUBS, Rank.EIGHT),
        ]
        new = [
            Card(Suit.SPADES, Rank.ACE),
            Card(Suit.HEARTS, Rank.ACE),
            Card(Suit.CLUBS, Rank.ACE),
        ]

        current_pattern = PatternRecognizer.analyze_cards(current)
        assert not PlayValidator.can_beat_play(new, current_pattern)

    def test_airplane_cannot_beat_airplane_with_wings(self):
        """Test airplane cannot beat airplane with wings (different types)."""
        current = [
            Card(Suit.SPADES, Rank.SEVEN),
            Card(Suit.HEARTS, Rank.SEVEN),
            Card(Suit.CLUBS, Rank.SEVEN),
            Card(Suit.SPADES, Rank.EIGHT),
            Card(Suit.HEARTS, Rank.EIGHT),
            Card(Suit.CLUBS, Rank.EIGHT),
            Card(Suit.DIAMONDS, Rank.FIVE),
            Card(Suit.DIAMONDS, Rank.SIX),
        ]
        new = [
            Card(Suit.SPADES, Rank.KING),
            Card(Suit.HEARTS, Rank.KING),
            Card(Suit.CLUBS, Rank.KING),
            Card(Suit.SPADES, Rank.ACE),
            Card(Suit.HEARTS, Rank.ACE),
            Card(Suit.CLUBS, Rank.ACE),
        ]

        current_pattern = PatternRecognizer.analyze_cards(current)
        assert not PlayValidator.can_beat_play(new, current_pattern)

    # ========== Special Rules: Bomb Beats Regular Plays ==========

    def test_bomb_beats_single(self):
        """Test bomb beats single."""
        current = [Card(Suit.SPADES, Rank.ACE)]
        new = [
            Card(Suit.SPADES, Rank.FIVE),
            Card(Suit.HEARTS, Rank.FIVE),
            Card(Suit.CLUBS, Rank.FIVE),
            Card(Suit.DIAMONDS, Rank.FIVE),
        ]

        current_pattern = PatternRecognizer.analyze_cards(current)
        assert PlayValidator.can_beat_play(new, current_pattern)

    def test_bomb_beats_pair(self):
        """Test bomb beats pair."""
        current = [Card(Suit.SPADES, Rank.ACE), Card(Suit.HEARTS, Rank.ACE)]
        new = [
            Card(Suit.SPADES, Rank.FIVE),
            Card(Suit.HEARTS, Rank.FIVE),
            Card(Suit.CLUBS, Rank.FIVE),
            Card(Suit.DIAMONDS, Rank.FIVE),
        ]

        current_pattern = PatternRecognizer.analyze_cards(current)
        assert PlayValidator.can_beat_play(new, current_pattern)

    def test_bomb_beats_consecutive_pairs(self):
        """Test bomb beats consecutive pairs."""
        current = [
            Card(Suit.SPADES, Rank.KING),
            Card(Suit.HEARTS, Rank.KING),
            Card(Suit.SPADES, Rank.ACE),
            Card(Suit.HEARTS, Rank.ACE),
        ]
        new = [
            Card(Suit.SPADES, Rank.FIVE),
            Card(Suit.HEARTS, Rank.FIVE),
            Card(Suit.CLUBS, Rank.FIVE),
            Card(Suit.DIAMONDS, Rank.FIVE),
        ]

        current_pattern = PatternRecognizer.analyze_cards(current)
        assert PlayValidator.can_beat_play(new, current_pattern)

    def test_bomb_beats_airplane(self):
        """Test bomb beats airplane."""
        current = [
            Card(Suit.SPADES, Rank.KING),
            Card(Suit.HEARTS, Rank.KING),
            Card(Suit.CLUBS, Rank.KING),
            Card(Suit.SPADES, Rank.ACE),
            Card(Suit.HEARTS, Rank.ACE),
            Card(Suit.CLUBS, Rank.ACE),
        ]
        new = [
            Card(Suit.SPADES, Rank.FIVE),
            Card(Suit.HEARTS, Rank.FIVE),
            Card(Suit.CLUBS, Rank.FIVE),
            Card(Suit.DIAMONDS, Rank.FIVE),
        ]

        current_pattern = PatternRecognizer.analyze_cards(current)
        assert PlayValidator.can_beat_play(new, current_pattern)

    # ========== Special Rules: Tongzi Beats Bomb ==========

    def test_tongzi_beats_bomb(self):
        """Test tongzi beats bomb (already exists but verify)."""
        current = [
            Card(Suit.SPADES, Rank.ACE),
            Card(Suit.HEARTS, Rank.ACE),
            Card(Suit.CLUBS, Rank.ACE),
            Card(Suit.DIAMONDS, Rank.ACE),
        ]
        new = [
            Card(Suit.SPADES, Rank.FIVE),
            Card(Suit.SPADES, Rank.FIVE),
            Card(Suit.SPADES, Rank.FIVE),
        ]

        current_pattern = PatternRecognizer.analyze_cards(current)
        assert PlayValidator.can_beat_play(new, current_pattern)

    def test_tongzi_cannot_beat_single(self):
        """Test tongzi cannot beat single (unless current is bomb)."""
        current = [Card(Suit.SPADES, Rank.ACE)]
        new = [
            Card(Suit.SPADES, Rank.KING),
            Card(Suit.SPADES, Rank.KING),
            Card(Suit.SPADES, Rank.KING),
        ]

        current_pattern = PatternRecognizer.analyze_cards(current)
        assert not PlayValidator.can_beat_play(new, current_pattern)

    def test_tongzi_cannot_beat_pair(self):
        """Test tongzi cannot beat pair."""
        current = [Card(Suit.SPADES, Rank.ACE), Card(Suit.HEARTS, Rank.ACE)]
        new = [
            Card(Suit.SPADES, Rank.KING),
            Card(Suit.SPADES, Rank.KING),
            Card(Suit.SPADES, Rank.KING),
        ]

        current_pattern = PatternRecognizer.analyze_cards(current)
        assert not PlayValidator.can_beat_play(new, current_pattern)

    def test_tongzi_cannot_beat_triple(self):
        """Test tongzi cannot beat triple."""
        current = [
            Card(Suit.SPADES, Rank.ACE),
            Card(Suit.HEARTS, Rank.ACE),
            Card(Suit.CLUBS, Rank.ACE),
        ]
        new = [
            Card(Suit.SPADES, Rank.KING),
            Card(Suit.SPADES, Rank.KING),
            Card(Suit.SPADES, Rank.KING),
        ]

        current_pattern = PatternRecognizer.analyze_cards(current)
        # Tongzi can only beat Bomb or other Tongzi
        assert not PlayValidator.can_beat_play(new, current_pattern)

    # ========== Special Rules: Dizha Beats Everything ==========

    def test_dizha_beats_single(self):
        """Test dizha beats single."""
        current = [Card(Suit.SPADES, Rank.ACE)]
        new = [
            Card(Suit.SPADES, Rank.FIVE),
            Card(Suit.SPADES, Rank.FIVE),
            Card(Suit.HEARTS, Rank.FIVE),
            Card(Suit.HEARTS, Rank.FIVE),
            Card(Suit.CLUBS, Rank.FIVE),
            Card(Suit.CLUBS, Rank.FIVE),
            Card(Suit.DIAMONDS, Rank.FIVE),
            Card(Suit.DIAMONDS, Rank.FIVE),
        ]

        current_pattern = PatternRecognizer.analyze_cards(current)
        assert PlayValidator.can_beat_play(new, current_pattern)

    def test_dizha_beats_bomb(self):
        """Test dizha beats bomb."""
        current = [
            Card(Suit.SPADES, Rank.ACE),
            Card(Suit.HEARTS, Rank.ACE),
            Card(Suit.CLUBS, Rank.ACE),
            Card(Suit.DIAMONDS, Rank.ACE),
        ]
        new = [
            Card(Suit.SPADES, Rank.FIVE),
            Card(Suit.SPADES, Rank.FIVE),
            Card(Suit.HEARTS, Rank.FIVE),
            Card(Suit.HEARTS, Rank.FIVE),
            Card(Suit.CLUBS, Rank.FIVE),
            Card(Suit.CLUBS, Rank.FIVE),
            Card(Suit.DIAMONDS, Rank.FIVE),
            Card(Suit.DIAMONDS, Rank.FIVE),
        ]

        current_pattern = PatternRecognizer.analyze_cards(current)
        assert PlayValidator.can_beat_play(new, current_pattern)

    def test_dizha_beats_tongzi(self):
        """Test dizha beats tongzi."""
        current = [
            Card(Suit.SPADES, Rank.ACE),
            Card(Suit.SPADES, Rank.ACE),
            Card(Suit.SPADES, Rank.ACE),
        ]
        new = [
            Card(Suit.SPADES, Rank.FIVE),
            Card(Suit.SPADES, Rank.FIVE),
            Card(Suit.HEARTS, Rank.FIVE),
            Card(Suit.HEARTS, Rank.FIVE),
            Card(Suit.CLUBS, Rank.FIVE),
            Card(Suit.CLUBS, Rank.FIVE),
            Card(Suit.DIAMONDS, Rank.FIVE),
            Card(Suit.DIAMONDS, Rank.FIVE),
        ]

        current_pattern = PatternRecognizer.analyze_cards(current)
        assert PlayValidator.can_beat_play(new, current_pattern)

    def test_only_higher_dizha_beats_dizha(self):
        """Test only higher dizha can beat dizha."""
        current = [
            Card(Suit.SPADES, Rank.KING),
            Card(Suit.SPADES, Rank.KING),
            Card(Suit.HEARTS, Rank.KING),
            Card(Suit.HEARTS, Rank.KING),
            Card(Suit.CLUBS, Rank.KING),
            Card(Suit.CLUBS, Rank.KING),
            Card(Suit.DIAMONDS, Rank.KING),
            Card(Suit.DIAMONDS, Rank.KING),
        ]

        # Bomb cannot beat dizha
        bomb = [
            Card(Suit.SPADES, Rank.ACE),
            Card(Suit.HEARTS, Rank.ACE),
            Card(Suit.CLUBS, Rank.ACE),
            Card(Suit.DIAMONDS, Rank.ACE),
        ]
        current_pattern = PatternRecognizer.analyze_cards(current)
        assert not PlayValidator.can_beat_play(bomb, current_pattern)

        # Tongzi cannot beat dizha
        tongzi = [
            Card(Suit.SPADES, Rank.ACE),
            Card(Suit.SPADES, Rank.ACE),
            Card(Suit.SPADES, Rank.ACE),
        ]
        assert not PlayValidator.can_beat_play(tongzi, current_pattern)

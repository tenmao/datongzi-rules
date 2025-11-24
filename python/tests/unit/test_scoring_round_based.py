"""
Unit tests for round-based scoring logic.

Test-Driven Development approach for ScoreComputation.
"""

import pytest

from datongzi_rules import (
    BonusType,
    Card,
    ConfigFactory,
    PatternRecognizer,
    PlayType,
    Rank,
    ScoreComputation,
    Suit,
)


class TestRoundBasedScoring:
    """Test round-based scoring calculations."""

    def setup_method(self):
        """Setup test fixtures."""
        self.config = ConfigFactory.create_standard_3deck_3player()
        self.engine = ScoreComputation(self.config)

    # ==================== Basic Round Scoring ====================

    def test_round_with_scoring_cards_winner_gets_all_points(self):
        """
        Scenario: Round with multiple players playing cards with 5/10/K.
        Expected: Winner gets ALL points from ALL cards in the round.
        """
        # Round cards: Player A plays [5♠, 5♥], Player B plays [10♠, K♥], Player C passes
        # Winner: Player B
        round_cards = [
            Card(Suit.SPADES, Rank.FIVE),  # 5 points
            Card(Suit.HEARTS, Rank.FIVE),  # 5 points
            Card(Suit.SPADES, Rank.TEN),  # 10 points
            Card(Suit.HEARTS, Rank.KING),  # 10 points
        ]

        event = self.engine.create_round_win_event(
            player_id="Player_B", round_cards=round_cards, round_number=1
        )

        assert event is not None
        assert event.player_id == "Player_B"
        assert event.points == 30  # 5+5+10+10 = 30
        assert event.bonus_type == BonusType.ROUND_WIN
        assert len(event.cards_involved) == 4

    def test_round_with_no_scoring_cards_no_points(self):
        """
        Scenario: Round where no one plays 5/10/K.
        Expected: Winner gets 0 points (no event created).
        """
        round_cards = [
            Card(Suit.SPADES, Rank.SIX),
            Card(Suit.HEARTS, Rank.SEVEN),
            Card(Suit.CLUBS, Rank.EIGHT),
        ]

        event = self.engine.create_round_win_event(
            player_id="Player_A", round_cards=round_cards, round_number=1
        )

        assert event is None  # No points, no event

    def test_round_with_only_fives(self):
        """All cards are 5s."""
        round_cards = [
            Card(Suit.SPADES, Rank.FIVE),
            Card(Suit.HEARTS, Rank.FIVE),
            Card(Suit.CLUBS, Rank.FIVE),
        ]

        event = self.engine.create_round_win_event(
            player_id="Player_A", round_cards=round_cards, round_number=1
        )

        assert event is not None
        assert event.points == 15  # 5+5+5 = 15

    def test_round_with_only_tens_and_kings(self):
        """All cards are 10s and Ks."""
        round_cards = [
            Card(Suit.SPADES, Rank.TEN),
            Card(Suit.HEARTS, Rank.TEN),
            Card(Suit.CLUBS, Rank.KING),
            Card(Suit.DIAMONDS, Rank.KING),
        ]

        event = self.engine.create_round_win_event(
            player_id="Player_A", round_cards=round_cards, round_number=1
        )

        assert event is not None
        assert event.points == 40  # 10+10+10+10 = 40

    def test_empty_round_no_cards(self):
        """Edge case: Empty round."""
        event = self.engine.create_round_win_event(
            player_id="Player_A", round_cards=[], round_number=1
        )

        assert event is None

    # ==================== Special Bonus - Tongzi ====================

    def test_round_ending_with_k_tongzi_gets_bonus(self):
        """
        Scenario: Round ends with K Tongzi as the winning play.
        Expected: Winner gets 100 bonus points.
        """
        # Create K Tongzi (3 same suit K)
        winning_cards = [
            Card(Suit.SPADES, Rank.KING),
            Card(Suit.SPADES, Rank.KING),
            Card(Suit.SPADES, Rank.KING),
        ]
        pattern = PatternRecognizer.analyze_cards(winning_cards)

        assert pattern.play_type == PlayType.TONGZI

        events = self.engine.create_special_bonus_events(
            player_id="Player_A",
            winning_pattern=pattern,
            round_number=1,
            is_round_winning_play=True,
        )

        assert len(events) == 1
        assert events[0].bonus_type == BonusType.K_TONGZI
        assert events[0].points == 100

    def test_round_ending_with_a_tongzi_gets_bonus(self):
        """A Tongzi gets 200 bonus."""
        winning_cards = [
            Card(Suit.HEARTS, Rank.ACE),
            Card(Suit.HEARTS, Rank.ACE),
            Card(Suit.HEARTS, Rank.ACE),
        ]
        pattern = PatternRecognizer.analyze_cards(winning_cards)

        events = self.engine.create_special_bonus_events(
            player_id="Player_B",
            winning_pattern=pattern,
            round_number=1,
            is_round_winning_play=True,
        )

        assert len(events) == 1
        assert events[0].bonus_type == BonusType.A_TONGZI
        assert events[0].points == 200

    def test_round_ending_with_two_tongzi_gets_bonus(self):
        """2 Tongzi gets 300 bonus."""
        winning_cards = [
            Card(Suit.CLUBS, Rank.TWO),
            Card(Suit.CLUBS, Rank.TWO),
            Card(Suit.CLUBS, Rank.TWO),
        ]
        pattern = PatternRecognizer.analyze_cards(winning_cards)

        events = self.engine.create_special_bonus_events(
            player_id="Player_C",
            winning_pattern=pattern,
            round_number=1,
            is_round_winning_play=True,
        )

        assert len(events) == 1
        assert events[0].bonus_type == BonusType.TWO_TONGZI
        assert events[0].points == 300

    def test_tongzi_in_middle_of_round_no_bonus(self):
        """
        Critical: Player A plays K Tongzi, but Player B beats it.
        Expected: Player A gets NO bonus (not the round winner).
        """
        k_tongzi = [
            Card(Suit.SPADES, Rank.KING),
            Card(Suit.SPADES, Rank.KING),
            Card(Suit.SPADES, Rank.KING),
        ]
        pattern_a = PatternRecognizer.analyze_cards(k_tongzi)

        # Player A's K Tongzi is NOT the winning play
        events_a = self.engine.create_special_bonus_events(
            player_id="Player_A",
            winning_pattern=pattern_a,
            round_number=1,
            is_round_winning_play=False,  # ← Key parameter
        )

        assert len(events_a) == 0  # No bonus for non-winning play

    def test_a_tongzi_beats_k_tongzi_only_a_gets_bonus(self):
        """
        Scenario: Player A plays K Tongzi (100), Player B plays A Tongzi (200) and wins.
        Expected: Player B gets 200, Player A gets 0.
        """
        # Player A's K Tongzi (not winning)
        k_tongzi = [
            Card(Suit.SPADES, Rank.KING),
            Card(Suit.SPADES, Rank.KING),
            Card(Suit.SPADES, Rank.KING),
        ]
        pattern_k = PatternRecognizer.analyze_cards(k_tongzi)

        events_a = self.engine.create_special_bonus_events(
            player_id="Player_A",
            winning_pattern=pattern_k,
            round_number=1,
            is_round_winning_play=False,
        )

        # Player B's A Tongzi (winning)
        a_tongzi = [
            Card(Suit.HEARTS, Rank.ACE),
            Card(Suit.HEARTS, Rank.ACE),
            Card(Suit.HEARTS, Rank.ACE),
        ]
        pattern_a = PatternRecognizer.analyze_cards(a_tongzi)

        events_b = self.engine.create_special_bonus_events(
            player_id="Player_B",
            winning_pattern=pattern_a,
            round_number=1,
            is_round_winning_play=True,
        )

        assert len(events_a) == 0
        assert len(events_b) == 1
        assert events_b[0].points == 200

    # ==================== Special Bonus - Dizha ====================

    def test_round_ending_with_dizha_gets_bonus(self):
        """Dizha gets 400 bonus."""
        # Create Dizha (2 of each suit for same rank)
        dizha_cards = [
            Card(Suit.SPADES, Rank.KING),
            Card(Suit.SPADES, Rank.KING),
            Card(Suit.HEARTS, Rank.KING),
            Card(Suit.HEARTS, Rank.KING),
            Card(Suit.CLUBS, Rank.KING),
            Card(Suit.CLUBS, Rank.KING),
            Card(Suit.DIAMONDS, Rank.KING),
            Card(Suit.DIAMONDS, Rank.KING),
        ]
        pattern = PatternRecognizer.analyze_cards(dizha_cards)

        assert pattern.play_type == PlayType.DIZHA

        events = self.engine.create_special_bonus_events(
            player_id="Player_A",
            winning_pattern=pattern,
            round_number=1,
            is_round_winning_play=True,
        )

        assert len(events) == 1
        assert events[0].bonus_type == BonusType.DIZHA
        assert events[0].points == 400

    def test_dizha_in_middle_of_round_no_bonus(self):
        """Dizha not at end of round gets no bonus."""
        dizha_cards = [
            Card(Suit.SPADES, Rank.ACE),
            Card(Suit.SPADES, Rank.ACE),
            Card(Suit.HEARTS, Rank.ACE),
            Card(Suit.HEARTS, Rank.ACE),
            Card(Suit.CLUBS, Rank.ACE),
            Card(Suit.CLUBS, Rank.ACE),
            Card(Suit.DIAMONDS, Rank.ACE),
            Card(Suit.DIAMONDS, Rank.ACE),
        ]
        pattern = PatternRecognizer.analyze_cards(dizha_cards)

        events = self.engine.create_special_bonus_events(
            player_id="Player_A",
            winning_pattern=pattern,
            round_number=1,
            is_round_winning_play=False,
        )

        assert len(events) == 0

    # ==================== Non-special Patterns ====================

    def test_regular_bomb_no_special_bonus(self):
        """Regular bomb (not tongzi/dizha) gets no special bonus."""
        bomb_cards = [
            Card(Suit.SPADES, Rank.TEN),
            Card(Suit.HEARTS, Rank.TEN),
            Card(Suit.CLUBS, Rank.TEN),
            Card(Suit.DIAMONDS, Rank.TEN),
        ]
        pattern = PatternRecognizer.analyze_cards(bomb_cards)

        assert pattern.play_type == PlayType.BOMB

        events = self.engine.create_special_bonus_events(
            player_id="Player_A",
            winning_pattern=pattern,
            round_number=1,
            is_round_winning_play=True,
        )

        assert len(events) == 0  # No special bonus for regular bomb

    def test_regular_triple_no_special_bonus(self):
        """Regular triple gets no special bonus."""
        triple_cards = [
            Card(Suit.SPADES, Rank.SEVEN),
            Card(Suit.HEARTS, Rank.SEVEN),
            Card(Suit.CLUBS, Rank.SEVEN),
        ]
        pattern = PatternRecognizer.analyze_cards(triple_cards)

        events = self.engine.create_special_bonus_events(
            player_id="Player_A",
            winning_pattern=pattern,
            round_number=1,
            is_round_winning_play=True,
        )

        assert len(events) == 0

    # ==================== Finish Position Bonuses ====================

    def test_finish_bonuses_standard_3_player(self):
        """
        Standard 3-player finish bonuses:
        - First: +100
        - Second: -40
        - Third: -60
        """
        finish_order = ["Player_A", "Player_B", "Player_C"]

        events = self.engine.create_finish_bonus_events(finish_order)

        assert len(events) == 3

        # First place
        assert events[0].player_id == "Player_A"
        assert events[0].bonus_type == BonusType.FINISH_FIRST
        assert events[0].points == 100

        # Second place
        assert events[1].player_id == "Player_B"
        assert events[1].bonus_type == BonusType.FINISH_SECOND
        assert events[1].points == -40

        # Third place
        assert events[2].player_id == "Player_C"
        assert events[2].bonus_type == BonusType.FINISH_THIRD
        assert events[2].points == -60

    def test_finish_bonuses_sum_to_zero(self):
        """Finish bonuses should sum to 0 (zero-sum game)."""
        finish_order = ["Player_A", "Player_B", "Player_C"]
        events = self.engine.create_finish_bonus_events(finish_order)

        total = sum(e.points for e in events)
        assert total == 0  # 100 + (-40) + (-60) = 0

    # ==================== Complex Round Scenarios ====================

    def test_complete_round_with_base_and_special_bonus(self):
        """
        Complete round scenario:
        - Round has 5/10/K cards (base score)
        - Winning play is K Tongzi (special bonus)
        - Winner gets both base score AND special bonus
        """
        # Round cards from all players
        round_cards = [
            # Player A plays pair of 5s
            Card(Suit.SPADES, Rank.FIVE),
            Card(Suit.HEARTS, Rank.FIVE),
            # Player B plays K Tongzi (and wins)
            Card(Suit.SPADES, Rank.KING),
            Card(Suit.SPADES, Rank.KING),
            Card(Suit.SPADES, Rank.KING),
        ]

        # Base score
        base_event = self.engine.create_round_win_event(
            player_id="Player_B", round_cards=round_cards, round_number=1
        )

        # Special bonus
        k_tongzi_pattern = PatternRecognizer.analyze_cards(round_cards[2:5])
        special_events = self.engine.create_special_bonus_events(
            player_id="Player_B",
            winning_pattern=k_tongzi_pattern,
            round_number=1,
            is_round_winning_play=True,
        )

        # Verify
        assert base_event.points == 40  # 5+5+10+10+10 = 40
        assert len(special_events) == 1
        assert special_events[0].points == 100

        # Total score for Player B
        total = self.engine.calculate_total_score_for_player("Player_B")
        assert total == 140  # 40 + 100 = 140

    def test_multiple_rounds_accumulate_correctly(self):
        """Multiple rounds accumulate scores correctly."""
        # Round 1: Player A wins with 10 points
        round1_cards = [Card(Suit.SPADES, Rank.TEN)]
        self.engine.create_round_win_event("Player_A", round1_cards, 1)

        # Round 2: Player B wins with 20 points
        round2_cards = [
            Card(Suit.HEARTS, Rank.TEN),
            Card(Suit.CLUBS, Rank.TEN),
        ]
        self.engine.create_round_win_event("Player_B", round2_cards, 2)

        # Round 3: Player A wins with 15 points
        round3_cards = [
            Card(Suit.SPADES, Rank.FIVE),
            Card(Suit.HEARTS, Rank.FIVE),
            Card(Suit.CLUBS, Rank.FIVE),
        ]
        self.engine.create_round_win_event("Player_A", round3_cards, 3)

        assert self.engine.calculate_total_score_for_player("Player_A") == 25  # 10 + 15
        assert self.engine.calculate_total_score_for_player("Player_B") == 20
        assert self.engine.calculate_total_score_for_player("Player_C") == 0

    # ==================== Edge Cases ====================

    def test_scoring_events_recorded_correctly(self):
        """All scoring events are recorded in engine history."""
        # Create 3 events
        self.engine.create_round_win_event(
            "Player_A", [Card(Suit.SPADES, Rank.FIVE)], 1
        )

        k_tongzi = [
            Card(Suit.SPADES, Rank.KING),
            Card(Suit.SPADES, Rank.KING),
            Card(Suit.SPADES, Rank.KING),
        ]
        pattern = PatternRecognizer.analyze_cards(k_tongzi)
        self.engine.create_special_bonus_events("Player_B", pattern, 2, True)

        self.engine.create_finish_bonus_events(["Player_A", "Player_B", "Player_C"])

        # Should have 5 events: 1 round + 1 tongzi + 3 finish
        assert len(self.engine.scoring_events) == 5

    def test_validate_scores_consistency(self):
        """Score validation works correctly."""
        # Create some events
        self.engine.create_round_win_event("Player_A", [Card(Suit.SPADES, Rank.TEN)], 1)

        # Correct scores
        assert self.engine.validate_scores({"Player_A": 10, "Player_B": 0})

        # Incorrect scores
        assert not self.engine.validate_scores({"Player_A": 20, "Player_B": 0})


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

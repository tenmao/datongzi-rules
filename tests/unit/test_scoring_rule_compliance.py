"""
Critical tests for scoring rule compliance.

These tests verify the most important rule from GAME_RULE.md:
"只有一轮牌的最后一手牌才能计算分数，假如A出牌K筒子，B出牌A筒子，
假如其他玩家没有比该A筒子更大的手牌，那么B得到该200分，A不得分。"
"""

from datongzi_rules import (
    Card,
    Rank,
    Suit,
    ConfigFactory,
    ScoreComputation,
    PatternRecognizer,
    PlayType,
)


def test_tongzi_bonus_only_for_round_winning_play():
    """
    Test that Tongzi bonus is only awarded to round-winning play.

    Scenario: Player A plays K Tongzi, Player B beats it with A Tongzi.
    Expected: Only Player B gets the bonus (200 points), Player A gets nothing.
    """
    config = ConfigFactory.create_standard_3deck_3player()
    engine = ScoreComputation(config)

    # Player A plays K Tongzi (NOT round winning)
    k_tongzi_cards = [
        Card(Suit.SPADES, Rank.KING),
        Card(Suit.SPADES, Rank.KING),
        Card(Suit.SPADES, Rank.KING),
    ]
    k_tongzi_pattern = PatternRecognizer.analyze_cards(k_tongzi_cards)
    assert k_tongzi_pattern.play_type == PlayType.TONGZI

    # Create special bonus event with is_round_winning_play=False
    events_a = engine.create_special_bonus_events(
        "player_a",
        k_tongzi_pattern,
        round_number=1,
        is_round_winning_play=False  # NOT the winning play
    )

    # Player A should get NO bonus
    assert len(events_a) == 0
    assert engine.calculate_total_score_for_player("player_a") == 0

    # Player B plays A Tongzi (round winning)
    a_tongzi_cards = [
        Card(Suit.SPADES, Rank.ACE),
        Card(Suit.SPADES, Rank.ACE),
        Card(Suit.SPADES, Rank.ACE),
    ]
    a_tongzi_pattern = PatternRecognizer.analyze_cards(a_tongzi_cards)
    assert a_tongzi_pattern.play_type == PlayType.TONGZI

    # Create special bonus event with is_round_winning_play=True
    events_b = engine.create_special_bonus_events(
        "player_b",
        a_tongzi_pattern,
        round_number=1,
        is_round_winning_play=True  # This IS the winning play
    )

    # Player B should get 200 points
    assert len(events_b) == 1
    assert events_b[0].points == 200
    assert engine.calculate_total_score_for_player("player_b") == 200

    print("✓ Tongzi bonus only for round winning play test passed")


def test_dizha_bonus_only_for_round_winning_play():
    """
    Test that Dizha bonus is only awarded to round-winning play.
    """
    config = ConfigFactory.create_standard_3deck_3player()
    engine = ScoreComputation(config)

    # Player A plays King Dizha (NOT round winning)
    k_dizha_cards = [
        Card(Suit.SPADES, Rank.KING),
        Card(Suit.SPADES, Rank.KING),
        Card(Suit.HEARTS, Rank.KING),
        Card(Suit.HEARTS, Rank.KING),
        Card(Suit.CLUBS, Rank.KING),
        Card(Suit.CLUBS, Rank.KING),
        Card(Suit.DIAMONDS, Rank.KING),
        Card(Suit.DIAMONDS, Rank.KING),
    ]
    k_dizha_pattern = PatternRecognizer.analyze_cards(k_dizha_cards)
    assert k_dizha_pattern.play_type == PlayType.DIZHA

    # NOT the winning play
    events_a = engine.create_special_bonus_events(
        "player_a",
        k_dizha_pattern,
        round_number=1,
        is_round_winning_play=False
    )

    # Player A should get NO bonus
    assert len(events_a) == 0
    assert engine.calculate_total_score_for_player("player_a") == 0

    # Player B plays Ace Dizha (round winning)
    a_dizha_cards = [
        Card(Suit.SPADES, Rank.ACE),
        Card(Suit.SPADES, Rank.ACE),
        Card(Suit.HEARTS, Rank.ACE),
        Card(Suit.HEARTS, Rank.ACE),
        Card(Suit.CLUBS, Rank.ACE),
        Card(Suit.CLUBS, Rank.ACE),
        Card(Suit.DIAMONDS, Rank.ACE),
        Card(Suit.DIAMONDS, Rank.ACE),
    ]
    a_dizha_pattern = PatternRecognizer.analyze_cards(a_dizha_cards)
    assert a_dizha_pattern.play_type == PlayType.DIZHA

    # This IS the winning play
    events_b = engine.create_special_bonus_events(
        "player_b",
        a_dizha_pattern,
        round_number=1,
        is_round_winning_play=True
    )

    # Player B should get 400 points
    assert len(events_b) == 1
    assert events_b[0].points == 400
    assert engine.calculate_total_score_for_player("player_b") == 400

    print("✓ Dizha bonus only for round winning play test passed")


def test_multiple_tongzi_in_same_round():
    """
    Test scenario with multiple Tongzi plays in same round.

    Scenario:
    - Round 1: A plays K Tongzi (100), B plays A Tongzi (200)
    - Expected: Only B gets 200, A gets 0
    """
    config = ConfigFactory.create_standard_3deck_3player()
    engine = ScoreComputation(config)

    # Player A plays K Tongzi (middle of round)
    k_tongzi = PatternRecognizer.analyze_cards([
        Card(Suit.SPADES, Rank.KING),
        Card(Suit.SPADES, Rank.KING),
        Card(Suit.SPADES, Rank.KING),
    ])

    engine.create_special_bonus_events(
        "player_a",
        k_tongzi,
        round_number=1,
        is_round_winning_play=False
    )

    # Player B plays A Tongzi (wins round)
    a_tongzi = PatternRecognizer.analyze_cards([
        Card(Suit.HEARTS, Rank.ACE),
        Card(Suit.HEARTS, Rank.ACE),
        Card(Suit.HEARTS, Rank.ACE),
    ])

    engine.create_special_bonus_events(
        "player_b",
        a_tongzi,
        round_number=1,
        is_round_winning_play=True
    )

    # Verify scores
    assert engine.calculate_total_score_for_player("player_a") == 0
    assert engine.calculate_total_score_for_player("player_b") == 200

    # Player B should have only one event
    player_b_events = [
        e for e in engine.scoring_events if e.player_id == "player_b"
    ]
    assert len(player_b_events) == 1
    assert player_b_events[0].points == 200

    print("✓ Multiple Tongzi in same round test passed")


def test_backward_compatibility_default_true():
    """
    Test that default behavior (is_round_winning_play=True) maintains
    backward compatibility.
    """
    config = ConfigFactory.create_standard_3deck_3player()
    engine = ScoreComputation(config)

    # Call without is_round_winning_play parameter (should default to True)
    tongzi = PatternRecognizer.analyze_cards([
        Card(Suit.SPADES, Rank.ACE),
        Card(Suit.SPADES, Rank.ACE),
        Card(Suit.SPADES, Rank.ACE),
    ])

    events = engine.create_special_bonus_events(
        "player_a",
        tongzi,
        round_number=1
        # is_round_winning_play not specified - should default to True
    )

    # Should get bonus (backward compatibility)
    assert len(events) == 1
    assert events[0].points == 200

    print("✓ Backward compatibility test passed")


def test_all_tongzi_ranks():
    """Test all Tongzi ranks get correct bonuses when winning."""
    config = ConfigFactory.create_standard_3deck_3player()
    engine = ScoreComputation(config)

    # K Tongzi = 100
    k_tongzi = PatternRecognizer.analyze_cards([
        Card(Suit.DIAMONDS, Rank.KING),
        Card(Suit.DIAMONDS, Rank.KING),
        Card(Suit.DIAMONDS, Rank.KING),
    ])
    events_k = engine.create_special_bonus_events(
        "player1", k_tongzi, 1, is_round_winning_play=True
    )
    assert len(events_k) == 1
    assert events_k[0].points == 100

    # A Tongzi = 200
    a_tongzi = PatternRecognizer.analyze_cards([
        Card(Suit.CLUBS, Rank.ACE),
        Card(Suit.CLUBS, Rank.ACE),
        Card(Suit.CLUBS, Rank.ACE),
    ])
    events_a = engine.create_special_bonus_events(
        "player2", a_tongzi, 2, is_round_winning_play=True
    )
    assert len(events_a) == 1
    assert events_a[0].points == 200

    # 2 Tongzi = 300
    two_tongzi = PatternRecognizer.analyze_cards([
        Card(Suit.HEARTS, Rank.TWO),
        Card(Suit.HEARTS, Rank.TWO),
        Card(Suit.HEARTS, Rank.TWO),
    ])
    events_two = engine.create_special_bonus_events(
        "player3", two_tongzi, 3, is_round_winning_play=True
    )
    assert len(events_two) == 1
    assert events_two[0].points == 300

    # Verify all scores
    assert engine.calculate_total_score_for_player("player1") == 100
    assert engine.calculate_total_score_for_player("player2") == 200
    assert engine.calculate_total_score_for_player("player3") == 300

    print("✓ All Tongzi ranks test passed")


def test_non_special_patterns_not_affected():
    """
    Test that non-Tongzi/Dizha patterns are not affected by the
    is_round_winning_play parameter.
    """
    config = ConfigFactory.create_standard_3deck_3player()
    engine = ScoreComputation(config)

    # Regular bomb should not create special bonus events
    bomb = PatternRecognizer.analyze_cards([
        Card(Suit.SPADES, Rank.KING),
        Card(Suit.HEARTS, Rank.KING),
        Card(Suit.CLUBS, Rank.KING),
        Card(Suit.DIAMONDS, Rank.KING),
    ])
    assert bomb.play_type == PlayType.BOMB

    # Should return empty list regardless of is_round_winning_play
    events_true = engine.create_special_bonus_events(
        "player_a", bomb, 1, is_round_winning_play=True
    )
    events_false = engine.create_special_bonus_events(
        "player_b", bomb, 1, is_round_winning_play=False
    )

    assert len(events_true) == 0
    assert len(events_false) == 0

    print("✓ Non-special patterns not affected test passed")

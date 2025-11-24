"""Unit tests for scoring engine."""

from datongzi_rules import (
    BonusType,
    Card,
    GameConfig,
    PatternRecognizer,
    PlayType,
    Rank,
    ScoreComputation,
    ScoringEvent,
    Suit,
)


def test_calculate_round_base_score():
    """Test basic round score calculation from scoring cards."""
    config = GameConfig()
    engine = ScoreComputation(config)

    # Cards with different scores
    cards = [
        Card(Suit.SPADES, Rank.FIVE),  # 5 points
        Card(Suit.HEARTS, Rank.TEN),  # 10 points
        Card(Suit.CLUBS, Rank.KING),  # 10 points
        Card(Suit.DIAMONDS, Rank.SIX),  # 0 points
    ]

    score = engine.calculate_round_base_score(cards)
    assert score == 25, f"Expected 25, got {score}"
    print("✓ Round base score calculation test passed")


def test_calculate_round_base_score_no_scoring_cards():
    """Test round score with no scoring cards."""
    config = GameConfig()
    engine = ScoreComputation(config)

    cards = [
        Card(Suit.SPADES, Rank.SIX),
        Card(Suit.HEARTS, Rank.SEVEN),
        Card(Suit.CLUBS, Rank.EIGHT),
    ]

    score = engine.calculate_round_base_score(cards)
    assert score == 0, f"Expected 0, got {score}"
    print("✓ Round score with no scoring cards test passed")


def test_create_round_win_event():
    """Test creating round win event."""
    config = GameConfig()
    engine = ScoreComputation(config)

    cards = [
        Card(Suit.SPADES, Rank.FIVE),
        Card(Suit.HEARTS, Rank.TEN),
    ]

    event = engine.create_round_win_event("player1", cards, round_number=1)

    assert event is not None
    assert event.player_id == "player1"
    assert event.bonus_type == BonusType.ROUND_WIN
    assert event.points == 15
    assert event.round_number == 1
    assert len(event.cards_involved) == 2
    print("✓ Round win event creation test passed")


def test_create_round_win_event_no_points():
    """Test round win event returns None when no scoring cards."""
    config = GameConfig()
    engine = ScoreComputation(config)

    cards = [Card(Suit.SPADES, Rank.SIX)]

    event = engine.create_round_win_event("player1", cards, round_number=1)

    assert event is None
    print("✓ Round win event with no points test passed")


def test_create_tongzi_bonus_k():
    """Test K Tongzi bonus event."""
    config = GameConfig()
    engine = ScoreComputation(config)

    # Create K Tongzi pattern (3 cards, same suit, same rank)
    cards = [
        Card(Suit.SPADES, Rank.KING),
        Card(Suit.SPADES, Rank.KING),
        Card(Suit.SPADES, Rank.KING),
    ]
    pattern = PatternRecognizer.analyze_cards(cards)
    assert pattern.play_type == PlayType.TONGZI

    events = engine.create_special_bonus_events("player1", pattern, round_number=1)

    assert len(events) == 1
    assert events[0].player_id == "player1"
    assert events[0].bonus_type == BonusType.K_TONGZI
    assert events[0].points == 100
    print("✓ K Tongzi bonus test passed")


def test_create_tongzi_bonus_a():
    """Test A Tongzi bonus event."""
    config = GameConfig()
    engine = ScoreComputation(config)

    cards = [
        Card(Suit.HEARTS, Rank.ACE),
        Card(Suit.HEARTS, Rank.ACE),
        Card(Suit.HEARTS, Rank.ACE),
    ]
    pattern = PatternRecognizer.analyze_cards(cards)

    events = engine.create_special_bonus_events("player1", pattern, round_number=1)

    assert len(events) == 1
    assert events[0].bonus_type == BonusType.A_TONGZI
    assert events[0].points == 200
    print("✓ A Tongzi bonus test passed")


def test_create_tongzi_bonus_two():
    """Test 2 Tongzi bonus event."""
    config = GameConfig()
    engine = ScoreComputation(config)

    cards = [
        Card(Suit.CLUBS, Rank.TWO),
        Card(Suit.CLUBS, Rank.TWO),
        Card(Suit.CLUBS, Rank.TWO),
    ]
    pattern = PatternRecognizer.analyze_cards(cards)

    events = engine.create_special_bonus_events("player1", pattern, round_number=1)

    assert len(events) == 1
    assert events[0].bonus_type == BonusType.TWO_TONGZI
    assert events[0].points == 300
    print("✓ 2 Tongzi bonus test passed")


def test_create_dizha_bonus():
    """Test Dizha bonus event."""
    config = GameConfig()
    engine = ScoreComputation(config)

    # Create Dizha pattern (8 cards, 2 of each suit for same rank)
    cards = [
        Card(Suit.SPADES, Rank.TEN),
        Card(Suit.SPADES, Rank.TEN),
        Card(Suit.HEARTS, Rank.TEN),
        Card(Suit.HEARTS, Rank.TEN),
        Card(Suit.CLUBS, Rank.TEN),
        Card(Suit.CLUBS, Rank.TEN),
        Card(Suit.DIAMONDS, Rank.TEN),
        Card(Suit.DIAMONDS, Rank.TEN),
    ]
    pattern = PatternRecognizer.analyze_cards(cards)
    assert pattern.play_type == PlayType.DIZHA

    events = engine.create_special_bonus_events("player1", pattern, round_number=1)

    assert len(events) == 1
    assert events[0].bonus_type == BonusType.DIZHA
    assert events[0].points == 400
    print("✓ Dizha bonus test passed")


def test_create_finish_bonus_events():
    """Test finish position bonus events."""
    config = GameConfig()
    engine = ScoreComputation(config)

    player_ids = ["player1", "player2", "player3"]

    events = engine.create_finish_bonus_events(player_ids)

    assert len(events) == 3

    # First place (上游)
    assert events[0].player_id == "player1"
    assert events[0].bonus_type == BonusType.FINISH_FIRST
    assert events[0].points == 100

    # Second place (二游)
    assert events[1].player_id == "player2"
    assert events[1].bonus_type == BonusType.FINISH_SECOND
    assert events[1].points == -40

    # Third place (三游)
    assert events[2].player_id == "player3"
    assert events[2].bonus_type == BonusType.FINISH_THIRD
    assert events[2].points == -60

    print("✓ Finish bonus events test passed")


def test_calculate_total_score_for_player():
    """Test calculating total score from multiple events."""
    config = GameConfig()
    engine = ScoreComputation(config)

    # Create some events manually
    engine.scoring_events = [
        ScoringEvent("player1", BonusType.ROUND_WIN, 15, "Round 1"),
        ScoringEvent("player1", BonusType.K_TONGZI, 100, "K Tongzi"),
        ScoringEvent("player2", BonusType.ROUND_WIN, 25, "Round 2"),
        ScoringEvent("player1", BonusType.FINISH_FIRST, 100, "First place"),
    ]

    score1 = engine.calculate_total_score_for_player("player1")
    score2 = engine.calculate_total_score_for_player("player2")

    assert score1 == 215, f"Expected 215, got {score1}"
    assert score2 == 25, f"Expected 25, got {score2}"
    print("✓ Total score calculation test passed")


def test_validate_scores_correct():
    """Test score validation with correct scores."""
    config = GameConfig()
    engine = ScoreComputation(config)

    engine.scoring_events = [
        ScoringEvent("player1", BonusType.ROUND_WIN, 15, "Round 1"),
        ScoringEvent("player2", BonusType.ROUND_WIN, 25, "Round 2"),
    ]

    player_scores = {"player1": 15, "player2": 25}

    assert engine.validate_scores(player_scores) is True
    print("✓ Score validation (correct) test passed")


def test_validate_scores_incorrect():
    """Test score validation with incorrect scores."""
    config = GameConfig()
    engine = ScoreComputation(config)

    engine.scoring_events = [
        ScoringEvent("player1", BonusType.ROUND_WIN, 15, "Round 1"),
        ScoringEvent("player2", BonusType.ROUND_WIN, 25, "Round 2"),
    ]

    player_scores = {"player1": 20, "player2": 25}  # player1 score wrong

    assert engine.validate_scores(player_scores) is False
    print("✓ Score validation (incorrect) test passed")


def test_get_game_summary():
    """Test generating comprehensive game summary."""
    config = GameConfig()
    engine = ScoreComputation(config)

    # Simulate a game with various events
    engine.scoring_events = [
        ScoringEvent("player1", BonusType.ROUND_WIN, 15, "Round 1 win", round_number=1),
        ScoringEvent("player1", BonusType.K_TONGZI, 100, "K Tongzi", round_number=1),
        ScoringEvent("player2", BonusType.ROUND_WIN, 25, "Round 2 win", round_number=2),
        ScoringEvent("player1", BonusType.FINISH_FIRST, 100, "First place"),
        ScoringEvent("player2", BonusType.FINISH_SECOND, -40, "Second place"),
        ScoringEvent("player3", BonusType.FINISH_THIRD, -60, "Third place"),
    ]

    player_ids = ["player1", "player2", "player3"]
    summary = engine.get_game_summary(player_ids)

    # Check final scores
    assert summary["final_scores"]["player1"] == 215
    assert summary["final_scores"]["player2"] == -15
    assert summary["final_scores"]["player3"] == -60

    # Check winner
    assert summary["winner_id"] == "player1"

    # Check total events
    assert summary["total_events"] == 6

    # Check events by type
    assert "round_win" in summary["events_by_type"]
    assert len(summary["events_by_type"]["round_win"]) == 2

    # Check events by player
    assert len(summary["events_by_player"]["player1"]["events"]) == 3
    assert summary["events_by_player"]["player1"]["total_score"] == 215

    # Check round breakdown
    assert "round_1" in summary["round_breakdown"]
    assert len(summary["round_breakdown"]["round_1"]) == 2

    print("✓ Game summary generation test passed")


def test_custom_config_bonuses():
    """Test scoring with custom bonus configuration."""
    config = GameConfig(
        k_tongzi_bonus=150,
        a_tongzi_bonus=250,
        two_tongzi_bonus=350,
        dizha_bonus=500,
        finish_bonus=[200, -50, -150],
    )
    engine = ScoreComputation(config)

    # Test K Tongzi with custom bonus (3 cards, same suit)
    cards = [
        Card(Suit.SPADES, Rank.KING),
        Card(Suit.SPADES, Rank.KING),
        Card(Suit.SPADES, Rank.KING),
    ]
    pattern = PatternRecognizer.analyze_cards(cards)
    events = engine.create_special_bonus_events("player1", pattern, round_number=1)

    assert len(events) == 1
    assert events[0].points == 150

    # Test finish bonuses with custom values
    finish_events = engine.create_finish_bonus_events(["p1", "p2", "p3"])
    assert finish_events[0].points == 200
    assert finish_events[1].points == -50
    assert finish_events[2].points == -150

    print("✓ Custom config bonuses test passed")


def test_scoring_event_dataclass():
    """Test ScoringEvent dataclass properties."""
    event = ScoringEvent(
        player_id="player1",
        bonus_type=BonusType.ROUND_WIN,
        points=25,
        reason="Won round with 25 points",
        round_number=1,
        cards_involved=["♠5", "♥10", "♣K"],
    )

    assert event.player_id == "player1"
    assert event.bonus_type == BonusType.ROUND_WIN
    assert event.points == 25
    assert event.round_number == 1
    assert len(event.cards_involved) == 3
    print("✓ ScoringEvent dataclass test passed")


# All tests can be run with pytest
# pytest will autodiscover all test_* functions

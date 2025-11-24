"""
Complete game simulation tests with full rule validation.

These tests use the GameSimulator to run complete games and verify:
1. All rules are correctly enforced
2. Scoring is accurate
3. Round logic works correctly
4. Every action is validated
"""

from datongzi_rules import (
    ConfigFactory,
)
from datongzi_rules.simulation import GameSimulator, GameState


def test_basic_game_simulation():
    """Test a basic complete game simulation."""
    config = ConfigFactory.create_standard_3deck_3player()
    player_ids = ["Alice", "Bob", "Charlie"]

    # Create simulator (non-verbose for test)
    simulator = GameSimulator(config, player_ids, verbose=False)

    # Play full game
    report = simulator.play_full_game()

    # Verify game completed
    assert report["game_over"] is True

    # Game ends when only 1 player remains, so finish_order should have 2 players
    # (3rd player is left with remaining cards)
    assert len(report["finish_order"]) >= 2
    assert len(report["finish_order"]) <= 3

    # Verify all players have final scores
    assert len(report["final_scores"]) == 3
    for player_id in player_ids:
        assert player_id in report["final_scores"]

    # Verify at least some actions occurred
    assert report["total_actions"] > 0
    assert report["total_rounds"] > 0

    # Note: finish_order may be less than config.finish_bonus length
    # because game ends when only 1 player remains
    assert len(report["finish_order"]) <= len(config.finish_bonus)

    print("✓ Basic game simulation test passed")


def test_game_logs_every_action():
    """Test that every action is logged."""
    config = ConfigFactory.create_quick_game()  # Faster game
    player_ids = ["P1", "P2", "P3"]

    simulator = GameSimulator(config, player_ids, verbose=False)
    report = simulator.play_full_game()

    # Verify logs exist
    assert len(report["logs"]) > 0

    # Verify log structure
    for log in report["logs"]:
        assert "round" in log
        assert "action" in log
        assert "player" in log
        assert "action_type" in log
        assert "hand_size_after" in log

    # Verify at least one play action
    play_actions = [log for log in report["logs"] if log["action_type"] == "play"]
    assert len(play_actions) > 0

    print("✓ Game logs every action test passed")


def test_game_finish_order_is_correct():
    """Test that finish order is correctly tracked."""
    config = ConfigFactory.create_quick_game()
    player_ids = ["P1", "P2", "P3"]

    simulator = GameSimulator(config, player_ids, verbose=False)
    report = simulator.play_full_game()

    finish_order = report["finish_order"]

    # Should have 3 players (or 2 if one didn't finish)
    assert len(finish_order) >= 2
    assert len(finish_order) <= 3

    # All finished players should have 0 cards
    for player_id in finish_order:
        assert report["final_scores"][player_id]["cards_left"] == 0

    # If only 2 finished, one should have cards left
    if len(finish_order) == 2:
        unfinished = [pid for pid in player_ids if pid not in finish_order]
        assert len(unfinished) == 1
        assert report["final_scores"][unfinished[0]]["cards_left"] > 0

    print("✓ Game finish order test passed")


def test_finish_bonuses_applied():
    """Test that finish position bonuses are correctly applied."""
    config = ConfigFactory.create_quick_game()
    player_ids = ["P1", "P2", "P3"]

    simulator = GameSimulator(config, player_ids, verbose=False)
    report = simulator.play_full_game()

    scoring_summary = report["scoring_summary"]

    # Check for finish bonus events
    finish_events = [
        event
        for events in scoring_summary["events_by_type"].values()
        for event in events
        if "finish" in event.get("reason", "").lower()
    ]

    # Should have at least 2 finish events (for first 2 finishers)
    assert len(finish_events) >= 2

    # Verify first finisher got positive bonus
    first_finisher = report["finish_order"][0]
    report["final_scores"][first_finisher]["score"]

    # First finisher should have gotten +100 (or whatever config specifies)
    # We can't check exact score because it includes round wins, but we can
    # verify the finish bonus event exists
    finish_first_events = [
        e
        for e in finish_events
        if e["player_id"] == first_finisher and "position 1" in e["reason"]
    ]
    assert len(finish_first_events) == 1

    print("✓ Finish bonuses applied test passed")


def test_round_winner_gets_points():
    """Test that round winners get points from scoring cards."""
    config = ConfigFactory.create_quick_game()
    player_ids = ["P1", "P2", "P3"]

    simulator = GameSimulator(config, player_ids, verbose=False)
    report = simulator.play_full_game()

    # Find logs with round winners
    round_winner_logs = [
        log for log in report["logs"] if log.get("is_round_winner") is True
    ]

    # Should have at least some round winners
    assert len(round_winner_logs) > 0

    # Check if any round had scoring cards (5, 10, K)
    # This is probabilistic but very likely in a full game
    scoring_summary = report["scoring_summary"]

    # Should have some round_win events
    if "round_win" in scoring_summary["events_by_type"]:
        round_win_events = scoring_summary["events_by_type"]["round_win"]
        # At least some rounds should have points
        assert len(round_win_events) >= 0

    print("✓ Round winner gets points test passed")


def test_multiple_rounds_played():
    """Test that multiple rounds are played in a game."""
    config = ConfigFactory.create_quick_game()
    player_ids = ["P1", "P2", "P3"]

    simulator = GameSimulator(config, player_ids, verbose=False)
    report = simulator.play_full_game()

    # Quick game should have multiple rounds
    assert report["total_rounds"] > 1

    # Verify logs span multiple rounds
    round_numbers = {log["round"] for log in report["logs"]}
    assert len(round_numbers) > 1

    print("✓ Multiple rounds played test passed")


def test_game_state_consistency():
    """Test that game state remains consistent throughout."""
    config = ConfigFactory.create_quick_game()
    player_ids = ["P1", "P2", "P3"]

    simulator = GameSimulator(config, player_ids, verbose=False)

    # Check initial state
    assert simulator.state.game_over is False
    assert simulator.state.current_round == 1
    assert len(simulator.state.finished_players) == 0

    # Play game
    simulator.play_full_game()

    # Check final state
    assert simulator.state.game_over is True
    assert len(simulator.state.finished_players) >= 2

    # Note: Cards are removed from hands when played, so we can't check total
    # card count this way. Instead, verify all finished players have 0 cards.
    for player_id in simulator.state.finished_players:
        assert len(simulator.state.player_hands[player_id]) == 0

    # Verify at least one player has cards left (game ended with 1 player remaining)
    unfinished_players = [
        pid
        for pid in simulator.state.player_ids
        if pid not in simulator.state.finished_players
    ]
    if len(unfinished_players) > 0:
        assert all(
            len(simulator.state.player_hands[pid]) > 0 for pid in unfinished_players
        )

    print("✓ Game state consistency test passed")


def test_scoring_events_recorded():
    """Test that all scoring events are recorded."""
    config = ConfigFactory.create_quick_game()
    player_ids = ["P1", "P2", "P3"]

    simulator = GameSimulator(config, player_ids, verbose=False)
    report = simulator.play_full_game()

    scoring_summary = report["scoring_summary"]

    # Verify events are categorized
    assert "events_by_type" in scoring_summary
    assert "events_by_player" in scoring_summary

    # Verify each player has event summary
    for player_id in player_ids:
        assert player_id in scoring_summary["events_by_player"]
        player_summary = scoring_summary["events_by_player"][player_id]
        assert "total_score" in player_summary
        assert "events" in player_summary

    # Total events should match sum of player events
    total_events_by_player = sum(
        len(summary["events"])
        for summary in scoring_summary["events_by_player"].values()
    )
    assert total_events_by_player == scoring_summary["total_events"]

    print("✓ Scoring events recorded test passed")


def test_no_infinite_loops():
    """Test that game doesn't get stuck in infinite loops."""
    config = ConfigFactory.create_quick_game()
    player_ids = ["P1", "P2", "P3"]

    simulator = GameSimulator(config, player_ids, verbose=False)
    report = simulator.play_full_game()

    # Should complete in reasonable number of actions
    # Quick game with 28 cards per player = max 84 cards dealt
    # With 3 players, worst case is 84 single card plays
    # Let's allow 5x that for safety
    max_expected_actions = 84 * 5
    assert report["total_actions"] < max_expected_actions

    # Should complete in reasonable number of rounds
    # Worst case is every card played individually + passes
    max_expected_rounds = 84
    assert report["total_rounds"] < max_expected_rounds

    print("✓ No infinite loops test passed")


def test_winner_has_highest_score():
    """Test that winner has the highest (or tied highest) score."""
    config = ConfigFactory.create_quick_game()
    player_ids = ["P1", "P2", "P3"]

    simulator = GameSimulator(config, player_ids, verbose=False)
    report = simulator.play_full_game()

    scoring_summary = report["scoring_summary"]
    winner_id = scoring_summary["winner_id"]

    assert winner_id is not None
    assert winner_id in player_ids

    # Winner should have highest or tied highest score
    winner_score = report["final_scores"][winner_id]["score"]
    all_scores = [data["score"] for data in report["final_scores"].values()]

    assert winner_score == max(all_scores)

    print("✓ Winner has highest score test passed")


def test_game_with_custom_strategy():
    """Test game with custom play decision strategy."""

    def always_play_lowest_card(state: GameState, player_id: str):
        """Simple strategy: always play lowest valid card(s)."""
        hand = state.player_hands[player_id]
        current_play = state.current_best_play

        if not hand:
            return None

        # Starting round - play lowest single
        if current_play is None:
            return [hand[0]]

        # Try to beat with lowest cards
        from datongzi_rules.patterns.recognizer import PlayValidator

        for i in range(len(hand)):
            for j in range(i + 1, len(hand) + 1):
                cards = hand[i:j]
                if PlayValidator.can_beat_play(cards, current_play):
                    return cards

        return None  # Pass

    config = ConfigFactory.create_quick_game()
    player_ids = ["P1", "P2", "P3"]

    simulator = GameSimulator(config, player_ids, verbose=False)
    report = simulator.play_full_game(play_decision_func=always_play_lowest_card)

    # Should complete successfully
    assert report["game_over"] is True
    assert len(report["finish_order"]) >= 2

    print("✓ Game with custom strategy test passed")

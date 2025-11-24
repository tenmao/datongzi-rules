//! Integration tests for scoring system

use datongzi_rules::{
    BonusType, Card, GameConfig, PlayPattern, PlayType, Rank, ScoreComputation, Suit,
};

#[test]
fn test_complete_game_scoring_flow() {
    let config = GameConfig::default();
    let mut engine = ScoreComputation::new(config);

    // Round 1: Player1 wins with scoring cards and K Tongzi
    let round1_cards = vec![
        Card::new(Suit::Spades, Rank::Five),
        Card::new(Suit::Hearts, Rank::Ten),
        Card::new(Suit::Clubs, Rank::King),
        Card::new(Suit::Diamonds, Rank::Six),
    ];
    engine.create_round_win_event("player1".to_string(), &round1_cards, 1);

    let k_tongzi_pattern = PlayPattern::new(
        PlayType::Tongzi,
        Rank::King,
        Some(Suit::Spades),
        vec![],
        3,
        0,
    );
    engine.create_special_bonus_events("player1".to_string(), &k_tongzi_pattern, 1, true);

    // Round 2: Player2 wins with scoring cards
    let round2_cards = vec![
        Card::new(Suit::Spades, Rank::Ten),
        Card::new(Suit::Hearts, Rank::King),
    ];
    engine.create_round_win_event("player2".to_string(), &round2_cards, 2);

    // Round 3: Player3 wins with Dizha
    let dizha_pattern = PlayPattern::new(PlayType::Dizha, Rank::Ace, None, vec![], 8, 0);
    engine.create_special_bonus_events("player3".to_string(), &dizha_pattern, 3, true);

    // Finish bonuses
    let finish_order = vec![
        "player1".to_string(),
        "player2".to_string(),
        "player3".to_string(),
    ];
    engine.create_finish_bonus_events(&finish_order);

    // Verify scores
    let player1_score = engine.calculate_total_score_for_player("player1");
    let player2_score = engine.calculate_total_score_for_player("player2");
    let player3_score = engine.calculate_total_score_for_player("player3");

    // Player1: 25 (round1) + 100 (K Tongzi) + 100 (finish first) = 225
    assert_eq!(player1_score, 225);

    // Player2: 20 (round2) + (-40) (finish second) = -20
    assert_eq!(player2_score, -20);

    // Player3: 400 (Dizha) + (-60) (finish third) = 340
    assert_eq!(player3_score, 340);

    // Verify summary
    let summary = engine.get_game_summary(&finish_order);
    assert_eq!(summary.final_scores.get("player1"), Some(&225));
    assert_eq!(summary.final_scores.get("player2"), Some(&-20));
    assert_eq!(summary.final_scores.get("player3"), Some(&340));
    assert_eq!(summary.winner_id, Some("player3".to_string()));
    assert_eq!(summary.total_events, 7);
}

#[test]
fn test_round_winning_play_only_gets_bonus() {
    let config = GameConfig::default();
    let mut engine = ScoreComputation::new(config);

    let tongzi_pattern = PlayPattern::new(
        PlayType::Tongzi,
        Rank::Ace,
        Some(Suit::Hearts),
        vec![],
        3,
        0,
    );

    // Player1 plays A Tongzi but loses the round
    let events1 =
        engine.create_special_bonus_events("player1".to_string(), &tongzi_pattern, 1, false);
    assert_eq!(events1.len(), 0);

    // Player2 wins the round with A Tongzi
    let events2 =
        engine.create_special_bonus_events("player2".to_string(), &tongzi_pattern, 1, true);
    assert_eq!(events2.len(), 1);
    assert_eq!(events2[0].bonus_type, BonusType::ATongzi);
    assert_eq!(events2[0].points, 200);

    // Only player2 should have the bonus
    assert_eq!(engine.calculate_total_score_for_player("player1"), 0);
    assert_eq!(engine.calculate_total_score_for_player("player2"), 200);
}

#[test]
fn test_custom_scoring_configuration() {
    let config = GameConfig::new(
        3,
        4,
        32,
        0,
        vec![200, -50, -100, -150], // 4 player finish bonuses
        150,                        // K Tongzi
        250,                        // A Tongzi
        350,                        // 2 Tongzi
        500,                        // Dizha
    );
    let mut engine = ScoreComputation::new(config);

    // Test custom K Tongzi bonus
    let tongzi_pattern = PlayPattern::new(
        PlayType::Tongzi,
        Rank::King,
        Some(Suit::Spades),
        vec![],
        3,
        0,
    );
    let events =
        engine.create_special_bonus_events("player1".to_string(), &tongzi_pattern, 1, true);
    assert_eq!(events[0].points, 150);

    // Test custom finish bonuses
    let finish_order = vec![
        "p1".to_string(),
        "p2".to_string(),
        "p3".to_string(),
        "p4".to_string(),
    ];
    let finish_events = engine.create_finish_bonus_events(&finish_order);
    assert_eq!(finish_events[0].points, 200);
    assert_eq!(finish_events[1].points, -50);
    assert_eq!(finish_events[2].points, -100);
    assert_eq!(finish_events[3].points, -150);
}

#[test]
fn test_zero_score_round() {
    let config = GameConfig::default();
    let mut engine = ScoreComputation::new(config);

    // Round with no scoring cards
    let cards = vec![
        Card::new(Suit::Spades, Rank::Six),
        Card::new(Suit::Hearts, Rank::Seven),
    ];

    let event = engine.create_round_win_event("player1".to_string(), &cards, 1);
    assert!(event.is_none());

    // No events should be recorded
    assert_eq!(engine.scoring_events().len(), 0);
}
